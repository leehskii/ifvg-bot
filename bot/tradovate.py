import requests
from config import (BASE_URL, TRADOVATE_USERNAME, TRADOVATE_PASSWORD,
                    TRADOVATE_APP_ID, TRADOVATE_APP_VERSION,
                    TRADOVATE_DEVICE_ID, TRADOVATE_CID, TRADOVATE_SECRET)


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
        self.access_token = resp.json()["accessToken"]
        self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
        return self.access_token

    def get_accounts(self):
        resp = self.session.get(f"{BASE_URL}/account/list")
        resp.raise_for_status()
        return resp.json()

    def get_contract_id(self, symbol: str) -> int:
        resp = self.session.get(f"{BASE_URL}/contract/find", params={"name": symbol})
        resp.raise_for_status()
        return resp.json()["id"]

    def place_bracket_order(self, account_id: int, symbol: str, action: str,
                            qty: int, stop: float, target: float) -> dict:
        """
        Places an OSO bracket: market entry + stop loss + profit target.
        action: "Buy" or "Sell"
        """
        contract_id = self.get_contract_id(symbol)

        # Opposite side for exit legs
        exit_action = "Sell" if action == "Buy" else "Buy"

        payload = {
            "accountId":  account_id,
            "contractId": contract_id,
            "action":     action,
            "orderQty":   qty,
            "orderType":  "Market",
            "timeInForce": "GTC",
            "bracket1": {
                "action":     exit_action,
                "orderType":  "Stop",
                "stopPrice":  round(stop, 2),
                "orderQty":   qty,
                "timeInForce": "GTC",
            },
            "bracket2": {
                "action":     exit_action,
                "orderType":  "Limit",
                "price":      round(target, 2),
                "orderQty":   qty,
                "timeInForce": "GTC",
            },
        }
        resp = self.session.post(f"{BASE_URL}/order/placeoso", json=payload)
        resp.raise_for_status()
        return resp.json()
