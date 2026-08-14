import os
import csv
from datetime import datetime, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GA4_PROPERTY_ID = "541897723"
SITE_URL = "sc-domain:jobrecruitment.in"
DOMAIN = "https://jobrecruitment.in"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

def get_gsc_pages():
    print("Fetching Top URLs from Google Search Console (Last 90 Days)...")
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build('searchconsole', 'v1', credentials=creds)

    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['page'],
        'rowLimit': 5000,
    }

    try:
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
        return response.get('rows', [])
    except Exception as e:
        # Try URL prefix if sc-domain fails
        try:
            response = service.searchanalytics().query(siteUrl=DOMAIN+"/", body=request).execute()
            return response.get('rows', [])
        except Exception as e2:
            print(f"GSC Error: {str(e2)}")
            return []

def get_ga4_engagement():
    print("Fetching Engagement Data from GA4 (Last 90 Days)...")
    client = BetaAnalyticsDataClient()
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="activeUsers"), Metric(name="engagementRate")],
        date_ranges=[DateRange(start_date="90daysAgo", end_date="today")],
        limit=5000
    )
    
    ga4_data = {}
    try:
        response = client.run_report(request)
        for row in response.rows:
            path = row.dimension_values[0].value
            users = int(row.metric_values[0].value)
            engagement = float(row.metric_values[1].value)
            ga4_data[path] = {"users": users, "engagement": engagement}
        return ga4_data
    except Exception as e:
        print(f"GA4 Error: {str(e)}")
        return {}

if __name__ == "__main__":
    gsc_rows = get_gsc_pages()
    ga4_data = get_ga4_engagement()
    
    final_pillars = []
    
    for row in gsc_rows:
        full_url = row['keys'][0]
        clicks = row['clicks']
        impressions = row['impressions']
        
        # Only focus on pSEO html pages (or meaningful pages)
        # Skip pure home page or core pages for the "migration" pillar list, or keep them to see all.
        # Let's keep all for now.
        
        # Extract path
        path = full_url.replace(DOMAIN, "")
        if not path.startswith("/"): path = "/" + path
        
        # Get GA4 data
        ga_metrics = ga4_data.get(path, {"users": 0, "engagement": 0.0})
        
        # Score calculation: We want high impressions + high engagement
        # Only consider pages with at least some impressions
        if impressions > 10:
            final_pillars.append({
                "url": full_url,
                "path": path,
                "impressions": impressions,
                "clicks": clicks,
                "ga4_users": ga_metrics["users"],
                "engagement_rate": round(ga_metrics["engagement"] * 100, 2)
            })
            
    # Sort by impressions descending
    final_pillars.sort(key=lambda x: x["impressions"], reverse=True)
    
    # Save Top 50 to CSV
    output_file = "top_50_pseo_pillars.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["url", "path", "impressions", "clicks", "ga4_users", "engagement_rate"])
        writer.writeheader()
        writer.writerows(final_pillars[:50])
        
    print(f"\n✅ Successfully extracted {len(final_pillars[:50])} pillar pages.")
    print(f"Saved to: {output_file}")
    print("\nTop 5 Examples:")
    for p in final_pillars[:5]:
        print(f"{p['path'][:30]:<30} | Impr: {p['impressions']:<6} | Clicks: {p['clicks']:<4} | Users: {p['ga4_users']:<4} | Eng: {p['engagement_rate']}%")
