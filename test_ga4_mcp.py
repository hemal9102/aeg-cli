import os
import sys
import asyncio

# Set the credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"

# Add the project root to python path so it can import aeg.analytics_mcp
sys.path.append(r"C:\hk\DUMP\big_fish_SAGEO")

from aeg.analytics_mcp.tools.admin.info import get_account_summaries

async def test():
    try:
        print("Testing Google Analytics API connection...")
        summaries = await get_account_summaries()
        print(f"Success! Connected to GA4. Found {len(summaries)} account summaries linked to this service account.")
        for s in summaries:
            print(f"- Account: {s.get('displayName')} (Resource: {s.get('account')})")
            if 'propertySummaries' in s:
                for p in s['propertySummaries']:
                    print(f"   -> Property: {p.get('displayName')} (ID: {p.get('property')})")
    except Exception as e:
        print(f"Connection failed! Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test())
