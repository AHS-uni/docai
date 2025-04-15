from pathlib import Path
from typing import Any, Dict
from docai.utils.config_utils import load_environment, load_config


def get_storage_config() -> Dict[str, Any]:
    """
    Retrieves the storage service configuration from the main YAML config.

    Returns:
        Dict[str, Any]: Dictionary containing storage configuration settings.

    Raises:
        RuntimeError: If the 'storage' section is not found in the config file.
    """
    config = load_config()
    storage_config = config.get("storage")
    if not storage_config:
        raise RuntimeError("The storage configuration is missing in the config file.")
    return storage_config


load_environment()
_storage_config = get_storage_config()

BASE_PATH = Path(_storage_config.get("base_path", "data"))
HOST = _storage_config.get("host", "0.0.0.0")
PORT = _storage_config.get("port", 8000)
LOG_FILE = _storage_config.get("log_file", "logs/storage_service.log")
