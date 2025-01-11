"""
Monkeytype Level and XP Calculation Utilities

The following functions are adapted from the Monkeytype project:
GitHub Repo: https://github.com/monkeytypegame/monkeytype/blob/master/frontend/src/ts/utils/levels.ts
"""

import math


def get_level(xp: int) -> int:
    """Return the level based on the XP."""

    return math.floor((math.sqrt(392 * xp + 22801) - 53) / 98)


def get_level_max_xp(level: int) -> int:
    """Return the XP required to complete a given level."""

    return 49 * (level - 1) + 100


def get_total_level_xp(level: int) -> int:
    """
    Return the total XP required to reach a specific level.

    This is the inverse of the function calculate_level().

    Calculated as the sum of xp required for all levels up to `level`,
    where xp required for `level` is calculated using level_max_xp(),
    and the first level is 1 and it requires 100xp to reach level 2.

    @param level The level.
    @returns The total experience points required to reach the level.
    """

    return (49 * (level**2) + 53 * level - 102) // 2


def get_level_current_xp(xp: int) -> int:
    """Return the partial XP of the present level."""

    level = get_level(xp)
    return xp - get_total_level_xp(level)
