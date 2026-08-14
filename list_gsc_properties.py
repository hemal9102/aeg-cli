"""List all GSC properties accessible by the service account."""
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

SERVICE_ACCOUNT_PATH = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"
GSC_SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_PATH, scopes=GSC_SCOPES
    )
    service = build("searchconsole", "v1", credentials=creds)
    resp = service.sites().list().execute()
    sites = resp.get("siteEntry", [])
    print(f"Found {len(sites)} GSC properties:\n")
    for s in sites:
        print(f"  {s.get('siteUrl', 'N/A'):<50} | Permission: {s.get('permissionLevel', 'N/A')}")

if __name__ == "__main__":
    main()
