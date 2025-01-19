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


def test_counts(data: Profile) -> str:
    """Fetch and display the user's current test counts."""

    joined = data.date_joined
    days_since_joined = (NOW - joined).days

    completed_tests = data.tests.completed
    started_tests = data.tests.started
    time_typing = data.tests.time_typing

    completion_rate = completed_tests / started_tests * 100 if started_tests else 0

    time_str = format_time(timedelta(seconds=time_typing))
    time_per_day = format_time(timedelta(seconds=time_typing / days_since_joined))
    time_per_test = format_time(timedelta(seconds=time_typing / completed_tests))
    avg_tests = completed_tests / days_since_joined

    return (
        f"{'tests:':>{ALIGN}} "
        f"{started_tests} started | "
        f"{completed_tests} completed ({completion_rate:.1f}%) | "
        f"~{avg_tests:.0f} tests/day\n"
        f"{'time:':>{ALIGN}} {time_str} | ~{time_per_day}/day | ~{time_per_test}/test"
    )


def last_test(client: MonkeytypeClient) -> str:
    """Fetch and display the user's last test information and PB."""

    last = client.last_test
    bests = client.profile.personal_bests

    # Find the matching PB
    pb = next((pb for pb in bests if pb == last), None)

    pb_text = (
        "★ new pb ★"
        if last.is_pb
        else (
            f"pb: {pb.wpm:.1f} wpm {pb.acc:.0f}% acc {pb.consistency:.0f}% con"
            if pb
            else "no matching pb"
        )
    )

    test_time = last.test_time
    time_str = test_time.strftime("%Y-%m-%d %H:%M:%S UTC")
    time_ago = format_time(NOW - test_time)

    test_modifiers = f"@{'on' if last.punctuation else 'off'} #{'on' if last.numbers else 'off'}"

    return (
        f"{'latest:':>{ALIGN}} {last.test_mode} {last.mode_unit} | {test_modifiers} | "
        f"{last.language} | {time_str} ({time_ago} ago)\n"
        f"{'result:':>{ALIGN}} {last.wpm:.1f} wpm {last.acc:.0f}% acc {last.consistency:.0f}% con | {pb_text}"
    )


def joined(data: Profile) -> str:
    """
    Format the user's profile information. Including the current level, XP, and progress.
    """

    joined = data.date_joined
    days_since_joined = (NOW - joined).days

    return f"{'joined:':>{ALIGN}} {joined.strftime('%d %b %Y')} ({days_since_joined} days ago)"


def level(data: Profile) -> str:
    """
    Format the user's profile information. Including the current level, XP, and progress.
    """

    current_xp = data.level_current_xp
    max_xp = data.level_max_xp
    needed_xp = max_xp - current_xp

    return (
        f"{'level:':>{ALIGN}} {data.level} | "
        f"{shorten_number(data.xp)} xp | "
        f"{shorten_number(current_xp)}/{shorten_number(max_xp)} "
        f"({shorten_number(needed_xp)} to go)"
    )


def main():
    """Main function to fetch and display user streak information."""

    client = MonkeytypeClient()
    client.fetch_all()

    output = [
        "",
        f"Monkeytype info for {client.profile.username}:",
        "",
        joined(client.profile),
        level(client.profile),
        streaks(client.streaks),
        "",
        test_counts(client.profile),
        "",
        activity_heatmap(client.activity),
        "",
        last_test(client),
        "",
    ]

    print("\n".join(output))


if __name__ == "__main__":
    main()
