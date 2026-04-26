import requests
import csv

# =========================
# CONFIG
# =========================
UNDERLYING_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"
ENCODED_INSTRUMENT_KEY = "NSE_INDEX%7CNifty%2050"  # URL encoded
UNIT = "minutes"
INTERVAL = "1"
ACCESS_TOKEN="eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIyNENDWkgiLCJqdGkiOiI2OTg0MTE4ZjI5NTgwOTQyZTMwY2NkMWIiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzcwMjYyOTI3LCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NzAzMjg4MDB9.bS3LbUajmbzCWyg5-y1VWfBcHHIW4SHaadiTivVdJrU"
OUTPUT_CSV = "nifty_intraday.csv"

# Extra columns (static values as per sample)
INDEX_NAME = "NIFTY"
STRIKE_PRICE = 25700
OPTION_TYPE = "CE"
EXPIRY_DATE = "2026-02-10"

# =========================
# API CALL
# =========================
url = f"https://api.upstox.com/v3/historical-candle/intraday/{ENCODED_INSTRUMENT_KEY}/{UNIT}/{INTERVAL}"

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Bearer {ACCESS_TOKEN}"
}

response = requests.get(url, headers=headers)
response.raise_for_status()

data = response.json()
candles = data.get("data", {}).get("candles", [])

# =========================
# SAVE TO CSV
# =========================
with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)

    # Header
    writer.writerow([
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "index",
        "strike_price",
        "option_type",
        "expiry_date"
    ])

    # Rows
    for c in candles:
        timestamp, open_, high, low, close, volume, oi = c

        writer.writerow([
            timestamp,
            open_,
            high,
            low,
            close,
            INDEX_NAME,
            STRIKE_PRICE,
            OPTION_TYPE,
            EXPIRY_DATE
        ])

print(f"CSV saved successfully: {OUTPUT_CSV}")
