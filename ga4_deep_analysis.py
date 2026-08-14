import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GA4_PROPERTY_ID = "541897723"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

def run_ga4_report(dimensions_list, metrics_list, title, limit=10):
    client = BetaAnalyticsDataClient()
    
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions_list],
        metrics=[Metric(name=m) for m in metrics_list],
        date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
        limit=limit
    )
    
    try:
        response = client.run_report(request)
        print(f"\n{'='*60}")
        print(f" {title.upper()} (Last 30 Days)")
        print(f"{'='*60}")
        
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
                # Formatting tweaks
                if metrics_list[i] == 'averageSessionDuration':
                    val = f"{float(val):.0f} sec"
                elif metrics_list[i] == 'bounceRate' or metrics_list[i] == 'engagementRate':
                    val = f"{float(val)*100:.1f}%"
                met_values.append(val)
                
            row_data = dim_values + met_values
            print(" | ".join(f"{str(v)[:15]:<15}" for v in row_data))
            
    except Exception as e:
        print(f"Error fetching {title}: {str(e)}")


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    print("Running GA4 Deep Analysis...")
    
    # 1. Traffic Acquisition (Where is traffic coming from?)
    run_ga4_report(
        dimensions_list=["sessionDefaultChannelGroup"],
        metrics_list=["sessions", "engagedSessions", "averageSessionDuration"],
        title="Traffic Sources (Acquisition)",
        limit=5
    )
    
    # 2. Geographic Data (Which cities are visiting?)
    run_ga4_report(
        dimensions_list=["city"],
        metrics_list=["activeUsers", "sessions", "engagementRate"],
        title="Top Cities (Geographic)",
        limit=5
    )
    
    # 3. User Behavior / Events (What are they clicking/doing?)
    run_ga4_report(
        dimensions_list=["eventName"],
        metrics_list=["eventCount", "totalUsers"],
        title="Top Events & Conversions",
        limit=10
    )
    
    # 4. Devices (Mobile vs Desktop)
    run_ga4_report(
        dimensions_list=["deviceCategory"],
        metrics_list=["sessions", "averageSessionDuration"],
        title="Device Categories",
        limit=3
    )
