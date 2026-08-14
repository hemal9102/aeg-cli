import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "cosmic-mariner-503804-c4-981c45ff145b.json")
SITE_URL = "https://jobrecruitment.in/" # Sometimes it's sc-domain:jobrecruitment.in if verified via DNS

def get_gsc_keywords():
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    service = build('searchconsole', 'v1', credentials=creds)

    request = {
        'startDate': '2023-11-01', # Just a broad date range, we'll try something recent
        'endDate': 'today',        # Note: GSC API requires specific date formats, let's use a dynamic one
    }
    
    # Get dates dynamically
    from datetime import datetime, timedelta
    end_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d') # GSC data lags by ~3 days
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

    request = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': ['query'],
        'dimensionFilterGroups': [{
            'filters': [{
                'dimension': 'query',
                'operator': 'contains',
                'expression': 'job recruitment'
            }]
        }],
        'rowLimit': 20,
    }

    try:
        # First try URL-prefix property
        response = service.searchanalytics().query(siteUrl=SITE_URL, body=request).execute()
    except Exception as e:
        # If URL-prefix fails, try Domain property
        if "User does not have sufficient permission" in str(e) or "not found" in str(e):
            try:
                response = service.searchanalytics().query(siteUrl="sc-domain:jobrecruitment.in", body=request).execute()
            except Exception as e2:
                return {"error": f"Failed with both URL and Domain property: {str(e2)}"}
        else:
            return {"error": str(e)}
            
    return response.get('rows', [])

if __name__ == "__main__":
    print("Fetching 'job recruitment' Keywords from Google Search Console (Last 30 Days)...\n")
    keywords = get_gsc_keywords()
    
    if isinstance(keywords, dict) and "error" in keywords:
        print(f"Error: {keywords['error']}")
    elif not keywords:
        print("No keyword data found. The site might be too new or has no impressions yet.")
    else:
        print(f"{'Keyword':<35} | {'Clicks':<8} | {'Impressions':<12} | {'CTR':<8} | {'Position'}")
        print("-" * 80)
        for row in keywords:
            query = row['keys'][0]
            clicks = row['clicks']
            impressions = row['impressions']
            ctr = row['ctr'] * 100
            position = row['position']
            print(f"{query:<35} | {clicks:<8} | {impressions:<12} | {ctr:.2f}%   | {position:.1f}")
