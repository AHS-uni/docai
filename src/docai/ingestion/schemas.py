import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

##############################################
# Document Related Classes
##############################################


class DocumentStatus(Enum):
    """Enumeration of possible document statuses."""

    CREATED = "created"
    PROCESSED = "processed"
    INDEXED = "indexed"


class Document:
    """
    Represents a document consisting of PageImages and associated metadata.

    Attributes:
        id (str): Unique identifier for the document.
        file_name (str): Name of the original PDF file.
        created_at (datetime): Timestamp when the document object was created.
        processed_at (Optional[datetime]): Timestamp when processing completed.
        indexed_at (Optional[datetime]): Timestamp when the document was indexed.
        _status (DocumentStatus): Current status of the document.
        metadata (dict): Additional metadata for the document.
        pages (List[PageImage]): A list of PageImage objects.
    """

    def __init__(
        self,
        doc_id: str,
        file_name: str,
        pages: Optional[List["PageImage"]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a Document object with default values.

        Args:
            doc_id (str): Unique identifier for the document.
            file_name (str): Name of the original PDF file.
            pages (Optional[List[PageImage]], optional): A list of PageImage objects. Defaults to None.
            metadata (Optional[dict], optional): Additional metadata for the document. Defaults to None.
        """
        self.id: str = doc_id
        self.file_name: str = file_name
        self.created_at: datetime = datetime.now()
        self._status: DocumentStatus = DocumentStatus.CREATED
        self.processed_at: Optional[datetime] = None
        self.indexed_at: Optional[datetime] = None
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}
        self.pages: List[PageImage] = pages if pages is not None else []

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
            self.processed_at = datetime.now()
        elif new_status == DocumentStatus.INDEXED:
            self.indexed_at = datetime.now()

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


class PageImage:
    """
    Represents a single page of a document.

    Attributes:
        id (str): Unique identifier for the page.
        page_number (int): Page index within the document.
        image_path (str): File path to the JPG image of the page.
    """

    def __init__(self, page_id: str, page_number: int, image_path: str) -> None:
        """
        Initializes a PageImage object.

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
        Converts the PageImage instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the page image's details.
        """
        return {
            "id": self.id,
            "page_number": self.page_number,
            "image_path": self.image_path,
        }


##############################################
# Query Related Classes
##############################################


class QueryStatus(Enum):
    """Enumeration of possible query statuses."""

    CREATED = "created"
    PROCESSED = "processed"
    INDEXED = "indexed"
    CONTEXT_RETRIEVED = "context-retrieved"
    ANSWERED = "answered"


class Query:
    """
    Represents a user query with associated metadata and state transitions.

    Attributes:
        id (str): Unique identifier for the query.
        text (str): The raw query text submitted by the user.
        created_at (datetime): Timestamp when the query was created.
        processed_at (Optional[datetime]): Timestamp when query processing finished.
        indexed_at (Optional[datetime]): Timestamp when the query was indexed.
        context_retrieved_at (Optional[datetime]): Timestamp when query context was retrieved.
        answered_at (Optional[datetime]): Timestamp when the final answer was generated.
        _status (QueryStatus): Current state of the query.
        metadata (dict): Additional metadata for the query.
        associated_document_ids (List[str]): List of document IDs available at the time of submission.
        answer (Optional[str]): The generated answer (if available).
    """

    def __init__(
        self,
        query_id: str,
        text: str,
        associated_document_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a Query object.

        Args:
            query_id (str): Unique identifier for the query.
            text (str): Raw query text.
            associated_document_ids (Optional[List[str]], optional): List of document IDs linked with the query.
            metadata (Optional[Dict[str, Any]], optional): Additional metadata for the query.
        """
        self.id: str = query_id
        self.text: str = text
        self.created_at: datetime = datetime.now()
        self.processed_at: Optional[datetime] = None
        self.indexed_at: Optional[datetime] = None
        self.context_retrieved_at: Optional[datetime] = None
        self.answered_at: Optional[datetime] = None
        self._status: QueryStatus = QueryStatus.CREATED
        self.metadata: Dict[str, Any] = metadata if metadata is not None else {}
        self.associated_document_ids: List[str] = (
            associated_document_ids if associated_document_ids is not None else []
        )
        self.answer: Optional[str] = None

    @property
    def status(self) -> QueryStatus:
        """Returns the current status of the query."""
        return self._status

    @status.setter
    def status(self, new_status: QueryStatus) -> None:
        """
        Updates the query status and associated timestamps.

        Args:
            new_status (QueryStatus): The new state to set for the query.

        Raises:
            ValueError: If the new status is not a QueryStatus or if the state transition is invalid.
        """
        if not isinstance(new_status, QueryStatus):
            raise ValueError("Invalid status provided. Must be a QueryStatus value.")

        valid_transitions: Dict[QueryStatus, List[QueryStatus]] = {
            QueryStatus.CREATED: [QueryStatus.PROCESSED],
            QueryStatus.PROCESSED: [QueryStatus.INDEXED],
            QueryStatus.INDEXED: [QueryStatus.CONTEXT_RETRIEVED],
            QueryStatus.CONTEXT_RETRIEVED: [QueryStatus.ANSWERED],
            QueryStatus.ANSWERED: [],  # No further transitions allowed
        }

        if new_status not in valid_transitions[self._status]:
            raise ValueError(
                f"Cannot transition from {self._status.value} to {new_status.value}."
            )

        self._status = new_status

        if new_status == QueryStatus.PROCESSED:
            self.processed_at = datetime.now()
        elif new_status == QueryStatus.INDEXED:
            self.indexed_at = datetime.now()
        elif new_status == QueryStatus.CONTEXT_RETRIEVED:
            self.context_retrieved_at = datetime.now()
        elif new_status == QueryStatus.ANSWERED:
            self.answered_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the Query instance to a dictionary representation.

        Returns:
            dict: Dictionary containing the query's details.
        """
        return {
            "id": self.id,
            "text": self.text,
            "created_at": self.created_at.isoformat() + "Z",
            "processed_at": (
                self.processed_at.isoformat() + "Z" if self.processed_at else None
            ),
            "indexed_at": (
                self.indexed_at.isoformat() + "Z" if self.indexed_at else None
            ),
            "context_retrieved_at": (
                self.context_retrieved_at.isoformat() + "Z"
                if self.context_retrieved_at
                else None
            ),
            "answered_at": (
                self.answered_at.isoformat() + "Z" if self.answered_at else None
            ),
            "status": self.status.value,
            "metadata": self.metadata,
            "associated_document_ids": self.associated_document_ids,
            "answer": self.answer,
        }

    def save(self, save_path: Path) -> None:
        """
        Saves the Query details to a JSON file.

        Args:
            save_path (Path): The directory in which to save the metadata file.
        """
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / f"{self.id}.json"
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
            print(f"Query metadata saved to {file_path}")
