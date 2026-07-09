import os
import re
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
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for item in soup.find_all('li'):
            text = clean_text(item.get_text())
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"listing": text, "is_placeholder": False})
        return trucks if trucks else [{"listing": "Schedule rotating online.", "is_placeholder": True}]
    except:
        return [{"listing": "Schedule rotating online.", "is_placeholder": True}]

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
                trucks.append({"listing": f"{clean_text(title.get_text())} — {clean_text(dt.get_text())}", "is_placeholder": False})
        return trucks if trucks else [{"listing": "Schedule rotating online.", "is_placeholder": True}]
    except:
        return [{"listing": "Schedule rotating online.", "is_placeholder": True}]

def main():
    print("Initiating production data-sync routine...")
    
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
            "Zwei Brewing": [{"listing": "Schedule rotating online.", "is_placeholder": True}],
            "Mythmaker Brewing": [{"listing": "Schedule rotating online.", "is_placeholder": True}],
            "Odell Brewing": [{"listing": "Schedule rotating online.", "is_placeholder": True}],
            "New Belgium": [{"listing": "Schedule rotating online.", "is_placeholder": True}],
            "Purpose Brewing": [{"listing": "Schedule rotating online.", "is_placeholder": True}]
        }
    }
    
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, "food-trucks.json"), "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print("Payload compiled and delivered successfully.")

if __name__ == "__main__":
    main()
