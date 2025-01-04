#!/usr/bin/env python3

"""
monkeystats.py

This module fetches and displays selected user information from the Monkeytype API.

created by: https://github.com/Mizrakjian
date: 2024-12-29
"""

import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from xp_utils import format_level_details

utc = ZoneInfo("UTC")

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
        return
    if os.path.exists(file):
        with open(file, "r") as f:
            API_KEY = f.read().strip()
            return
    raise ValueError(
        "API key not found. Set the APE_KEY environment variable or save it in monkeytype.apikey."
    )


def fetch_data(endpoint: str, params=None) -> dict:
    """Fetch data from a specified Monkeytype API endpoint."""
    headers = {"Authorization": f"ApeKey {API_KEY}"}
    url = f"{API_BASE_URL}{endpoint}"
    response = requests.get(url, headers=headers, params=params or {})
    # print("\n\n", response.json(), "\n\n")
    response.raise_for_status()
    return response.json().get("data", {})


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


def show_streak_info():
    """Fetch and display the user's current streak information."""

    data = fetch_data("/users/streak")

    current_streak = data["length"]
    best_streak = data["maxLength"]
    last_result = datetime.fromtimestamp(data["lastResultTimestamp"] / 1000, tz=utc)

    now = datetime.now(tz=utc)
    tomorrow = now.date() + timedelta(days=1)
    midnight = datetime.min.time()
    reset = datetime.combine(tomorrow, midnight, tzinfo=utc)
    time_left = format_time(reset - now)

    claimed = last_result.date() == now.date()
    streak_status = "claimed — resets in" if claimed else "unclaimed — lost in"

    print(
        f"{'Streaks':>11} -> "
        f"{current_streak} days ({streak_status} {time_left}) | "
        f"best: {best_streak} days"
    )


def show_test_counts():
    """Fetch and display the user's current test counts."""

    data = fetch_data("/users/stats")

    completed_tests = data["completedTests"]
    started_tests = data["startedTests"]
    time_typing = data["timeTyping"]

    completion_rate = completed_tests / started_tests * 100 if started_tests else 0

    time_str = format_time(timedelta(seconds=time_typing))

    print(
        f"{'Tests':>11} -> "
        f"{started_tests} started | "
        f"{completed_tests} completed ({completion_rate:.1f}%) | "
        f"time: {time_str} (~{time_typing/completed_tests:.0f}s/test)"
    )


def show_last_test_info():
    """Fetch and display the user's last test information and PB."""

    data = fetch_data("/results/last")

    test_mode = data["mode"]
    mode_unit = data["mode2"]
    language = data["language"]
    punctuation = data.get("punctuation", False)
    numbers = data.get("numbers", False)

    pb_params = {"mode": test_mode, "mode2": mode_unit}
    pb_data = fetch_data("/users/personalBests", params=pb_params)

    pb_wpm, pb_accuracy = next(
        (pb["wpm"], pb["acc"])
        for pb in pb_data
        if pb["language"] == language
        if pb.get("punctuation", False) == punctuation
        if pb.get("numbers", False) == numbers
    )

    test_time = datetime.fromtimestamp(data["timestamp"] / 1000, tz=utc)
    time_str = test_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    time_ago = format_time(datetime.now(tz=utc) - test_time)

    print(
        f"{'Last Test':>11} -> {test_mode} {mode_unit} | "
        f"@{'on' if punctuation else 'off'} #{'on' if numbers else 'off'} | "
        f"{language} | {time_str} ({time_ago} ago)"
    )
    print(
        f"{'Results':>11} -> {data['wpm']:.1f} wpm {data['acc']:.0f}% acc | "
        f"pb: {pb_wpm:.1f} wpm {pb_accuracy:.0f}% acc"
    )


def show_profile():
    """Fetch and display the user's profile information."""
    data = fetch_data("/users/DuncanMcTung/profile")

    print(f"Monkeytype info for {data['name']}:")

    joined = datetime.fromtimestamp(data["addedAt"] / 1000, tz=utc)
    days_since_joined = (datetime.now(tz=utc) - joined).days

    print(
        f"{'Profile':>11} -> joined {joined.strftime('%d %b %Y')} "
        f"({days_since_joined} days ago) | "
        f"{format_level_details(data['xp'])}"
    )


def main():
    """Main function to fetch and display user streak information."""
    get_api_key()

    print()
    show_profile()
    show_test_counts()
    show_last_test_info()
    show_streak_info()
    print()


if __name__ == "__main__":
    main()
