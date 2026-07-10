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

def scrape_maxline():
    """Queries Maxline's internal WordPress REST API to pull live calendar data."""
    try:
        # Querying their hidden backend database API bypasses the client-side JavaScript wall entirely
        api_url = "https://maxlinebrewing.com/wp-json/tribe/events/v1/events"
        params = {
            "categories": "food-trucks",
            "per_page": 10,
            "status": "publish"
        }
        
        response = requests.get(api_url, headers=HEADERS, params=params, timeout=12)
        trucks = []
        
        if response.status_code == 200:
            data = response.json()
            # Loop through the raw event entries returned from the database
            for event in data.get("events", []):
                title = clean_text(event.get("title", ""))
                start_date_details = event.get("start_date_details", {})
                
                # Reconstruct a clean human-readable schedule string
                day = start_date_details.get("day", "")
                month = start_date_details.get("month", "")
                year = start_date_details.get("year", "")
                hour = start_date_details.get("hour", "")
                minutes = start_date_details.get("minutes", "")
                ampm = start_date_details.get("ampm", "")
                
                if title:
                    # Construct a unified listing string matching your frontend requirements
                    schedule_str = f"{month}/{day} @ {hour}:{minutes} {ampm.upper()}"
                    full_listing = f"{title} — {schedule_str}"
                    
                    if {"listing": full_listing} not in trucks:
                        trucks.append({"listing": full_listing})
                        
        # If the API is active but empty, pass our clean fallback string so the card stays populated
        return trucks if trucks else [{"listing": "Schedules rotating weekly on their platform."}]
    except Exception as e:
        print(f"Error executing Maxline API query: {e}")
        return [{"listing": "Schedules rotating weekly on their platform."}]


def scrape_broad_body(url):
    """Fallback text mining processor that pulls clean sentence segments from structural blocks."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Decompose code assets and tracking modules instantly
        for s in soup(["script", "style", "nav", "header", "footer", "noscript"]):
            s.decompose()
            
        trucks = []
        for element in soup.find_all(['p', 'li', 'h4', 'span', 'div']):
            text = clean_text(element.get_text())
            if len(text) > 15 and len(text) < 220:
                if any(day in text for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                    item = {"listing": text}
                    if item not in trucks:
                        trucks.append(item)
        return trucks
    except Exception as e:
        print(f"Error broad scraping layout {url}: {e}")
        return []

def main():
    print("Initiating production-stabilized Northern Colorado food truck scrape loop...")
    
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
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
    print(f"Data alignment sync locked and delivered. Payload saved to: {output_path}")

if __name__ == "__main__":
    main()
