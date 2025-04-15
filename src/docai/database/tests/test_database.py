import json
import time
import pytest
from datetime import datetime
from pathlib import Path
from typing import List

from sqlalchemy.exc import SQLAlchemyError

from docai.database.database import DatabaseService
from docai.database.models import Document, Query  # ORM models
from docai.models.document import Document as DomainDocument, DocumentStatus
from docai.models.query import Query as DomainQuery, QueryStatus

# Import synthetic data generators from your test resources.
from docai.database.tests.test_resources import (
    create_synthetic_documents,
    create_synthetic_queries,
)

# Instantiate the DatabaseService.
db_service = DatabaseService()


def measure_time(func):
    """
    Decorator to measure and print elapsed time for each test function.
    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} completed in {elapsed:.4f} seconds")
        return result

    return wrapper


# Helper mapping functions for tests.
def domain_doc_to_orm_doc(domain_doc: DomainDocument) -> Document:
    """
    Minimal mapping from a rich domain Document to an anemic ORM Document.

    Only id, file_name, and extra (metadata) are mapped. Relationship details (pages)
    are omitted since they are not needed for these tests.
    """
    orm_doc = Document(
        id=domain_doc.id, file_name=domain_doc.file_name, extra=domain_doc.metadata
    )
    # If timestamps are present in the domain model, copy them over.
    orm_doc.created_at = domain_doc.created_at
    orm_doc.processed_at = domain_doc.processed_at
    orm_doc.indexed_at = domain_doc.indexed_at
    # The status enum will be copied directly.
    orm_doc.status = domain_doc.status
    return orm_doc


def domain_query_to_orm_query(domain_query: DomainQuery) -> Query:
    """
    Minimal mapping from a rich domain Query to an anemic ORM Query.

    Only id, text, and extra (metadata) are mapped. Complex relationships (like associated documents)
    may be handled separately if needed.
    """
    orm_query = Query(
        id=domain_query.id, text=domain_query.text, extra=domain_query.metadata
    )
    orm_query.created_at = domain_query.created_at
    orm_query.processed_at = domain_query.processed_at
    orm_query.indexed_at = domain_query.indexed_at
    orm_query.context_retrieved_at = domain_query.context_retrieved_at
    orm_query.answered_at = domain_query.answered_at
    orm_query.status = domain_query.status
    orm_query.answer = domain_query.answer
    return orm_query


# ----------------------------
# DOCUMENT TESTS
# ----------------------------


@measure_time
def test_bulk_create_documents():
    """
    Test creating multiple Document records using synthetic data.
    """
    synthetic_docs: List[DomainDocument] = create_synthetic_documents()
    created_doc_ids = []

    for domain_doc in synthetic_docs:
        orm_doc = domain_doc_to_orm_doc(domain_doc)
        # Persist the ORM document using DatabaseService.
        created_doc = db_service.create_document(orm_doc)
        created_doc_ids.append(created_doc.id)
        # Verify that the status is INDEXED (as set by the synthetic function).
        assert created_doc.status.value == DocumentStatus.INDEXED.value
        # At least one timestamp (processed_at or indexed_at) should be set.
        assert (
            created_doc.processed_at is not None or created_doc.indexed_at is not None
        )

    # List documents and verify the created ones appear
    all_docs = db_service.list_documents()
    listed_ids = [doc.id for doc in all_docs]
    for doc_id in created_doc_ids:
        assert doc_id in listed_ids


@measure_time
def test_update_document_status_bulk():
    """
    Test updating the status of synthetic documents.

    Initially, synthetic documents are created with status INDEXED.
    We then update a document's status back to PROCESSED (if allowed by domain logic, this should raise an error)
    or try a valid transition from INDEXED (which in our current rules does not allow any further change)
    to verify that invalid transitions are caught.
    """
    # Use the synthetic documents to create a fresh document.
    synthetic_docs: List[DomainDocument] = create_synthetic_documents()
    domain_doc = synthetic_docs[0]  # Pick the first document.
    orm_doc = domain_doc_to_orm_doc(domain_doc)
    db_service.create_document(orm_doc)

    # Attempt an invalid transition: from INDEXED to PROCESSED (not allowed)
    with pytest.raises(ValueError):
        db_service.update_document_status(domain_doc.id, DocumentStatus.PROCESSED)


@measure_time
def test_get_nonexistent_document():
    """
    Test that retrieving a nonexistent document returns None.
    """
    result = db_service.get_document("nonexistent_doc")
    assert result is None


# ----------------------------
# QUERY TESTS
# ----------------------------


@measure_time
def test_bulk_create_queries():
    """
    Test creating multiple Query records using synthetic data.

    Use the synthetic document IDs generated from the synthetic documents.
    """
    # Create synthetic documents first.
    synthetic_docs: List[DomainDocument] = create_synthetic_documents()
    document_ids = [doc.id for doc in synthetic_docs]

    synthetic_queries: List[DomainQuery] = create_synthetic_queries(document_ids)
    created_query_ids = []
    for domain_query in synthetic_queries:
        orm_query = domain_query_to_orm_query(domain_query)
        created_query = db_service.create_query(orm_query)
        created_query_ids.append(created_query.id)
        # Verify that the final status (ANSWERED) is set in the synthetic data.
        assert created_query.status.value == QueryStatus.ANSWERED.value
        # Check that the answer field has been set.
        assert created_query.answer is not None

    all_queries = db_service.list_queries()
    listed_query_ids = [q.id for q in all_queries]
    for qid in created_query_ids:
        assert qid in listed_query_ids


@measure_time
def test_update_query_status_bulk():
    """
    Test updating the status of a synthetic query.

    This verifies that the domain logic for status transitions for queries (e.g.,
    CREATED -> PROCESSED -> INDEXED -> CONTEXT_RETRIEVED -> ANSWERED) is enforced.
    """
    # Create a synthetic query.
    synthetic_queries: List[DomainQuery] = create_synthetic_queries(
        ["doc1", "doc2", "doc3"]
    )
    domain_query = synthetic_queries[0]
    orm_query = domain_query_to_orm_query(domain_query)
    db_service.create_query(orm_query)

    # Attempt to change the status to an invalid transition (for instance, from ANSWERED to PROCESSED)
    # First, update to ANSWERED (synthetic generator does so). Now try changing it back.
    with pytest.raises(ValueError):
        db_service.update_query_status(domain_query.id, QueryStatus.PROCESSED)


@measure_time
def test_get_nonexistent_query():
    """
    Test that retrieving a nonexistent query returns None.
    """
    result = db_service.get_query("nonexistent_query")
    assert result is None


# -----------------------------------------------------------------------------
# Main block for manual test running
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Run each test manually to print timings.
    test_bulk_create_documents()
    test_update_document_status_bulk()
    test_get_nonexistent_document()
    test_bulk_create_queries()
    test_update_query_status_bulk()
    test_get_nonexistent_query()
