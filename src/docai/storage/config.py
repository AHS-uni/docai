from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class StorageSettings(BaseSettings):
    """
    Application settings for the Storage Service, loaded from environment
    variables and an optional .env file.
    """

    version: str = Field(default="1.0.0", description="Version of the storage service")
    base_path: Path = Field(
        default=Path("data"), description="Base directory for storage"
    )
    host: str = Field(default="0.0.0.0", description="Storage API bind host")
    port: int = Field(default=8000, description="Storage API bind port")
    log_file: Path = Field(
        default=Path("logs/storage_service.log"),
        description="Path to the service log file",
    )
    lock_stripes: int = Field(default=1024, description="How many lock stripes to use.")
    client_max_connections: int = Field(
        default=10, description="Max concurrent HTTP connections"
    )
    client_max_keepalive: int = Field(
        default=5, description="Max idle HTTP keep-alive connections"
    )
    client_request_timeout_seconds: float = Field(
        default=10.0, description="Per-request timeout in seconds"
    )

    model_config = SettingsConfigDict(
        env_prefix="STORAGE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ← ignore unknown .env keys
    )


_settings = StorageSettings()

VERSION: str = _settings.version
BASE_PATH: Path = _settings.base_path
HOST: str = _settings.host
PORT: int = _settings.port
LOG_FILE: Path = _settings.log_file
LOCK_STRIPES: int = _settings.lock_stripes

CLIENT_MAX_CONNECTIONS: int = _settings.client_max_connections
CLIENT_MAX_KEEPALIVE_CONNECTIONS: int = _settings.client_max_keepalive
CLIENT_REQUEST_TIMEOUT_SECONDS: float = _settings.client_request_timeout_seconds
