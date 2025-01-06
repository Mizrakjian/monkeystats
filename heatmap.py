from datetime import datetime, timedelta
from itertools import pairwise, zip_longest
from zoneinfo import ZoneInfo

# Constants
TOTAL_DAYS = 7 * 53  # 7 rows (days) × 53 columns (weeks)


def calc_limits(data) -> list[float]:
    filtered = [v for v in data if v]

    sorted_data = sorted(filtered)
    trim_start = int(len(sorted_data) * 0.1)
    trimmed = sorted_data[trim_start:-trim_start]

    mean = sum(trimmed) / len(trimmed)

    return [0.0, mean / 2, mean, mean * 1.5, float("inf")]


def map_counts(data: list[int | None]) -> list[str]:
    symbols = [" ", "░", "▒", "▓", "█"]  # Symbols for buckets
    limits = calc_limits(data)

    output = []
    for count in data:
        for symbol, limit in zip(symbols, limits):
            if count is None or count < limit:
                output.append(symbol)
                break

    return output


def add_row_labels(rows: list[tuple[str]]) -> list[str]:
    days = ["   ", "mon", "   ", "wed", "   ", "fri", "   "]
    return ["".join((f" {day} ", *row)) for day, row in zip(days, rows)]


def identify_month_starts(start_date):
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_names = []
    month_starts = []

    for i in range(7, TOTAL_DAYS, 7):
        week_end = start_date + timedelta(days=i)
        if week_end.day < 8:
            month_names.append(months[week_end.month - 1])
            month_starts.append(i // 7 - 1)

    return month_starts, month_names


def add_month_labels(start_date):
    """
    Generate dynamically spaced month labels for the heatmap.
    Alternate months are shown for space / clarity.
    """
    # Get month start indices and names
    month_starts, month_names = identify_month_starts(start_date)

    # Compute spacing between months (for alternate months only)
    spacing = [" " * ((b - a) - 3) for a, b in pairwise(month_starts[::2])]

    # Interleave months and spacing
    output = [month + space for month, space in zip(month_names[::2], spacing)]
    output.append(month_names[::2][-1])  # Append the last month

    return (" " * (5 + month_starts[0])) + "".join(output)


def pad_heatmap_data(data, start_date, today):
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
    padded_data = data[-full_range:]

    return padded_data


def get_start_date(last_test_date: datetime) -> datetime:

    # Calculate the start date by subtracting 52 weeks
    start_date = last_test_date - timedelta(weeks=52)

    # Adjust start_date to the nearest previous Sunday
    return start_date - timedelta(days=start_date.weekday() + 1)


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
    rows = list(zip_longest(*weeks, fillvalue=" "))

    # Add weekday and month labels
    header = f"     last 12 months — {sum(d for d in data if d)} tests"
    labeled_rows = add_row_labels(rows)
    month_labels = add_month_labels(start_date)

    return "\n".join((header, *labeled_rows, month_labels))


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
