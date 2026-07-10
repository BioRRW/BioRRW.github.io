import os
import re
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Global configuration to mimic a regular desktop browser and bypass simple bot-walls
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

def clean_text(text):
    """Utility to strip out extra whitespaces and newline breaks."""
    return re.sub(r'\s+', ' ', text).strip() if text else ""

def scrape_stodgy():
    """Scrapes Stodgy Brewing's clean list items."""
    try:
        url = "https://stodgybrewing.com/food/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Stodgy lists their truck schedules inside standard clean list elements
        for item in soup.find_all('li'):
            text = item.get_text()
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                trucks.append({"day_listing": clean_text(text)})
        return trucks
    except Exception as e:
        print(f"Error scraping Stodgy: {e}")
        return []

def scrape_maxline():
    """Scrapes Maxline Brewing's WordPress Event Calendar category feed."""
    try:
        url = "https://maxlinebrewing.com/events/categories/food-trucks/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Selects elements from Maxline's modern event block components
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
        print(f"Error scraping Maxline: {e}")
        return []

def scrape_zwei():
    """Scrapes Zwei Brewing's ASPX structure by targeting the main menu wrappers."""
    try:
        url = "https://www.zweibrewing.com/food-trucks.aspx"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Zwei maps out their grid elements using generic paragraph elements within text containers
        main_content = soup.find(id="main-content") or soup.find(class_="content") or soup.body
        if main_content:
            for p in main_content.find_all('p'):
                text = p.get_text()
                if any(day in text for day in ["Mon:", "Tue:", "Wed:", "Thu:", "Fri:", "Sat:", "Sun:", "Monday", "Friday"]):
                    trucks.append({"listing": clean_text(text)})
        return trucks
    except Exception as e:
        print(f"Error scraping Zwei: {e}")
        return []

def scrape_mythmaker():
    """Scrapes Mythmaker's text frames by searching for key day identifiers."""
    try:
        url = "https://www.mythmakerbrewing.com/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Mythmaker keeps text sequences updated inside their generic text and span blocks
        for element in soup.find_all(['p', 'span', 'div']):
            text = element.get_text()
            # Strict string validation to grab food truck references while dropping trivia or general text
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                if "truck" in text.lower() or "food" in text.lower() or "at mythmaker" in text.lower():
                    cleaned = clean_text(text)
                    if cleaned and len(cleaned) < 150 and {"listing": cleaned} not in trucks:
                        trucks.append({"listing": cleaned})
        return trucks
    except Exception as e:
        print(f"Error scraping Mythmaker: {e}")
        return []

def scrape_odell():
    """Scrapes Odell's location page for upcoming patio event listings."""
    try:
        url = "https://www.odellbrewing.com/locations/fort-collins/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Focuses on events or text containing explicit truck data
        for block in soup.find_all(class_=re.compile(r'(event|calendar|truck|info)', re.I)):
            text = block.get_text()
            if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
                cleaned = clean_text(text)
                if cleaned and 20 < len(cleaned) < 200 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
        return trucks
    except Exception as e:
        print(f"Error scraping Odell: {e}")
        return []

def scrape_new_belgium():
    """Target endpoint for New Belgium's corporate tour/taproom system API layout."""
    try:
        # Pulling directly from their live events/calendar pages
        url = "https://www.newbelgium.com/taproom/fort-collins/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        for item in soup.find_all(class_=re.compile(r'(event|card|schedule|food)', re.I)):
            text = item.get_text()
            if "truck" in text.lower() or "food" in text.lower():
                cleaned = clean_text(text)
                if cleaned and len(cleaned) < 180 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
        return trucks
    except Exception as e:
        print(f"Error scraping New Belgium: {e}")
        return []

def scrape_purpose():
    """Scrapes Purpose Brewing's single-page structure for localized details."""
    try:
        url = "https://purposebrewing.com/"
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        trucks = []
        
        # Grabs text frames listing times or dates 
        for el in soup.find_all(['p', 'h3', 'div', 'li']):
            text = el.get_text()
            if "truck" in text.lower() or "food" in text.lower() or "serving" in text.lower():
                cleaned = clean_text(text)
                if cleaned and 15 < len(cleaned) < 150 and {"listing": cleaned} not in trucks:
                    trucks.append({"listing": cleaned})
        return trucks
    except Exception as e:
        print(f"Error scraping Purpose: {e}")
        return []

def main():
    print("Initiating full Northern Colorado brewery food truck scrape sequence...")
    
    # Initialize the output master data block
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
    
    # Target directory handling (creates directory if missing inside local or remote actions system)
    output_dir = "assets/data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "food-trucks.json")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(master_schedule, f, indent=2, ensure_ascii=False)
        
    print(f"Scrape executed successfully. Comprehensive payload saved to: {output_path}")

if __name__ == "__main__":
    main()
