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
