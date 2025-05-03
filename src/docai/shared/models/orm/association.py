from sqlalchemy import Column, ForeignKey, String, Table

from docai.shared.models.orm.base import Base

query_document_association = Table(
    "query_documents",
    Base.metadata,
    Column("query_id", String, ForeignKey("queries.id"), primary_key=True),
    Column("document_id", String, ForeignKey("documents.id"), primary_key=True),
)

query_page_association = Table(
    "query_pages",
    Base.metadata,
    Column("query_id", String, ForeignKey("queries.id"), primary_key=True),
    Column("page_id", String, ForeignKey("pages.id"), primary_key=True),
)
