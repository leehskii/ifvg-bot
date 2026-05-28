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

# NQ instrument details
# Swap to "MNQM5" and TICK_VALUE=2.0 to trade Micro NQ instead
INSTRUMENT    = os.getenv("INSTRUMENT", "NQM5")   # update expiry each quarter
TICK_SIZE     = 0.25   # minimum price move in points
TICK_VALUE    = 20.0   # USD per tick (NQ full) — MNQ = 2.0
