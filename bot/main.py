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
account_id: int | None = None


def verify_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return True
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/webhook", methods=["POST"])
def webhook():
    sig = request.headers.get("X-Signature", "")
    if not verify_signature(request.data, sig):
        log.warning("Invalid webhook signature — request rejected")
        return jsonify({"error": "unauthorized"}), 401

    try:
        data = json.loads(request.data)
    except json.JSONDecodeError:
        return jsonify({"error": "invalid JSON"}), 400

    action  = data.get("action", "").capitalize()   # "buy" → "Buy"
    ticker  = data.get("ticker", "")
    price   = float(data.get("price", 0))
    stop    = float(data.get("stop", 0))
    target  = float(data.get("target", 0))
    qty     = int(data.get("qty", 1))

    if action not in ("Buy", "Sell"):
        return jsonify({"error": f"unknown action: {action}"}), 400
    if not ticker:
        return jsonify({"error": "missing ticker"}), 400
    if stop == 0 or target == 0:
        return jsonify({"error": "missing stop or target"}), 400

    log.info("Signal: %s %s x%d | entry=%.2f stop=%.2f target=%.2f",
             action, ticker, qty, price, stop, target)

    result = client.place_bracket_order(account_id, ticker, action, qty, stop, target)
    log.info("Order placed: %s", result)

    return jsonify({"status": "ok", "order": result}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    client.authenticate()
    accounts = client.get_accounts()
    account_id = accounts[0]["id"]
    log.info("Authenticated. Account ID: %d. Starting server on port %d", account_id, WEBHOOK_PORT)
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)
