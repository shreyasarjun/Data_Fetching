# api_client.py

import os
import time
import requests
from dotenv import load_dotenv
from custom_exceptions import APIClientError

load_dotenv()  # load ONCE here

class BaseAPIClient:
    def __init__(self, timeout=30):
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")

        if not self.access_token:
            raise ValueError("UPSTOX_ACCESS_TOKEN not found in environment")

        self.timeout = timeout

        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Rate-limit handling
        self.max_retries = 5
        self.base_delay = 1

    def trigger_api(self, url: str):
        for attempt in range(1, self.max_retries + 1):
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                wait_time = self.base_delay * attempt
                print(
                    f"⚠️ 429 Rate limit hit. Retry {attempt} after {wait_time}s"
                )
                time.sleep(wait_time)
                continue

            raise APIClientError(
                f"API Error {response.status_code}: {response.text}"
            )

        raise APIClientError("Max retries exceeded")
