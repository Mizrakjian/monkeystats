"""
Monkeytype Level and XP Calculation Utilities

The following functions are adapted from the Monkeytype project:
GitHub Repo: https://github.com/monkeytypegame/monkeytype/blob/master/frontend/src/ts/utils/levels.ts
"""

import math


def calculate_level(xp: int) -> int:
    """Calculate the level based on the XP."""

    return math.floor((math.sqrt(392 * xp + 22801) - 53) / 98)


def remaining_level_xp(level: int) -> int:
    """Calculate the XP required to complete a given level."""

    return 49 * (level - 1) + 100


def total_level_xp(level: int) -> int:
    """Calculate the total XP required to reach a specific level."""

    return (49 * (level**2) + 53 * level - 102) // 2


def shorten_number(number: int, places: int = 1) -> str:
    """Shorten a large number to a more human-readable format."""

    if number < 1e3:
        return str(int(number))

    magnitude = math.floor(math.log(number, 1e3))
    suffix = "kmbtqQsSond"[magnitude - 1]

    return f"{number / (1e3**magnitude):.{places}f}{suffix}"


def level_details(xp: int) -> str:
    """Generate a summary string for the current level, XP, and progress."""

    level = calculate_level(xp)
    current_xp = xp - total_level_xp(level)
    max_xp = remaining_level_xp(level)
    needed_xp = max_xp - current_xp

    return (
        f"level {level} | {shorten_number(xp)} xp | "
        f"{shorten_number(current_xp)}/{shorten_number(max_xp)} "
        f"({shorten_number(needed_xp)} to go)"
    )
