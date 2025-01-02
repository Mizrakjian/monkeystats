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

    timestamp = streak_data.get("lastResultTimestamp", None)
    streak_length = streak_data.get("length", 0)
    max_streak_length = streak_data.get("maxLength", 0)

    test_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    now = datetime.now(tz=timezone.utc)
    midnight = datetime.combine(now.date() + timedelta(days=1), datetime.min.time(), tzinfo=now.tzinfo)
    time_left = format_time(midnight - now)

    if test_time.date() == now.date():
        streak_status = "claimed — reset in"
    else:
        streak_status = "unclaimed — lost in"

    print(
        f"{'Streaks':>13} -> "
        f"{streak_length}d ({streak_status} {time_left}) | "
        f"best: {max_streak_length}d"
    )


def get_test_counts():
    """Fetch and display the user's current test counts."""
    data = fetch_data("/users/stats")
    test_data = data.get("data", {})

    completed_tests = test_data.get("completedTests", 0)
    started_tests = test_data.get("startedTests", 0)
    time_typing = int(test_data.get("timeTyping", 0))

    completion_rate = completed_tests / started_tests * 100 if started_tests > 0 else 0

    time_str = format_time(timedelta(seconds=time_typing))

    print(
        f"{'Tests':>13} -> "
        f"{started_tests} started | "
        f"{completed_tests} completed ({completion_rate:.1f}%) | "
        f"time: {time_str} (~{time_typing/completed_tests:.0f}s/test)"
    )


def get_last_test_info():
    """Fetch and display the user's last test information and PB."""
    # Fetch the last test result from the /last endpoint
    response = fetch_data("/results/last")
    last_result = response.get("data", {})
    if not last_result:
        print(f"{'Last Test':>13} -> No recent test data available.")
        return

    # Extract last test details
    wpm = last_result.get("wpm", 0)
    accuracy = last_result.get("acc", 0.0)
    mode = last_result.get("mode", "Unknown").capitalize()
    duration = f"{last_result.get('testDuration', 'Unknown')}s"
    language = last_result.get("language", "Unknown").replace("_", " ").capitalize()
    punctuation = last_result.get("punctuation", False)
    numbers = last_result.get("numbers", False)
    timestamp = last_result.get("timestamp", None)

    # Fetch PBs for the specific mode and duration
    pb_params = {"mode": mode.lower(), "mode2": last_result.get("testDuration", 0)}
    pb_response = fetch_data("/users/personalBests", params=pb_params)
    pb_list = pb_response.get("data", [])
    pb_wpm = 0
    pb_accuracy = 0.0

    # Parse PBs to find the most relevant entry
    for pb in pb_list:
        if (
            pb.get("language", "").replace("_", " ").capitalize() == language
            and pb.get("punctuation", False) == punctuation
            and pb.get("numbers", False) == numbers
        ):
            pb_wpm = pb.get("wpm", 0)
            pb_accuracy = pb.get("acc", 0.0)
            break

    # Convert timestamp to datetime
    test_time = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc) if timestamp else None
    time_str = test_time.strftime("%Y-%m-%d %H:%M:%S UTC") if test_time else "Unknown"
    time_ago = format_time(datetime.now(tz=timezone.utc) - test_time) if test_time else "Unknown"

    # Construct test type string
    test_type = f"{language} | {mode} ({duration})"
    if punctuation:
        test_type += " | Punctuation"
    if numbers:
        test_type += " | Numbers"

    print(f"{'Last Test':>13} -> {test_type} | {time_str} ({time_ago} ago)")
    print(
        f"{'Speed':>13} -> {wpm:.1f} wpm {accuracy:.0f}% acc | "
        f"pb: {pb_wpm:.1f} wpm {pb_accuracy:.0f}% acc"
    )


def main():
    """Main function to fetch and display user streak information."""
    get_api_key()

    print("\nMonkeytype info:")
    get_test_counts()
    get_last_test_info()
    get_streak_info()
    print()


if __name__ == "__main__":
    main()

"""
Monkeytype Info:
         Tests : 8657 completed | 9191 started (94.1%) | time: 137h 17m (~57s/test)
     Last Test : english 1k | Timed (60s) | 2025-01-02 17:39:35 UTC (16s ago)
       Results : 81.1 wpm 98% acc | pb: 89.2 wpm 95% acc
        Streak : 22d (claimed | reset in 6h 20m) | best: 65d
"""
