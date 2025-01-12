class ANSI:
    """Utility class for generating optimized ANSI escape sequences with chainable attributes."""

    ESC = "\033["

    def __init__(self):
        self.codes = []  # Current list of pending ANSI codes
        self.state = {}  # Retained state for fg, bg, and other styles

    @property
    def bold(self):
        """Enable bold text."""
        if "bold" not in self.state:
            self.codes.append("1")
            self.state["bold"] = True
        return self

    @property
    def bold_off(self):
        """Disable bold text."""
        if self.state.get("bold"):
            self.codes.append("22")
            self.state.pop("bold", None)
        return self

    @property
    def ital(self):
        """Enable italic text."""
        if "ital" not in self.state:
            self.codes.append("3")
            self.state["ital"] = True
        return self

    @property
    def ital_off(self):
        """Disable italic text."""
        if self.state.get("ital"):
            self.codes.append("23")
            self.state.pop("ital", None)
        return self

    @property
    def uline(self):
        """Enable underlined text."""
        if "uline" not in self.state:
            self.codes.append("4")
            self.state["uline"] = True
        return self

    @property
    def uline_off(self):
        """Disable underlined text."""
        if self.state.get("uline"):
            self.codes.append("24")
            self.state.pop("uline", None)
        return self

    @property
    def fg(self):
        """Return a proxy object for setting foreground colors."""
        return _ColorProxy(self, "fg")

    @property
    def bg(self):
        """Return a proxy object for setting background colors."""
        return _ColorProxy(self, "bg")

    @property
    def reset(self):
        """Return the ANSI reset code and clear the current codes and state."""
        self.codes = []
        self.state = {}
        return f"{self.ESC}0m"

    def apply(self, text: str) -> str:
        """
        Apply the accumulated ANSI codes to the given text and reset the state.
        """
        if not self.codes:
            return text
        sequence = f"{self}{text}{self.reset}"
        return sequence

    def __str__(self):
        """Return the accumulated ANSI codes as a single sequence."""
        if not self.codes:
            return ""
        sequence = f"{self.ESC}{';'.join(self.codes)}m"
        self.codes = []  # Clear the codes after generating the sequence
        return sequence

    @staticmethod
    def _get_color_code(color: str | int, mode: str) -> str:
        """
        Convert a color name or number to a short ANSI color code (0-15),
        or fall back to 256-color codes for other values.
        """
        SHORT_CODES = {
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

        # Resolve named colors
        if isinstance(color, str):
            resolved_color = SHORT_CODES.get(color.lower())
            if resolved_color is None:
                raise ValueError(f"Unknown color name: {color}")
            color = resolved_color

        # Ensure color is an int
        if not isinstance(color, int):
            raise TypeError("Color must be an integer or a valid color name.")

        # Validate the range
        if not (0 <= color <= 255):
            raise ValueError("Color must be between 0 and 255.")

        # Return short ANSI codes for 0-15
        if 0 <= color <= 7:
            return f"{30 + color if mode == 'fg' else 40 + color}"
        elif 8 <= color <= 15:
            return f"{90 + (color - 8) if mode == 'fg' else 100 + (color - 8)}"

        # Fall back to 256-color codes
        return f"{38 if mode == 'fg' else 48};5;{color}"

    def _set_color(self, color: str | int, mode: str):
        """Set the foreground or background color."""
        color_code = self._get_color_code(color, mode)
        if self.state.get(mode) != color_code:
            self.codes.append(color_code)
            self.state[mode] = color_code


class _ColorProxy:
    """Helper class to dynamically resolve colors for fg or bg."""

    def __init__(self, parent: ANSI, mode: str):
        self.parent = parent  # Reference to the ANSI instance
        self.mode = mode  # Either "fg" or "bg"

    def __getattr__(self, name):
        """Set the color dynamically when an attribute is accessed."""
        try:
            # Handle named colors (dot notation)
            self.parent._set_color(name, self.mode)
            return self.parent
        except ValueError:
            raise AttributeError(f"No such color: {name}")

    def __call__(self, value: str | int):
        """Allow setting the color dynamically via a callable."""
        self.parent._set_color(value, self.mode)
        return self.parent


def display_grouped_palette():
    """Displays the 256 ANSI colors grouped into standard colors, RGB cube, and grayscale ramp."""

    ansi = ANSI()

    def print_color(i: int) -> None:
        print(f"{ansi.bg(i)} {i:>3} ", end="")

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

    ansi = ANSI()

    print(ansi.bold.apply("This is bold text"))
    print(ansi.ital.apply("This is italic text"))
    print(ansi.uline.apply("This is underlined text"))

    # Foreground color
    print(ansi.fg.red.apply("This is red text"))
    print(f"{ansi.fg(1)}This is {ansi.ital}also{ansi.ital_off} red text{ansi.reset}")

    # Background color
    print(ansi.bg.blue.apply("This is text with a blue background"))
    # Foreground and background colors together
    print(ansi.fg.yellow.bg.black.apply("Yellow text on a black background"))
    # Combine styles
    print(ansi.bold.ital.uline.fg.white.bg.blue.apply("Bold, Italic, Underlined, White on Blue"))
