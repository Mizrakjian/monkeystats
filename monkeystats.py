#!/usr/bin/env python3

"""
monkeystats.py

This module fetches and displays selected user information from the Monkeytype API.

created by: https://github.com/Mizrakjian
date: 2024-12-29
"""

import os
from datetime import datetime, timedelta, timezone

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


def format_time(elapsed: timedelta) -> str:
    """Format a timedelta duration as a human-readable string."""

    total_seconds = int(elapsed.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if total_seconds < 60:
        return f"{seconds}s"

    if total_seconds < 3600:
        return f"{minutes}m"

    return f"{hours}h {minutes:02d}m"


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

    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=now.tzinfo)
    time_left = format_time(midnight - now)
    time_ago = format_time(now - latest_test)

    print(f"{'Last Test':>13} -> {latest_test.strftime('%Y-%m-%d %H:%M:%S UTC')} ({time_ago} ago)")
    print(
        f"{'Streaks':>13} -> "
        f"Current: {streak_length}d | "
        f"Status: {'Claimed' if claimed_today else 'At risk'} | "
        f"Time Left: {time_left} | "
        f"Longest: {max_streak_length}d"
    )


def get_test_counts():
    """Fetch and display the user's current test counts."""

    data = fetch_data("/users/stats")
    test_data = data.get("data", {})

    completed_tests = test_data.get("completedTests", 0)
    started_tests = test_data.get("startedTests", 0)
    time_typing = int(test_data.get("timeTyping", 0))

    completion_rate = completed_tests / started_tests * 100 if started_tests > 0 else 0
    hours, remainder = divmod(time_typing, 3600)
    minutes, seconds = divmod(remainder, 60)

    print(
        f"{'Tests':>13} -> "
        f"{completed_tests} completed | "
        f"{started_tests} started | "
        f"{completion_rate:.2f}% completion"
    )
    print(
        f"{'Time Typing':>13} -> "
        f"{hours}h {minutes:02}m {seconds:02}s | "
        f"~{time_typing/completed_tests:.0f}s/test"
    )


def main():
    """Main function to fetch and display user streak information."""
    get_api_key()

    print("\nMonkeytype info:")
    get_test_counts()
    get_streak_info()

    print()


if __name__ == "__main__":
    main()
