from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional
from datetime import datetime

from sqlalchemy import String, DateTime, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from docai.shared.models.domain.query import QueryStatus
from docai.shared.models.orm.base import Base
from docai.shared.models.orm.association import query_document_association

if TYPE_CHECKING:
    from docai.shared.models.orm.document import Document


class Query(Base):
    """
    ORM model representing a user query in DocAI.

    Attributes:
        id (str): Unique identifier for the query.
        text (str): The raw query text.
        created_at (datetime): Timestamp when the query was created.
        processed_at (Optional[datetime]): Timestamp when processing was completed.
        indexed_at (Optional[datetime]): Timestamp when indexing was completed.
        context_retrieved_at (Optional[datetime]): Timestamp when context was retrieved.
        answered_at (Optional[datetime]): Timestamp when the answer was generated.
        status (QueryStatus): Current status of the query.
        extra (dict): Additional metadata for the query.
        answer (Optional[str]): The generated answer text.
        documents (List[Document]): Associated documents for this query (many-to-many).
    """

    __tablename__ = "queries"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    text: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    context_retrieved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    answered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    status: Mapped[QueryStatus] = mapped_column(
        Enum(QueryStatus), default=QueryStatus.CREATED, nullable=False
    )
    extra: Mapped[dict] = mapped_column(JSON, default=dict)
    answer: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Many-to-many relationship with Document.
    documents: Mapped[List[Document]] = relationship(
        "Document",
        secondary=query_document_association,
        back_populates="queries",
    )
