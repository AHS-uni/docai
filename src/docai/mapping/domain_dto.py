import logging

from docai.models.document import (
    Document as DomainDocument,
    MinimalDocument as DomainMinimalDocument,
    Page as DomainPage,
)
from docai.models.query import Query as DomainQuery, MinimalQuery as DomainMinimalQuery
from docai.database.schemas import (
    Document as DTODocument,
    MinimalDocument as DTOMinimalDocument,
    Page as DTOPage,
    Query as DTOQuery,
    MinimalQuery as DTOMinimalQuery,
)

logger = logging.getLogger(__name__)

# --- Domain to DTO Conversions --- #


def domain_to_dto_page(domain_page: DomainPage) -> DTOPage:
    """
    Convert a Domain Page instance to a DTO Page instance.

    Args:
        domain_page (DomainPage): The domain Page to convert.

    Returns:
        DTOPage: The converted DTO Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        dto_page = DTOPage(
            id=domain_page.id,
            page_number=domain_page.page_number,
            image_path=domain_page.image_path,
        )
        return dto_page
    except Exception as e:
        logger.error(
            "Error converting Domain Page (id: %s) to DTO: %s",
            domain_page.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for Domain Page (id: {domain_page.id})"
        ) from e


def domain_to_dto_document(domain_doc: DomainDocument) -> DTODocument:
    """
    Convert a Domain Document instance to a full DTO Document instance.

    Args:
        domain_doc (DomainDocument): The domain Document to convert.

    Returns:
        DTODocument: The converted DTO Document containing full details.

    Raises:
        ValueError: If required fields are missing or conversion fails.
    """
    try:
        dto_doc = DTODocument(
            id=domain_doc.id,
            file_name=domain_doc.file_name,
            status=domain_doc.status,  # Assumes the enum values are compatible.
            metadata=domain_doc.metadata,
            created_at=domain_doc.created_at,
            processed_at=domain_doc.processed_at,
            indexed_at=domain_doc.indexed_at,
            pages=[domain_to_dto_page(page) for page in domain_doc.pages],
        )
        return dto_doc
    except Exception as e:
        logger.error(
            "Error converting Domain Document (id: %s) to DTO: %s",
            domain_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for Domain Document (id: {domain_doc.id})"
        ) from e


def domain_to_dto_minimal_document(
    domain_min_doc: DomainMinimalDocument,
) -> DTOMinimalDocument:
    """
    Convert a Domain MinimalDocument instance to a DTO MinimalDocument instance.

    Args:
        domain_min_doc (DomainMinimalDocument): The minimal representation of the document from the domain layer.

    Returns:
        DTOMinimalDocument: The corresponding DTO MinimalDocument instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        dto_min_doc = DTOMinimalDocument(
            id=domain_min_doc.id,
            status=domain_min_doc.status,
            updated_at=domain_min_doc.updated_at,
        )
        return dto_min_doc
    except Exception as e:
        logger.error(
            "Error converting Domain MinimalDocument (id: %s) to DTO: %s",
            domain_min_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for Domain MinimalDocument (id: {domain_min_doc.id})"
        ) from e


def domain_to_dto_query(domain_query: DomainQuery) -> DTOQuery:
    """
    Convert a Domain Query instance to a full DTO Query instance.

    Args:
        domain_query (DomainQuery): The domain Query to convert.

    Returns:
        DTOQuery: The converted DTO Query instance.

    Raises:
        ValueError: If required fields are missing or conversion fails.
    """
    try:
        dto_query = DTOQuery(
            id=domain_query.id,
            text=domain_query.text,
            target_document_ids=domain_query.target_document_ids,
            metadata=domain_query.metadata,
            answer=domain_query.answer,
            created_at=domain_query.created_at,
            processed_at=domain_query.processed_at,
            indexed_at=domain_query.indexed_at,
            context_retrieved_at=domain_query.context_retrieved_at,
            answered_at=domain_query.answered_at,
            status=domain_query.status,
        )
        return dto_query
    except Exception as e:
        logger.error(
            "Error converting Domain Query (id: %s) to DTO: %s",
            domain_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for Domain Query (id: {domain_query.id})"
        ) from e


