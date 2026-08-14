import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GA4_PROPERTY_ID = "541897723"
SITE_URL = "https://jobrecruitment.in/"

def get_top_pages_ga4():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name="pagePath")],
        metrics=[Metric(name="screenPageViews"), Metric(name="bounceRate")],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=5
    )
    
    response = client.run_report(request)
    pages = []
    for row in response.rows:
        path = row.dimension_values[0].value
        if not path.startswith("http"):
            # Strip trailing/leading slashes to prevent double slashes
            url = SITE_URL.rstrip('/') + '/' + path.lstrip('/')
        else:
            url = path
            
        pages.append({
            "path": path,
            "url": url,
            "views": row.metric_values[0].value,
            "bounce_rate": row.metric_values[1].value
        })
    return pages

def check_rich_results(url):
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build('searchconsole', 'v1', credentials=creds)
    
    request_body = {
        "inspectionUrl": url,
        "siteUrl": SITE_URL,
        "languageCode": "en-US"
    }
    
    try:
        response = service.urlInspection().index().inspect(body=request_body).execute()
        rich_results = response.get("inspectionResult", {}).get("richResultsResult", {})
        return {
            "verdict": rich_results.get("verdict", "UNKNOWN"),
            "types": [item.get("richResultType") for item in rich_results.get("detectedItems", [])]
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print("Fetching Top 5 Pages from GA4...")
    top_pages = get_top_pages_ga4()
    
    print("\n--- COMBINED AUDIT DATA ---")
    for page in top_pages:
        print(f"\nURL: {page['url']}")
        print(f"GA4 Views: {page['views']} | Bounce Rate: {float(page['bounce_rate'])*100:.2f}%")
        
        print("Checking Rich Results API...")
        rr_data = check_rich_results(page['url'])
        
        if "error" in rr_data:
            print(f"Rich Results Error: {rr_data['error']}")
        else:
            print(f"Rich Results Verdict: {rr_data['verdict']}")
            print(f"Detected Schemas: {', '.join(rr_data['types']) if rr_data['types'] else 'None'}")
