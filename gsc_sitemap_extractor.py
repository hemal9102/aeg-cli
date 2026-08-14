"""
GSC Sitemap Extractor
Fetches all sitemaps registered in Google Search Console,
then extracts every URL from each sitemap and saves them
into individual .txt files in the root folder.
"""
import os
import re
import sys
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_PATH = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GSC_SITE_URL = "sc-domain:jobrecruitment.in"
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
OUTPUT_DIR = r"C:\hk\DUMP\big_fish_SAGEO"

# XML namespace used by sitemap protocol
NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


def get_gsc_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=GSC_SCOPES
    )
    return build("searchconsole", "v1", credentials=creds)


def list_sitemaps(service):
    """List all sitemaps registered in GSC."""
    try:
        resp = service.sitemaps().list(siteUrl=GSC_SITE_URL).execute()
    except Exception:
        alt_url = GSC_SITE_URL.replace("sc-domain:", "https://") + "/"
        resp = service.sitemaps().list(siteUrl=alt_url).execute()
    return resp.get("sitemap", [])


def fetch_sitemap_urls(sitemap_url):
    """Download a sitemap XML and extract all <loc> URLs.
    Handles sitemap index files (sitemapindex) recursively."""
    urls = []
    try:
        r = requests.get(sitemap_url, timeout=30)
        r.raise_for_status()
        root = ET.fromstring(r.content)

        # Check if this is a sitemap index
        if root.tag == "{http://www.sitemaps.org/schemas/sitemap/0.9}sitemapindex":
            # It's an index — recurse into each child sitemap
            for sitemap_elem in root.findall("sm:sitemap/sm:loc", NS):
                child_url = sitemap_elem.text.strip()
                print(f"  -> Found child sitemap: {child_url}")
                urls.extend(fetch_sitemap_urls(child_url))
        else:
            # It's a regular sitemap — extract <loc> entries
            for loc in root.findall("sm:url/sm:loc", NS):
                if loc.text:
                    urls.append(loc.text.strip())
    except Exception as e:
        print(f"  [ERROR] Could not fetch {sitemap_url}: {e}")
    return urls


def sanitize_filename(sitemap_url):
    """Turn a sitemap URL into a safe filename."""
    parsed = urlparse(sitemap_url)
    name = parsed.path.strip("/").replace("/", "_").replace(".", "_")
    if not name:
        name = "root_sitemap"
    # Remove any non-alphanumeric chars except underscore/hyphen
    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    return f"sitemap_{name}.txt"


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 60)
    print("  GSC SITEMAP EXTRACTOR")
    print("=" * 60)

    service = get_gsc_service()

    print(f"\nFetching sitemaps from GSC for: {GSC_SITE_URL}")
    sitemaps = list_sitemaps(service)

    if not sitemaps:
        print("No sitemaps found in GSC. Trying to fetch default sitemap.xml directly...")
        sitemaps = [{"path": "https://jobrecruitment.in/sitemap.xml"}]

    print(f"\nFound {len(sitemaps)} sitemap(s) in GSC:\n")

    all_urls_combined = []
    summary = []

    for sm in sitemaps:
        sm_url = sm.get("path", sm.get("url", ""))
        sm_type = sm.get("type", "unknown")
        sm_submitted = sm.get("lastSubmitted", "N/A")
        sm_errors = sm.get("errors", 0)
        sm_warnings = sm.get("warnings", 0)

        print(f"Sitemap: {sm_url}")
        print(f"  Type: {sm_type} | Last Submitted: {sm_submitted}")
        print(f"  Errors: {sm_errors} | Warnings: {sm_warnings}")

        # Fetch and parse URLs
        urls = fetch_sitemap_urls(sm_url)
        print(f"  URLs extracted: {len(urls)}")

        # Save to individual txt file
        filename = sanitize_filename(sm_url)
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            for url in sorted(urls):
                f.write(url + "\n")
        print(f"  Saved to: {filepath}\n")

        summary.append({
            "sitemap_url": sm_url,
            "filename": filename,
            "url_count": len(urls),
            "errors": sm_errors,
            "warnings": sm_warnings,
        })
        all_urls_combined.extend(urls)

    # Save a combined master file
    all_urls_combined = sorted(set(all_urls_combined))
    master_path = os.path.join(OUTPUT_DIR, "sitemap_all_urls_combined.txt")
    with open(master_path, "w", encoding="utf-8") as f:
        for url in all_urls_combined:
            f.write(url + "\n")

    # Print summary
    print("=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    for s in summary:
        print(f"  {s['filename']:<45} | {s['url_count']} URLs | Errors: {s['errors']} | Warnings: {s['warnings']}")
    print(f"\n  Combined master file: sitemap_all_urls_combined.txt ({len(all_urls_combined)} unique URLs)")
    print("=" * 60)


if __name__ == "__main__":
    main()
