import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def clean_text(text):
    return " ".join(text.split()).strip() if text else ""

# --- ALL VERIFIED SCRAPERS ---

def scrape_stodgy():
    try:
        res = requests.get("https://stodgybrewing.com/food/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for ol in soup.find_all('ol'):
            for li in ol.find_all('li'):
                text = clean_text(li.get_text())
                if text: trucks.append(text)
        return trucks
    except: return []

def scrape_zwei():
    try:
        res = requests.get("https://www.zweibrewing.com/food-truck.aspx", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for food_div in soup.find_all('div', class_='food'):
            b_tags = food_div.find_all('b')
            if len(b_tags) >= 2:
                date_text = clean_text(b_tags[0].get_text())
                truck_name = clean_text(b_tags[1].get_text())
                if date_text and truck_name and len(date_text) > 5:
                    listing = f"{date_text} - {truck_name}"
                    if listing not in trucks: trucks.append(listing)
        return trucks
    except: return []

def scrape_maxline():
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        header = soup.find('h3', string=lambda text: text and "Upcoming Events" in text)
        if header:
            event_list = header.find_next('ul')
            if event_list:
                return [clean_text(li.get_text()) for li in event_list.find_all('li') if "-" in li.get_text()]
        return []
    except: return []

def scrape_mythmaker():
    try:
        url = "https://calendar.google.com/calendar/ical/c_50raf1sssnkevsaiokod7rgjjg%40group.calendar.google.com/public/basic.ics"
        res = requests.get(url, headers=HEADERS, timeout=10)
        ics_data = re.sub(r'\r\n\s+', '', res.text)
        events, today = [], datetime.now().date()
        for match in re.finditer(r'BEGIN:VEVENT(.*?)END:VEVENT', ics_data, re.DOTALL):
            event_str = match.group(1)
            summary = re.search(r'SUMMARY:(.*?)(?:\r\n|$)', event_str)
            dtstart = re.search(r'DTSTART(?:;[^:]+)?:(.*?)(?:\r\n|$)', event_str)
            if summary and dtstart:
                title, dt_raw = summary.group(1).strip(), dtstart.group(1).strip()
                try:
                    dt_obj = datetime.strptime(dt_raw[:8], "%Y%m%d").date()
                    if dt_obj >= today and any(kwd in title.lower() for kwd in ["truck", "food", "bbq", "pizza", "burger", "taco", "cuisine"]):
                        events.append((dt_obj, f"{dt_obj.strftime('%A, %b %-d')} - {title}"))
                except: pass
        events.sort(key=lambda x: x[0])
        return [item[1] for item in events]
    except: return []

def scrape_new_belgium():
    try:
        res = requests.get("https://www.newbelgium.com/visit/fort-collins/", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks, food_keywords = [], ["food", "truck", "taco", "bbq", "pizza", "burger", "cuisine", "eats"]
        for slide in soup.find_all('li', class_='glide__slide'):
            date_el = slide.find('p', class_='date')
            title_el = slide.find('p', class_='header-title')
            desc_el = slide.find('p', class_='description')
            if date_el and title_el:
                title, desc = clean_text(title_el.get_text()), clean_text(desc_el.get_text()) if desc_el else ""
                if any(kwd in (title + " " + desc).lower() for kwd in food_keywords):
                    trucks.append(f"{clean_text(date_el.get_text())} - {title}")
        return trucks
    except: return []

def scrape_purpose():
    try:
        res = requests.get("https://purposebrewing.com/food-trucks", headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for article in soup.find_all('article', class_='eventlist-event'):
            title_el = article.find('h1', class_='eventlist-title')
            month = article.find('div', class_='eventlist-datetag-startdate--month')
            day = article.find('div', class_='eventlist-datetag-startdate--day')
            if title_el and month and day:
                trucks.append(f"{clean_text(month.get_text())} {clean_text(day.get_text())} - {clean_text(title_el.get_text())}")
        return trucks
    except: return []

# --- PRODUCTION SAVER ---

def main():
    data = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "breweries": {
            "Stodgy Brewing": scrape_stodgy(),
            "Zwei Brewing": scrape_zwei(),
            "Maxline Brewing": scrape_maxline(),
            "Mythmaker Brewing": scrape_mythmaker(),
            "New Belgium": scrape_new_belgium(),
            "Purpose Brewing": scrape_purpose()
        }
    }
    # Save to your assets folder
    output_path = os.path.join("assets", "data", "food-trucks.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Scrape successful. Data saved to {output_path}")

if __name__ == "__main__":
    main()