import requests
from config import BASE_URL, TRADOVATE_USERNAME, TRADOVATE_PASSWORD, \
    TRADOVATE_APP_ID, TRADOVATE_APP_VERSION, TRADOVATE_DEVICE_ID, \
    TRADOVATE_CID, TRADOVATE_SECRET


class TradovateClient:
    def __init__(self):
        self.session = requests.Session()
        self.access_token = None

    def authenticate(self):
        payload = {
            "name":       TRADOVATE_USERNAME,
            "password":   TRADOVATE_PASSWORD,
            "appId":      TRADOVATE_APP_ID,
            "appVersion": TRADOVATE_APP_VERSION,
            "deviceId":   TRADOVATE_DEVICE_ID,
            "cid":        TRADOVATE_CID,
            "sec":        TRADOVATE_SECRET,
        }
        resp = self.session.post(f"{BASE_URL}/auth/accesstokenrequest", json=payload)
        resp.raise_for_status()
        data = resp.json()
        self.access_token = data["accessToken"]
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        return self.access_token

    def get_accounts(self):
        resp = self.session.get(f"{BASE_URL}/account/list")
        resp.raise_for_status()
        return resp.json()

    def place_order(self, account_id: int, symbol: str, action: str, qty: int = 1):
        """
        action: "Buy" or "Sell"
        """
        payload = {
            "accountId":  account_id,
            "symbol":     symbol,
            "orderQty":   qty,
            "orderType":  "Market",
            "action":     action,
            "timeInForce": "GTC",
        }
        resp = self.session.post(f"{BASE_URL}/order/placeorder", json=payload)
        resp.raise_for_status()
        return resp.json()
