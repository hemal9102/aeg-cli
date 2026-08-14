import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(__file__), "cosmic-mariner-503804-c4-981c45ff145b.json")
GA4_PROPERTY_ID = "541897723"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

def run_ga4_report(dimensions_list, metrics_list, title, limit=10):
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions_list] if dimensions_list else [],
        metrics=[Metric(name=m) for m in metrics_list],
        date_ranges=[DateRange(start_date="today", end_date="today")],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        print(f"\n{'='*60}")
        print(f" {title.upper()} (TODAY)")
        print(f"{'='*60}")
        
        # If no rows, print message
        if not response.rows:
            print("No data found for today yet (or GA4 hasn't processed it fully).")
            return

        # Print Headers
        headers = dimensions_list + metrics_list
        header_str = " | ".join(f"{h[:15]:<15}" for h in headers)
        print(header_str)
        print("-" * len(header_str))
        
        # Print Rows
        for row in response.rows:
            dim_values = [d.value for d in row.dimension_values]
            met_values = []
            
            for i, m in enumerate(row.metric_values):
                val = m.value
                met_values.append(val)
                
            row_data = dim_values + met_values
            print(" | ".join(f"{str(v)[:15]:<15}" for v in row_data))
            
    except Exception as e:
        print(f"Error fetching {title}: {str(e)}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("Running GA4 Analysis for TODAY...")
    
    # Overview
    run_ga4_report(
        dimensions_list=[],
        metrics_list=["activeUsers", "sessions", "screenPageViews"],
        title="Overall Traffic",
        limit=1
    )
    
    # Top Pages Today
    run_ga4_report(
        dimensions_list=["pagePath"],
        metrics_list=["screenPageViews", "activeUsers"],
        title="Top Pages",
        limit=5
    )
    
    # Events Today
    run_ga4_report(
        dimensions_list=["eventName"],
        metrics_list=["eventCount"],
        title="Top Events",
        limit=5
    )
    
    # Traffic Sources Today
    run_ga4_report(
        dimensions_list=["sessionDefaultChannelGroup"],
        metrics_list=["sessions"],
        title="Traffic Sources",
        limit=5
    )
