import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# Explicitly filter out navigation junk, footer links, and site menus
BLACKLIST = [
    "contact us", "our story", "back taproom", "hours", "brewery", "pricing", 
    "harvest host", "book an event", "location", "gift card", "careers", 
    "newsletter", "privacy policy", "terms of use", "cart", "shop"
]

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def is_valid_listing(text):
    text_lower = text.lower()
    # Must contain a day element to be a valid schedule item
    has_day = any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Mon:", "Tue:", "Wed:", "Thu:", "Fri:", "Sat:", "Sun:"])
    # Must NOT contain blacklisted navigation keywords
    is_not_junk = not any(junk in text_lower for junk in BLACKLIST)
    return has_day and is_not_junk

def scrape_stodgy():
    try:
        url = "https://stodgybrewing.com/food/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for item in soup.find_all('li'):
            text = clean_text(item.get_text())
            if is_valid_listing(text):
                trucks.append({"day_listing": text})
        return trucks
    except Exception as e:
        print(f"Error Stodgy: {e}")
        return []

def scrape_maxline():
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for event in soup.find_all(class_="tribe-events-calendar-list__event-details"):
            title_el = event.find(class_="tribe-events-calendar-list__event-title")
            date_el = event.find(class_="tribe-events-calendar-list__event-datetime")
            if title_el and date_el:
                trucks.append({
                    "truck": clean_text(title_el.get_text()),
                    "schedule": clean_text(date_el.get_text())
                })
        return trucks
    except Exception as e:
        print(f"Error Maxline: {e}")
        return []

def scrape_zwei():
    try:
        url = "https://www.zweibrewing.com/food-trucks.aspx"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for p in soup.find_all(['p', 'div', 'li']):
            text = clean_text(p.get_text())
            if is_valid_listing(text) and len(text) < 100:
                if {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except Exception as e:
        print(f"Error Zwei: {e}")
        return []

def scrape_mythmaker():
    try:
        url = "https://www.mythmakerbrewing.com/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for element in soup.find_all(['p', 'span', 'li']):
            text = clean_text(element.get_text())
            if is_valid_listing(text) and ("truck" in text.lower() or "serving" in text.lower()):
                if len(text) < 120 and {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except Exception as e:
        print(f"Error Mythmaker: {e}")
        return []

def scrape_odell():
    try:
        url = "https://www.odellbrewing.com/locations/fort-collins/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for item in soup.find_all(['p', 'li', 'div', 'h4', 'span']):
            text = clean_text(item.get_text())
            if is_valid_listing(text) and ("truck" in text.lower() or "serving" in text.lower() or "patio" in text.lower()):
                if 20 < len(text) < 150 and {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except Exception as e:
        print(f"Error Odell: {e}")
        return []

def scrape_new_belgium():
    try:
        url = "https://www.newbelgium.com/taproom/fort-collins/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for item in soup.find_all(['p', 'div', 'span', 'li']):
            text = clean_text(item.get_text())
            if is_valid_listing(text) and ("truck" in text.lower() or "feature" in text.lower()):
                if 20 < len(text) < 150 and {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except Exception as e:
        print(f"Error New Belgium: {e}")
        return []

def scrape_purpose():
    try:
        url = "https://purposebrewing.com/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        for el in soup.find_all(['p', 'h3', 'li', 'div']):
            text = clean_text(el.get_text())
            if is_valid_listing(text) and ("truck" in text.lower() or "serving" in text.lower() or "food" in text.lower()):
                if 15 < len(text) < 120 and {"listing": text} not in trucks:
                    trucks.append({"listing": text})
        return trucks
    except Exception as e:
        print(f"Error Purpose: {e}")
        return []

def main():
    print("Running master blacklist-filtered brewery scraper...")
    master_schedule = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Maxline Brewing": scrape_maxline(),
            "Zwei Brewing": scrape_zwei(),
            "Mythmaker Brewing": scrape_mythmaker(),
            "Odell Brewing": scrape_odell(),
            "New Belgium": scrape_new_belgium(),
            "Purpose Brewing": scrape_purpose()
        }
    }
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    with open(os.path.join(output_dir, "food-trucks.json"), "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print("Data deployment successful.")

if __name__ == "__main__":
    main()
