#!/usr/bin/env python3

"""
monkeystats.py

This module fetches and displays selected user information from the Monkeytype API.

created by: https://github.com/Mizrakjian
date: 2024-12-29
"""

import os
from datetime import datetime, time, timedelta, timezone

import requests

# Constants
API_BASE_URL = "https://api.monkeytype.com"
API_KEY_FILE = "monkeytype.apikey"
API_KEY = ""


def get_api_key(file=API_KEY_FILE):
    """Retrieve the API key from a file or environment variable."""

    global API_KEY

    api_key = os.getenv("APE_KEY")
    if api_key:
        API_KEY = api_key
        return ()
    if os.path.exists(file):
        with open(file, "r") as f:
            API_KEY = f.read().strip()
            return ()
    raise ValueError(
        "API key not found. Set the APE_KEY environment variable or save it in monkeytype.apikey."
    )


def fetch_data(endpoint: str) -> dict:
    """Fetch data from a specified Monkeytype API endpoint."""
    headers = {"Authorization": f"ApeKey {API_KEY}"}
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_streak_info():
    """Fetch and display the user's current streak information."""

    data = fetch_data("/users/streak")
    streak_data = data.get("data", {})

    latest_timestamp = streak_data.get("lastResultTimestamp", None)
    streak_length = streak_data.get("length", 0)
    max_streak_length = streak_data.get("maxLength", 0)

    latest_test = datetime.fromtimestamp(latest_timestamp / 1000, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    claimed_today = latest_test.date() == now.date()

    midnight = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=now.tzinfo)
    hours_left = (midnight - now).seconds // 3600
    minutes_left = (midnight - now).seconds % 3600 // 60

    print(
        f"Last Test Taken: {latest_test.strftime('%Y-%m-%d %H:%M:%S UTC') or 'No recent test data available.'}"
    )
    print(f" Current Streak: {streak_length} days")
    print(f" Longest Streak: {max_streak_length} days")
    print(f"  Claimed Today: {'Yes' if claimed_today else 'No'}")
    print(f"      Time Left: {hours_left}h {minutes_left:02d}m")


def get_test_counts():
    """Fetch and display the user's current test counts."""

    data = fetch_data("/users/stats")
    test_data = data.get("data", {})

    completed_tests = test_data.get("completedTests", 0)
    started_tests = test_data.get("startedTests", 0)
    time_typing = test_data.get("timeTyping", 0)
    total_seconds = int(time_typing)  # Truncate fractional seconds
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(f"  Started Tests: {started_tests}")
    print(f"Completed Tests: {completed_tests}")
    if started_tests > 0:
        print(f"Completion Rate: {completed_tests / started_tests * 100:.2f}%")
    else:
        print("Completion Rate: N/A")
    print(f"    Time Typing: {hours}:{minutes:02}:{seconds:02}")


def main():
    """Main function to fetch and display user streak information."""
    get_api_key()

    print("\nMonkeytype info:")
    get_streak_info()
    get_test_counts()

    print()


if __name__ == "__main__":
    main()
