class ANSI:
    """Utility class for generating ANSI escape codes for terminal output."""

    ESC = "\033["

    COLOR_NAMES = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
        "bright_black": 8,
        "bright_red": 9,
        "bright_green": 10,
        "bright_yellow": 11,
        "bright_blue": 12,
        "bright_magenta": 13,
        "bright_cyan": 14,
        "bright_white": 15,
    }

    @classmethod
    def reset(cls) -> str:
        """Return ANSI code to reset all styles."""
        return f"{cls.ESC}0m"

    @classmethod
    def bold(cls, text: str) -> str:
        """Return the given text wrapped in ANSI bold codes."""
        return f"{cls.ESC}1m{text}{cls.ESC}22m"

    @classmethod
    def ital(cls, text: str) -> str:
        """Return the given text wrapped in ANSI italics codes."""
        return f"{cls.ESC}3m{text}{cls.ESC}23m"

    @classmethod
    def uline(cls, text: str) -> str:
        """Return the given text wrapped in ANSI underline codes."""
        return f"{cls.ESC}4m{text}{cls.ESC}24m"

    @classmethod
    def fg(cls, color: str | int, text: str) -> str:
        """Return text with the specified foreground color."""
        color_code = cls._get_color_code(color)
        return f"{cls.ESC}38;5;{color_code}m{text}{cls.reset()}"

    @classmethod
    def bg(cls, color: str | int, text: str) -> str:
        """Return text with the specified background color."""
        color_code = cls._get_color_code(color)
        return f"{cls.ESC}48;5;{color_code}m{text}{cls.reset()}"

    @classmethod
    def paint(cls, fg_color: str | int, bg_color: str | int, text: str) -> str:
        """Return text with both foreground and background colors."""
        fg_code = cls._get_color_code(fg_color)
        bg_code = cls._get_color_code(bg_color)
        return f"{cls.ESC}38;5;{fg_code};48;5;{bg_code}m{text}{cls.reset()}"

    @classmethod
    def custom_fg(cls, r: int, g: int, b: int, text: str) -> str:
        """Return text with a custom RGB foreground color."""
        return f"{cls.ESC}38;2;{r};{g};{b}m{text}{cls.reset()}"

    @classmethod
    def custom_bg(cls, r: int, g: int, b: int, text: str) -> str:
        """Return text with a custom RGB background color."""
        return f"{cls.ESC}48;2;{r};{g};{b}m{text}{cls.reset()}"

    @classmethod
    def _get_color_code(cls, color: str | int) -> int:
        """Helper to get the numeric code for a color."""
        if isinstance(color, int):
            if 0 <= color <= 255:
                return color
            raise ValueError("Color must be between 0 and 255.")
        elif isinstance(color, str):
            color_code = cls.COLOR_NAMES.get(color.lower())
            if color_code is None:
                raise ValueError(f"Unknown color name: {color}")
            return color_code
        else:
            raise TypeError("Color must be a string or integer.")


def display_grouped_palette():
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
    display_grouped_palette()

    print(ANSI.bold("This is bold text"))
    print(ANSI.ital("This is italic text"))
    print(ANSI.uline("This is underlined text"))
    # Foreground color
    print(ANSI.fg("red", "This is red text"))
    # Background color
    print(ANSI.bg("blue", "This is text with a blue background"))
    # Foreground and background colors together
    print(ANSI.paint("yellow", "black", "Yellow text on a black background"))
    # Combine styles
    print(
        ANSI.bold(
            ANSI.ital(ANSI.uline(ANSI.paint("white", "blue", "Bold, Italic, Underlined, White on Blue")))
        )
    )
