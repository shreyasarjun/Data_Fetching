import os
from urllib.parse import quote
from typing import List, Dict, Any
from api_client import BaseAPIClient
import os
from dotenv import load_dotenv

load_dotenv()  

class ExpiredOptionContractsAPI(BaseAPIClient):
    """
    Handles:
    - Constructing expired option contracts URL
    - Fetching data from API
    - Normalizing response for consumers
    """

    REQUIRED_FIELDS = (
        "underlying_symbol",
        "expiry",
        "strike_price",
        "instrument_type",
        "instrument_key",
    )

    def __init__(self):
        super().__init__()

        self.expired_option_contracts_url = os.getenv(
            "EXPIRED_OPTION_CONTRACTS_URL"
        )

        if not self.expired_option_contracts_url:
            raise ValueError(
                "EXPIRED_OPTION_CONTRACTS_URL not found in .env"
            )

    def _build_expired_contracts_url(
        self,
        instrument_key: str,
        expiry_date: str
    ) -> str:
        encoded_key = quote(instrument_key)

        return self.expired_option_contracts_url.format(
            instrument_key=encoded_key,
            expiry_date=expiry_date
        )

    @staticmethod
    def _extract_required_fields(
        raw_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract only required fields from API response.
        """
        extracted = []

        for item in raw_data:
            extracted.append({
                "underlying_symbol": item.get("underlying_symbol"),
                "expiry": item.get("expiry"),
                "strike_price": item.get("strike_price"),
                "instrument_type": item.get("instrument_type"),
                "instrument_key": item.get("instrument_key"),
            })

        return extracted

    def fetch_expired_option_contracts(
        self,
        instrument_key: str,
        expiry_date: str
    ) -> List[Dict[str, Any]]:
        """
        Public method used by consumers.
        Returns normalized contract data.
        """
        url = self._build_expired_contracts_url(
            instrument_key=instrument_key,
            expiry_date=expiry_date
        )

        response = self.trigger_api(url)

        # Defensive validation
        if "data" not in response or not isinstance(response["data"], list):
            raise ValueError("Unexpected API response structure")

        return self._extract_required_fields(response["data"])
