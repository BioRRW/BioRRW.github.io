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
                trucks.append({"day_listing": text})
        return trucks
    except:
        return []

def scrape_maxline():
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        # Pull explicitly from their custom event card text containers
        for container in soup.find_all(class_=re.compile(r'(event-details|event-meta|tribe-events-calendar-list)', re.I)):
            text = clean_text(container.get_text())
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                if len(text) > 15 and len(text) < 180 and {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except:
        return []

def scrape_broad_body(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        
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
    except:
        return []

def main():
    print("Executing final high-accuracy food truck scrape run...")
    
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
            "Zwei Brewing": scrape_broad_body("https://www.zweibrewing.com/food-trucks.aspx"),
            "Mythmaker Brewing": scrape_broad_body("https://www.mythmakerbrewing.com/home/events-food-truck-calendar"), # Target sub-path
            "Odell Brewing": scrape_broad_body("https://www.odellbrewing.com/locations/fort-collins/"),
            "New Belgium": scrape_broad_body("https://www.newbelgium.com/taproom/fort-collins/"),
            "Purpose Brewing": scrape_broad_body("https://purposebrewing.com/")
        }
    }
    
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    with open(os.path.join(output_dir, "food-trucks.json"), "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print("All schedules packed.")

if __name__ == "__main__":
    main()
