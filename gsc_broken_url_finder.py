"""
FAST Multi-Site Broken URL Finder
─────────────────────────────────
Replaces slow GSC URL Inspection API (2000/day limit) with:
  Phase 1: Sitemap extraction from GSC
  Phase 2: Parallel HTTP status checks (15 workers) → ~30 sec per 1000 URLs
  Phase 3: GSC Search Analytics cross-ref → finds pages with 0 impressions (not indexed / invisible)

Total runtime: ~60 seconds per site instead of hours.
"""
import sys
import os
import time
import requests as http_requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_PATH = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
ROOT = r"C:\hk\DUMP\big_fish_SAGEO"

SITES = {
    "jobrecruitment": {
        "gsc_url": "https://jobrecruitment.in/",
        "domain": "jobrecruitment.in",
    },
    "techandcarsinfo": {
        "gsc_url": "https://techandcarsinfo.com/",
        "domain": "techandcarsinfo.com",
    },
}


def get_gsc_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=GSC_SCOPES
    )
    return build("searchconsole", "v1", credentials=creds)


# ═══════════════════════════════════════
#  PHASE 1: SITEMAP EXTRACTION
# ═══════════════════════════════════════

def fetch_sitemap_urls(url):
    urls = []
    try:
        r = http_requests.get(url, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.content)
        if root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex":
            for elem in root.findall("sm:sitemap/sm:loc", NS):
                urls.extend(fetch_sitemap_urls(elem.text.strip()))
        else:
            for loc in root.findall("sm:url/sm:loc", NS):
                if loc.text:
                    urls.append(loc.text.strip())
    except Exception as e:
        print(f"    [WARN] {url}: {e}")
    return urls


def extract_sitemaps(service, gsc_url, domain):
    print(f"  Fetching sitemaps from GSC...")
    try:
        resp = service.sitemaps().list(siteUrl=gsc_url).execute()
    except Exception:
        resp = {"sitemap": []}

    sitemaps = resp.get("sitemap", [])
    if not sitemaps:
        sitemaps = [{"path": f"https://{domain}/sitemap.xml"}]

    all_urls = []
    details = []
    for sm in sitemaps:
        sm_url = sm.get("path", sm.get("url", ""))
        urls = fetch_sitemap_urls(sm_url)
        print(f"    {sm_url} → {len(urls)} URLs")
        all_urls.extend(urls)
        details.append((sm_url, len(urls)))

    unique = sorted(set(all_urls))
    print(f"  Total unique: {len(unique)}")
    return unique, details


# ═══════════════════════════════════════
#  PHASE 2: FAST PARALLEL HTTP CHECKS
# ═══════════════════════════════════════

def check_http(url, timeout=10):
    try:
        r = http_requests.head(url, timeout=timeout, allow_redirects=True)
        return url, r.status_code, len(r.history) > 0, r.url if r.history else url
    except http_requests.exceptions.Timeout:
        return url, 0, False, "TIMEOUT"
    except http_requests.exceptions.ConnectionError:
        return url, 0, False, "CONNECTION_ERROR"
    except Exception as e:
        return url, 0, False, str(e)[:80]


def run_http_checks(urls):
    broken, redirects, ok = [], [], []
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(check_http, u): u for u in urls}
        done = 0
        for f in as_completed(futures):
            url, code, redir, final = f.result()
            done += 1
            if code == 0:
                broken.append((url, code, "UNREACHABLE", final))
            elif 400 <= code < 600:
                broken.append((url, code, f"HTTP_{code}", final))
            elif redir:
                redirects.append((url, code, final))
            else:
                ok.append(url)
            if done % 200 == 0:
                print(f"    {done}/{len(urls)}...", flush=True)
    return broken, redirects, ok


# ═══════════════════════════════════════
#  PHASE 3: GSC SEARCH ANALYTICS CROSS-REF
#  (replaces slow URL Inspection API)
# ═══════════════════════════════════════

