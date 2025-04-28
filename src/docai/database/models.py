"""
SQLAlchemy ORM model definitions for Document, Page, and Query.

All domain‐model definitions have been moved to `docai.shared.models.orm.*`.
This file simply imports and re-exports those mapped classes.
"""

from docai.shared.models.orm.base import Base
from docai.shared.models.orm.document import Document
from docai.shared.models.orm.page import Page
from docai.shared.models.orm.query import Query
from docai.shared.models.orm.association import (
    query_document_association,
    query_page_association,
)

__all__ = [
    "Base",
    "Document",
    "Page",
    "Query",
    "query_document_association",
    "query_page_association",
]
