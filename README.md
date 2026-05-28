# IFVG Trading Bot

Automated trading bot that detects **Imbalance / Fair Value Gaps (IFVG)** on TradingView and executes trades on Tradovate.

## How it works

1. Pine Script strategy runs on TradingView and detects IFVG setups
2. TradingView fires a webhook alert when a signal triggers
3. Python webhook server receives the alert and places the order on Tradovate

## Project structure

```
ifvg-bot/
  strategies/
    ifvg.pine       # TradingView strategy (Pine Script v5)
  bot/
    main.py         # Webhook server entry point
    tradovate.py    # Tradovate REST/WebSocket API client
    config.py       # Credentials and settings
  requirements.txt
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Copy `.env.example` to `.env` and fill in your Tradovate credentials and webhook secret.

### 3. Run the webhook server

```bash
python bot/main.py
```

### 4. Add the Pine Script to TradingView

- Open TradingView → Pine Script Editor
- Paste the contents of `strategies/ifvg.pine`
- Set your webhook URL in the alert settings

## Disclaimer

This bot is for educational purposes only. Trading futures carries **significant financial risk** and you may lose more than your initial investment. Always test on a demo account before going live. Past performance does not guarantee future results.
