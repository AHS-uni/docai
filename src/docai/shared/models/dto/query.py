from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from docai.shared.models.domain.query import QueryStatus
from docai.shared.models.dto.meta import Meta


class Query(BaseModel):
    """
    Full DTO representation of a query.

    Attributes:
        id (str): Unique identifier for the query.
        text (str): The raw query text.
        target_document_ids (List[str]): List of document IDs related to the query.
         context_page_ids (List[str]): List of retrieved page IDs.
        metadata (dict): Additional metadata for the query.
        answer (Optional[str]): Generated answer for the query.
        created_at (datetime): Timestamp when the query was created.
        processed_at (Optional[datetime]): Timestamp when the query was processed.
        indexed_at (Optional[datetime]): Timestamp when the query was indexed.
        context_retrieved_at (Optional[datetime]): Timestamp when context was retrieved.
        answered_at (Optional[datetime]): Timestamp when the query was answered.
        status (QueryStatus): Current status of the query.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the query",
        examples=["query_1234567890"],
    )
    text: str = Field(
        ..., description="The raw query text", examples=["Find document about AI"]
    )
    target_document_ids: List[str] = Field(
        default_factory=list,
        description="List of document IDs associated with the query",
        examples=[["doc_abcdef123456"]],
    )
    context_page_ids: List[str] = Field(
        default_factory=list,
        description="List of page IDs that represent the context of the query",
        examples=[["page_abcdef123456"]],
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional query metadata",
        examples=[{"priority": "high"}],
    )
    answer: Optional[str] = Field(
        None,
        description="Generated answer for the query",
        examples=["The document is available."],
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp of the query",
        examples=["2025-04-10T12:00:00Z"],
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Processing timestamp of the query",
        examples=["2025-04-10T12:30:00Z"],
    )
    indexed_at: Optional[datetime] = Field(
        None,
        description="Indexing timestamp of the query",
        examples=["2025-04-10T12:45:00Z"],
    )
    context_retrieved_at: Optional[datetime] = Field(
        None,
        description="Timestamp when query context was retrieved",
        examples=["2025-04-10T12:50:00Z"],
    )
    answered_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the query was answered",
        examples=["2025-04-10T13:00:00Z"],
    )
    status: QueryStatus = Field(
        ..., description="Current status of the query", examples=["answered"]
    )


class MinimalQuery(BaseModel):
    """
    Minimal DTO representation of a query for summary endpoints.

    Attributes:
        id (str): Unique identifier for the query.
        status (QueryStatus): Current status of the query.
        updated_at (Optional[datetime]): Timestamp when the query was last updated.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the query",
        examples=["query_1234567890"],
    )
    status: QueryStatus = Field(
        ..., description="Current status of the query", examples=["answered"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of the last update to the query",
        examples=["2025-04-12T16:00:00Z"],
    )


class QueryResponse(BaseModel):
    """
    Response model for query-related endpoints.

    Attributes:
        data (List[Query]): Array of full Query DTO objects.
        meta (dict): Metadata for the response including timestamp and version information.
    """

    data: List[Query] = Field(
        ...,
        description="List of query records",
        examples=[
            [
                {
                    "id": "query_1234567890",
                    "text": "Find document about AI",
                    "target_document_ids": ["doc_abcdef123456"],
                    "context_page__ids": ["page_abcdef123456"],
                    "metadata": {"priority": "high"},
                    "answer": "The document is available.",
                    "created_at": "2025-04-10T12:00:00Z",
                    "processed_at": "2025-04-10T12:30:00Z",
                    "indexed_at": "2025-04-10T12:45:00Z",
                    "context_retrieved_at": "2025-04-10T12:50:00Z",
                    "answered_at": "2025-04-10T13:00:00Z",
                    "status": "answered",
                }
            ]
        ],
    )
    meta: Meta = Field(
        ..., description="Response metadata including timestamp, version, etc."
    )
