#!/usr/bin/env python3

from typing import Iterable


def display_usage_grouped_palette():
    """Displays the 256 ANSI colors grouped into standard colors, RGB cube, and grayscale ramp."""

    def print_color(i: int) -> None:
        set_bg = f"\033[48;5;{i}m"
        reset = "\033[0m"
        print(f"{set_bg} {i:>3} {reset}", end="")

    print("\nStandard Colors (0–15):")
    for i in range(16):
        print_color(i)
        if (i + 1) % 8 == 0:
            print()
    print()

    print("216-Color RGB Cube (16–231):")
    for i in range(16, 232):
        print_color(i)
        if (i - 16 + 1) % 6 == 0:
            print()
        if (i - 16 + 1) % 36 == 0:
            print()

    print("Grayscale Ramp (232–255):")
    for i in range(232, 256):
        print_color(i)
        if (i - 16 + 1) % 6 == 0:
            print()
    print()


if __name__ == "__main__":
    display_usage_grouped_palette()


def display_ansi_palette():
    """Displays the 256 ANSI colors grouped into standard colors, RGB cube, and grayscale ramp."""

    def color_block(color: int) -> str:
        """Prints a single color block with its index."""
        bg_code = f"\033[48;5;{color}m"
        reset = "\033[0m"
        return f"{bg_code} {color:>3} {reset}"

    def print_color_row(color_ids: Iterable[int]):
        """Prints a row of color blocks."""
        print("".join(color_block(color) for color in color_ids))

    print("\nStandard Colors (0–15):")
    for row_start in range(0, 16, 8):  # Each row contains 8 colors
        print_color_row(range(row_start, row_start + 8))
    print()

    print("216-Color RGB Cube (16–231):")
    for block_start in range(16, 232, 36):  # Each block contains 36 colors
        for row_start in range(block_start, block_start + 36, 6):  # Each row contains 6 colors
            print_color_row(range(row_start, row_start + 6))
        print()  # Blank line between blocks

    print("Grayscale Ramp (232–255):")
    for row_start in range(232, 256, 6):  # Each row contains 6 colors
        print_color_row(range(row_start, row_start + 6))
    print()


def display_nord_colors_by_number():
    """
    Displays the Nord colors with foreground and background arranged by number (0, 8, 1, 9, etc.).
    """
    reset = "\033[0m"
    color_order = [0, 8, 1, 9, 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

    print("\nNord Colors by Number (Foreground and Background):\n")

    # Header row with background colors
    print("   ", end="")
    for bg in color_order:
        print(f"\033[48;5;{bg}m {bg:>2} {reset}", end="")
    print()

    # Rows with foreground colors
    for fg in color_order:
        print(f"{fg:>2} ", end="")
        for bg in color_order:
            fg_code = f"\033[38;5;{fg}m"
            bg_code = f"\033[48;5;{bg}m"
            print(f"{bg_code}{fg_code} ■■ {reset}", end="")
        print()


def display_nord_palette_rgb():
    # Nord palette with RGB values
    nord_colors_rgb = [
        ("#2E3440", (46, 52, 64)),  # Nord0
        ("#3B4252", (59, 66, 82)),  # Nord1
        ("#434C5E", (67, 76, 94)),  # Nord2
        ("#4C566A", (76, 86, 106)),  # Nord3
        ("#D8DEE9", (216, 222, 233)),  # Nord4
        ("#E5E9F0", (229, 233, 240)),  # Nord5
        ("#ECEFF4", (236, 239, 244)),  # Nord6
        ("#8FBCBB", (143, 188, 187)),  # Nord7
        ("#88C0D0", (136, 192, 208)),  # Nord8
        ("#81A1C1", (129, 161, 193)),  # Nord9
        ("#5E81AC", (94, 129, 172)),  # Nord10
        ("#BF616A", (191, 97, 106)),  # Nord11
        ("#D08770", (208, 135, 112)),  # Nord12
        ("#EBCB8B", (235, 203, 139)),  # Nord13
        ("#A3BE8C", (163, 190, 140)),  # Nord14
        ("#B48EAD", (180, 142, 173)),  # Nord15
    ]

    reset = "\033[0m"

    # Create a grid of Nord colors using RGB
    print("\nNord Color Palette (Foreground on Background - RGB):\n")
    print(" ", end="")

    # Print column headers (backgrounds)
    for _, (bg_r, bg_g, bg_b) in nord_colors_rgb:
        print(f" \033[48;2;{bg_r};{bg_g};{bg_b}m   {reset}", end="")
    print()

    # Print rows for each foreground color
    for _, (fg_r, fg_g, fg_b) in nord_colors_rgb:
        print("   ", end="")
        for _, (bg_r, bg_g, bg_b) in nord_colors_rgb:
            fg_ansi = f"\033[38;2;{fg_r};{fg_g};{fg_b}m"
            bg_ansi = f"\033[48;2;{bg_r};{bg_g};{bg_b}m"
            print(f"{bg_ansi}{fg_ansi} TEXT {reset}", end="")
        print()
