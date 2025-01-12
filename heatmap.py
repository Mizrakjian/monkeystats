from datetime import datetime, timedelta
from itertools import batched, zip_longest
from math import ceil
from zoneinfo import ZoneInfo

from utils import ANSI

# Constants
ansi = ANSI()
TOTAL_DAYS = 7 * 53  # 7 rows (days) × 53 columns (weeks)
# COLOR_MAP = [
#     234,  # Level 0: Dark gray
#     25,  # Level 1: Dim gray
#     31,  # Level 2: Light blue
#     38,  # Level 3: Light cyan
#     6,  # Level 4: White
#     3,  # Level 5: Yellow
# ]
# COLOR_MAP = [
#     16,  # Level 0: Dark gray
#     27,  # Level 1: Dim gray
#     33,  # Level 2: Light blue
#     39,  # Level 3: Light cyan
#     45,  # Level 4: White
#     3,  # Level 5: Yellow
# ]
COLOR_MAP = [
    236,  # Level 0: Dark gray
    239,  # Level 1: Dim gray
    243,  # Level 2: Light blue
    246,  # Level 3: Light cyan
    252,  # Level 4: White
    3,  # Level 5: Yellow
]


def calc_limits(data: list[int | None]) -> list[int]:
    filtered = [v for v in data if v]

    sorted_data = sorted(filtered)
    trim_start = int(len(sorted_data) * 0.1)
    trimmed = sorted_data[trim_start:-trim_start]

    mean = sum(trimmed) / len(trimmed)
    max_value = max(filtered)

    return [0, ceil(mean / 2), ceil(mean), ceil(mean * 1.5), max_value - 1, max_value]


def map_counts(data: list[int | None]) -> list[int]:

    limits = calc_limits(data)

    output = []
    for count in data:
        for symbol, limit in zip(COLOR_MAP, limits):
            if count is None or count <= limit:
                output.append(symbol)
                break

    return output


def indent_and_margin(rows: list[str]) -> list[str]:
    indent = " "
    margin = ansi.bg(0).apply(indent)
    return [f"{indent}{margin}{row}{margin}" for row in rows]


def month_labels(start_date: datetime) -> str:

    output = [" "] * 53

    label_count = 0
    for i in range(51):
        week_end = start_date + timedelta(weeks=i, days=6)
        if week_end.day < 8:
            if label_count % 2 == 0:
                output[i : i + 3] = week_end.strftime("%b").lower()
            label_count += 1

    return ansi.bg(0).apply("".join(output))


def pad_heatmap_data(data, start_date: datetime, today: datetime) -> list[int | None]:
    """
    Pads data to ensure it spans 53 weeks starting on a Sunday, with the last week being partial if needed.

    Args:
        data (list): List of daily test counts, oldest to newest.
        last_test_date (datetime): The date of the most recent test in the data.
        total_days (int): Total number of days for the heatmap (default: 7 * 53).

    Returns:
        list: A list of test counts padded to cover the required range.
    """

    # Determine the total range of days for the heatmap
    full_range = (today - start_date).days + 1

    # Pad data at the beginning if it's shorter than the full range
    if len(data) < full_range:
        padding = [0] * (full_range - len(data))
        data = padding + data

    # Trim excess data to match the full range
    padded_data = data[-full_range:] + [0] * (53 * 7 - full_range)

    return padded_data


def get_start_date(last_test_date: datetime) -> datetime:

    # Calculate the start date by subtracting 52 weeks
    start_date = last_test_date - timedelta(weeks=52)

    # Adjust start_date to the nearest previous Sunday
    return start_date - timedelta(days=start_date.weekday() + 1)


def draw_rows(rows: list[tuple[int, ...]]) -> list[str]:

    def plot(fg: int, bg: int) -> str:
        block = "▄"
        return f"{ansi.fg(fg).bg(bg)}{block}"

    padded = [(0,) * 53] + rows

    output = []

    for even, odd in batched(padded, 2):
        line = "".join(plot(fg, bg) for bg, fg in zip(even, odd))  # Top is bg color, bottom is fg color
        output.append(line + ansi.reset)

    return output


