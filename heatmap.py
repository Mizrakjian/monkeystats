from datetime import datetime, timedelta
from itertools import pairwise, zip_longest
from math import ceil
from zoneinfo import ZoneInfo

# Constants
TOTAL_DAYS = 7 * 53  # 7 rows (days) × 53 columns (weeks)


def calc_limits(data) -> list[int | float]:
    filtered = [v for v in data if v]

    sorted_data = sorted(filtered)
    trim_start = int(len(sorted_data) * 0.1)
    trimmed = sorted_data[trim_start:-trim_start]

    mean = sum(trimmed) / len(trimmed)
    max_value = max(filtered)

    return [0, ceil(mean / 2), ceil(mean), ceil(mean * 1.5), max_value - 1, max_value]


def map_counts(data: list[int | None]) -> list[str]:
    colors = [
        234,  # Level 0: Dark gray
        25,  # Level 1: Dim gray
        31,  # Level 2: Light blue
        38,  # Level 3: Light cyan
        6,  # Level 4: White
        3,  # Level 5: Yellow
    ]
    colors = [
        16,  # Level 0: Dark gray
        27,  # Level 1: Dim gray
        33,  # Level 2: Light blue
        39,  # Level 3: Light cyan
        45,  # Level 4: White
        3,  # Level 5: Yellow
    ]
    colors = [
        236,  # Level 0: Dark gray
        239,  # Level 1: Dim gray
        243,  # Level 2: Light blue
        246,  # Level 3: Light cyan
        252,  # Level 4: White
        3,  # Level 5: Yellow
    ]

    limits = calc_limits(data)

    output = []
    for count in data:
        for symbol, limit in zip(colors, limits):
            if count is None or count <= limit:
                output.append(symbol)
                break

    return output


def add_row_labels(rows: list[str]) -> list[str]:
    # days = ["   ", "mon", "   ", "wed", "   ", "fri", "   "]
    # return ["".join((f" {day} ", *row, "\033[0m")) for day, row in zip(days, rows)]
    return [f" \033[48;5;0m {row}\033[48;5;0m \033[0m" for row in rows]


def identify_month_starts(start_date: datetime):
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    month_names = []
    month_starts = []

    for i in range(6, TOTAL_DAYS, 7):
        week_end = start_date + timedelta(days=i)
        if week_end.day < 8:
            month_names.append(months[week_end.month - 1])
            month_starts.append(i // 7)

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

    return " \033[48;5;0m" + " " * (1 + month_starts[0]) + "".join(output) + "    " + "\033[0m"


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
    padded_data = data[-full_range:] + [0] * (53 * 7 - full_range)

    return padded_data


def get_start_date(last_test_date: datetime) -> datetime:

    # Calculate the start date by subtracting 52 weeks
    start_date = last_test_date - timedelta(weeks=52)

    # Adjust start_date to the nearest previous Sunday
    return start_date - timedelta(days=start_date.weekday() + 1)


def make_half_rows(rows) -> list[str]:

    def plot(bg, fg) -> str:
        fg_color = f"\033[38;5;{fg}m"
        bg_color = f"\033[48;5;{bg}m"
        reset = "\033[0m"
        block = "▄"
        return f"{fg_color}{bg_color}{block}{reset}"

    output = []

    padded = [(0,) * 53]
    padded.extend(rows)

    for top, bottom in zip_longest(padded[::2], padded[1::2], fillvalue=[0] * 53):
        line = [plot(*colors) for colors in zip(top, bottom)]
        output.append("".join(line))

    return output


# def make_half_rows(rows) -> list[str]:

#     output = []

#     fg_color = "\033[38;5;"
#     bg_color = "\033[48;5;"
#     reset = "\033[0m"

#     for top, bottom in zip_longest(rows[::2], rows[1::2], fillvalue=[0] * 53):
#         line = [f"{fg_color}{fg}m{bg_color}{bg}m▀" for fg, bg in zip(top, bottom)]
#         line.append(reset)
#         output.append("".join(line))

#     return output


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

    half_rows = make_half_rows(rows)

    # Add weekday and month labels
    header_left = f" \033[48;5;0m last 12 months — {sum(d for d in data if d)} tests"

    colors = [234, 25, 31, 38, 6, 3]
    key = "".join(f"\033[38;5;{color}m■" for color in colors)

    header_right = f"less {key} more \033[0m"
    header = f"{header_left}{" "*(48-len(header_left))}{header_right}"
    labeled_rows = add_row_labels(half_rows)
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

    def generate_heatmap(data, margin_size=2):
        """
        Generates a heatmap with a margin using ANSI color codes.
        :param data: 2D list of activity levels (0-4).
        :param margin_size: Width of the margin around the heatmap.
        """
        # Define color mappings
        heatmap_colors = {
            "margin": "\033[48;5;0m ",  # Chart margin
            0: "\033[0m ",  # Level 0: Reset
            1: "\033[48;5;8m ",  # Level 1: Dim gray
            2: "\033[48;5;4m ",  # Level 2: Light blue
            3: "\033[48;5;6m ",  # Level 3: Light cyan
            4: "\033[48;5;7m ",  # Level 4: White
            "peak": "\033[48;5;11m*",  # Peak activity
        }
        reset = "\033[0m"

        # Add margins and render the heatmap
        margin_row = heatmap_colors["margin"] * (len(data[0]) + 2 * margin_size)
        print(margin_row + reset)
        for row in data:
            print(heatmap_colors["margin"] * margin_size, end="")  # Left margin
            for level in row:
                print(heatmap_colors[level], end="")
            print(heatmap_colors["margin"] * margin_size + reset)  # Right margin
        print(margin_row + reset)

    # Example heatmap data
    heatmap_data = [
        [0, 0, 1, 1, 2, 2, 3, 3, 4, 4],
        [0, 0, 1, 1, 2, 3, 3, 4, 4, 4],
        [0, 1, 1, 2, 2, 3, 3, 4, 4, 4],
        [1, 1, 2, 2, 3, 3, 4, 4, 4, 4],
    ]

    # Generate the heatmap
    generate_heatmap(heatmap_data)
