import os
from dotenv import load_dotenv

load_dotenv()

TRADOVATE_USERNAME  = os.getenv("TRADOVATE_USERNAME", "")
TRADOVATE_PASSWORD  = os.getenv("TRADOVATE_PASSWORD", "")
TRADOVATE_APP_ID    = os.getenv("TRADOVATE_APP_ID", "")
TRADOVATE_APP_VERSION = os.getenv("TRADOVATE_APP_VERSION", "1.0")
TRADOVATE_DEVICE_ID = os.getenv("TRADOVATE_DEVICE_ID", "")
TRADOVATE_CID       = os.getenv("TRADOVATE_CID", "")
TRADOVATE_SECRET    = os.getenv("TRADOVATE_SECRET", "")

# "demo" or "live"
TRADOVATE_ENV       = os.getenv("TRADOVATE_ENV", "demo")

WEBHOOK_SECRET      = os.getenv("WEBHOOK_SECRET", "")
WEBHOOK_PORT        = int(os.getenv("WEBHOOK_PORT", "8080"))

BASE_URLS = {
    "demo": "https://demo.tradovateapi.com/v1",
    "live": "https://live.tradovateapi.com/v1",
}

BASE_URL = BASE_URLS[TRADOVATE_ENV]
