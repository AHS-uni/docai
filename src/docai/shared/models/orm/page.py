from __future__ import annotations
from typing import TYPE_CHECKING, List

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from docai.shared.models.orm.base import Base
from docai.shared.models.orm.association import query_page_association

if TYPE_CHECKING:
    from docai.shared.models.orm.document import Document
    from docai.shared.models.orm.query import Query


class Page(Base):
    """
    ORM model representing a single page image of a document.

    Attributes:
        id (str): Unique identifier for the page image.
        document_id (str): Foreign key to the parent document.
        page_number (int): Page index in the document.
        image_path (str): Filesystem path to the JPG image file.
    """

    __tablename__ = "pages"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id"), nullable=False)
    page_number: Mapped[int] = mapped_column(Integer, nullable=False)
    image_path: Mapped[str] = mapped_column(String, nullable=False)

    # Relationship back to the parent document.
    document: Mapped["Document"] = relationship("Document", back_populates="pages")

    # Relationship back to queries that use this page as context
    queries: Mapped[List[Query]] = relationship(
        "Query", secondary=query_page_association, back_populates="pages"
    )
