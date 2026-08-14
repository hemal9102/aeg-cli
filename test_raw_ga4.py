import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
    OrderBy
)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"

def analyze_ga4_seo():
    client = BetaAnalyticsDataClient()
    property_id = "541897723"

    print("==================================================")
    print("GA4 SEO ARCHITECT ANALYSIS (Last 28 Days)")
    print("==================================================\n")

    # 1. Geographic Cohorts (Multi-City Expansion Analysis)
    print("1. GEOGRAPHIC COHORTS (City-Level Engagement)")
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="city")],
            metrics=[
                Metric(name="sessions"), 
                Metric(name="engagedSessions"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration")
            ],
            date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
            limit=10
        )
        response = client.run_report(request)
        for row in response.rows:
            city = row.dimension_values[0].value
            sessions = row.metric_values[0].value
            engaged = row.metric_values[1].value
            bounce = round(float(row.metric_values[2].value) * 100, 2)
            avg_duration = round(float(row.metric_values[3].value), 2)
            print(f"- {city:<15} | Sessions: {sessions:<4} | Engaged: {engaged:<4} | Bounce Rate: {bounce}% | Avg Time: {avg_duration}s")
    except Exception as e:
        print(f"Error fetching city data: {e}")

    print("\n--------------------------------------------------\n")

    # 2. Dead-End Pages & Page Performance
    print("2. DEAD-END PAGES & ENGAGEMENT (Landing Pages)")
    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            dimensions=[Dimension(name="landingPagePlusQueryString")],
            metrics=[
                Metric(name="sessions"), 
                Metric(name="engagementRate"),
                Metric(name="bounceRate")
            ],
            date_ranges=[DateRange(start_date="28daysAgo", end_date="today")],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name="sessions"), desc=True)],
            limit=10
        )
        response = client.run_report(request)
        for row in response.rows:
            page = row.dimension_values[0].value
            sessions = row.metric_values[0].value
            eng_rate = round(float(row.metric_values[1].value) * 100, 2)
            bounce = round(float(row.metric_values[2].value) * 100, 2)
            # Flag dead-end pages
            status = "DEAD-END (High Bounce)" if bounce > 70 else "HEALTHY"
            
            print(f"Page: {page}")
            print(f"   -> Sessions: {sessions} | Engagement: {eng_rate}% | Bounce: {bounce}% | Status: {status}")
    except Exception as e:
        print(f"Error fetching landing page data: {e}")

if __name__ == "__main__":
    analyze_ga4_seo()
