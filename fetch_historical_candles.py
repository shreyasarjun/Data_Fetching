# fetch_historical_candles.py

import os
from urllib.parse import quote
from api_client import BaseAPIClient
import time
import os


class ExpiredHistoricalCandleAPI(BaseAPIClient):
    """
    Handles:
    - Constructing expired historical candle URL
    - Delegating API call to BaseAPIClient
    """

    def __init__(self,delay_seconds: int = 1.2):
        super().__init__()
        self.delay_seconds = delay_seconds


        self.expired_historical_candle_url = os.getenv(
            "EXPIRED_HISTORICAL_CANDLE_URL"
        )

        if not self.expired_historical_candle_url:
            raise ValueError(
                "EXPIRED_HISTORICAL_CANDLE_URL not found in .env"
            )

    def _build_historical_candle_url(
        self,
        expired_instrument_key: str,
        interval: str,
        to_date: str,
        from_date: str
    ) -> str:
        """
        Builds expired historical candle API URL.
        """
        encoded_key = quote(expired_instrument_key)

        return self.expired_historical_candle_url.format(
            expired_instrument_key=encoded_key,
            interval=interval,
            to_date=to_date,
            from_date=from_date
        )

    def fetch_expired_historical_candles(
        self,
        expired_instrument_key: str,
        interval: str,
        to_date: str,
        from_date: str
    ):
        """
        Public API method.
        """
        #print("\n \n waiting 1.2 Seconds \n \n")
        time.sleep(self.delay_seconds)
        url = self._build_historical_candle_url(
            expired_instrument_key=expired_instrument_key,
            interval=interval,
            to_date=to_date,
            from_date=from_date
        )
        return self.trigger_api(url)
