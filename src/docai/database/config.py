"""
Module configures database connection parameters from our YAML/ENV setup.
"""

from typing import Any, Dict

from docai.shared.utils.config_utils import load_config, load_environment

load_environment()


def get_database_config() -> Dict[str, Any]:
    """
    Load the 'database' section from the main configuration.

    Returns:
        A dict of database settings (must include 'url').

    Raises:
        RuntimeError: if the 'database' section is missing.
    """
    cfg = load_config()
    db_cfg = cfg.get("database")
    if not db_cfg:
        raise RuntimeError("Missing 'database' section in configuration.")
    return db_cfg


_db_cfg = get_database_config()

#: The SQLAlchemy database URL
DB_URL: str = _db_cfg["url"]
#: The size of the connection pool
POOL_SIZE: int = _db_cfg.get("pool_size", 10)
#: The max overflow for pool connections
MAX_OVERFLOW: int = _db_cfg.get("max_overflow", 5)
#: Log file path for database service
LOG_FILE: str = _db_cfg.get("log_file", "logs/database_service.log")
