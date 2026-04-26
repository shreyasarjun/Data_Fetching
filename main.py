# main.py

from datetime import datetime, timedelta
import pandas as pd

from fetch_expiry_dates import ExpiryDatesAPI
from fetch_option_contracts import ExpiredOptionContractsAPI
from fetch_historical_candles import ExpiredHistoricalCandleAPI
from dataframe_builder import DataFrameBuilder
from custom_exceptions import APIClientError
import time

import os
from dotenv import load_dotenv

load_dotenv()  

UNDERLYING_INSTRUMENT_KEY = "NSE_INDEX|Nifty 50"
INTERVAL = "1minute"
DAYS_BACK = 10
MAX_EXPIRIES = None  # testing limit


def main():
    expiry_api = ExpiryDatesAPI()
    contracts_api = ExpiredOptionContractsAPI()
    candles_api = ExpiredHistoricalCandleAPI()

    expiry_response = expiry_api.fetch_expiry_dates(
        UNDERLYING_INSTRUMENT_KEY
    )

    expiry_dates = expiry_response.get("data", [])[:MAX_EXPIRIES]
    expiry_dates = ['2025-06-26']
    for expiry_date in expiry_dates:
        print(f"\n🔄 Processing expiry: {expiry_date}")

        expiry_df = pd.DataFrame()

        contracts = contracts_api.fetch_expired_option_contracts(
            instrument_key=UNDERLYING_INSTRUMENT_KEY,
            expiry_date=expiry_date
        )

        if not contracts:
            print(f"No contracts for {expiry_date}")
            continue

        to_date = datetime.strptime(expiry_date, "%Y-%m-%d")
        from_date = to_date - timedelta(days=DAYS_BACK)

        for contract in contracts:
            try:
                candle_response = candles_api.fetch_expired_historical_candles(
                    expired_instrument_key=contract["instrument_key"],
                    interval=INTERVAL,
                    to_date=to_date.strftime("%Y-%m-%d"),
                    from_date=from_date.strftime("%Y-%m-%d")
                )

                candles = candle_response["data"]["candles"]
                if not candles:
                    continue

                df = DataFrameBuilder.build_dataframe(
                    candles=candles,
                    index=contract["underlying_symbol"],
                    strike_price=contract["strike_price"],
                    ce_or_pe_type=contract["instrument_type"],
                    expiry_date=contract["expiry"]
                )

                expiry_df = pd.concat(
                    [expiry_df, df],
                    ignore_index=True
                )

            except APIClientError as e:
                print(f"⚠️ Candle fetch failed: {e}")

        if expiry_df.empty:
            print(f"No candle data for expiry {expiry_date}")
            continue

        # Convert strike_price to int
        expiry_df["strike_price"] = expiry_df["strike_price"].astype(int)

        filename = f"csv_files/{UNDERLYING_INSTRUMENT_KEY.split('|')[1]}_{expiry_date}.csv"
        expiry_df.to_csv(filename, index=False)

        print(f"✅ Saved {filename} ({len(expiry_df)} rows)")
        print(expiry_df.head())
        print("⏸ \n \n Cooling down before next expiry... \n. \n ")
        time.sleep(60)


if __name__ == "__main__":
    start_time = time.perf_counter()
    main()
    # End the timer
    end_time = time.perf_counter()

    # Calculate duration
    execution_time = end_time - start_time

    print(f"Total Execution time: {execution_time:.6f} seconds")
