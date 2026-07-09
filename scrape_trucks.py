import os
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_text(text):
    return " ".join(text.split()).strip() if text else ""

def scrape_stodgy():
    try:
        url = "https://stodgybrewing.com/food/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for item in soup.find_all('li'):
            text = clean_text(item.get_text())
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"listing": text})
        return trucks if trucks else [{"listing": "Check current lineup online ➔"}]
    except:
        return [{"listing": "Check current lineup online ➔"}]

def scrape_maxline():
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for event in soup.find_all(class_="tribe-events-calendar-list__event-details"):
            title = event.find(class_="tribe-events-calendar-list__event-title")
            dt = event.find(class_="tribe-events-calendar-list__event-datetime")
            if title and dt:
                trucks.append({"listing": f"{clean_text(title.get_text())} — {clean_text(dt.get_text())}"})
        return trucks if trucks else [{"listing": "Check current lineup online ➔"}]
    except:
        return [{"listing": "Check current lineup online ➔"}]

def main():
    print("Executing fail-safe brewery data pipeline...")
    
    # Static fallbacks ensure the card ALWAYS shows up on your dashboard with a link if live scraping fails
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
            "Zwei Brewing": [{"listing": "View weekly rotation schedule ➔"}],
            "Mythmaker Brewing": [{"listing": "View weekly calendar ➔"}],
            "Odell Brewing": [{"listing": "View patio event schedule ➔"}],
            "New Belgium": [{"listing": "View taproom truck schedule ➔"}],
            "Purpose Brewing": [{"listing": "View weekend truck schedule ➔"}]
        }
    }
    
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, "food-trucks.json"), "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print("Failsafe data sync complete.")

if __name__ == "__main__":
    main()
