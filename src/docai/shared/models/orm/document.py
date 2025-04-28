from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from sqlalchemy.sql import func
from sqlalchemy import String, DateTime, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from docai.shared.models.domain.document import DocumentStatus
from docai.shared.models.orm.base import Base
from docai.shared.models.orm.association import query_document_association

if TYPE_CHECKING:
    from docai.shared.models.orm.page import Page
    from docai.shared.models.orm.query import Query


class Document(Base):
    """
    ORM model representing a Document record.

    Attributes:
        id (str): Unique identifier for the document.
        file_name (str): Original PDF file name.
        created_at (datetime): Timestamp when the document was created.
        processed_at (Optional[datetime]): Timestamp when document processing completed.
        indexed_at (Optional[datetime]): Timestamp when document indexing was finished.
        status (DocumentStatus): Current status of the document.
        extra (dict): Additional metadata (e.g., page count, extraction info).
        pages (List[PageImage]): Related page images for this document.
    """

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus), default=DocumentStatus.CREATED, nullable=False
    )
    extra: Mapped[dict] = mapped_column(JSON, default=dict)

    # One-to-many relationship: one document may have multiple pages.
    pages: Mapped[List[Page]] = relationship(
        "Page", back_populates="document", cascade="all, delete, delete-orphan"
    )
    # Many-to-many: a document can belong to multiple queries.
    queries: Mapped[List[Query]] = relationship(
        "Query", secondary=query_document_association, back_populates="documents"
    )
