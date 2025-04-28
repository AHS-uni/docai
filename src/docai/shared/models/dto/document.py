from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from docai.shared.models.domain.document import DocumentStatus
from docai.shared.models.dto.page import Page
from docai.shared.models.dto.meta import Meta


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
    meta: Meta = Field(
        ..., description="Response metadata including timestamp, version, etc."
    )
