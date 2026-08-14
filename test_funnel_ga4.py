import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    FilterExpression,
    FilterExpressionList,
    Filter,
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"

def analyze_advanced_ga4():
    client = BetaAnalyticsDataClient()
    property_id = "541897723"

    print("==================================================")
    print("GA4 ADVANCED FUNNEL & EVENT ANALYSIS")
    print("==================================================\n")

    # 1. Check Events (Scroll, Search, File Upload)
    print("1. ENHANCED MEASUREMENT & CUSTOM EVENTS (Are they firing?)")
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="eventName")],
            metrics=[Metric(name="eventCount"), Metric(name="totalUsers")],
            date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
        )
        response = client.run_report(request)
        event_dict = {}
        for row in response.rows:
            event_dict[row.dimension_values[0].value] = {
                "count": row.metric_values[0].value,
                "users": row.metric_values[1].value
            }
        
        target_events = ["scroll", "view_search_results", "file_upload", "page_view"]
        for evt in target_events:
            data = event_dict.get(evt, {"count": 0, "users": 0})
            print(f"- {evt:<20} | Total Events: {data['count']:<5} | Unique Users: {data['users']}")
            
        if event_dict.get("scroll", {"count": 0}).get("count") == 0:
            print("  -> WARNING: No 'scroll' data. Enhanced Measurement might be off or no one is scrolling.")
    except Exception as e:
        print(f"Error fetching events: {e}")

    print("\n--------------------------------------------------\n")

    # 2. Mimic B2C Candidate Funnel
    print("2. SYNTHETIC FUNNEL (Candidate Drop-off Analysis)")
    try:
        print("Step 1: Users viewing /jobs or homepage")
        print("Step 2: Users actually firing file_upload (CV Submit)")
        
        views = event_dict.get("page_view", {"users": 0})["users"]
        uploads = event_dict.get("file_upload", {"users": 0})["users"]
        
        print(f"Total Candidate Pool (Page Views): {views} Users")
        print(f"Total CV Uploads: {uploads} Users")
        
        if int(views) > 0:
            conversion_rate = (int(uploads) / int(views)) * 100
            print(f"Estimated Funnel Conversion Rate: {round(conversion_rate, 2)}%")
        else:
            print("Not enough data to calculate conversion.")
            
    except Exception as e:
        print(f"Error fetching funnel: {e}")

if __name__ == "__main__":
    analyze_advanced_ga4()
