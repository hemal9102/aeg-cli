import os
from google.analytics.admin import AnalyticsAdminServiceClient
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

class AnalyticsDiscoveryAgent:
    """
    Automatically discovers and links GA4 and GSC properties 
    based purely on the Service Account JSON and the target domain.
    """
    
    def __init__(self):
        # Ensure credentials exist in env
        self.creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not self.creds_path or not os.path.exists(self.creds_path):
            print("[!] WARNING: GOOGLE_APPLICATION_CREDENTIALS is not set or file is missing.")
            
    def discover_ga4_property_id(self, target_domain: str) -> str:
        """Searches all accessible GA4 accounts and returns the Property ID matching the domain."""
        print(f"[*] Discovering GA4 property for domain: {target_domain}...")
        try:
            client = AnalyticsAdminServiceClient()
            accounts = client.list_accounts()
            
            for account in accounts:
                from google.analytics.admin_v1alpha.types import ListPropertiesRequest
                request = ListPropertiesRequest(filter=f"parent:{account.name}")
                properties = client.list_properties(request=request)
                
                for prop in properties:
                    # Very simple match: check if domain is in the property display name or URL
                    if target_domain.lower() in prop.display_name.lower():
                        prop_id = prop.name.replace('properties/', '')
                        print(f"[+] Found Match! GA4 Property: {prop.display_name} (ID: {prop_id})")
                        return prop_id
                        
            print("[-] No matching GA4 property found.")
            return None
        except Exception as e:
            print(f"[-] Error discovering GA4: {e}")
            return None
            
    def fetch_page_analytics(self, target_url: str):
        """
        Main entry point for the MAS Pipeline. 
        Will automatically discover IDs and fetch traffic/keywords.
        """
        # Extract domain from URL (e.g., https://jobrecruitment.in/jobs -> jobrecruitment.in)
        domain = target_url.replace("https://", "").replace("http://", "").split("/")[0]
        
        ga4_id = self.discover_ga4_property_id(domain)
        # TODO: Implement GSC discovery
        # gsc_url = self.discover_gsc_property(domain)
        
        if not ga4_id:
            return {"status": "error", "message": "Could not auto-discover GA4 property."}
            
        print(f"[*] Proceeding to fetch deep analytics for {target_url} using GA4 ID: {ga4_id}")
        
        # Placeholder for actual data pulling logic (from ga4_deep_analysis.py)
        # ...
        
        return {
            "status": "success",
            "top_keywords": ["it recruitment", "hiring ahmedabad"], # Mocked
            "engagement_rate": 65.4,
            "impressions": 1200
        }

# For manual testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    agent = AnalyticsDiscoveryAgent()
    agent.fetch_page_analytics("https://jobrecruitment.in/some-page")
