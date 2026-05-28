import logging
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

log = logging.getLogger(__name__)


def send(message: str) -> None:
    """Send a Telegram message. Silently skips if credentials are not set."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       message,
            "parse_mode": "HTML",
        }, timeout=5)
    except Exception as e:
        log.warning("Telegram notification failed: %s", e)


def trade_opened(data: dict) -> None:
    action = data["action"].upper()
    emoji  = "🟢" if action == "BUY" else "🔴"
    send(
        f"{emoji} <b>{action} {data['ticker']}</b>\n"
        f"Entry:     {data['price']}\n"
        f"Stop:      {data['stop']}\n"
        f"Target:    {data['target']}\n"
        f"BE level:  {data['be']}\n"
        f"Contracts: {data['qty']}\n"
        f"Risk:      ${data.get('risk', '?')}"
    )


def breakeven_set(symbol: str, entry: float) -> None:
    send(f"🔒 <b>Break even set</b>\n{symbol} @ {entry}")


def trade_skipped(reason: str, ticker: str) -> None:
    send(f"⚠️ Trade skipped — {ticker}\n{reason}")
