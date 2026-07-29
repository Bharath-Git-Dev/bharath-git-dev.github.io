import os
from datetime import datetime
import requests

# Get current date and time
now = datetime.utcnow()
current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

# Construct the requested message layout
message = (
    f"👋 Hi!\n\n"
    f"📅 Date: {current_date}\n"
    f"🕒 Time: {current_time} UTC"
)

# Fetch Telegram secret credentials from GitHub Actions environment
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

# Execute dispatch over corrected endpoint layout
telegram_url = f"https://telegram.org{bot_token}/sendMessage"

try:
    response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message}, timeout=10)
    response.raise_for_status()
    print(f"✅ Status: Daily 'Hi' message dispatched successfully at {current_time} UTC.")
except Exception as e:
    print(f"❌ Status: Telegram transmission failed. Error details: {e}")
    exit(1)