def activity_heatmap(activity: dict) -> str:
    """
    Generate a 7x53 heatmap for test counts over the trailing 53 weeks.

    Args:
        data (list): List of daily test counts, oldest to newest.
        today (datetime): The reference date for the heatmap (default: now).

    Returns:
        str: Formatted heatmap as a string.
    """

    data = activity["testsByDays"]

    today = datetime.fromtimestamp(activity["lastDay"] / 1000, tz=ZoneInfo("UTC"))

    start_date = get_start_date(today)

    data = pad_heatmap_data(data, start_date, today)

    heatmap = map_counts(data)

    # Split into weeks and transpose into rows
    weeks = [heatmap[i : i + 7] for i in range(0, TOTAL_DAYS, 7)]
    rows = list(zip_longest(*weeks, fillvalue=0))

    half_rows = draw_rows(rows)

    # Add weekday and month labels
    header_left = f"{ansi.bg.black}last 12 months — {sum(d for d in data if d)} tests"
    key = "".join(f"{ansi.fg(color)}■" for color in COLOR_MAP)
    header_right = f"less {key} more{ansi.reset}"
    header = f"{header_left}{" "*10}{header_right}"
    footer = month_labels(start_date)

    output = indent_and_margin([header, *half_rows, footer])

    return "\n".join(output)


# Test Function
def test_month_labels(date: datetime):
    """
    Test the heatmap month label alignment with a custom 'today' date.
    """
    sample_data = [40, 10, 49, 169, 53, 85, 117, 34, 32, 23, 48, 19, 44, 77, 15, 55, 122, 15, 41, 17, 45, 33, 68, 80, 57, 15, 33, 4, 47, 20, 29, 30, 28, 18, 9, 1, 10, 10, 6, 9, 10, None, 40, 4, 20, 13, 1, 3, 6, 3, 1, 2, 1, 1, 1, 1, None, 3, 1, None, None, 1, None, None, None, 2, 1, None, 1, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, 6, None, 1, 1, 6, None, None, None, None, None, None, None, None, None, 2, 1, 6, 3, None, 1, 5, 1, 9, 5, 1, 6, 1, 1, 6, 2, None, 1, None, None, 1, None, None, None, None, None, None, None, 4, 1, None, None, None, None, None, None, None, 9, None, 1, 1, 9, 11, 12, 18, None, None, 1, 17, 15, 16, 80, 9, 15, 35, 15, 12, 38, 37, 2, 39, 42, 9, 17, 83, 8, 16, 78, 34, 25, 60, 38, 19, 8, 69, 25, 21, 27, 15, 6, 23, 20, 6, 29, 3, 28, 15, 4, 33, 17, 14, 8, 6, 18, None, 1, None, None, None, 2, 7, 4, 7, 2, 2, 6, 25, 2, 8, 16, 9, 1, 39, 43, 21, 54, 19, 6, 3, 15, 3, 45, 3, 80, 45, 17, 7, 66, 31, 19, 10, 27, 19, 2, 11, 4, 15, 6, 1, None, 1, 10, 16, 3, 39, None, 6, 4, 20, 13, 9, 17, 3, 26, 4, 5, 10, 1, 15, 16, 27, 6, 17, 3, 1, 12, 1, 1, 5, 12, 1, 12, 3, 15, 14, 10, 6, 4, 71, 31, 4, 1, 30, 8, 9, 1, 1, 2, 13, 3, 3, 2, 4, None, 43, 25, 7, 14, 45, 29, 31, 18, 19, 3, 25, 47, 17, 46, 3, 25, 19, 12, 18, None, 1, 1, 23, 1, 12, 28, 9, 18, 31, 71, 25, 26, 9, 17, 12, 59, 31, 11, 45, 2, 1, 1, 1, 2, 4, 23, 7, 4, 3, 15, 18, 21, None, 1, 30, 81, 8, 10, 69, 21, 18, 13, 67, 14, 44, 2, 9, 20, 93, 98, 56, 27, 31, 1, 7, 7, 40, 1, 5]  # fmt:skip

    print(f"Testing with custom today: {date.strftime('%Y-%m-%d')}")

    print(activity_heatmap({"testsByDays": sample_data, "lastDay": date.timestamp() * 1000}))


# Example Usage
if __name__ == "__main__":
    test_month_labels(datetime(2025, 1, 6))
    test_month_labels(datetime(2025, 1, 10))
    test_month_labels(datetime(2025, 1, 28))
