from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field

from docai.shared.models.document import DocumentStatus
from docai.shared.models.query import QueryStatus

# --- Pure DTO Models --- #


class Document(BaseModel):
    """
    Full DTO representation of a document.

    Attributes:
        id (str): Unique identifier for the document.
        file_name (str): The name of the document file.
        status (DocumentStatus): Current status of the document.
        metadata (dict): Additional metadata for the document.
        created_at (datetime): Timestamp when the document was created.
        processed_at (Optional[datetime]): Timestamp when the document was processed.
        indexed_at (Optional[datetime]): Timestamp when the document was indexed.
        pages (List[Page]): List of associated pages in the document.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the document",
        examples=["doc_abcdef123456"],
    )
    file_name: str = Field(
        ..., description="Name of the document file", examples=["report.pdf"]
    )
    status: DocumentStatus = Field(
        ..., description="Current status of the document", examples=["processed"]
    )
    metadata: dict = Field(
        default_factory=dict,
        description="Additional document metadata",
        examples=[{"author": "John Doe", "category": "finance"}],
    )
    created_at: datetime = Field(
        ...,
        description="Creation timestamp of the document",
        examples=["2025-04-10T12:00:00Z"],
    )
    processed_at: Optional[datetime] = Field(
        None,
        description="Processing timestamp of the document",
        examples=["2025-04-11T09:30:00Z"],
    )
    indexed_at: Optional[datetime] = Field(
        None,
        description="Indexing timestamp of the document",
        examples=["2025-04-11T10:00:00Z"],
    )
    pages: List["Page"] = Field(
        default_factory=list, description="List of associated pages"
    )


class MinimalDocument(BaseModel):
    """
    Minimal DTO representation of a document for summary endpoints.

    Attributes:
        id (str): Unique identifier for the document.
        status (DocumentStatus): Current status of the document.
        updated_at (Optional[datetime]): Timestamp when the document was last updated.
    """

    id: str = Field(
        ...,
        description="Unique identifier for the document",
        examples=["doc_abcdef123456"],
    )
    status: DocumentStatus = Field(
        ..., description="Current status of the document", examples=["processed"]
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp of the last update to the document",
        examples=["2025-04-12T15:45:00Z"],
    )


class Page(BaseModel):
    """
    DTO representation of a page.

    Attributes:
        id (str): Unique identifier for the page.
        page_number (int): The page number within the document.
        image_path (str): The file path to the page image.
    """

    id: str = Field(
        ..., description="Unique identifier for the page", examples=["page_001"]
    )
    page_number: int = Field(
        ..., description="Page number in the document", examples=[1]
    )
    image_path: str = Field(
        ...,
        description="Filesystem path to the page image",
        examples=["/images/page1.jpg"],
    )


class Query(BaseModel):
    """
    Full DTO representation of a query.

    Attributes:
        id (str): Unique identifier for the query.
        text (str): The raw query text.
        target_document_ids (List[str]): List of document IDs related to the query.
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


class Error(BaseModel):
    """
    DTO representation for error information.

    Attributes:
        code (int): Numeric error code.
        message (str): A brief error message.
        detail (str): Detailed error description.
    """

    code: int = Field(..., description="Numeric error code", examples=[404])
    message: str = Field(
        ..., description="A brief error message", examples=["Not Found"]
    )
    detail: str = Field(
        ...,
        description="Detailed error description",
        examples=["The requested document was not found in the database."],
    )


# --- Response Models --- #


class DocumentResponse(BaseModel):
    """
    Response model for document-related endpoints.

    Attributes:
        data (List[Document]): Array of full Document DTO objects.
        meta (dict): Metadata for the response, e.g., timestamp and version information.
    """

    data: List[Document] = Field(
        ...,
        description="List of full document records",
        examples=[
            [
                {
                    "id": "doc_abcdef123456",
                    "file_name": "report.pdf",
                    "status": "processed",
                    "metadata": {"author": "John Doe"},
                    "created_at": "2025-04-10T12:00:00Z",
                    "processed_at": "2025-04-11T09:30:00Z",
                    "indexed_at": "2025-04-11T10:00:00Z",
                    "pages": [],
                }
            ]
        ],
    )
    meta: dict = Field(
        ...,
        description="Response metadata including timestamp, version, etc.",
        examples=[{"timestamp": "2025-04-12T17:00:00Z", "version": "1.0.0"}],
    )


class PageResponse(BaseModel):
    """
    Response model for page-related endpoints.

    Attributes:
        data (List[Page]): Array of Page DTO objects.
        meta (dict): Metadata for the response including timestamp and version.
    """

    data: List[Page] = Field(
        ...,
        description="List of page records",
        examples=[
            [{"id": "page_001", "page_number": 1, "image_path": "/images/page1.jpg"}]
        ],
    )
    meta: dict = Field(
        ...,
        description="Response metadata",
        examples=[{"timestamp": "2025-04-12T17:00:00Z", "version": "1.0.0"}],
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
    meta: dict = Field(
        ...,
        description="Response metadata including timestamp, version, etc.",
        examples=[{"timestamp": "2025-04-12T17:00:00Z", "version": "1.0.0"}],
    )


class ErrorResponse(BaseModel):
    """
    Response model for error responses.

    Attributes:
        errors (List[Error]): Array of error DTO objects.
        meta (dict): Metadata for the response including timestamp, version, etc.
    """

    errors: List[Error] = Field(
        ...,
        description="Array of error details",
        examples=[
            [
                {
                    "code": 404,
                    "message": "Not Found",
                    "detail": "The requested document was not found in the database.",
                }
            ]
        ],
    )
    meta: dict = Field(
        ...,
        description="Response metadata",
        examples=[{"timestamp": "2025-04-12T17:00:00Z", "version": "1.0.0"}],
    )
