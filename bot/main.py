import hashlib
import hmac
import json
import logging
import threading
import time

from flask import Flask, request, jsonify
from config import WEBHOOK_SECRET, WEBHOOK_PORT, MNQ_PER_POINT, MAX_RISK_USD
from tradovate import TradovateClient
from trade_logger import log_trade, update_trade_status
import notifier

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

app = Flask(__name__)
client = TradovateClient()
account_id: int | None = None

# Tracks open positions for break even monitoring
# key: ticker, value: {entry, stop, be_level, action, qty, stop_order_id, be_set, contract_id}
open_positions: dict[str, dict] = {}


def verify_signature(payload: bytes, signature: str) -> bool:
    if not WEBHOOK_SECRET:
        return True
    expected = hmac.new(WEBHOOK_SECRET.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def extract_stop_order_id(order_response) -> int | None:
    """
    Tradovate placeoso returns a list: [entry_order, stop_order, target_order].
    Extracts the stop order ID (bracket1 = index 1).
    """
    try:
        if isinstance(order_response, list) and len(order_response) > 1:
            return order_response[1].get("orderId")
    except Exception:
        pass
    return None


# ─── Break Even Monitor ───────────────────────────────────────────────────────
def monitor_break_even():
    """Background thread: checks prices every 30s and moves stop to entry at 1R."""
    while True:
        time.sleep(30)
        for ticker, pos in list(open_positions.items()):
            if pos["be_set"]:
                continue
            try:
                contract_id = pos.get("contract_id")
                if not contract_id:
                    continue
                quote  = client.get_quote(contract_id)
                price  = quote.get("trade", {}).get("price") or quote.get("bid")
                if not price:
                    continue

                hit_be = (pos["action"] == "Buy"  and float(price) >= pos["be_level"]) or \
                         (pos["action"] == "Sell" and float(price) <= pos["be_level"])

                if hit_be and pos.get("stop_order_id"):
                    client.modify_stop(pos["stop_order_id"], pos["entry"])
                    pos["be_set"] = True
                    log.info("Break even set: %s @ %.2f", ticker, pos["entry"])
                    notifier.breakeven_set(ticker, pos["entry"])
                    update_trade_status(ticker, "open_be", f"BE set at {pos['entry']}")

            except Exception as e:
                log.warning("BE monitor error for %s: %s", ticker, e)


# ─── Webhook Handler ──────────────────────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def webhook():
    sig = request.headers.get("X-Signature", "")
    if not verify_signature(request.data, sig):
        log.warning("Invalid webhook signature — rejected")
        return jsonify({"error": "unauthorized"}), 401

    try:
        data = json.loads(request.data)
    except json.JSONDecodeError:
        return jsonify({"error": "invalid JSON"}), 400

    action = data.get("action", "").capitalize()   # "buy" → "Buy"
    ticker = data.get("ticker", "")
    price  = float(data.get("price", 0))
    stop   = float(data.get("stop", 0))
    target = float(data.get("target", 0))
    be     = float(data.get("be", 0))
    qty    = int(float(data.get("qty", 1)))
    risk   = float(data.get("risk", 0))

    if action not in ("Buy", "Sell"):
        return jsonify({"error": f"unknown action: {action}"}), 400
    if not ticker or stop == 0 or target == 0:
        return jsonify({"error": "missing required fields"}), 400

    # Safety check: never exceed max risk
    stop_dist = abs(price - stop)
    actual_risk = qty * stop_dist * MNQ_PER_POINT
    if actual_risk > MAX_RISK_USD:
        reason = f"Risk ${actual_risk:.2f} exceeds max ${MAX_RISK_USD}"
        log.warning("Trade skipped — %s: %s", ticker, reason)
        notifier.trade_skipped(reason, ticker)
        return jsonify({"error": reason}), 400

    log.info("Signal: %s %s x%d | entry=%.2f stop=%.2f target=%.2f be=%.2f risk=$%.2f",
             action, ticker, qty, price, stop, target, be, actual_risk)

    result = client.place_bracket_order(account_id, ticker, action, qty, stop, target)
    stop_order_id = extract_stop_order_id(result)
    contract_id   = client.get_contract_id(ticker)

    open_positions[ticker] = {
        "action":        action,
        "entry":         price,
        "stop":          stop,
        "target":        target,
        "be_level":      be,
        "qty":           qty,
        "stop_order_id": stop_order_id,
        "contract_id":   contract_id,
        "be_set":        False,
    }

    log_trade({
        "symbol":    ticker,
        "action":    action,
        "entry":     price,
        "stop":      stop,
        "target":    target,
        "be_level":  be,
        "contracts": qty,
        "risk_usd":  round(actual_risk, 2),
        "status":    "open",
    })

    notifier.trade_opened(data)
    log.info("Order placed: %s", result)

    return jsonify({"status": "ok", "order": result}), 200


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "open_positions": list(open_positions.keys())}), 200


# ─── Startup ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    client.authenticate()
    accounts   = client.get_accounts()
    account_id = accounts[0]["id"]
    log.info("Authenticated. Account ID: %d", account_id)

    be_thread = threading.Thread(target=monitor_break_even, daemon=True)
    be_thread.start()
    log.info("Break even monitor started (checks every 30s)")

    log.info("Starting webhook server on port %d", WEBHOOK_PORT)
    app.run(host="0.0.0.0", port=WEBHOOK_PORT)
