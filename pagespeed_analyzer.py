import requests
import json
import time

def check_pagespeed(target_url, strategy="mobile"):
    print(f"\n⏳ Fetching PageSpeed Insights for {target_url} ({strategy.upper()})...")
    # Using the free PSI API endpoint (No API key needed for basic usage, but rate limited)
    api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={target_url}&strategy={strategy}"
    
    try:
        response = requests.get(api_url)
        data = response.json()
        
        if 'error' in data:
            print(f"❌ Error: {data['error']['message']}")
            return
            
        lighthouse = data.get('lighthouseResult', {})
        categories = lighthouse.get('categories', {})
        
        # Get Scores
        performance = categories.get('performance', {}).get('score', 0) * 100
        accessibility = categories.get('accessibility', {}).get('score', 0) * 100
        best_practices = categories.get('best-practices', {}).get('score', 0) * 100
        seo = categories.get('seo', {}).get('score', 0) * 100
        
        # Get Core Web Vitals (Field Data if available, otherwise Lab Data)
        audits = lighthouse.get('audits', {})
        lcp = audits.get('largest-contentful-paint', {}).get('displayValue', 'N/A')
        fid = audits.get('max-potential-fid', {}).get('displayValue', 'N/A') # Proxy for FID
        cls = audits.get('cumulative-layout-shift', {}).get('displayValue', 'N/A')
        speed_index = audits.get('speed-index', {}).get('displayValue', 'N/A')
        
        print(f"\n✅ RESULTS FOR: {target_url}")
        print("="*40)
        print("📊 LIGHTHOUSE SCORES:")
        print(f"  - Performance:    {performance:.0f}/100")
        print(f"  - Accessibility:  {accessibility:.0f}/100")
        print(f"  - Best Practices: {best_practices:.0f}/100")
        print(f"  - SEO:            {seo:.0f}/100")
        
        print("\n⚡ CORE WEB VITALS (Lab Data):")
        print(f"  - LCP (Largest Contentful Paint): {lcp}")
        print(f"  - CLS (Cumulative Layout Shift):  {cls}")
        print(f"  - Speed Index:                    {speed_index}")
        print("="*40)
        
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    test_urls = [
        "https://jobrecruitment.in/",
        "https://jobrecruitment.in/jobs.html"
    ]
    
    for url in test_urls:
        check_pagespeed(url, strategy="mobile")
        # Sleep for a few seconds to avoid rate limiting
        time.sleep(3)
