import pandas as pd
from typing import List, Dict, Any


class DataFrameBuilder:
    """
    Responsible for converting candle API response
    into a clean, typed Pandas DataFrame.
    """

    DEFAULT_COLUMNS = [
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "oi",
    ]

    @staticmethod
    def build_dataframe(
        candles: List[List[Any]],
        index: str,
        strike_price: float,
        ce_or_pe_type: str,
        expiry_date: str
    ) -> pd.DataFrame:
        """
        Builds a dataframe from candle data and enriches it
        with option/index metadata.

        :param candles: Raw candle list from API
        :param index: e.g. NIFTY / BANKNIFTY
        :param strike_price: Option strike price
        :param ce_or_pe_type: CE or PE
        :param expiry_date: Expiry date (YYYY-MM-DD)
        """

        if not candles:
            raise ValueError("Candles data is empty or None")

        df = pd.DataFrame(
            candles,
            columns=DataFrameBuilder.DEFAULT_COLUMNS
        )

        # Parse timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Explicit data types (important for analytics)
        df = df.astype({
            "open": "float64",
            "high": "float64",
            "low": "float64",
            "close": "float64",
            "volume": "int64",
            "oi": "int64",
        })

        # Add metadata columns (same for all rows)
        df["index"] = index
        df["strike_price"] = strike_price
        df["option_type"] = ce_or_pe_type
        df["expiry_date"] = pd.to_datetime(expiry_date)

        return df
