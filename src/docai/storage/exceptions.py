"""
Custom exception types for the Storage Service.
"""


class StorageError(Exception):
    """Base exception for all storage‐related errors."""


class SavePDFError(StorageError):
    """Raised when saving a PDF file fails."""


class SaveImageError(StorageError):
    """Raised when saving an image file fails."""


class PDFNotFoundError(StorageError):
    """Raised when a requested PDF file does not exist."""


class ImageNotFoundError(StorageError):
    """Raised when a requested image file does not exist."""


class DeleteDocumentError(StorageError):
    """Raised when deleting a document or its associated files fails."""
