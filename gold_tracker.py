import os
import csv
from datetime import datetime
import requests

# 1. EXTRACT: Fetch gold price in INR using ultra-stable public endpoints
try:
    # Fetch live PAX Gold price in USD from Coinbase Public API
    gold_url = "https://coinbase.com"
    gold_response = requests.get(gold_url, timeout=10)
    
    # Fallback to older v2 endpoint if v3 experiences a localized cloud hiccup
    if gold_response.status_code != 200:
        gold_url = "https://coinbase.com"
        gold_response = requests.get(gold_url, timeout=10)
        gold_response.raise_for_status()
        price_per_ounce_usd = float(gold_response.json()["data"]["amount"])
    else:
        # Parse the price from Coinbase's primary v3 engine
        price_per_ounce_usd = float(gold_response.json()["price"])

    # Fetch live USD to INR fiat conversion rate from an open exchange api
    fx_url = "https://er-api.com"
    fx_response = requests.get(fx_url, timeout=10)
    fx_response.raise_for_status()
    usd_to_inr_rate = float(fx_response.json()["rates"]["INR"])

    # Combine metrics: Convert total Ounce value to INR, then reduce to 1 Gram of 24K Gold
    price_per_ounce_inr = price_per_ounce_usd * usd_to_inr_rate
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
        f"🌐 Source: Public Market API Feed"
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
