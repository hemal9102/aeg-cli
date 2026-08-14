import os
import sys
import asyncio
import json

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
sys.path.append(r"C:\hk\DUMP\big_fish_SAGEO")

from aeg.analytics_mcp.tools.reporting.core import run_report

async def main():
    property_id = "541897723"
    
    print("--- 1. Search Console Trend (Last 28 Days) ---")
    try:
        # GSC metrics are typically organicGoogleSearchClicks, organicGoogleSearchImpressions, organicGoogleSearchClickThroughRate
        # But wait, GA4 data API might restrict mixing GSC metrics with regular dimensions. 
        # Let's try regular SEO traffic first to be safe, or just pull sessionSourceMedium
        seo_report = await run_report(
            property_id=property_id,
            date_ranges=[{"start_date": "28daysAgo", "end_date": "today"}],
            dimensions=[{"name": "date"}],
            metrics=[{"name": "sessions"}, {"name": "engagedSessions"}, {"name": "bounceRate"}]
        )
        print(json.dumps(seo_report, indent=2))
    except Exception as e:
        print(f"Error fetching SEO trend: {e}")
        
    print("\n--- 2. Traffic Sources (Checking for GMB) ---")
    try:
        source_report = await run_report(
            property_id=property_id,
            date_ranges=[{"start_date": "28daysAgo", "end_date": "today"}],
            dimensions=[{"name": "sessionSourceMedium"}, {"name": "sessionCampaignName"}],
            metrics=[{"name": "sessions"}]
        )
        print(json.dumps(source_report, indent=2))
    except Exception as e:
        print(f"Error fetching traffic sources: {e}")

if __name__ == "__main__":
    asyncio.run(main())
