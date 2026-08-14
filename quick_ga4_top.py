import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GA4_PROPERTY_ID = "541897723"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

client = BetaAnalyticsDataClient()

request = RunReportRequest(
    property=f"properties/{GA4_PROPERTY_ID}",
    dimensions=[Dimension(name="pagePath")],
    metrics=[Metric(name="screenPageViews"), Metric(name="activeUsers")],
    date_ranges=[DateRange(start_date="30daysAgo", end_date="today")],
    limit=10
)

response = client.run_report(request)
print("TOP 10 PAGES BY VIEWS:")
print("-" * 50)
for row in response.rows:
    path = row.dimension_values[0].value
    views = row.metric_values[0].value
    users = row.metric_values[1].value
    print(f"Page: {path:<30} | Views: {views:<6} | Users: {users}")
