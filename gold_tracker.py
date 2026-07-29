import os
import csv
from datetime import datetime
import requests

# 1. EXTRACT: Fetch gold spot value using highly scalable public CDN endpoints
try:
    # Fetch global currency metrics mapped directly to Gold (XAU) from an open CDN mirror
    url = "https://jsdelivr.net"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    response = requests.get(url, headers=headers, timeout=15)
    
    # Backup alternative engine endpoint route if the primary CDN is routing slow
    if response.status_code != 200:
        url = "https://pages.dev"
        response = requests.get(url, headers=headers, timeout=15)
        
    response.raise_for_status()
    data = response.json()
    
    # Get the value of 1 Troy Ounce of Gold converted to Indian Rupees (INR)
    # The API returns the value of 1 INR in XAU, so we take the inverse (1 / value)
    inr_to_xau_rate = float(data["xau"]["inr"])
    price_per_ounce_inr = 1 / inr_to_xau_rate
    
    # Convert 1 Troy Ounce directly to 1 Gram of 24K Gold
    price_per_gram_24k = round(price_per_ounce_inr / 31.1034768, 2)
    
except Exception as e:
    print(f"❌ DATA EXTRACTION FAILED: {e}")
    exit(1)

# Split up the timestamps into distinct data metrics
now = datetime.utcnow()
current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

# 2. LOAD: Append the 24K data with separate date columns
file_path = "gold_prices.csv"
file_exists = os.path.isfile(file_path)

with open(file_path, mode="a", newline="") as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Date", "Time", "Price_per_Gram_24K_INR"])
    writer.writerow([current_date, current_time, price_per_gram_24k])

# 3. ALERT CONDITIONAL: Fire alert only if price targets ₹14,000 or lower
# (To test your Telegram bot right now, you can temporarily change this to 200000.00!)
ALERT_THRESHOLD = 14000.00

if price_per_gram_24k <= ALERT_THRESHOLD:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    message = (
        f"🚨 24K GOLD PRICE DROP ALERT!\n\n"
        f"The price of 1 gram of 24K gold has dropped below your threshold!\n"
        f"📉 Current Price: ₹{price_per_gram_24k}/gm\n"
        f"🎯 Target Level: ≤ ₹{ALERT_THRESHOLD}\n"
        f"🕒 Time: {current_date} {current_time} UTC\n"
        f"🌐 Source: Open Currency Engine"
    )
    
    telegram_url = f"https://telegram.org{bot_token}/sendMessage"
    
    try:
        alert_response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message}, timeout=10)
        alert_response.raise_for_status()
        print(f"Alert triggered and sent! Current price (₹{price_per_gram_24k}) is <= ₹{ALERT_THRESHOLD}")
    except Exception as telegram_error:
        print(f"⚠️ Price targeted successfully but Telegram notification failed: {telegram_error}")
else:
    print(f"No alert sent. 24K Gold is at ₹{price_per_gram_24k}/gm (Target: ≤ ₹{ALERT_THRESHOLD})")
