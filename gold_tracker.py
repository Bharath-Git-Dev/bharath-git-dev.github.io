import os
import csv
from datetime import datetime
import requests

# 1. EXTRACT: Fetch free real-time gold price directly from GoldPrice.org's data engine
try:
    # Querying GoldPrice.org's direct backend endpoint for Indian Rupees (INR)
    url = "https://goldprice.org"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    data = response.json()
    
    # GoldPrice.org provides the standard spot price per Troy Ounce ('xauPrice')
    price_per_ounce_inr = data["items"][0]["xauPrice"]
    
    # Convert Troy Ounce directly to 1 Gram of 24K Gold
    price_per_gram_24k = round(price_per_ounce_inr / 31.1034768, 2)
    
except Exception as e:
    print(f"❌ DATA EXTRACTION FAILED FROM GOLDPRICE.ORG: {e}")
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
        f"🌐 Source: GoldPrice.org"
    )
    
    # Corrected Endpoint routing to handle Telegram Bot API specifications securely
    telegram_url = f"https://telegram.org{bot_token}/sendMessage"
    
    try:
        alert_response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message})
        alert_response.raise_for_status()
        print(f"Alert triggered and sent! Current price (₹{price_per_gram_24k}) is <= ₹{ALERT_THRESHOLD}")
    except Exception as telegram_error:
        print(f"⚠️ Price targeted successfully but Telegram notification failed: {telegram_error}")
else:
    print(f"No alert sent. 24K Gold is at ₹{price_per_gram_24k}/gm (Target: ≤ ₹{ALERT_THRESHOLD})")
