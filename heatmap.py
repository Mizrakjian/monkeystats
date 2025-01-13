from datetime import datetime, timedelta
from itertools import batched, zip_longest
from math import ceil
from zoneinfo import ZoneInfo

from utils import ANSI

# Constants
ansi = ANSI()
TOTAL_DAYS = 7 * 53  # 7 rows (days) × 53 columns (weeks)
BACKGROUND = 0
COLOR_MAP = [
    236,  # Level 0: Dark gray
    239,  # Level 1: Dim gray
    243,  # Level 2: Light blue
    246,  # Level 3: Light cyan
    252,  # Level 4: White
    3,  # Level 5: Yellow
]
"""
COLOR_MAP = [
    234,  # Level 0: Dark gray
    25,  # Level 1: Dim gray
    31,  # Level 2: Light blue
    38,  # Level 3: Light cyan
    6,  # Level 4: White
    3,  # Level 5: Yellow
]
COLOR_MAP = [
    16,  # Level 0: Dark gray
    27,  # Level 1: Dim gray
    33,  # Level 2: Light blue
    39,  # Level 3: Light cyan
    45,  # Level 4: White
    3,  # Level 5: Yellow
]
"""


def calc_limits(data: list[int | None]) -> list[int]:
    filtered = [v for v in data if v]

    sorted_data = sorted(filtered)
    trim_start = int(len(sorted_data) * 0.1)
    trimmed = sorted_data[trim_start:-trim_start]

    mean = sum(trimmed) / len(trimmed)
    max_value = max(filtered)

    return [
        0,
        ceil(mean / 2),
        ceil(mean),
        ceil(mean * 1.5),
        max_value - 1,
        max_value,
    ]


def map_counts(data: list[int | None]) -> list[int]:

    limits = calc_limits(data)

    output = []
    for count in data:
        if count is None:
            output.append(BACKGROUND)
            continue
        for color, limit in zip(COLOR_MAP, limits):
            if count <= limit:
                output.append(color)
                break

    return output


def indent_and_margin(rows: list[str]) -> list[str]:
    indent = " "
    margin = ansi.bg(BACKGROUND).apply(indent)
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

    return ansi.bg(BACKGROUND).apply("".join(output))


def pad_heatmap_data(data: list[int | None], last_date: datetime, today: datetime) -> list[int | None]:
    """
    Pads or trims data to span exactly 53 weeks (371 days),
    ensuring it starts on a Sunday and ends on a Saturday.

    Args:
        data (list): List of daily test counts, oldest to newest.
        last_date (datetime): The date of the most recent data point in the dataset.
        today (datetime): The current date.

    Returns:
        list: A list of test counts padded with None to fit 371 days.
    """

    # Calculate the Saturday after today
    days_to_saturday = (5 - today.weekday()) % 7
    end_saturday = today + timedelta(days=days_to_saturday)

    # Calculate forward padding needed to reach the end Saturday
    forward_padding = max(0, (end_saturday - last_date).days)
    padded_data = data + [None] * forward_padding

    # Trim the dataset to the most recent 371 days
    padded_data = padded_data[-TOTAL_DAYS:]

    # Calculate backward padding if the dataset is shorter than 371 days
    backward_padding = TOTAL_DAYS - len(padded_data)
    padded_data = [None] * backward_padding + padded_data

    return padded_data


def get_start_date(today: datetime) -> datetime:

    # Calculate the last Saturday (Saturday after today)
    days_to_next_saturday = (5 - today.weekday()) % 7
    end_saturday = today + timedelta(days=days_to_next_saturday)

    # Calculate the first Sunday of the 53-week range
    start_sunday = end_saturday - timedelta(days=371 - 1)

    return start_sunday


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

    data = [tests if tests else 0 for tests in activity["testsByDays"]]

    last_day = datetime.fromtimestamp(activity["lastDay"] / 1000, tz=ZoneInfo("UTC"))

    today = datetime.now(tz=ZoneInfo("UTC"))

    start_date = get_start_date(today)

    data = pad_heatmap_data(data, last_day, today)

    heatmap = map_counts(data)

    # Split into weeks and transpose into rows
    weeks = [heatmap[i : i + 7] for i in range(0, TOTAL_DAYS, 7)]
    rows = list(zip_longest(*weeks, fillvalue=0))

    half_rows = draw_rows(rows)

    # Add weekday and month labels
    header_left = f"{ansi.bg(BACKGROUND)}last 12 months — {sum(d for d in data if d)} tests"
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
    sample_data = [100, 3, 28, 15, 4, 33, 17, 14, 8, 6, 18, None, 1, 2, 7, 4, 7, 2, 2, 6, 25, 2, 8, 16, 9, 1, 39, 43, 21, 54, 19, 6, 3, 15, 3, 45, 3, 80, 45, 17, 7, 66, 31, 19, 10, 27, 19, 2, 11, 4, 15, 6, 1, None, 1, 10, 16, 3, 39, None, 6, 4, 20, 13, 9, 17, 3, 26, 4, 5, 10, 1, 15, 16, 27, 6, 17, 3, 1, 12, 1, 1, 5, 12, 1, 12, 3, 15, 14, 10, 6, 4, 71, 31, 4, 1, 30, 8, 9, 1, 1, 2, 13, 3, 3, 2, 4, None, 43, 25, 7, 14, 45, 29, 31, 18, 19, 3, 25, 47, 17, 46, 3, 25, 19, 12, 18, None, 1, 1, 23, 1, 12, 28, 9, 18, 31, 71, 25, 26, 9, 17, 12, 59, 31, 11, 45, 2, 1, 1, 1, 2, 4, 23, 7, 4, 3, 15, 18, 21, None, 1, 30, 81, 8, 10, 69, 21, 18, 13, 67, 14, 44, 2, 9, 20, 93, 98, 56, 27, 31, 1, 7, 7, 40, 1, 5]  # fmt:skip

    print(f"Testing with custom today: {date.strftime('%Y-%m-%d')}")

    print(activity_heatmap({"testsByDays": sample_data, "lastDay": date.timestamp() * 1000}))


# Example Usage
if __name__ == "__main__":
    test_month_labels(datetime(2024, 12, 24))
    test_month_labels(datetime(2025, 1, 6))
    test_month_labels(datetime(2025, 1, 12))