def domain_to_dto_minimal_query(
    domain_min_query: DomainMinimalQuery,
) -> DTOMinimalQuery:
    """
    Convert a Domain MinimalQuery instance to a DTO MinimalQuery instance.

    Args:
        domain_min_query (DomainMinimalQuery): The minimal representation of the query from the domain layer.

    Returns:
        DTOMinimalQuery: The corresponding DTO MinimalQuery instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        dto_min_query = DTOMinimalQuery(
            id=domain_min_query.id,
            status=domain_min_query.status,
            updated_at=domain_min_query.updated_at,
        )
        return dto_min_query
    except Exception as e:
        logger.error(
            "Error converting Domain MinimalQuery (id: %s) to DTO: %s",
            domain_min_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for Domain MinimalQuery (id: {domain_min_query.id})"
        ) from e


# --- DTO to Domain Conversions --- #


def dto_to_domain_page(dto_page: DTOPage) -> DomainPage:
    """
    Convert a DTO Page instance back to a Domain Page instance.

    Args:
        dto_page (DTOPage): The DTO Page to convert.

    Returns:
        DomainPage: The corresponding Domain Page instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        domain_page = DomainPage(
            page_id=dto_page.id,
            page_number=dto_page.page_number,
            image_path=dto_page.image_path,
        )
        return domain_page
    except Exception as e:
        logger.error(
            "Error converting DTO Page (id: %s) to Domain: %s",
            dto_page.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for DTO Page (id: {dto_page.id})") from e


def dto_to_domain_document(dto_doc: DTODocument) -> DomainDocument:
    """
    Convert a full DTO Document instance back to a Domain Document instance.

    Args:
        dto_doc (DTODocument): The DTO Document to convert.

    Returns:
        DomainDocument: The corresponding Domain Document instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        domain_doc = DomainDocument(
            doc_id=dto_doc.id,
            file_name=dto_doc.file_name,
            pages=[dto_to_domain_page(page) for page in dto_doc.pages],
            metadata=dto_doc.metadata,
        )
        domain_doc.created_at = dto_doc.created_at
        domain_doc.processed_at = dto_doc.processed_at
        domain_doc.indexed_at = dto_doc.indexed_at
        # Assuming that the domain model has an attribute for status that can be directly set.
        domain_doc._status = dto_doc.status  # Bypass any setter logic if necessary.
        return domain_doc
    except Exception as e:
        logger.error(
            "Error converting DTO Document (id: %s) to Domain: %s",
            dto_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for DTO Document (id: {dto_doc.id})"
        ) from e


def dto_to_domain_minimal_document(
    dto_min_doc: DTOMinimalDocument,
) -> DomainMinimalDocument:
    """
    Convert a DTO MinimalDocument instance to a Domain MinimalDocument instance.

    Args:
        dto_min_doc (DTOMinimalDocument): The minimal DTO representation of a document.

    Returns:
        DomainMinimalDocument: The corresponding Domain MinimalDocument instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        domain_min_doc = DomainMinimalDocument(
            id=dto_min_doc.id,
            status=dto_min_doc.status,
            updated_at=dto_min_doc.updated_at,
        )
        return domain_min_doc
    except Exception as e:
        logger.error(
            "Error converting DTO MinimalDocument (id: %s) to Domain: %s",
            dto_min_doc.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for DTO MinimalDocument (id: {dto_min_doc.id})"
        ) from e


def dto_to_domain_query(dto_query: DTOQuery) -> DomainQuery:
    """
    Convert a full DTO Query instance back to a Domain Query instance.

    Args:
        dto_query (DTOQuery): The DTO Query to convert.

    Returns:
        DomainQuery: The corresponding Domain Query instance.

    Raises:
        ValueError: If conversion fails due to missing or incompatible data.
    """
    try:
        domain_query = DomainQuery(
            query_id=dto_query.id,
            text=dto_query.text,
            target_document_ids=dto_query.target_document_ids,
            metadata=dto_query.metadata,
        )
        domain_query.created_at = dto_query.created_at
        domain_query.processed_at = dto_query.processed_at
        domain_query.indexed_at = dto_query.indexed_at
        domain_query.context_retrieved_at = dto_query.context_retrieved_at
        domain_query.answered_at = dto_query.answered_at
        domain_query._status = dto_query.status  # Bypass setter if necessary.
        domain_query.answer = dto_query.answer
        return domain_query
    except Exception as e:
        logger.error(
            "Error converting DTO Query (id: %s) to Domain: %s",
            dto_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(f"Conversion failed for DTO Query (id: {dto_query.id})") from e


def dto_to_domain_minimal_query(dto_min_query: DTOMinimalQuery) -> DomainMinimalQuery:
    """
    Convert a DTO MinimalQuery instance to a Domain MinimalQuery instance.

    Args:
        dto_min_query (DTOMinimalQuery): The minimal DTO representation of a query.

    Returns:
        DomainMinimalQuery: The corresponding Domain MinimalQuery instance.

    Raises:
        ValueError: If conversion fails due to missing or invalid fields.
    """
    try:
        domain_min_query = DomainMinimalQuery(
            id=dto_min_query.id,
            status=dto_min_query.status,
            updated_at=dto_min_query.updated_at,
        )
        return domain_min_query
    except Exception as e:
        logger.error(
            "Error converting DTO MinimalQuery (id: %s) to Domain: %s",
            dto_min_query.id,
            e,
            exc_info=True,
        )
        raise ValueError(
            f"Conversion failed for DTO MinimalQuery (id: {dto_min_query.id})"
        ) from e
