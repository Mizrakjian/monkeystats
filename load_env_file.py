import os
from pathlib import Path


def load_env_file():
    """
    Load environment variables from a `.env` file located in the same directory as this script.

    Raises:
        FileNotFoundError: If the `.env` file does not exist.
    """
    # Determine the directory of the currently executing script
    script_dir = Path(__file__).parent
    env_file = script_dir / ".env"

    if not env_file.is_file():
        raise FileNotFoundError(f"No `.env` file found in the script directory: {script_dir}")

    with env_file.open("r") as file:
        for line in file:
            line = line.strip()
            if line.startswith("#") or not line:  # Ignore comments and empty lines
                continue
            if "=" in line:  # Only process lines with key=value format
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip()
                # Remove surrounding quotes from the value, if any
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                # Set the environment variable
                os.environ[key] = value
