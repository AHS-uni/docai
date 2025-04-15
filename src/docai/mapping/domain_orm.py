import logging

from docai.models.document import (
    Document as DomainDocument,
    Page as DomainPage,
)
from docai.models.query import Query as DomainQuery
from docai.database.models import (
    Document as ORMDocument,
    Page as ORMPage,
    Query as ORMQuery,
)
from docai.database.database import DatabaseService
from docai.mapping.utils import link_documents_to_query


logger = logging.getLogger(__name__)


# --- Domain to ORM Conversions --- #


def domain_page_to_orm(domain_page: DomainPage, orm_document: ORMDocument) -> ORMPage:
    """
        Convert a Domain Page instance to an ORM Page instance, associating it with the given ORM Document.

    Args:
        domain_page (DomainPage): The domain Page to convert.
        orm_document (ORMDocument): The parent ORM Document to associate with.

    Returns:
        ORMPage: The corresponding ORM Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        orm_page = ORMPage(
            id=domain_page.id,
            page_number=domain_page.page_number,
            image_path=domain_page.image_path,
            document=orm_document,  # Establish the relationship.
        )
        return orm_page
    except Exception as e:
        logger.error(
            "Failed to map domain Page (id: %s) to ORM Page: %s", domain_page.id, e
        )
        raise ValueError(
            f"Error mapping Domain Page (id: {domain_page.id}) to ORM Page"
        ) from e


def domain_document_to_orm(domain_doc: DomainDocument) -> ORMDocument:
    """
    Convert a Domain Document instance to an ORM Document instance.

    Args:
        domain_doc (DomainDocument): The domain Document to convert.

    Returns:
        ORMDocument: The corresponding ORM Document instance.

    Raises:
        ValueError: If required fields are missing or data types are incompatible.
    """
    try:
        orm_doc = ORMDocument(
            id=domain_doc.id,
            file_name=domain_doc.file_name,
            created_at=domain_doc.created_at,
            processed_at=domain_doc.processed_at,
            indexed_at=domain_doc.indexed_at,
            status=domain_doc.status,
            extra=domain_doc.metadata,
        )
        # Map nested Page objects.
        orm_doc.pages = [domain_page_to_orm(page, orm_doc) for page in domain_doc.pages]
        return orm_doc
    except Exception as e:
        logger.error("Failed to map domain Document to ORM Document: %s", e)
        raise ValueError(
            f"Error mapping Domain Document (id: {domain_doc.id}) to ORM Document"
        ) from e


def domain_query_to_orm(
    domain_query: DomainQuery, db_service: DatabaseService
) -> ORMQuery:
    """
    Convert a Domain Query instance to an ORM Query instance.

    Args:
        domain_query (DomainQuery): The domain Query to convert.
        db_service (DatabaseService): The database service used for document retrieval
                                      and linking.

    Returns:
        ORMQuery: The corresponding ORM Query instance with related documents linked.

    Raises:
        ValueError: If required fields are missing, data types are incompatible, or if linked
                    documents cannot be found.
    """
    try:
        orm_query = ORMQuery(
            id=domain_query.id,
            text=domain_query.text,
            created_at=domain_query.created_at,
            processed_at=domain_query.processed_at,
            indexed_at=domain_query.indexed_at,
            context_retrieved_at=domain_query.context_retrieved_at,
            answered_at=domain_query.answered_at,
            status=domain_query.status,
            extra=domain_query.metadata,
            answer=domain_query.answer,
        )
        orm_query = link_documents_to_query(
            db_service, orm_query, domain_query.target_document_ids
        )
        return orm_query
    except Exception as e:
        logger.error(
            "Failed to map Domain Query (id: %s) to ORM Query: %s",
            domain_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Error mapping Domain Query (id: {domain_query.id}) to ORM Query"
        ) from e


# --- ORM to Domain Conversions --- #


def orm_page_to_domain(orm_page: ORMPage) -> DomainPage:
    """
    Convert an ORM Page instance to a Domain Page instance.

    Args:
        orm_page (ORMPage): The ORM Page to convert.

    Returns:
        DomainPage: The corresponding Domain Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        domain_page = DomainPage(
            page_id=orm_page.id,  # type: ignore
            page_number=orm_page.page_number,  # type: ignore
            image_path=orm_page.image_path,  # type: ignore
        )
        return domain_page
    except Exception as e:
        logger.error(
            "Failed to map ORM Page (id: %s) to Domain Page: %s", orm_page.id, e
        )
        raise ValueError(
            f"Error mapping ORM Page (id: {orm_page.id}) to Domain Page"
        ) from e


def orm_document_to_domain(orm_doc: ORMDocument) -> DomainDocument:
    """
    Convert an ORM Document instance to a Domain Document instance.

    Args:
        orm_doc (ORMDocument): The ORM Document to convert.

    Returns:
        DomainDocument: The corresponding Domain Document instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        domain_doc = DomainDocument(
            doc_id=orm_doc.id,  # type: ignore
            file_name=orm_doc.file_name,  # type: ignore
            pages=[orm_page_to_domain(page) for page in orm_doc.pages],
            metadata=orm_doc.extra,  # type: ignore
        )
        # Update timestamps.
        domain_doc.created_at = orm_doc.created_at  # type: ignore
        domain_doc.processed_at = orm_doc.processed_at  # type: ignore
        domain_doc.indexed_at = orm_doc.indexed_at  # type: ignore
        # Set the internal status directly to bypass the setter logic.
        domain_doc._status = orm_doc.status  # type: ignore
        return domain_doc
    except Exception as e:
        logger.error(
            "Failed to map ORM Document (id: %s) to Domain Document: %s", orm_doc.id, e
        )
        raise ValueError(
            f"Error mapping ORM Document (id: {orm_doc.id}) to Domain Document"
        ) from e


def orm_query_to_domain(orm_query: ORMQuery) -> DomainQuery:
    """
    Convert an ORM Query instance to a Domain Query instance.

    Args:
        orm_query (ORMQuery): The ORM Query instance to convert.

    Returns:
        DomainQuery: The corresponding Domain Query instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        domain_query = DomainQuery(
            query_id=orm_query.id,  # type: ignore
            text=orm_query.text,  # type: ignore
            target_document_ids=[doc.id for doc in orm_query.documents],
            metadata=orm_query.extra,  # type: ignore
        )
        # Update timestamps.
        domain_query.created_at = orm_query.created_at  # type: ignore
        domain_query.processed_at = orm_query.processed_at  # type: ignore
        domain_query.indexed_at = orm_query.indexed_at  # type: ignore
        domain_query.context_retrieved_at = orm_query.context_retrieved_at  # type: ignore
        domain_query.answered_at = orm_query.answered_at  # type: ignore
        # Set the internal status directly.
        domain_query._status = orm_query.status  # type: ignore
        domain_query.answer = orm_query.answer  # type: ignore
        return domain_query
    except Exception as e:
        logger.error(
            "Failed to map ORM Query (id: %s) to Domain Query: %s", orm_query.id, e
        )
        raise ValueError(
            f"Error mapping ORM Query (id: {orm_query.id}) to Domain Query"
        ) from e
