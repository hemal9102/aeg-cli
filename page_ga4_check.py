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

# Set up credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "cosmic-mariner-503804-c4-981c45ff145b.json")

property_id = "541897723"
client = BetaAnalyticsDataClient()

request = RunReportRequest(
    property=f"properties/{property_id}",
    dimensions=[Dimension(name="pagePath")],
    metrics=[
        Metric(name="screenPageViews"),
        Metric(name="sessions"),
        Metric(name="bounceRate"),
        Metric(name="averageSessionDuration")
    ],
    date_ranges=[DateRange(start_date="2023-01-01", end_date="today")],
    dimension_filter=FilterExpression(
        filter=Filter(
            field_name="pagePath",
            string_filter=Filter.StringFilter(
                match_type=Filter.StringFilter.MatchType.EXACT,
                value="/"
            )
        )
    )
)

response = client.run_report(request)

print("--- GA4 DATA FOR HOME PAGE (/) ---")
if not response.rows:
    print("No traffic data found for this page in GA4.")
else:
    for row in response.rows:
        print(f"Page Path: {row.dimension_values[0].value}")
        print(f"Total Views: {row.metric_values[0].value}")
        print(f"Sessions: {row.metric_values[1].value}")
        bounce = float(row.metric_values[2].value) * 100
        print(f"Bounce Rate: {bounce:.2f}%")
        print(f"Avg Session Duration: {row.metric_values[3].value} seconds")
