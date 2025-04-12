import os
from pathlib import Path
import yaml
from dotenv import load_dotenv
from typing import Any, Dict, Optional, Union

_config: Any = None


def load_environment(dotenv_path: Optional[Union[Path, str]] = None) -> None:
    """
    Load environment variables from a .env file.

    Args:
        dotenv_path (str or Path, optional): Path to the `.env` file. Defaults to None.

    Raises:
        FileNotFoundError: If a custom path is specified and the file does not exist.
    """
    if dotenv_path:
        load_dotenv(str(dotenv_path))
    else:
        load_dotenv()


def load_config() -> Dict[str, Any]:
    """
    Load the main configuration from the YAML file specified by the CONFIG_PATH environment variable.

    Returns:
        dict: Parsed configuration data as a dictionary.

    Raises:
        RuntimeError: If CONFIG_PATH is not set in the environment.
        FileNotFoundError: If the config file specified by CONFIG_PATH does not exist.
        yaml.YAMLError: If the config file contains invalid YAML.
    """
    config_path: str | None = os.getenv("CONFIG_PATH")
    if not config_path:
        raise RuntimeError("CONFIG_PATH not set in .env or environment variables.")

    config_file: Path = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")

    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def get_config() -> Dict[str, Any]:
    """
    Get the loaded config (requires load_config to be called first).

    Returns:
        dict: A dictionary containing the configuration settings parsed from the YAML file.

    Raises:
        RuntimeError: If the configuration has not been loaded yet.
    """
    global _config
    if _config is None:
        raise RuntimeError("Config not loaded. Call load_config() first.")
    return _config
