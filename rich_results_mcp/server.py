import os
import json
import sys
from mcp.server.lowlevel import Server
from mcp import types as mcp_types
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Server(name="Rich Results SEO MCP")

SERVICE_ACCOUNT_FILE = r"C:\Users\Dell\Downloads\cosmic-mariner-503804-c4-981c45ff145b.json"

def get_gsc_service():
    scopes = ['https://www.googleapis.com/auth/webmasters.readonly']
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scopes)
    return build('searchconsole', 'v1', credentials=creds)

@app.list_tools()
async def list_tools() -> list[mcp_types.Tool]:
    return [
        mcp_types.Tool(
            name="test_rich_results",
            description="Tests a URL for Rich Results (SEO Schema) using Google Search Console.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to test (e.g., https://jobrecruitment.in/job-consultancy-in-ahmedabad.html)"},
                    "site_url": {"type": "string", "description": "The GSC property URL (default: https://jobrecruitment.in/)"}
                },
                "required": ["url"],
                "additionalProperties": True
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[mcp_types.Content]:
    if name != "test_rich_results":
        return [mcp_types.TextContent(type="text", text=json.dumps({"error": "Unknown tool"}))]
        
    url = arguments.get("url")
    site_url = arguments.get("site_url", "https://jobrecruitment.in/")
    
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        return [mcp_types.TextContent(type="text", text=json.dumps({"error": "Service account JSON not found."}))]
        
    try:
        service = get_gsc_service()
        request_body = {
            "inspectionUrl": url,
            "siteUrl": site_url,
            "languageCode": "en-US"
        }
        
        # This is a blocking call, but for this lightweight script it's fine
        response = service.urlInspection().index().inspect(body=request_body).execute()
        inspection_result = response.get("inspectionResult", {})
        rich_results = inspection_result.get("richResultsResult", {})
        
        formatted_output = {
            "URL": url,
            "Verdict": rich_results.get("verdict", "UNKNOWN"),
            "Detected_Items": []
        }
        
        for item in rich_results.get("detectedItems", []):
            item_data = {
                "Rich_Result_Name": item.get("richResultType", "Unknown"),
                "Items_Found": item.get("items", []),
                "Issues": item.get("issues", [])
            }
            formatted_output["Detected_Items"].append(item_data)
            
        return [mcp_types.TextContent(type="text", text=json.dumps(formatted_output, indent=2))]
        
    except Exception as e:
        return [mcp_types.TextContent(type="text", text=json.dumps({"error": str(e)}))]

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await app.run(read_stream, write_stream, app.create_initialization_options())
            
    asyncio.run(main())
