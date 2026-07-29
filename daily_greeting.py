import os
from datetime import datetime
import pytz
import requests

def send_telegram_greeting():
    # Fetch environment variables
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("Error: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables.")
        return

    # Get current time in India (IST)
    ist_tz = pytz.timezone('Asia/Kolkata')
    now_ist = datetime.now(ist_tz)
    
    # Format date and time
    current_date = now_ist.strftime("%d-%m-%Y")
    current_time = now_ist.strftime("%I:%M %p")

    # Construct the greeting message
    message = f"Hi\n📅 Date: {current_date}\n🕒 Time: {current_time} IST"
    
    # Correct Telegram API URL endpoint
    telegram_url = f"https://telegram.org{bot_token}/sendMessage"
    
    try:
        response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message})
        if response.status_code == 200:
            print(f"Message sent successfully at {current_time} IST")
        else:
            print(f"Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    send_telegram_greeting()
