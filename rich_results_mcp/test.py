import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json

SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cosmic-mariner-503804-c4-981c45ff145b.json")

scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
service = build('searchconsole', 'v1', credentials=creds)

request_body = {
    "inspectionUrl": "https://jobrecruitment.in/",
    "siteUrl": "https://jobrecruitment.in/",
    "languageCode": "en-US"
}

try:
    response = service.urlInspection().index().inspect(body=request_body).execute()
    print(json.dumps(response.get("inspectionResult", {}).get("richResultsResult", {}), indent=2))
except Exception as e:
    print(str(e))
