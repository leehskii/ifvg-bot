import csv
import os
from datetime import datetime, timezone

LOG_FILE = "trades.csv"
FIELDS = [
    "timestamp", "symbol", "action", "entry", "stop", "target",
    "be_level", "contracts", "risk_usd", "status", "note"
]


def log_trade(record: dict) -> None:
    record.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
    record.setdefault("note", "")
    row = {f: record.get(f, "") for f in FIELDS}

    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def update_trade_status(symbol: str, new_status: str, note: str = "") -> None:
    """Rewrites the CSV to update the last open trade for a symbol."""
    if not os.path.exists(LOG_FILE):
        return
    rows = []
    updated = False
    with open(LOG_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not updated and row["symbol"] == symbol and row["status"] == "open":
                row["status"] = new_status
                row["note"] = note
                updated = True
            rows.append(row)

    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
