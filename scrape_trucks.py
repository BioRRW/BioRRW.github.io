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

def clean_text(text):
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def scrape_stodgy():
    try:
        url = "https://stodgybrewing.com/food/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        # Target the actual content entry block to avoid footer/header lists
        content = soup.find(class_="entry-content") or soup
        for item in content.find_all('li'):
            text = item.get_text()
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"day_listing": clean_text(text)})
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
        main_content = soup.find(id="main-content") or soup.find(class_="content")
        if main_content:
            for p in main_content.find_all('p'):
                text = p.get_text()
                if any(day in text for day in ["Mon:", "Tue:", "Wed:", "Thu:", "Fri:", "Sat:", "Sun:"]):
                    trucks.append({"listing": clean_text(text)})
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
        for element in soup.find_all(['p', 'span']):
            text = element.get_text()
            if "food truck" in text.lower() or "truck:" in text.lower():
                cleaned = clean_text(text)
                if cleaned and len(cleaned) < 120 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
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
        
        # Look specifically inside an operations or calendar wrapper block, avoiding main navigation
        schedule_block = soup.find(class_=re.compile(r'(schedules|food|hours-operation|events-wrapper)', re.I))
        target = schedule_block if schedule_block else soup
        
        for item in target.find_all(['p', 'li', 'div', 'h4']):
            text = item.get_text().lower()
            # Only accept it if it strictly mentions a food truck context, bypassing general site announcements
            if "truck" in text or "serving" in text or "food vendor" in text:
                if any(day in item.get_text() for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                    cleaned = clean_text(item.get_text())
                    if cleaned and 15 < len(cleaned) < 150 and {"listing": cleaned} not in trucks:
                        trucks.append({"listing": cleaned})
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
        # Target main container text blocks to bypass standard navigation panels
        main_body = soup.find('main') or soup
        for item in main_body.find_all(['p', 'div', 'span']):
            text = item.get_text().lower()
            if "food truck" in text or "truck feature" in text:
                cleaned = clean_text(item.get_text())
                if cleaned and 20 < len(cleaned) < 150 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
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
        # Exclude header/footer navigation elements completely
        for nav_element in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
            nav_element.decompose()
            
        for el in soup.find_all(['p', 'h3', 'li']):
            text = el.get_text()
            if any(kwd in text.lower() for kwd in ["truck", "food", "serving"]):
                cleaned = clean_text(text)
                if cleaned and 15 < len(cleaned) < 120 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
        return trucks
    except Exception as e:
        print(f"Error Purpose: {e}")
        return []

def main():
    print("Running precision Fort Collins brewery food truck scraper...")
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
    print("Scrape complete.")

if __name__ == "__main__":
    main()
