#!/usr/bin/env python3

"""
monkeystats.py

This module fetches and displays selected user information from the Monkeytype API.

created by: https://github.com/Mizrakjian
date: 2024-12-29
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from client import MonkeytypeClient, Profile, Streaks
from client.models import Stats
from heatmap import activity_heatmap
from utils import format_time, shorten_number
from utils.ansi import ANSI

ansi = ANSI()
utc = ZoneInfo("UTC")
NOW = datetime.now(tz=utc)

ALIGN = 9  # Alignment for row labels


def streaks(data: Streaks) -> str:
    """Fetch and display the user's current streak information."""

    tomorrow = NOW.date() + timedelta(days=1)
    midnight = datetime.min.time()
    reset = datetime.combine(tomorrow, midnight, tzinfo=utc)
    time_left = format_time(reset - NOW)

    style = ansi.fg.green.bold if data.claimed else ansi.fg.red.bold
    streak_status = "claimed — resets in" if data.claimed else "unclaimed — lost in"

    return (
        f"{'streak:':>{ALIGN}} "
        f"{data.current_length} days ({style}{streak_status} {time_left}{ansi.reset}) | "
        f"best: {data.max_length} days"
    )


def test_counts(client: MonkeytypeClient) -> str:
    """Fetch and display the user's current test counts."""

    data = client.stats()
    joined = client.profile().date_joined
    days_since_joined = (NOW - joined).days

    completed_tests = data.tests_completed
    started_tests = data.tests_started
    time_typing = data.time_typing

    completion_rate = completed_tests / started_tests * 100 if started_tests else 0

    time_str = format_time(timedelta(seconds=time_typing))
    time_per_day = format_time(timedelta(seconds=time_typing / days_since_joined))
    time_per_test = format_time(timedelta(seconds=time_typing / completed_tests))

    return (
        f"{'tests:':>{ALIGN}} "
        f"{started_tests} started | "
        f"{completed_tests} completed ({completion_rate:.1f}%)\n"
        f"{'time:':>{ALIGN}} {time_str} | ~{time_per_day}/day | ~{time_per_test}/test"
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


def profile(data: Profile) -> str:
    """
    Format the user's profile information. Including the current level, XP, and progress.
    """

    joined = data.date_joined
    days_since_joined = (NOW - joined).days

    current_xp = data.level_current_xp
    max_xp = data.level_max_xp
    needed_xp = max_xp - current_xp

    return (
        f"Monkeytype info for {data.username}:\n\n"
        f"{'joined:':>{ALIGN}} {joined.strftime('%d %b %Y')} "
        f"({days_since_joined} days ago)\n"
        f"{'level:':>{ALIGN}} {data.level} | "
        f"{shorten_number(data.xp)} xp | "
        f"{shorten_number(current_xp)}/{shorten_number(max_xp)} "
        f"({shorten_number(needed_xp)} to go)"
    )


def main():
    """Main function to fetch and display user streak information."""

    client = MonkeytypeClient()

    output = [
        profile(client.profile()),
        streaks(client.streaks()),
        "",
        test_counts(client),
        "",
        activity_heatmap(client.activity()),
        "",
        last_test(client),
    ]

    print("\n", "\n".join(output), "\n", sep="")


if __name__ == "__main__":
    main()
