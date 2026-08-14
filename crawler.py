import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import sys

START_URL = "https://jobrecruitment.in/"
DOMAIN = "jobrecruitment.in"

visited = set()
to_visit = set([START_URL])
white_pages = []

def is_white_page(html_content):
    if not html_content or len(html_content.strip()) == 0:
        return True
    soup = BeautifulSoup(html_content, 'html.parser')
    if not soup.body or len(soup.body.get_text(strip=True)) == 0:
        return True
    return False

print(f"Starting crawl on {START_URL}")

while to_visit:
    current_url = to_visit.pop()
    if current_url in visited:
        continue
    
    visited.add(current_url)
    try:
        response = requests.get(current_url, timeout=10)
        # Check if content type is HTML
        if 'text/html' not in response.headers.get('Content-Type', ''):
            continue
            
        if is_white_page(response.text):
            print(f"[WHITE PAGE] {current_url}", flush=True)
            white_pages.append(current_url)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(current_url, href)
            # Remove fragment
            full_url = full_url.split('#')[0]
            
            parsed = urlparse(full_url)
            if parsed.netloc == DOMAIN or parsed.netloc == f"www.{DOMAIN}":
                if full_url not in visited:
                    to_visit.add(full_url)
                    
    except Exception as e:
        print(f"[ERROR] {current_url}: {e}", flush=True)
        
    time.sleep(0.5) # Politeness delay
    if len(visited) % 50 == 0:
        print(f"Crawled {len(visited)} pages. Found {len(white_pages)} white pages so far.", flush=True)

print(f"\nCrawl complete. Total pages crawled: {len(visited)}", flush=True)
print(f"Total white pages found: {len(white_pages)}", flush=True)
with open("white_pages.txt", "w") as f:
    for wp in white_pages:
        f.write(wp + "\n")
