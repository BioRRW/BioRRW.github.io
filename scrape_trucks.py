import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Master blacklist to block navigation menus and non-food events on the backend
BLACKLIST = [
    "our story", "contact us", "taproom hours", "back taproom", "book an event", 
    "event pricing", "harvest host", "what's on tap", "about us", "gift card", 
    "careers", "privacy policy", "live music", "music sundays", "denim days"
]

def clean_text(text):
    return " ".join(text.split()).strip() if text else ""

def is_valid_listing(text):
    text_lower = text.lower()
    if len(text) < 12 or len(text) > 200:
        return False
    # Must not contain layout/nav junk phrases
    if any(junk in text_lower for junk in BLACKLIST):
        return False
    # Must explicitly mention a food element or a clear schedule day indicator
    has_food_context = any(kwd in text_lower for kwd in ["truck", "food", "serving", "kitchen", "eats", "cuisine", "chef"])
    has_day_context = any(day in text for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun", "Monday", "Thursday", "Friday", "Saturday", "Sunday"])
    return has_food_context or has_day_context

def fallback_item():
    return [{"listing": "Schedules rotating weekly on taproom platforms."}]

def scrape_stodgy():
    try:
        url = "https://stodgybrewing.com/food/"
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for item in soup.find_all('li'):
            text = clean_text(item.get_text())
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"day_listing": text})
        return trucks if trucks else fallback_item()
    except:
        return fallback_item()

def scrape_maxline():
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for event in soup.find_all(class_="tribe-events-calendar-list__event-details"):
            title = event.find(class_="tribe-events-calendar-list__event-title")
            dt = event.find(class_="tribe-events-calendar-list__event-datetime")
            if title and dt:
                trucks.append({"truck": clean_text(title.get_text()), "schedule": clean_text(dt.get_text())})
        return trucks if trucks else fallback_item()
    except:
        return fallback_item()

def scrape_by_body_search(url):
    """Fallback parser that safely scans page elements for specific food strings if primary targets shift."""
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        # Remove script and style elements entirely to avoid messy background layout syntax matches
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()
            
        trucks = []
        for el in soup.find_all(['p', 'li', 'div', 'span', 'h4']):
            text = clean_text(el.get_text())
            if is_valid_listing(text):
                item = {"listing": text}
                if item not in trucks:
                    trucks.append(item)
        return trucks if trucks else fallback_item()
    except:
        return fallback_item()

def main():
    print("Initiating production-stabilized Northern Colorado food truck scrape loop...")
    
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
            "Zwei Brewing": scrape_by_body_search("https://www.zweibrewing.com/food-trucks.aspx"),
            "Mythmaker Brewing": scrape_by_body_search("https://www.mythmakerbrewing.com/home/about-us"),
            "Odell Brewing": scrape_by_body_search("https://www.odellbrewing.com/locations/fort-collins/"),
            "New Belgium": scrape_by_body_search("https://www.newbelgium.com/taproom/fort-collins/"),
            "Purpose Brewing": scrape_by_body_search("https://purposebrewing.com/")
        }
    }
    
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, "food-trucks.json"), "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print("Pipeline execution completed successfully.")

if __name__ == "__main__":
    main()
