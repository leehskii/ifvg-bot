import os
from dotenv import load_dotenv

load_dotenv()

TRADOVATE_USERNAME    = os.getenv("TRADOVATE_USERNAME", "")
TRADOVATE_PASSWORD    = os.getenv("TRADOVATE_PASSWORD", "")
TRADOVATE_APP_ID      = os.getenv("TRADOVATE_APP_ID", "")
TRADOVATE_APP_VERSION = os.getenv("TRADOVATE_APP_VERSION", "1.0")
TRADOVATE_DEVICE_ID   = os.getenv("TRADOVATE_DEVICE_ID", "")
TRADOVATE_CID         = os.getenv("TRADOVATE_CID", "")
TRADOVATE_SECRET      = os.getenv("TRADOVATE_SECRET", "")

# "demo" or "live"
TRADOVATE_ENV = os.getenv("TRADOVATE_ENV", "demo")

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")
WEBHOOK_PORT   = int(os.getenv("WEBHOOK_PORT", "8080"))

BASE_URLS = {
    "demo": "https://demo.tradovateapi.com/v1",
    "live": "https://live.tradovateapi.com/v1",
}
BASE_URL = BASE_URLS[TRADOVATE_ENV]

# MNQ instrument — update the expiry code each quarter (M5=June, U5=Sep, Z5=Dec, H6=Mar)
INSTRUMENT    = os.getenv("INSTRUMENT", "MNQM5")
MNQ_PER_POINT = float(os.getenv("MNQ_PER_POINT", "2.0"))  # $2/pt MNQ, $20/pt NQ

# Risk management hard caps (Python-side safety net, mirrors Pine Script)
RISK_PER_TRADE = float(os.getenv("RISK_PER_TRADE", "100.0"))
MAX_RISK_USD   = float(os.getenv("MAX_RISK_USD",   "130.0"))

# Telegram notifications (optional — leave blank to disable)
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
