from zoneinfo import ZoneInfo

import requests

from client.models import Profile, Stats, Streaks
from config import load_auth


class MonkeytypeClient:
    """Client for interacting with the Monkeytype API."""

    def __init__(self, base_url: str = "https://api.monkeytype.com"):
        auth = load_auth()  # Load key and user variables from auth file
        self.api_key = auth.get("MONKEYTYPE_API_KEY", "")
        self.user = auth.get("MONKEYTYPE_USER", "")
        if not (self.api_key and self.user):
            raise ValueError(
                "MONKEYTYPE_API_KEY and MONKEYTYPE_USER must be set in environment variables."
            )

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

    def profile(self) -> Profile:
        """Retrieve the user's profile information."""
        data = self.fetch_data(f"/users/{self.user}/profile")
        return Profile.from_api(data)

    def streaks(self) -> Streaks:
        """Retrieve the user's streak information."""
        data = self.fetch_data(f"/users/streak")
        return Streaks.from_api(data)

    def stats(self) -> Stats:
        """Retrieve the user's test count stats."""
        data = self.fetch_data(f"/users/stats")
        return Stats.from_api(data)

    def activity(self) -> dict:
        """Retrieve the user's current test activity."""
        return self.fetch_data("/users/currentTestActivity")

    def last_test(self) -> dict:
        """Retrieve the user's last test information."""
        return self.fetch_data(f"/results/last")

    def personal_bests(self, test_mode: str, mode_unit: str) -> dict:
        """
        Retrieve the user's personal bests for a specific test mode and unit.

        Args:
            test_mode (str): The test mode (e.g., "time", "words").
            mode_unit (str): The mode unit (e.g., "60s", "100w").

        Returns:
            dict: The personal best data.
        """
        params = {"mode": test_mode, "mode2": mode_unit}
        return self.fetch_data("/users/personalBests", params=params)
