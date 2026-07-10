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
    """Scrapes Maxline Brewing's static RSS event feed to bypass JavaScript restrictions."""
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/feed/"
        response = requests.get(url, headers=HEADERS, timeout=12)
        
        # Parse using 'xml' parser to handle the RSS feed nodes cleanly
        soup = BeautifulSoup(response.text, 'xml')
        trucks = []
        
        for item in soup.find_all('item'):
            title = item.find('title')
            description = item.find('description')
            
            if title:
                title_text = clean_text(title.get_text())
                desc_text = clean_text(description.get_text()) if description else ""
                
                # Drop dynamic HTML tags inside description if they leak into the RSS block
                desc_clean = re.sub(r'<[^>]+>', '', desc_text)
                
                # Pull out the event date/time block cleanly if provided, otherwise snap a clean snippet
                schedule_match = re.search(r'(?:Date|Time):\s*([^<]+)', desc_clean, re.I)
                schedule_text = schedule_match.group(1).strip() if schedule_match else desc_clean[:75]
                
                # Format to seamlessly match our frontend mapping variables
                full_listing = f"{title_text} — {schedule_text}"
                
                if {"listing": full_listing} not in trucks:
                    trucks.append({"listing": full_listing})
        return trucks
    except Exception as e:
        print(f"Error scraping Maxline RSS: {e}")
        return []

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
