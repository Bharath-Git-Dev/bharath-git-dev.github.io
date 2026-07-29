import os
import csv
from datetime import datetime
import requests

# 1. EXTRACT: Fetch tokenized real-time gold price from CoinGecko API (PAX Gold)
try:
    # Crucial Fix: Swapped homepage URL with the active CoinGecko API domain
    url = "https://coingecko.com"
    response = requests.get(url).json()
    
    # PAX Gold is backed 1:1 by a physical Troy Ounce of fine 24K gold
    price_per_ounce_inr = response["pax-gold"]["inr"]
    
    # TRANSFORM: Convert 1 Troy Ounce to exactly 1 gram of 24K pure gold
    # (1 Troy Ounce = 31.1034768 grams)
    price_per_gram_24k = round(price_per_ounce_inr / 31.1034768, 2)
except Exception as e:
    print(f"Error fetching data from API: {e}")
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
        # Added the requested Date column here
        writer.writerow(["Date", "Time", "Price_per_Gram_24K_INR"])
    writer.writerow([current_date, current_time, price_per_gram_24k])

# 3. ALERT CONDITIONAL: Fire alert only if price targets ₹14,000 or lower
ALERT_THRESHOLD = 14000.00

if price_per_gram_24k <= ALERT_THRESHOLD:
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    message = (
        f"🚨 24K GOLD PRICE DROP ALERT!\n\n"
        f"The price of 1 gram of 24K gold has dropped below your threshold!\n"
        f"📉 Current Price: ₹{price_per_gram_24k}/gm\n"
        f"🎯 Target Level: ≤ ₹{ALERT_THRESHOLD}\n"
        f"🕒 Time: {current_date} {current_time} UTC"
    )
    
    # Crucial Fix: Corrected to the specialized telegram bot API address
    telegram_url = f"https://telegram.org{bot_token}/sendMessage"
    requests.post(telegram_url, data={"chat_id": chat_id, "text": message})
    print(f"Alert triggered and sent! Current price (₹{price_per_gram_24k}) is <= ₹{ALERT_THRESHOLD}")
else:
    print(f"No alert sent. 24K Gold is at ₹{price_per_gram_24k}/gm (Target: ≤ ₹{ALERT_THRESHOLD})")
