import os
import csv
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# 1. EXTRACT & PARSE: Scrape the direct static HTML from GoodReturns
try:
    url = "https://www.goodreturns.in/gold-rates/hyderabad.html"
    
    # Mirroring realistic browser parameters prevents immediate firewall blocks
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Locating the specific text elements inside the GoodReturns data grid
    # Grabbing the 24K raw pricing value string
    price_element = soup.find("div", {"id": "current-price"}).find("strong")
    
    if not price_element:
        # Fallback tracking if their element structure changes slightly
        gold_table = soup.find("table")
        rows = gold_table.find_all("tr")
        # Extract row containing 1 gram metrics 
        for row in rows:
            if "1" in row.text and "₹" in row.text:
                price_text = row.find_all("td")[1].text
                break
    else:
        price_text = price_element.text

    # TRANSFORM: Clean string characters like currency symbols or commas
    # e.g., '₹14,351' becomes float 14351.00
    clean_price = price_text.replace("₹", "").replace(",", "").strip()
    price_per_gram_24k = float(clean_price)

except Exception as e:
    print(f"❌ WEB SCRAPING FAILED: {e}")
    exit(1)

# Format structured date entries
now = datetime.utcnow()
current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

# 2. LOAD: Append variables to your CSV
file_path = "gold_prices.csv"
file_exists = os.path.isfile(file_path)

with open(file_path, mode="a", newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Date", "Time", "Price_per_Gram_24K_INR"])
    writer.writerow([current_date, current_time, price_per_gram_24k])

# 3. ALERT CONDITIONAL: Fire alert only if price targets ₹14,000 or lower
ALERT_THRESHOLD = 14000.00

if price_per_gram_24k <= ALERT_THRESHOLD:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    message = (
        f"🚨 24K HYDERABAD GOLD PRICE DROP ALERT!\n\n"
        f"The price of 1 gram of 24K gold has dropped below your threshold!\n"
        f"📉 Current Price: ₹{price_per_gram_24k}/gm\n"
        f"🎯 Target Level: ≤ ₹{ALERT_THRESHOLD}\n"
        f"🕒 Time: {current_date} {current_time} UTC"
    )
    
    telegram_url = f"https://telegram.org{bot_token}/sendMessage"
    requests.post(telegram_url, data={"chat_id": chat_id, "text": message})
    print(f"Alert triggered and sent! Current price (₹{price_per_gram_24k}) is <= ₹{ALERT_THRESHOLD}")
else:
    print(f"No alert sent. 24K Gold is at ₹{price_per_gram_24k}/gm (Target: ≤ ₹{ALERT_THRESHOLD})")
