from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    """
    Application settings for the Ingestion Service, loaded from environment
    variables and an optional .env file.
    """

    # General
    version: str = Field(
        default="1.0.0", description="Version of the ingestion service"
    )
    log_file: Path = Field(
        default=Path("logs/ingestion_service.log"), description="Path to log file"
    )

    # Document conversion
    conversion_output_dir: Path = Field(
        default=Path("tmp/conversions"),
        description="Temporary directory to store converted images",
    )
    conversion_dpi: int = Field(
        default=200, description="DPI for PDF to image conversion"
    )
    conversion_quality: int = Field(
        default=90, description="JPEG quality for output images (0–100)"
    )
    image_width: int = Field(default=2000, description="Maximum width of output image")
    image_height: int = Field(
        default=2000, description="Maximum height of output image"
    )
    max_file_size_mb: float = Field(
        default=50.0, description="Max allowed file size in MB"
    )
    page_threshold: int = Field(
        default=50, description="Threshold at which pages are processed in parallel"
    )

    # Client settings
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
        env_prefix="INGESTION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


_settings = IngestionSettings()

VERSION = _settings.version
LOG_FILE = _settings.log_file

CONVERSION_OUTPUT_DIR = _settings.conversion_output_dir
CONVERSION_DPI = _settings.conversion_dpi
CONVERSION_QUALITY = _settings.conversion_quality
IMAGE_WIDTH = _settings.image_width
IMAGE_HEIGHT = _settings.image_height
MAX_FILE_SIZE_MB = _settings.max_file_size_mb
PAGE_THRESHOLD = _settings.page_threshold

CLIENT_MAX_CONNECTIONS = _settings.client_max_connections
CLIENT_MAX_KEEPALIVE = _settings.client_max_keepalive
CLIENT_REQUEST_TIMEOUT_SECONDS = _settings.client_request_timeout_seconds
