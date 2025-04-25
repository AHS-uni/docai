import json
from datetime import datetime
from pathlib import Path
from enum import Enum
from typing import List, Optional, Any, Dict


class QueryStatus(Enum):
    """Enumeration of possible query statuses."""

    CREATED = "created"
    PROCESSED = "processed"
    INDEXED = "indexed"
    CONTEXT_RETRIEVED = "context-retrieved"
    ANSWERED = "answered"


class MinimalQuery:
    """
    Minimal representation of a Query.

    This minimal model contains the essential fields for summary views.

    Attributes:
        id (str): Unique identifier for the query.
        status (QueryStatus): Current status of the query.
        updated_at (datetime): Timestamp of the last update.
    """

    __slots__ = ["id", "status", "updated_at"]

    def __init__(self, id: str, status: QueryStatus, updated_at: datetime):
        self.id = id
        self.status = status
        self.updated_at = updated_at

    def __repr__(self) -> str:
        return (
            f"MinimalQuery(id={self.id!r}, status={self.status.value!r}, "
            f"updated_at={self.updated_at!r})"
        )


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
        extra (dict): Additional metadata for the query.
        target_document_ids (List[str]): List of document IDs available at the time of submission.
        context_page_ids (Optional[List[str]]): List of retrieved page IDs.
        answer (Optional[str]): The generated answer (if available).
    """

    def __init__(
        self,
        query_id: str,
        text: str,
        target_document_ids: Optional[List[str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initializes a Query object.

        Args:
            query_id (str): Unique identifier for the query.
            text (str): Raw query text.
            target_document_ids (Optional[List[str]], optional): List of document IDs linked with the query.
            extra (Optional[Dict[str, Any]], optional): Additional metadata for the query.
        """
        self.id: str = query_id
        self.text: str = text
        self.created_at: datetime = datetime.now()
        self.processed_at: Optional[datetime] = None
        self.indexed_at: Optional[datetime] = None
        self.context_retrieved_at: Optional[datetime] = None
        self.answered_at: Optional[datetime] = None
        self._status: QueryStatus = QueryStatus.CREATED
        self.extra: Dict[str, Any] = extra if extra is not None else {}
        self.target_document_ids: List[str] = (
            target_document_ids if target_document_ids is not None else []
        )
        self.context_page_ids: Optional[List[str]] = None
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

    def to_minimal(self) -> MinimalQuery:
        """
        Create a minimal representation of this Query.

        The returned MinimalQuery contains only the id, status, and a last updated timestamp (the most recent
        among processed_at, indexed_at, context_retrieved_at, answered_at, or created_at).

        Returns:
            MinimalQuery: The minimal version of this query.
        """
        # Determine updated_at by comparing available timestamps in order of priority.
        updated = (
            self.answered_at
            or self.context_retrieved_at
            or self.indexed_at
            or self.processed_at
            or self.created_at
        )
        return MinimalQuery(id=self.id, status=self._status, updated_at=updated)

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
            "extra": self.extra,
            "target_document_ids": self.target_document_ids,
            "answer": self.answer,
        }

    def save(self, save_path: Path) -> None:
        """
        Saves the Query details to a JSON file.

        Args:
            save_path (Path): The directory in which to save the JSON file.
        """
        save_path.mkdir(parents=True, exist_ok=True)
        file_path = save_path / f"{self.id}.json"
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=4)
            print(f"Query object saved to {file_path}")
