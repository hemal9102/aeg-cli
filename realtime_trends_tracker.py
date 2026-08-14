import pandas as pd
import time
import os
from pytrends.request import TrendReq

# Set the geographic region to Gujarat, India.
# 'IN' targets the whole of India, 'IN-GJ' narrows it down to Gujarat state.
GEO_LOCATION = 'IN-GJ' 

# Timezone offset: India is UTC+5:30, which is -330 minutes from UTC in pytrends.
TZ_OFFSET = -330 

# The max number of keywords you can query in one pytrends request is 5.
KEYWORDS = [
    "job consultancy",
    "recruitment agency",
    "jobs in ahmedabad",
    "it recruitment",
    "hiring"
]

def fetch_realtime_trends():
    print(f"Initializing Google Trends Tracker for Region: {GEO_LOCATION}...")
    
    # hl='en-US' controls the language of the returned results
    pytrends = TrendReq(hl='en-US', tz=TZ_OFFSET, timeout=(10,25))
    
    print(f"Fetching real-time Interest Over Time for the last 24 hours...")
    # timeframe='now 1-d' gives real-time data for the last 24 hours.
    # timeframe='today 1-m' gives data for the last 30 days.
    pytrends.build_payload(kw_list=KEYWORDS, cat=0, timeframe='now 1-d', geo=GEO_LOCATION, gprop='')
    
    try:
        # Get interest over time
        interest_over_time_df = pytrends.interest_over_time()
        
        if not interest_over_time_df.empty:
            # Drop the internal 'isPartial' column if it exists
            if 'isPartial' in interest_over_time_df.columns:
                interest_over_time_df = interest_over_time_df.drop(columns=['isPartial'])
            
            # Save to CSV
            output_file = 'realtime_trends_gujarat.csv'
            interest_over_time_df.to_csv(output_file)
            print(f"Success! Real-time trends saved to {output_file}")
            print(interest_over_time_df.tail())
        else:
            print("No data found for these keywords in the given timeframe/region.")
            
    except Exception as e:
        print(f"Error fetching trends data. Note that Google might rate-limit frequent requests.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    fetch_realtime_trends()
