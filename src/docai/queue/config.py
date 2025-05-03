from pathlib import Path
from typing import List, Set

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class QueueSettings(BaseSettings):
    """
    Application settings for the Queue Service, loaded from environment
    variables and an optional .env file.
    """

    version: str = Field(default="1.0.0", description="Version of the queue service")
    log_file: Path = Field(
        default=Path("logs/queue_service.log"),
        description="Path to the service log file",
    )
    broker_url: str = Field(
        default="redis://localhost:6379/0", description="Broker connection URL"
    )
    default_queues: List[str] = Field(
        default=["queue_a", "queue_b"], description="Default logical queue names"
    )
    prefetch_count: int = Field(
        default=10, description="How many messages each consumer will prefetch at once"
    )
    visibility_timeout: int = Field(
        default=300, description="Seconds before an un-acked message is requeued"
    )
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
        env_prefix="QUEUE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # ← ignore unknown .env keys
    )


_settings = QueueSettings()

VERSION: str = _settings.version
LOG_FILE: Path = _settings.log_file

BROKER_URL: str = _settings.broker_url
DEFAULT_QUEUES: Set[str] = set(_settings.default_queues)
PREFETCH_COUNT: int = _settings.prefetch_count
VISIBILITY_TIMEOUT: int = _settings.visibility_timeout
