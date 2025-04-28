class IngestionError(Exception):
    """Base class for all ingestion‐related errors."""


class ConversionError(IngestionError):
    """Raised when PDF→image conversion fails."""


class StorageError(IngestionError):
    """Raised on failures writing to the Storage Service."""


class QueueError(IngestionError):
    """Raised when enqueueing or dequeuing fails."""
