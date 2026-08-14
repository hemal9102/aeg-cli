import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from apify_client import ApifyClient
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")

# Initialize Apify Client
apify = ApifyClient(APIFY_TOKEN)

app = FastAPI(
    title="Omnichannel Trending & AEO Pipeline",
    description="Fetches trends via Apify (Google Trends, Dorking, Reddit, LinkedIn) and synthesizes via LLM for SEO, AEO, and GEO.",
    version="1.0.0"
)

# --- Pydantic Models ---
class TrendRequest(BaseModel):
    query: str
    region: str = "IN"
    max_items: int = 5

class TrendResponse(BaseModel):
    query: str
    status: str
    message: str

# --- Apify Scraping Functions ---
async def scrape_google_trends(query: str, region: str, max_items: int):
    """Scrapes Google Trends via Apify."""
    print(f"[*] Starting Google Trends scrape for: {query}")
    # Using a popular Google Trends scraper actor on Apify
    run = apify.actor("emastra/google-trends-scraper").call(run_input={
        "searchTerms": [query],
        "geo": region,
        "timeframe": "now 1-d",
        "category": 0
    })
    items = [item for item in apify.dataset(run["defaultDatasetId"]).iterate_items()]
    return items[:max_items]

async def scrape_google_dorks(query: str, region: str, max_items: int):
    """Scrapes Google Search using advanced Dorking techniques."""
    print(f"[*] Starting Google Dorking scrape for: {query}")
    # Example dork: intitle:"trend" OR inurl:"trends" "query"
    dork_query = f'intitle:"{query}" OR intext:"{query} trends" site:medium.com OR site:quora.com'
    run = apify.actor("apify/google-search-scraper").call(run_input={
        "queries": dork_query,
        "resultsPerPage": max_items,
        "countryCode": region.lower()
    })
    items = [item for item in apify.dataset(run["defaultDatasetId"]).iterate_items()]
    return items[:max_items]

async def scrape_reddit(query: str, max_items: int):
    """Scrapes Reddit for organic discussions."""
    print(f"[*] Starting Reddit scrape for: {query}")
    run = apify.actor("trudax/reddit-scraper").call(run_input={
        "searchQueries": [query],
        "sort": "hot",
        "time": "day",
        "maxItems": max_items
    })
    items = [item for item in apify.dataset(run["defaultDatasetId"]).iterate_items()]
    return items[:max_items]

async def scrape_linkedin(query: str, max_items: int):
    """Scrapes LinkedIn Posts for B2B trends."""
    print(f"[*] Starting LinkedIn scrape for: {query}")
    run = apify.actor("curious_coder/linkedin-post-scraper").call(run_input={
        "keyword": query,
        "limit": max_items
    })
    items = [item for item in apify.dataset(run["defaultDatasetId"]).iterate_items()]
    return items[:max_items]

# --- LLM Processing (AEO / SEO / GEO synthesis) ---
async def synthesize_with_llm(query: str, aggregated_data: dict):
    """
    Pipes all the raw scraped data into an LLM to extract actionable 
    entities for Answer Engine Optimization (AEO) and SEO.
    """
    print(f"[*] Sending aggregated data to LLM for AEO synthesis...")
    # NOTE: You would integrate your preferred LLM here (e.g., openai or google-genai).
    # This is a placeholder showing the prompt engineering structure.
    
    prompt = f"""
    You are an expert in SEO, AEO (Answer Engine Optimization), and GEO.
    Analyze the following real-time data collected for the query: '{query}'.
    
    DATA FROM APIFY:
    - Google Trends Data: {aggregated_data.get('google_trends')}
    - Google Search (Dorks): {aggregated_data.get('dorks')}
    - Reddit Discussions: {aggregated_data.get('reddit')}
    - LinkedIn Posts: {aggregated_data.get('linkedin')}
    
    Based on this data, provide:
    1. The top 3 rising sub-topics or entities to target.
    2. Suggested H2/H3 structures that Answer Engines (like ChatGPT/Perplexity) are looking for.
    3. Sentiment and intent analysis (Informational, Transactional).
    """
    
    # Mocking LLM response for now
    await asyncio.sleep(2)
    return {
        "status": "success",
        "aeo_entities": ["Example Entity 1", "Example Entity 2"],
        "suggested_headings": ["What is " + query, "Top trends in " + query],
        "intent": "Informational"
    }

# --- Core Pipeline Runner ---
async def run_trend_pipeline(query: str, region: str, max_items: int):
    """Runs all Apify scrapers concurrently and synthesizes the results."""
    try:
        # Run all scraping tasks in parallel using asyncio.gather
        trends_task = scrape_google_trends(query, region, max_items)
        dorks_task = scrape_google_dorks(query, region, max_items)
        reddit_task = scrape_reddit(query, max_items)
        linkedin_task = scrape_linkedin(query, max_items)
        
        # Wait for all scrapers to finish
        trends_data, dorks_data, reddit_data, linkedin_data = await asyncio.gather(
            trends_task, dorks_task, reddit_task, linkedin_task,
            return_exceptions=True # Prevent one failure from crashing others
        )
        
        aggregated_data = {
            "google_trends": trends_data if not isinstance(trends_data, Exception) else str(trends_data),
            "dorks": dorks_data if not isinstance(dorks_data, Exception) else str(dorks_data),
            "reddit": reddit_data if not isinstance(reddit_data, Exception) else str(reddit_data),
            "linkedin": linkedin_data if not isinstance(linkedin_data, Exception) else str(linkedin_data)
        }
        
        # Send to LLM for Synthesis
        synthesis_result = await synthesize_with_llm(query, aggregated_data)
        
        print(f"[+] Pipeline completed for '{query}'. Synthesis: {synthesis_result}")
        # In a real app, you would save this to DuckDB/SQLite or emit an event.
        
    except Exception as e:
        print(f"[-] Pipeline failed: {str(e)}")

# --- Endpoints ---
@app.post("/api/v1/trigger-trend-pipeline", response_model=TrendResponse)
async def trigger_trend_pipeline(request: TrendRequest, background_tasks: BackgroundTasks):
    """
    Triggers the Apify + LLM pipeline in the background.
    Useful for slow scraping tasks so the client doesn't time out.
    """
    if not APIFY_TOKEN:
        raise HTTPException(status_code=500, detail="APIFY_TOKEN environment variable is not set.")
        
    # Add the pipeline to FastAPI's background tasks
    background_tasks.add_task(run_trend_pipeline, request.query, request.region, request.max_items)
    
    return TrendResponse(
        query=request.query,
        status="processing",
        message="Omnichannel pipeline has been started in the background."
    )

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Omnichannel Trend Server is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
