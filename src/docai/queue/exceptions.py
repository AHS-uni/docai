class QueueError(Exception):
    """Base exception for all queue-related errors."""


class InvalidQueueNameError(QueueError):
    """Raised when an unknown or unauthorized queue name is used."""


class EnqueueError(QueueError):
    """Raised when enqueue operation fails."""


class FetchError(QueueError):
    """Raised when fetch operation fails."""


class AckError(QueueError):
    """Raised when acknowledgment operation fails."""


class NackError(QueueError):
    """Raised when negative-acknowledgment operation fails."""


class ConnectionError(QueueError):
    """Raised when the underlying broker connection fails."""
