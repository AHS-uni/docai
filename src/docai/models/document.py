import json
from datetime import datetime, timezone
from pathlib import Path
from enum import Enum
from typing import List, Optional, Any, Dict


class DocumentStatus(Enum):
    """Enumeration of possible document statuses."""

    CREATED = "created"
    PROCESSED = "processed"
    INDEXED = "indexed"


class MinimalDocument:
    """
    Minimal representation of a Document.

    This minimal model only contains the essential fields for summary views.

    Attributes:
        id (str): Unique identifier for the document.
        status (DocumentStatus): Current status of the document.
        updated_at (datetime): Timestamp of the last update.
    """

    __slots__ = ["id", "status", "updated_at"]

    def __init__(self, id: str, status: DocumentStatus, updated_at: datetime):
        self.id = id
        self.status = status
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return (
            f"MinimalDocument(id={self.id!r}, status={self.status.value!r}, "
            f"updated_at={self.updated_at!r})"
        )


class Document:
    """
    Represents a document consisting of Pages and associated metadata.

    Attributes:
        id (str): Unique identifier for the document.
        file_name (str): Name of the original PDF file.
        created_at (datetime): Timestamp when the document object was created.
        processed_at (Optional[datetime]): Timestamp when processing completed.
        indexed_at (Optional[datetime]): Timestamp when the document was indexed.
        _status (DocumentStatus): Current status of the document.
        metadata (dict): Additional metadata for the document.
        pages (List[Page]): A list of Page objects.
    """

    def __init__(
        self,
        doc_id: str,
        file_name: str,
        pages: Optional[List["Page"]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a Document object with default values.

        Args:
            doc_id (str): Unique identifier for the document.
            file_name (str): Name of the original PDF file.
            pages (Optional[List[Page]], optional): A list of Page objects. Defaults to None.
            metadata (Optional[dict], optional): Additional metadata for the document. Defaults to None.
        """
        self.id: str = doc_id
        self.file_name: str = file_name
        self.created_at: datetime = datetime.now(timezone.utc)
        self._status: DocumentStatus = DocumentStatus.CREATED
        self.processed_at: Optional[datetime] = None
        self.indexed_at: Optional[datetime] = None
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}
        self.pages: List[Page] = pages if pages is not None else []

    @property
    def status(self) -> DocumentStatus:
        """Returns the current status of the document."""
        return self._status

    @status.setter
    def status(self, new_status: DocumentStatus) -> None:
        """
        Updates the document status and related timestamps.

        Args:
            new_status (DocumentStatus): The new state to which the document transitions.

        Raises:
            ValueError: If the new status is invalid or if the state transition is not allowed.
        """
        if not isinstance(new_status, DocumentStatus):
            raise ValueError("Invalid status provided. Must be a DocumentStatus value.")

        valid_transitions: Dict[DocumentStatus, List[DocumentStatus]] = {
            DocumentStatus.CREATED: [DocumentStatus.PROCESSED],
            DocumentStatus.PROCESSED: [DocumentStatus.INDEXED],
            DocumentStatus.INDEXED: [],  # No further transitions allowed
        }
        if new_status not in valid_transitions[self._status]:
            raise ValueError(
                f"Cannot transition from {self._status.value} to {new_status.value}."
            )

        self._status = new_status

        if new_status == DocumentStatus.PROCESSED:
            self.processed_at = datetime.now(timezone.utc)
        elif new_status == DocumentStatus.INDEXED:
            self.indexed_at = datetime.now(timezone.utc)

    def to_minimal(self) -> MinimalDocument:
        """
        Create a minimal representation of this Document.

        The returned MinimalDocument instance contains only the id, status, and an updated_at timestamp.
        The updated_at is determined as the most recent of processed_at, indexed_at, or created_at.

        Returns:
            MinimalDocument: The minimal version of this document.
        """
        updated = self.indexed_at or self.processed_at or self.created_at
        return MinimalDocument(id=self.id, status=self._status, updated_at=updated)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Document instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the document's details.
        """
        return {
            "id": self.id,
            "file_name": self.file_name,
            "created_at": self.created_at.isoformat() + "Z",
            "processed_at": (
                self.processed_at.isoformat() + "Z" if self.processed_at else None
            ),
            "indexed_at": (
                self.indexed_at.isoformat() + "Z" if self.indexed_at else None
            ),
            "status": self.status.value,
            "metadata": self.metadata,
            "pages": [page.to_dict() for page in self.pages],
        }

    def save(self, save_path: Path) -> None:
        """
        Persists the Document data as a JSON file.

        Args:
            save_path (Path): Directory where the document metadata file will be saved.
        """
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / f"{self.id}.json"
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
            print(f"Document metadata saved to {file_path}")


class Page:
    """
    Represents a single page of a document.

    Attributes:
        id (str): Unique identifier for the page.
        page_number (int): Page index within the document.
        image_path (str): File path to the JPG image of the page.
    """

    def __init__(self, page_id: str, page_number: int, image_path: str) -> None:
        """
        Initializes a Page object.

        Args:
            page_id (str): Unique identifier for the page.
            page_number (int): The page's number in the document.
            image_path (str): Path to the image file representing this page.
        """
        self.id: str = page_id
        self.page_number: int = page_number
        self.image_path: str = image_path

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Page instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the page image's details.
        """
        return {
            "id": self.id,
            "page_number": self.page_number,
            "image_path": self.image_path,
        }
