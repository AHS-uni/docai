from typing import Any, Dict
from docai.utils.config_utils import load_environment, load_config


def get_database_config() -> Dict[str, Any]:
    """
    Retrieves the database service configuration from the main YAML config.

    Returns:
        Dict[str, Any]: Dictionary containing database configuration settings.

    Raises:
        RuntimeError: If the 'database' section is not found in the config file.
    """
    config = load_config()
    database_config = config.get("database")
    if not database_config:
        raise RuntimeError("The database configuration is missing in the config file.")
    return database_config


load_environment()
_database_config = get_database_config()

DB_URL = _database_config["url"]
POOL_SIZE = _database_config.get("pool_size", 10)
MAX_OVERFLOW = _database_config.get("max_overflow", 5)
LOG_FILE = _database_config.get("log_file", "logs/database_service.log")
