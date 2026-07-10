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
    """Parses ordered list items <ol><li> directly."""
    try:
        res = requests.get("https://stodgybrewing.com/food/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for ol in soup.find_all('ol'):
            for li in ol.find_all('li'):
                text = clean_text(li.get_text())
                if text: trucks.append(text)
        return trucks
    except: return []

def scrape_maxline():
    """Parses The Events Calendar plugin's native list markup."""
    try:
        res = requests.get("https://maxlinebrewing.com/events/categories/food-trucks/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for event in soup.find_all(class_=re.compile("type-tribe_events")):
            title_el = event.find(re.compile(r"h\d"), class_=re.compile("title"))
            date_el = event.find(class_=re.compile("datetime"))
            if title_el and date_el:
                trucks.append(f"{clean_text(title_el.get_text())} - {clean_text(date_el.get_text())}")
        return trucks
    except: return []

def scrape_zwei():
    """Walks <strong> tags mapping dates/names in the schedule section."""
    try:
        res = requests.get("https://www.zweibrewing.com/food-trucks.aspx", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        for strong in soup.find_all('strong'):
            text = clean_text(strong.get_text())
            if any(day in text for day in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
                parent = strong.parent
                if parent:
                    trucks.append(clean_text(parent.get_text()))
        return list(dict.fromkeys(trucks)) # Preserves order while removing duplicates
    except: return []

def scrape_purpose():
    """Exploits the Squarespace Events backend JSON payload."""
    try:
        res = requests.get("https://purposebrewing.com/events?format=json-pretty", headers=HEADERS, timeout=12).json()
        trucks = []
        for item in res.get("items", []):
            title = item.get("title", "")
            start_time = item.get("startDate", 0) # Squarespace returns unix timestamp in ms
            if title and start_time:
                dt_obj = datetime.fromtimestamp(start_time / 1000.0)
                date_str = dt_obj.strftime("%A, %b %-d")
                trucks.append(f"{date_str} - {title}")
        return trucks
    except: return []

def scrape_mythmaker():
    """Pulls and parses the raw public Google Calendar ICS feed."""
    try:
        url = "https://calendar.google.com/calendar/ical/c_50raf1sssnkevsaiokod7rgjjg%40group.calendar.google.com/public/basic.ics"
        res = requests.get(url, headers=HEADERS, timeout=12)
        # Unfold multiline ICS format breaks
        ics_data = re.sub(r'\r\n\s+', '', res.text)
        trucks = []
        
        for match in re.finditer(r'BEGIN:VEVENT(.*?)END:VEVENT', ics_data, re.DOTALL):
            event_str = match.group(1)
            summary = re.search(r'SUMMARY:(.*?)(?:\r\n|$)', event_str)
            dtstart = re.search(r'DTSTART(?:;[^:]+)?:(.*?)(?:\r\n|$)', event_str)
            
            if summary and dtstart:
                title = summary.group(1).strip()
                dt_raw = dtstart.group(1).strip()
                if len(dt_raw) >= 8:
                    try:
                        dt_obj = datetime.strptime(dt_raw[:8], "%Y%m%d")
                        date_str = dt_obj.strftime("%A, %b %-d")
                        trucks.append(f"{date_str} - {title}")
                    except: pass
        return trucks
    except: return []

def scrape_odell():
    """Targets the static 'Hungry? Daily Food Trucks' block."""
    try:
        res = requests.get("https://www.odellbrewing.com/locations/fort-collins/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        header = soup.find(string=re.compile(r'Daily Food Trucks', re.I))
        if header:
            parent = header.find_parent('div') or header.find_parent('section')
            if parent:
                for el in parent.find_all(['h4', 'p', 'li']):
                    text = clean_text(el.get_text())
                    if len(text) > 8 and "food truck" not in text.lower():
                        trucks.append(text)
        return trucks
    except: return []

def scrape_new_belgium():
    """Extracts from the UPCOMING FOOD TRUCKS carousel slides."""
    try:
        res = requests.get("https://www.newbelgium.com/taproom/fort-collins/", headers=HEADERS, timeout=12)
        soup = BeautifulSoup(res.text, 'html.parser')
        trucks = []
        header = soup.find(string=re.compile(r'UPCOMING FOOD TRUCKS', re.I))
        if header:
            carousel = header.find_parent('section') or header.find_parent('div')
            if carousel:
                for item in carousel.find_all(class_=re.compile(r'card|slide|item', re.I)):
                    text = clean_text(item.get_text())
                    if text and text not in trucks:
                        trucks.append(text)
        return trucks
    except: return []

def main():
    print("Initiating surgical schema-based food truck scrape...")
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
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "food-trucks.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
    print(f"Surgical execution complete. Clean JSON array data delivered to: {output_path}")

if __name__ == "__main__":
    main()