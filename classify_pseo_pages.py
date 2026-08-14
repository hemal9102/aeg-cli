import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import urlparse

from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GA4_SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

GSC_ROW_LIMIT = 25000  # API max per request; script paginates beyond this


def slug_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    path = re.sub(r"\.html?$", "", path)
    return path or "home"


def fetch_gsc_page_performance(service_account_path, site_url, days):
    creds = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=GSC_SCOPES
    )
    service = build("searchconsole", "v1", credentials=creds)

    end = date.today() - timedelta(days=3)  
    start = end - timedelta(days=days)

    results = {}
    start_row = 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": GSC_ROW_LIMIT,
            "startRow": start_row,
        }
        try:
            resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        except Exception as e:
            # Fallback to https://
            site_url = site_url.replace("sc-domain:", "https://") + "/"
            resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
            
        rows = resp.get("rows", [])
        if not rows:
            break
        for row in rows:
            url = row["keys"][0]
            results[url] = {
                "gsc_clicks": row.get("clicks", 0),
                "gsc_impressions": row.get("impressions", 0),
            }
        if len(rows) < GSC_ROW_LIMIT:
            break
        start_row += GSC_ROW_LIMIT

    return results


def fetch_ga4_page_engagement(service_account_path, property_id, days):
    creds = service_account.Credentials.from_service_account_file(
        service_account_path, scopes=GA4_SCOPES
    )
    client = BetaAnalyticsDataClient(credentials=creds)

    # Note: property ID should be in format "properties/12345"
    if not property_id.startswith("properties/"):
        property_id = f"properties/{property_id}"
        
    request = RunReportRequest(
        property=property_id,
        dimensions=[Dimension(name="pagePath")],
        metrics=[
            Metric(name="activeUsers"), # fallback for engagedSessions if not available
            Metric(name="userEngagementDuration"),
        ],
        date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
        limit=100000,
    )
    response = client.run_report(request)

    results = {}
    for row in response.rows:
        path = row.dimension_values[0].value
        engaged = int(row.metric_values[0].value or 0)
        duration = float(row.metric_values[1].value or 0)
        results[path] = {
            "ga4_engaged_sessions": engaged,
            "ga4_engagement_seconds": round(duration, 1),
            "ga4_conversions": 0,
        }
    return results


def classify(gsc_data, ga4_data, pillar_clicks, pillar_engagement, base_domain):
    joined = {}
    all_urls = set(gsc_data.keys())

    for url in all_urls:
        path = urlparse(url).path
        if not path: path = "/"
        
        g = gsc_data.get(url, {"gsc_clicks": 0, "gsc_impressions": 0})
        a = ga4_data.get(path, {
            "ga4_engaged_sessions": 0,
            "ga4_engagement_seconds": 0.0,
            "ga4_conversions": 0,
        })
        row = {
            "url": url,
            "slug": slug_from_url(url),
            **g,
            **a,
        }

        if row["gsc_clicks"] >= pillar_clicks and row["ga4_engaged_sessions"] >= pillar_engagement:
            row["tier"] = "PILLAR"
        elif row["gsc_impressions"] > 0 or row["ga4_engaged_sessions"] > 0:
            row["tier"] = "WEAK"
        else:
            row["tier"] = "DEAD"

        joined[url] = row

    for path, a in ga4_data.items():
        full_url = f"{base_domain.rstrip('/')}{path}"
        if full_url not in joined and path not in ("/",):
            row = {
                "url": full_url,
                "slug": slug_from_url(full_url),
                "gsc_clicks": 0,
                "gsc_impressions": 0,
                **a,
            }
            row["tier"] = "WEAK" if a["ga4_engaged_sessions"] > 0 else "DEAD"
            joined[full_url] = row

    return joined


def nearest_pillar_for_weak(weak_slug, pillar_slugs):
    if not pillar_slugs:
        return None
    weak_words = set(re.split(r"[-_]", weak_slug))
    best, best_score = None, -1
    for p in pillar_slugs:
        score = len(weak_words & set(re.split(r"[-_]", p)))
        if score > best_score:
            best, best_score = p, score
    return best


def write_outputs(joined, outdir, base_domain):
    os.makedirs(outdir, exist_ok=True)

    fieldnames = [
        "url", "slug", "tier",
        "gsc_clicks", "gsc_impressions",
        "ga4_engaged_sessions", "ga4_engagement_seconds", "ga4_conversions",
    ]

    csv_path = os.path.join(outdir, "pseo_classification.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(joined.values(), key=lambda r: (-r["gsc_clicks"], r["slug"])):
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    pillar_slugs = [r["slug"] for r in joined.values() if r["tier"] == "PILLAR"]
    weak_map = {}
    dead_list = []
    for r in joined.values():
        if r["tier"] == "WEAK":
            weak_map[r["slug"]] = nearest_pillar_for_weak(r["slug"], pillar_slugs)
        elif r["tier"] == "DEAD":
            dead_list.append(r["slug"])

    php_shaped = {
        "generated_for": base_domain,
        "pillar": sorted(pillar_slugs),
        "weak": weak_map,      
        "dead": sorted(dead_list),
    }
    json_path = os.path.join(outdir, "pseo_classification.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(php_shaped, f, indent=2, ensure_ascii=False)

    summary_path = os.path.join(outdir, "summary.txt")
    unmapped_weak = [s for s, target in weak_map.items() if target is None]
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(f"Total URLs classified: {len(joined)}\\n")
        f.write(f"  PILLAR (HTTP 200): {len(pillar_slugs)}\\n")
        f.write(f"  WEAK   (HTTP 301): {len(weak_map)}\\n")
        f.write(f"  DEAD   (HTTP 410): {len(dead_list)}\\n\\n")

    return csv_path, json_path, summary_path


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--service-account", required=True, help="Path to service account JSON key")
    ap.add_argument("--gsc-site-url", required=True, help="Exact property as verified in GSC")
    ap.add_argument("--ga4-property-id", required=True, help="e.g. 'properties/123456789'")
    ap.add_argument("--days", type=int, default=90, help="Lookback window in days (default 90)")
    ap.add_argument("--pillar-clicks", type=int, default=5, help="Min GSC clicks")
    ap.add_argument("--pillar-engagement", type=int, default=3, help="Min GA4 engaged sessions")
    ap.add_argument("--outdir", default="./report", help="Where to write CSV/JSON/summary")
    args = ap.parse_args()

    base_domain = f"https://jobrecruitment.in"

    print(f"Fetching GSC data ({args.days}d lookback)...", file=sys.stderr)
    gsc_data = fetch_gsc_page_performance(args.service_account, args.gsc_site_url, args.days)
    
    print(f"Fetching GA4 data ({args.days}d lookback)...", file=sys.stderr)
    ga4_data = fetch_ga4_page_engagement(args.service_account, args.ga4_property_id, args.days)

    joined = classify(gsc_data, ga4_data, args.pillar_clicks, args.pillar_engagement, base_domain)

    csv_path, json_path, summary_path = write_outputs(joined, args.outdir, base_domain)
    print(f"\\nDone. Review before wiring into pseo_traffic_controller.php:", file=sys.stderr)

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    main()
