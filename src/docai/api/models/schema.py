from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class DocumentStatus(str, Enum):
    """Enumeration of possible document statuses."""

    CREATED = "created"
    PROCESSED = "processed"
    INDEXED = "indexed"


class PageImage(BaseModel):
    """Represents a page image of a document.

    Attributes:
        id (str): Unique identifier for the page image.
        page_number (int): Index of the page.
        image_path (str): Path to the image file.
    """

    id: str = Field(..., examples=["page_f7a731ac-b6c1-4f82-b395-602fa4a9137c"])
    page_number: int = Field(..., examples=[0, 1, 2])
    image_path: str = Field(
        ..., examples=["data/images/doc_ce5b3411-ed18-4e11-8b2c-e987ab241d0b_p0.jpg"]
    )


class Document(BaseModel):
    """Represents a document with its metadata, status, and page images.

    Attributes:
        id (str): Unique identifier for the document.
        file_name (str): Name of the original PDF file.
        created_at (datetime): Creation timestamp of the document.
        processed_at (Optional[datetime]): Timestamp when processing completed.
        indexed_at (Optional[datetime]): Timestamp when the document was indexed.
        status (DocumentStatus): Current status of the document.
        metadata (dict): Additional metadata.
        pages (List[PageImage]): List of page images included in the document.
    """

    id: str = Field(..., examples=["doc_ce5b3411-ed18-4e11-8b2c-e987ab241d0b"])
    file_name: str = Field(..., examples=["document.pdf"])
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = Field(default=None)
    indexed_at: Optional[datetime] = Field(default=None)
    status: DocumentStatus = Field(
        default=DocumentStatus.CREATED, description="Document status"
    )
    metadata: Optional[dict] = Field(default_factory=dict)
    pages: List[PageImage]
