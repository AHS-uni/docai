import logging
from typing import List

from docai.database.models import (
    Document as ORMDocument,
    Page as ORMPage,
    Query as ORMQuery,
)
from docai.database.schemas import (
    Document as DTODocument,
    Page as DTOPage,
    Query as DTOQuery,
)
from docai.database.database import DatabaseService
from docai.mapping.utils import link_documents_to_query

logger = logging.getLogger(__name__)


# --- ORM to DTO Conversions --- #


def orm_to_dto_page(orm_page: ORMPage) -> DTOPage:
    """
    Convert an ORM Page instance to a DTO Page instance.

    Args:
        orm_page (ORMPage): The ORM Page to convert.

    Returns:
        DTOPage: The resulting DTO Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        dto_page = DTOPage(
            id=orm_page.id,  # type: ignore
            page_number=orm_page.page_number,  # type: ignore
            image_path=orm_page.image_path,  # type: ignore
        )
        return dto_page
    except Exception as e:
        logger.error(
            "Error converting ORM Page (id: %s) to DTO: %s",
            orm_page.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for ORM Page (id: {orm_page.id})") from e


def orm_to_dto_document(orm_doc: ORMDocument) -> DTODocument:
    """
    Convert an ORM Document instance to a full DTO Document instance.

    Args:
        orm_doc (ORMDocument): The ORM Document to convert.

    Returns:
        DTODocument: The resulting DTO Document with all fields mapped.

    Raises:
        ValueError: If conversion fails due to missing or incompatible fields.
    """
    try:
        dto_pages: List[DTOPage] = [orm_to_dto_page(page) for page in orm_doc.pages]  # type: ignore
        dto_doc = DTODocument(
            id=orm_doc.id,  # type: ignore
            file_name=orm_doc.file_name,  # type: ignore
            status=orm_doc.status,  # type: ignore
            metadata=orm_doc.extra,  # type: ignore
            created_at=orm_doc.created_at,  # type: ignore
            processed_at=orm_doc.processed_at,  # type: ignore
            indexed_at=orm_doc.indexed_at,  # type: ignore
            pages=dto_pages,
        )
        return dto_doc
    except Exception as e:
        logger.error(
            "Error converting ORM Document (id: %s) to DTO: %s",
            orm_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for ORM Document (id: {orm_doc.id})"
        ) from e


def orm_to_dto_query(orm_query: ORMQuery) -> DTOQuery:
    """
    Convert an ORM Query instance to a full DTO Query instance.

    Args:
        orm_query (ORMQuery): The ORM Query to convert.

    Returns:
        DTOQuery: The resulting DTO Query instance with all fields mapped.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        dto_query = DTOQuery(
            id=orm_query.id,  # type: ignore
            text=orm_query.text,  # type: ignore
            target_document_ids=[doc.id for doc in orm_query.documents],  # type: ignore
            metadata=orm_query.extra,  # type: ignore
            answer=orm_query.answer,  # type: ignore
            created_at=orm_query.created_at,  # type: ignore
            processed_at=orm_query.processed_at,  # type: ignore
            indexed_at=orm_query.indexed_at,  # type: ignore
            context_retrieved_at=orm_query.context_retrieved_at,  # type: ignore
            answered_at=orm_query.answered_at,  # type: ignore
            status=orm_query.status,  # type: ignore
        )
        return dto_query
    except Exception as e:
        logger.error(
            "Error converting ORM Query (id: %s) to DTO: %s",
            orm_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for ORM Query (id: {orm_query.id})") from e


# --- DTO to ORM Conversions --- #


def dto_to_orm_document(dto_doc: DTODocument) -> ORMDocument:
    """
    Convert a full DTO Document instance to an ORM Document instance.

    Args:
        dto_doc (DTODocument): The DTO Document to convert.

    Returns:
        ORMDocument: The resulting ORM Document instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible fields.
    """
    try:
        # Map pages from DTO to ORM using dto_to_orm_page
        orm_pages: List[ORMPage] = [dto_to_orm_page(page) for page in dto_doc.pages]
        orm_doc = ORMDocument(
            id=dto_doc.id,
            file_name=dto_doc.file_name,
            created_at=dto_doc.created_at,
            processed_at=dto_doc.processed_at,
            indexed_at=dto_doc.indexed_at,
            status=dto_doc.status,
            extra=dto_doc.metadata,
        )
        # Establish the one-to-many relationship for pages.
        orm_doc.pages = orm_pages
        return orm_doc
    except Exception as e:
        logger.error(
            "Error converting DTO Document (id: %s) to ORM: %s",
            dto_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for DTO Document (id: {dto_doc.id})"
        ) from e


def dto_to_orm_page(dto_page: DTOPage) -> ORMPage:
    """
    Convert a DTO Page instance to an ORM Page instance.

    Args:
        dto_page (DTOPage): The DTO Page to convert.

    Returns:
        ORMPage: The resulting ORM Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        orm_page = ORMPage(
            id=dto_page.id,
            page_number=dto_page.page_number,
            image_path=dto_page.image_path,
        )
        return orm_page
    except Exception as e:
        logger.error(
            "Error converting DTO Page (id: %s) to ORM: %s",
            dto_page.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for DTO Page (id: {dto_page.id})") from e


def dto_to_orm_query(dto_query: DTOQuery, db_service: DatabaseService) -> ORMQuery:
    """
    Convert a full DTO Query instance to an ORM Query instance.

    Args:
        dto_query (DTOQuery): The DTO Query to convert.
        db_service (DatabaseService): The database service used for document retrieval
                                      and linking.

    Returns:
        ORMQuery: The resulting ORM Query instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        orm_query = ORMQuery(
            id=dto_query.id,
            text=dto_query.text,
            created_at=dto_query.created_at,
            processed_at=dto_query.processed_at,
            indexed_at=dto_query.indexed_at,
            context_retrieved_at=dto_query.context_retrieved_at,
            answered_at=dto_query.answered_at,
            status=dto_query.status,
            extra=dto_query.metadata,
            answer=dto_query.answer,
        )
        if db_service is not None:
            orm_query = link_documents_to_query(
                db_service, orm_query, dto_query.target_document_ids
            )
        return orm_query
    except Exception as e:
        logger.error(
            "Error converting DTO Query (id: %s) to ORM: %s",
            dto_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for DTO Query (id: {dto_query.id})") from e
