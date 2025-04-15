from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, DateTime, Enum, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from docai.models.document import DocumentStatus
from docai.models.query import QueryStatus

Base = declarative_base()


# Association table for many-to-many relationship between query and document
query_document_association = Table(
    "query_documents",
    Base.metadata,
    Column("query_id", String, ForeignKey("queries.id"), primary_key=True),
    Column("document_id", String, ForeignKey("documents.id"), primary_key=True),
)


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

    id = Column(String, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    indexed_at = Column(DateTime, nullable=True)
    status = Column(
        Enum(DocumentStatus), default=DocumentStatus.CREATED, nullable=False
    )
    extra = Column(JSON, default=dict)

    # One-to-many relationship: one document may have multiple pages.
    pages = relationship(
        "Page", back_populates="document", cascade="all, delete, delete-orphan"
    )

    # Many-to-many: a document can belong to multiple queries.
    queries = relationship(
        "Query", secondary=query_document_association, back_populates="documents"
    )


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

    id = Column(String, primary_key=True, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    page_number = Column(Integer, nullable=False)
    image_path = Column(String, nullable=False)

    # Relationship back to the parent document.
    document = relationship("Document", back_populates="pages")


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

    id = Column(String, primary_key=True, index=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)
    indexed_at = Column(DateTime, nullable=True)
    context_retrieved_at = Column(DateTime, nullable=True)
    answered_at = Column(DateTime, nullable=True)
    status = Column(Enum(QueryStatus), default=QueryStatus.CREATED, nullable=False)
    extra = Column(JSON, default=dict)
    answer = Column(String, nullable=True)

    # Many-to-many relationship with Document.
    documents = relationship(
        "Document", secondary=query_document_association, back_populates="queries"
    )
