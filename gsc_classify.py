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

GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
GSC_ROW_LIMIT = 25000

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

def classify(gsc_data):
    joined = {}
    for url, data in gsc_data.items():
        row = {
            "url": url,
            "slug": slug_from_url(url),
            "gsc_clicks": data["gsc_clicks"],
            "gsc_impressions": data["gsc_impressions"],
        }
        
        if row["gsc_impressions"] > 15:
            row["tier"] = "PILLAR"
        elif row["gsc_impressions"] > 0:
            row["tier"] = "WEAK"
        else:
            row["tier"] = "DEAD"
            
        joined[url] = row
    return joined

def write_outputs(joined, outdir, base_domain):
    os.makedirs(outdir, exist_ok=True)
    fieldnames = ["url", "slug", "tier", "gsc_clicks", "gsc_impressions"]

    csv_path = os.path.join(outdir, "gsc_classification.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(joined.values(), key=lambda r: (-r["gsc_impressions"], r["slug"])):
            writer.writerow({k: row.get(k, "") for k in fieldnames})

    pillar_slugs = [r["slug"] for r in joined.values() if r["tier"] == "PILLAR"]
    pillar_data = sorted([r for r in joined.values() if r["tier"] == "PILLAR"], key=lambda x: -x["gsc_impressions"])
    
    with open(os.path.join(outdir, "pillars_list.txt"), "w", encoding="utf-8") as f:
        for p in pillar_data:
            f.write(f"{p['slug']} - Impressions: {p['gsc_impressions']} | Clicks: {p['gsc_clicks']}\\n")
            
    print(f"\\n--- TOP PILLAR PAGES (GSC Impressions > 15) ---")
    for p in pillar_data:
        print(f"{p['slug'][:40]:<40} | Impr: {p['gsc_impressions']:<5} | Clicks: {p['gsc_clicks']:<5}")
    print(f"-----------------------------------------------")
    print(f"Total PILLAR pages: {len(pillar_slugs)}")
    print(f"Total WEAK pages: {len([r for r in joined.values() if r['tier'] == 'WEAK'])}")

def main():
    service_account = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
    gsc_site_url = "sc-domain:jobrecruitment.in"
    days = 90
    outdir = "./report"
    
    print(f"Fetching GSC data ({days}d lookback)...")
    gsc_data = fetch_gsc_page_performance(service_account, gsc_site_url, days)
    
    joined = classify(gsc_data)
    write_outputs(joined, outdir, "https://jobrecruitment.in")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    main()
