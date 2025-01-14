import tomllib
from pathlib import Path


def load_auth(filename: str = ".auth") -> dict[str, str]:
    """
    Load authentication credentials from a TOML file.

    Args:
        filename (str): Name of the authentication file (default: '.auth').

    Returns:
        dict[str, str]: A dictionary containing 'api_key' and 'username'.

    Raises:
        FileNotFoundError: If the file does not exist.
        tomllib.TOMLDecodeError: If the file content is not valid TOML.
    """
    auth_file = Path(__file__).parent.parent / filename

    if not auth_file.is_file():
        raise FileNotFoundError(f"Authentication file `{filename}` not found in {auth_file.parent}")

    with auth_file.open("rb") as file:  # Use 'rb' mode as tomllib requires bytes
        return tomllib.load(file)
