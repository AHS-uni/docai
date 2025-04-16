import unittest
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

# Import domain models
from docai.models.document import Document as DomainDocument, MinimalDocument as DomainMinimalDocument, Page as DomainPage
from docai.models.query import Query as DomainQuery, MinimalQuery as DomainMinimalQuery

# Import DTO models (assumed in docai.database.schemas)
from docai.database.schemas import (
    Document as DTODocument,
    MinimalDocument as DTOMinimalDocument,
    Page as DTOPage,
    Query as DTOQuery,
    MinimalQuery as DTOMinimalQuery,
)

# Import ORM models (assumed in docai.database.models)
from docai.database.models import Document as ORMDocument, Page as ORMPage, Query as ORMQuery

# Import the mapping functions from the module
from docai.mapping import domain_dto, domain_orm, orm_dto, utils

# Sample synthetic data for testing
def create_sample_domain_page():
    return DomainPage(
        id="page_001",
        page_number=1,
        image_path="/fake/path/page1.jpg"
    )

def create_sample_domain_document():
    page = create_sample_domain_page()
    doc = DomainDocument(
        doc_id="doc_001",
        file_name="sample.pdf",
        pages=[page],
        metadata={"key": "value"}
    )
    # Set sample timestamps and status manually for testing.
    doc.created_at = datetime(2025, 4, 10, 12, 0, 0, tzinfo=timezone.utc)
    doc.processed_at = datetime(2025, 4, 11, 9, 30, 0, tzinfo=timezone.utc)
    doc.indexed_at = datetime(2025, 4, 11, 10, 0, 0, tzinfo=timezone.utc)
    return doc

def create_sample_domain_query():
    doc = create_sample_domain_document()
    query = DomainQuery(
        query_id="query_001",
        text="Find sample document",
        target_document_ids=[doc.id],
        metadata={"priority": "high"}
    )
    query.created_at = datetime(2025, 4, 10, 12, 0, 0, tzinfo=timezone.utc)
    query.processed_at = datetime(2025, 4, 10, 12, 30, 0, tzinfo=timezone.utc)
    query.indexed_at = datetime(2025, 4, 10, 12, 45, 0, tzinfo=timezone.utc)
    query.context_retrieved_at = datetime(2025, 4, 10, 12, 50, 0, tzinfo=timezone.utc)
    query.answered_at = datetime(2025, 4, 10, 13, 0, 0, tzinfo=timezone.utc)
    return query