def fetch_gsc_pages(service, gsc_url, days=90):
    """Fetch ALL pages that have ANY impressions in GSC (fast, bulk, no rate limit)."""
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=days)
    pages = {}
    start_row = 0
    while True:
        body = {
            "startDate": start.isoformat(),
            "endDate": end.isoformat(),
            "dimensions": ["page"],
            "rowLimit": 25000,
            "startRow": start_row,
        }
        resp = service.searchanalytics().query(siteUrl=gsc_url, body=body).execute()
        rows = resp.get("rows", [])
        if not rows:
            break
        for row in rows:
            url = row["keys"][0]
            pages[url] = {
                "clicks": row.get("clicks", 0),
                "impressions": row.get("impressions", 0),
                "ctr": round(row.get("ctr", 0) * 100, 2),
                "position": round(row.get("position", 0), 1),
            }
        if len(rows) < 25000:
            break
        start_row += 25000
    return pages


def cross_reference(sitemap_urls, gsc_pages):
    """Find sitemap URLs that have ZERO presence in GSC = not indexed / invisible."""
    gsc_url_set = set(gsc_pages.keys())
    # Normalize: strip trailing slashes for matching
    gsc_normalized = {}
    for u in gsc_url_set:
        gsc_normalized[u.rstrip("/")] = u

    invisible = []
    visible = []
    zero_click = []

    for url in sitemap_urls:
        norm = url.rstrip("/")
        if norm in gsc_normalized:
            data = gsc_pages[gsc_normalized[norm]]
            if data["clicks"] == 0 and data["impressions"] > 0:
                zero_click.append((url, data))
            visible.append((url, data))
        else:
            invisible.append(url)

    return invisible, visible, zero_click


# ═══════════════════════════════════════
#  REPORT WRITER
# ═══════════════════════════════════════

