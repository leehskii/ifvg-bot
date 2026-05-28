import hashlib
import hmac
import json
import logging

from flask import Flask, request, jsonify
from config import WEBHOOK_SECRET, WEBHOOK_PORT
from tradovate import TradovateClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
client = TradovateClient()


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verify TradingView webhook HMAC signature."""
    if not WEBHOOK_SECRET:
        return True
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/webhook", methods=["POST"])
def webhook():
    sig = request.headers.get("X-Signature", "")
    if not verify_signature(request.data, sig):
        log.warning("Invalid webhook signature")
        return jsonify({"error": "unauthorized"}), 401

    try:
        data = json.loads(request.data)
    except json.JSONDecodeError:
        return jsonify({"error": "invalid JSON"}), 400

    action = data.get("action", "").capitalize()   # "buy" → "Buy"
    symbol = data.get("ticker", "")
    qty    = int(data.get("qty", 1))

    if action not in ("Buy", "Sell"):
        return jsonify({"error": f"unknown action: {action}"}), 400

    log.info("Signal received: %s %s x%d", action, symbol, qty)

    accounts = client.get_accounts()
    account_id = accounts[0]["id"]

    result = client.place_order(account_id, symbol, action, qty)
    log.info("Order placed: %s", result)

    return jsonify({"status": "ok", "order": result}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    client.authenticate()
    log.info("Tradovate authenticated. Starting webhook server on port %d", WEBHOOK_PORT)
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)
