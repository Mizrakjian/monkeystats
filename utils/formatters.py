import math
from datetime import timedelta


def shorten_number(number: int, places: int = 1) -> str:
    """Shorten a large number to a more human-readable format."""

    if number < 1e3:
        return str(int(number))

    magnitude = math.floor(math.log(number, 1e3))
    suffix = "kmbtqQsSond"[magnitude - 1]

    return f"{number / (1e3**magnitude):.{places}f}{suffix}"


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
