from pathlib import Path


def load_env_file() -> dict[str, str]:
    """
    Return key-value pairs found in `.env`, a file located in the same directory as this script.

    Raises:
        FileNotFoundError: If the `.env` file does not exist.
    """
    # Determine the directory of the currently executing script
    mtstats = Path(__file__).parent.parent
    env_file = mtstats / ".env"

    settings = dict()

    if not env_file.is_file():
        raise FileNotFoundError(f"No `.env` file found in: {mtstats}")

    with env_file.open("r") as file:
        for line in file:
            line = line.strip()

            # Only process lines with key=value format, and ignore comments and empty lines
            if "=" not in line or line.startswith("#") or not line:
                continue

            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip()

            # Remove surrounding quotes from the value, if any
            if value.startswith(('"', "'")) and value[-1] == value[0]:
                value = value[1:-1]

            settings[key] = value

    return settings