def write_reports(outdir, domain, sitemap_details, urls,
                  broken, redirects, ok_urls,
                  invisible, visible, zero_click):
    os.makedirs(outdir, exist_ok=True)

    # 1. All sitemap URLs
    with open(os.path.join(outdir, "all_sitemap_urls.txt"), "w", encoding="utf-8") as f:
        for u in urls:
            f.write(u + "\n")

    # 2. Broken HTTP
    p = os.path.join(outdir, "broken_urls_http.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# HTTP Broken URLs — {len(broken)} total\n")
        f.write(f"# STATUS | TYPE | URL | DETAIL\n\n")
        for url, code, t, d in sorted(broken, key=lambda x: x[1]):
            f.write(f"{code} | {t} | {url} | {d}\n")

    # 3. Redirects
    p = os.path.join(outdir, "redirect_urls.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# Redirecting URLs — {len(redirects)} total\n\n")
        for url, code, final in sorted(redirects):
            f.write(f"{code} | {url} → {final}\n")

    # 4. Invisible (in sitemap but 0 GSC presence = NOT indexed)
    p = os.path.join(outdir, "not_indexed_invisible.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# URLs in sitemap with ZERO GSC presence (likely not indexed) — {len(invisible)} total\n\n")
        for url in sorted(invisible):
            f.write(url + "\n")

    # 5. Zero-click (indexed but useless)
    p = os.path.join(outdir, "zero_click_pages.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"# Indexed but 0 clicks (90 days) — {len(zero_click)} total\n")
        f.write(f"# IMPRESSIONS | CTR | POSITION | URL\n\n")
        for url, data in sorted(zero_click, key=lambda x: -x[1]["impressions"]):
            f.write(f"{data['impressions']} | {data['ctr']}% | {data['position']} | {url}\n")

    # 6. MASTER REPORT
    p = os.path.join(outdir, "MASTER_BROKEN_REPORT.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"  MASTER BROKEN URL REPORT: {domain}\n")
        f.write(f"  Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        f.write("── SITEMAPS ──\n")
        for sm_url, count in sitemap_details:
            f.write(f"  {sm_url} → {count} URLs\n")
        f.write(f"  Total unique: {len(urls)}\n\n")

        f.write(f"── SUMMARY ──\n")
        f.write(f"  HTTP OK (2xx):                    {len(ok_urls)}\n")
        f.write(f"  HTTP Broken (4xx/5xx/dead):        {len(broken)}\n")
        f.write(f"  HTTP Redirecting (3xx):             {len(redirects)}\n")
        f.write(f"  Not in GSC at all (invisible):      {len(invisible)}\n")
        f.write(f"  In GSC but 0 clicks (zombie):       {len(zero_click)}\n\n")

        f.write(f"── HTTP BROKEN ({len(broken)}) ──\n")
        for url, code, t, d in sorted(broken, key=lambda x: x[1]):
            f.write(f"  [{code}] {t}: {url}\n")

        f.write(f"\n── REDIRECTING ({len(redirects)}) ──\n")
        for url, code, final in sorted(redirects):
            f.write(f"  [{code}] {url} → {final}\n")

        f.write(f"\n── NOT INDEXED / INVISIBLE ({len(invisible)}) ──\n")
        for url in sorted(invisible):
            f.write(f"  ✗ {url}\n")

        f.write(f"\n── ZERO-CLICK ZOMBIES ({len(zero_click)}) ──\n")
        for url, data in sorted(zero_click, key=lambda x: -x[1]["impressions"]):
            f.write(f"  [{data['impressions']} impr, pos {data['position']}] {url}\n")

        total_problems = len(broken) + len(redirects) + len(invisible) + len(zero_click)
        f.write(f"\n{'='*70}\n")
        f.write(f"  TOTAL PROBLEMATIC: {total_problems}\n")
        f.write(f"{'='*70}\n")

    return total_problems


# ═══════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════

def process_site(service, key, config):
    domain = config["domain"]
    gsc_url = config["gsc_url"]
    outdir = os.path.join(ROOT, f"broken_report_{key}")

    print(f"\n{'█' * 70}")
    print(f"  {domain}")
    print(f"{'█' * 70}")

    t0 = time.time()

    # Phase 1
    print(f"\n  ⚡ Phase 1: Sitemap Extraction")
    urls, details = extract_sitemaps(service, gsc_url, domain)
    if not urls:
        print(f"  ⚠ No URLs. Skipping.")
        return 0

    # Phase 2
    print(f"\n  ⚡ Phase 2: HTTP Status Check ({len(urls)} URLs, 20 workers)")
    broken, redirects, ok_urls = run_http_checks(urls)
    print(f"    ✓ Broken: {len(broken)} | Redirecting: {len(redirects)} | OK: {len(ok_urls)}")

    # Phase 3
    print(f"\n  ⚡ Phase 3: GSC Search Analytics Cross-Reference (90 days)")
    gsc_pages = fetch_gsc_pages(service, gsc_url)
    print(f"    GSC has data for {len(gsc_pages)} pages")
    invisible, visible, zero_click = cross_reference(urls, gsc_pages)
    print(f"    ✓ Not indexed: {len(invisible)} | Zero-click: {len(zero_click)} | Visible: {len(visible)}")

    # Write
    print(f"\n  📄 Writing reports to: {outdir}")
    total = write_reports(outdir, domain, details, urls,
                          broken, redirects, ok_urls,
                          invisible, visible, zero_click)

    elapsed = time.time() - t0
    print(f"\n  ✅ {domain} DONE in {elapsed:.1f}s — {total} problems found")
    return total


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print("  ⚡ FAST MULTI-SITE BROKEN URL FINDER")
    print("  Sites: jobrecruitment.in + techandcarsinfo.com")
    print("  Method: HTTP checks + GSC Search Analytics (no slow Inspection API)")
    print("=" * 70)

    service = get_gsc_service()
    results = {}

    for key, config in SITES.items():
        try:
            results[key] = process_site(service, key, config)
        except Exception as e:
            print(f"\n  ✗ ERROR on {key}: {e}")
            import traceback
            traceback.print_exc()
            results[key] = f"ERROR: {e}"

    print(f"\n\n{'=' * 70}")
    print(f"  FINAL COMBINED SUMMARY")
    print(f"{'=' * 70}")
    for key, val in results.items():
        d = SITES[key]["domain"]
        rpt = os.path.join(ROOT, f"broken_report_{key}", "MASTER_BROKEN_REPORT.txt")
        print(f"  {d:<35} | Problems: {val}")
        print(f"    → {rpt}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
