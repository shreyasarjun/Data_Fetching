# upstox_expiry_api.py

import os
from urllib.parse import quote
from api_client import BaseAPIClient
import os


class ExpiryDatesAPI(BaseAPIClient):
    """
    Handles only:
    - Constructing expiry API URL
    - Calling common GET logic
    """

    def __init__(self):
        super().__init__()
        self.expiry_url_template = os.getenv(
            "EXPIRY_DATES_FETCHING_URL"
        )

        if not self.expiry_url_template:
            raise ValueError("EXPIRY_DATES_FETCHING_URL not found in .env")

    def _build_expiry_url(self, instrument_key: str) -> str:
        encoded_key = quote(instrument_key)
        return self.expiry_url_template.format(
            instrument_key=encoded_key
        )

    def fetch_expiry_dates(self, instrument_key: str):
        url = self._build_expiry_url(instrument_key)
        return self.trigger_api(url)
