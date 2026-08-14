import os
from google.analytics.admin import AnalyticsAdminServiceClient

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = SERVICE_ACCOUNT_FILE

def list_properties():
    client = AnalyticsAdminServiceClient()
    
    print("Fetching accessible GA4 Accounts & Properties...")
    
    # List Accounts
    accounts = client.list_accounts()
    for account in accounts:
        print(f"\nAccount: {account.display_name} ({account.name})")
        
        # List Properties for this account
        from google.analytics.admin_v1alpha.types import ListPropertiesRequest
        request = ListPropertiesRequest(filter=f"parent:{account.name}")
        properties = client.list_properties(request=request)
        for prop in properties:
            print(f"  - Property: {prop.display_name} (ID: {prop.name.replace('properties/', '')})")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    list_properties()
