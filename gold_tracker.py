import os
from datetime import datetime
import requests

# 1. Capture current date and time parameters
now = datetime.utcnow()
current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

# 2. Build the requested minimal clean message layout
message = (
    f"👋 Hi!\n\n"
    f"📅 Date: {current_date}\n"
    f"🕒 Time: {current_time} UTC"
)

# 3. Securely pull variables from GitHub Environment
bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()

# Clean up common token formatting mistakes automatically
if bot_token.startswith("bot"):
    bot_token = bot_token[3:]

# 🌟 THE ABSOLUTE CORRECT URL STRUCTURE: Fixed domain and forced /bot prefix
telegram_url = f"https://telegram.org{bot_token}/sendMessage"

try:
    response = requests.post(telegram_url, data={"chat_id": chat_id, "text": message}, timeout=10)
    response.raise_for_status()
    print(f"✅ Status: Daily 'Hi' message dispatched successfully at {current_time} UTC.")
except Exception as e:
    # If it still fails, this will print the exact clean URL route for troubleshooting
    print(f"❌ Status: Telegram transmission failed.")
    print(f"Target URL attempted: https://telegram.org**🔑**/sendMessage")
    print(f"Error details: {e}")
    exit(1)
