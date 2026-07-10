import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Global configuration to mimic a regular desktop browser and bypass simple bot-walls
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def clean_text(text):
    """Utility to strip out extra whitespaces and newline breaks."""
    return " ".join(text.split()).strip() if text else ""

def scrape_stodgy():
    """Scrapes Stodgy Brewing's clean list items."""
    try:
        url = "https://stodgybrewing.com/food/"
        response = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for item in soup.find_all('li'):
            text = clean_text(item.get_text())
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"day_listing": text})
        return trucks
    except Exception as e:
        print(f"Error scraping Stodgy: {e}")
        return []

def scrape_broad_body(url):
    """Robust fallback text-mining processor that pulls clean sentence rows from structural blocks."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Decompose script frameworks and layout nodes instantly to isolate pure text content
        for s in soup(["script", "style", "nav", "header", "footer", "noscript"]):
            s.decompose()
            
        trucks = []
        # Query generic layout cells to read sequential plain text lines
        for element in soup.find_all(['p', 'li', 'h4', 'span', 'div', 'h2', 'a']):
            text = clean_text(element.get_text())
            if len(text) > 12 and len(text) < 220:
                # Must contain a clear calendar day to be structured as a valid schedule listing row
                if any(day in text for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                    item = {"listing": text}
                    if item not in trucks:
                        trucks.append(item)
        return trucks
    except Exception as e:
        print(f"Error broad scraping layout {url}: {e}")
        return []

def main():
    print("Initiating full multi-brewery text mining extraction sweep...")
    
    # We pipeline Maxline directly through the functional broad-body processor to extract text rows
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_broad_body("https://maxlinebrewing.com/events/categories/food-trucks/"),
            "Zwei Brewing": scrape_broad_body("https://www.zweibrewing.com/food-trucks.aspx"),
            "Mythmaker Brewing": scrape_broad_body("https://www.mythmakerbrewing.com/home/events-food-truck-calendar"),
            "Odell Brewing": scrape_broad_body("https://www.odellbrewing.com/locations/fort-collins/"),
            "New Belgium": scrape_broad_body("https://www.newbelgium.com/taproom/fort-collins/"),
            "Purpose Brewing": scrape_broad_body("https://purposebrewing.com/")
        }
    }
    
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "food-trucks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print(f"Scraper sequence execution complete. Data delivered to: {output_path}")

if __name__ == "__main__":
    main()
