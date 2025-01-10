#!/usr/bin/env python3

"""
monkeystats.py

This module fetches and displays selected user information from the Monkeytype API.

created by: https://github.com/Mizrakjian
date: 2024-12-29
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from client import MonkeytypeClient
from heatmap import activity_heatmap
from utils import calculate_level, format_time, remaining_level_xp, shorten_number, total_level_xp

utc = ZoneInfo("UTC")


def streaks(data: dict) -> str:
    """Fetch and display the user's current streak information."""

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
    color_on = "\033[38;5;2m" if claimed else "\033[38;5;1m"
    reset = "\033[0m"

    return (
        f"  streak: "
        f"{current_streak} days ({color_on}{streak_status} {time_left}{reset}) | "
        f"best: {best_streak} days"
    )


def test_counts(data: dict) -> str:
    """Fetch and display the user's current test counts."""

    completed_tests = data["completedTests"]
    started_tests = data["startedTests"]
    time_typing = data["timeTyping"]

    completion_rate = completed_tests / started_tests * 100 if started_tests else 0

    time_str = format_time(timedelta(seconds=time_typing))

    return (
        f"   tests: "
        f"{started_tests} started | "
        f"{completed_tests} completed ({completion_rate:.1f}%)\n"
        f"    time: {time_str} (~{time_typing/completed_tests:.0f}s/test)"
    )


def last_test(client: MonkeytypeClient) -> str:
    """Fetch and display the user's last test information and PB."""

    data = client.last_test()

    test_mode = data["mode"]
    mode_unit = data["mode2"]
    language = data["language"]
    punctuation = data.get("punctuation", False)
    numbers = data.get("numbers", False)
    is_pb = data.get("isPb", False)

    pb_data = client.personal_bests(test_mode, mode_unit)

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

    test_modifiers = f"@{'on' if punctuation else 'off'} #{'on' if numbers else 'off'}"
    pb_text = "★ new pb ★" if is_pb else f"pb: {pb_wpm:.1f} wpm {pb_accuracy:.0f}% acc"

    return (
        f"  last test: {test_mode} {mode_unit} | {test_modifiers} | "
        f"{language} | {time_str} ({time_ago} ago)\n"
        f"  result: {data['wpm']:.1f} wpm {data['acc']:.0f}% acc | {pb_text}"
    )


def profile(data: dict, user: str) -> str:
    """Format the user's profile information."""

    joined = datetime.fromtimestamp(data["addedAt"] / 1000, tz=utc)
    days_since_joined = (datetime.now(tz=utc) - joined).days

    return (
        f"Monkeytype info for {user}:\n\n"
        f"  joined: {joined.strftime('%d %b %Y')} "
        f"({days_since_joined} days ago)\n"
        f"  {level_details(data['xp'])}"
    )


def level_details(xp: int) -> str:
    """Generate a summary string for the current level, XP, and progress."""

    level = calculate_level(xp)
    current_xp = xp - total_level_xp(level)
    max_xp = remaining_level_xp(level)
    needed_xp = max_xp - current_xp

    return (
        f" level: {level} | {shorten_number(xp)} xp | "
        f"{shorten_number(current_xp)}/{shorten_number(max_xp)} "
        f"({shorten_number(needed_xp)} to go)"
    )


def main():
    """Main function to fetch and display user streak information."""

    client = MonkeytypeClient()

    output = [
        profile(client.profile(), client.user),
        streaks(client.streaks()),
        "",
        test_counts(client.stats()),
        "",
        activity_heatmap(client.activity()),
        "",
        last_test(client),
    ]

    print("\n", "\n".join(output), "\n", sep="")


if __name__ == "__main__":
    main()
