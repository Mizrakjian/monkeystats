from functools import wraps
from time import perf_counter_ns
from zoneinfo import ZoneInfo

import requests

from client.models import Activity, LastTest, Profile, Streaks
from config import load_auth
from utils import timer


class MonkeytypeClient:
    """Client for interacting with the Monkeytype API."""

    def __init__(self, base_url: str = "https://api.monkeytype.com"):
        auth = load_auth()  # Load key and user variables from auth file
        self.api_key = auth.get("MONKEYTYPE_API_KEY", "")
        self.user = auth.get("MONKEYTYPE_USER", "")
        if not (self.api_key and self.user):
            raise ValueError("MONKEYTYPE_API_KEY and MONKEYTYPE_USER must be set in .auth file.")

        self.base_url = base_url
        self.headers = {"Authorization": f"ApeKey {self.api_key}"}
        self.utc = ZoneInfo("UTC")

    def fetch_data(self, endpoint: str, params=None) -> dict:
        """
        Fetch data from the Monkeytype API.

        Args:
            endpoint (str): API endpoint to query.
            params (dict, optional): Query parameters for the API call.

        Returns:
            dict: Parsed JSON response.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers, params=params or {})
        response.raise_for_status()
        return response.json().get("data", {})

    # --- Getters for specific endpoints ---
    @timer
    def profile(self) -> Profile:
        """Retrieve the user's profile information."""
        data = self.fetch_data(f"/users/{self.user}/profile")
        return Profile.from_api(data)

    @timer
    def streaks(self) -> Streaks:
        """Retrieve the user's streak information."""
        data = self.fetch_data(f"/users/streak")
        return Streaks.from_api(data)

    @timer
    def activity(self) -> Activity:
        """Retrieve the user's current test activity."""
        data = self.fetch_data("/users/currentTestActivity")
        return Activity.from_api(data)

    @timer
    def last_test(self) -> LastTest:
        """Retrieve the user's last test information."""
        data = self.fetch_data(f"/results/last")
        return LastTest.from_api(data)