class TestDomainDTOConversions(unittest.TestCase):
    """Unit tests for domain_dto.py conversion functions."""

    def test_domain_to_dto_page(self):
        domain_page = create_sample_domain_page()
        dto_page = domain_dto.domain_to_dto_page(domain_page)
        self.assertEqual(dto_page.id, domain_page.id)
        self.assertEqual(dto_page.page_number, domain_page.page_number)
        self.assertEqual(dto_page.image_path, domain_page.image_path)

    def test_domain_to_dto_document(self):
        domain_doc = create_sample_domain_document()
        dto_doc = domain_dto.domain_to_dto_document(domain_doc)
        self.assertEqual(dto_doc.id, domain_doc.id)
        self.assertEqual(dto_doc.file_name, domain_doc.file_name)
        self.assertEqual(dto_doc.status, domain_doc.status)
        self.assertEqual(dto_doc.metadata, domain_doc.metadata)
        self.assertEqual(len(dto_doc.pages), len(domain_doc.pages))

    def test_domain_to_dto_minimal_document(self):
        domain_doc = create_sample_domain_document()
        # For minimal conversion, we assume the Domain object has a method to_minimal that creates a minimal object.
        # Here we simulate it by directly constructing a DomainMinimalDocument.
        minimal_domain_doc = DomainMinimalDocument(
            id=domain_doc.id,
            status=domain_doc.status,
            updated_at=domain_doc.indexed_at or domain_doc.processed_at or domain_doc.created_at
        )
        dto_min_doc = domain_dto.domain_to_dto_minimal_document(minimal_domain_doc)
        self.assertEqual(dto_min_doc.id, minimal_domain_doc.id)
        self.assertEqual(dto_min_doc.status, minimal_domain_doc.status)
        self.assertEqual(dto_min_doc.updated_at, minimal_domain_doc.updated_at)

    def test_domain_to_dto_query(self):
        domain_query = create_sample_domain_query()
        dto_query = domain_dto.domain_to_dto_query(domain_query)
        self.assertEqual(dto_query.id, domain_query.id)
        self.assertEqual(dto_query.text, domain_query.text)
        self.assertEqual(dto_query.target_document_ids, domain_query.target_document_ids)
        self.assertEqual(dto_query.metadata, domain_query.metadata)
        self.assertEqual(dto_query.status, domain_query.status)

    def test_domain_to_dto_minimal_query(self):
        domain_query = create_sample_domain_query()
        minimal_domain_query = DomainMinimalQuery(
            id=domain_query.id,
            status=domain_query._status,
            updated_at=domain_query.answered_at or domain_query.created_at
        )
        dto_min_query = domain_dto.domain_to_dto_minimal_query(minimal_domain_query)
        self.assertEqual(dto_min_query.id, minimal_domain_query.id)
        self.assertEqual(dto_min_query.status, minimal_domain_query.status)
        self.assertEqual(dto_min_query.updated_at, minimal_domain_query.updated_at)

    # Additional tests (DTO to Domain conversions) can be similarly structured.
    def test_dto_to_domain_page(self):
        # Create DTO object mimicking DTOPage
        dto_page = DTOPage(id="dto_page_001", page_number=1, image_path="/fake/path/page1.jpg")
        domain_page = domain_dto.dto_to_domain_page(dto_page)
        self.assertEqual(domain_page.id if hasattr(domain_page, "id") else domain_page.page_id, dto_page.id)
        self.assertEqual(domain_page.page_number, dto_page.page_number)
        self.assertEqual(domain_page.image_path, dto_page.image_path)

    def test_dto_to_domain_document(self):
        # Create synthetic DTO Document with one page
        dto_page = DTOPage(id="dto_page_001", page_number=1, image_path="/fake/path/page1.jpg")
        dto_doc = DTODocument(
            id="dto_doc_001",
            file_name="dto_sample.pdf",
            status="processed",  # Enum represented as string for testing
            metadata={"key": "value"},
            created_at=datetime(2025, 4, 10, 12, 0, 0, tzinfo=timezone.utc),
            processed_at=datetime(2025, 4, 11, 9, 30, 0, tzinfo=timezone.utc),
            indexed_at=datetime(2025, 4, 11, 10, 0, 0, tzinfo=timezone.utc),
            pages=[dto_page]
        )
        domain_doc = domain_dto.dto_to_domain_document(dto_doc)
        self.assertEqual(domain_doc.id if hasattr(domain_doc, "id") else domain_doc.doc_id, dto_doc.id)
        self.assertEqual(domain_doc.file_name, dto_doc.file_name)
        self.assertEqual(len(domain_doc.pages), 1)

    def test_dto_to_domain_minimal_document(self):
        dto_min_doc = DTOMinimalDocument(
            id="dto_doc_001",
            status="processed",  # Using string to simulate enum conversion
            updated_at=datetime(2025, 4, 11, 10, 0, 0, tzinfo=timezone.utc)
        )
        domain_min_doc = domain_dto.dto_to_domain_minimal_document(dto_min_doc)
        self.assertEqual(domain_min_doc.id, dto_min_doc.id)
        self.assertEqual(domain_min_doc.status, dto_min_doc.status)
        self.assertEqual(domain_min_doc.updated_at, dto_min_doc.updated_at)

    def test_dto_to_domain_query(self):
        dto_query = DTOQuery(
            id="dto_query_001",
            text="Find sample",
            target_document_ids=["doc_001"],
            metadata={"priority": "high"},
            answer="Result",
            created_at=datetime(2025, 4, 10, 12, 0, 0, tzinfo=timezone.utc),
            processed_at=datetime(2025, 4, 10, 12, 30, 0, tzinfo=timezone.utc),
            indexed_at=datetime(2025, 4, 10, 12, 45, 0, tzinfo=timezone.utc),
            context_retrieved_at=datetime(2025, 4, 10, 12, 50, 0, tzinfo=timezone.utc),
            answered_at=datetime(2025, 4, 10, 13, 0, 0, tzinfo=timezone.utc),
            status="answered"
        )
        domain_query = domain_dto.dto_to_domain_query(dto_query)
        self.assertEqual(domain_query.id if hasattr(domain_query, "id") else domain_query.query_id, dto_query.id)
        self.assertEqual(domain_query.text, dto_query.text)
        self.assertEqual(domain_query.target_document_ids, dto_query.target_document_ids)

    def test_dto_to_domain_minimal_query(self):
        dto_min_query = DTOMinimalQuery(
            id="dto_query_001",
            status="answered",
            updated_at=datetime(2025, 4, 10, 13, 0, 0, tzinfo=timezone.utc)
        )
        domain_min_query = domain_dto.dto_to_domain_minimal_query(dto_min_query)
        self.assertEqual(domain_min_query.id, dto_min_query.id)
        self.assertEqual(domain_min_query.status, dto_min_query.status)
        self.assertEqual(domain_min_query.updated_at, dto_min_query.updated_at)

class TestUtilsLinkDocumentsToQuery(unittest.TestCase):
    """Unit tests for the link_documents_to_query function in utils.py."""

    def setUp(self):
        # Create synthetic ORM Query and fake DatabaseService
        self.orm_query = ORMQuery()
        self.orm_query.id = "orm_query_001"
        # For simplicity, we simulate ORM Query.documents as an empty list initially.
        self.orm_query.documents = []
        # Create a fake DatabaseService that returns synthetic documents
        self.db_service = MagicMock(spec=DatabaseService)
        # Create a synthetic list of ORM Document objects
        fake_doc = ORMDocument()
        fake_doc.id = "doc_001"
        self.fake_documents = [fake_doc]
        self.db_service.get_documents_by_ids.return_value = self.fake_documents

    def test_link_documents_to_query_success(self):
        # Call the linking function with a list of document IDs
        updated_query = utils.link_documents_to_query(self.db_service, self.orm_query, ["doc_001"])
        self.assertEqual(len(updated_query.documents), 1)
        self.assertEqual(updated_query.documents[0].id, "doc_001")
        self.db_service.get_documents_by_ids.assert_called_once_with(["doc_001"])

    def test_link_documents_to_query_failure(self):
        # Simulate failure by having the database service raise an exception.
        self.db_service.get_documents_by_ids.side_effect = ValueError("Document not found")
        with self.assertRaises(ValueError):
            utils.link_documents_to_query(self.db_service, self.orm_query, ["doc_missing"])

if __name__ == "__main__":
    unittest.main()