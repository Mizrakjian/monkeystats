import json
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from client.models import Activity, LastTest, Profile, Streaks
from config import load_auth


class MonkeytypeClient:
    """Client for interacting with the Monkeytype API."""

    def __init__(self, base_url: str = "https://api.monkeytype.com"):
        auth = load_auth()
        self.api_key = auth.get("MONKEYTYPE_API_KEY", "")
        self.user = auth.get("MONKEYTYPE_USER", "")
        if not (self.api_key and self.user):
            raise ValueError("MONKEYTYPE_API_KEY and MONKEYTYPE_USER must be set in .auth file.")

        self.base_url = base_url
        self.headers = {"Authorization": f"ApeKey {self.api_key}"}
        self.utc = ZoneInfo("UTC")

        # Explicit attributes for each model
        self.profile: Profile
        self.streaks: Streaks
        self.activity: Activity
        self.last_test: LastTest

        # Map attributes to their endpoints and model classes
        self._endpoints = {
            "profile": (f"/users/{self.user}/profile", Profile),
            "streaks": ("/users/streak", Streaks),
            "activity": ("/users/currentTestActivity", Activity),
            "last_test": ("/results/last", LastTest),
        }

    def _fetch_data(self, endpoint: str, params: dict | None = None) -> dict:
        """
        Fetch data from the Monkeytype API.

        Args:
            endpoint (str): API endpoint to query.

        Returns:
            dict: Parsed JSON response.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json().get("data", {})

    def fetch_all(self) -> None:
        """Fetch all available data and dynamically assign it to attributes."""

        for attr, (endpoint, model_class) in self._endpoints.items():
            data = self._fetch_data(endpoint)
            setattr(self, attr, model_class.from_api(data))

    def fetch_results(self) -> None:
        data = self._fetch_data("/results", {"limit": 1000})
        with open("results.json", "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
