from docai.database.models import Document as ORMDocument
from docai.database.models import Query as ORMQuery
from docai.database.schemas import DocumentResponse, QueryResponse
from docai.shared.models.document import Document as DomainDocument
from docai.shared.models.query import Query as DomainQuery

# --- Document Conversion --- #


# def orm_to_domain_document(orm_doc: ORMDocument) -> DomainDocument:
#     """
#     Converts an ORM Document instance to a domain Document instance.

#     Only maps basic fields (id, file_name, timestamps, status, and metadata).
#     Page data is intentionally omitted because the core domain logic does not require it.

#     Args:
#         orm_doc (ORMDocument): An ORM model instance of Document.

#     Returns:
#         DomainDocument: A new domain model instance populated from the ORM model.
#     """
#     domain_doc = DomainDocument(
#         doc_id=orm_doc.id,  # type: ignore
#         file_name=orm_doc.file_name,  # type: ignore
#     )
#     # Copy timestamps
#     domain_doc.created_at = orm_doc.created_at  # type: ignore
#     domain_doc.processed_at = orm_doc.processed_at  # type: ignore
#     domain_doc.indexed_at = orm_doc.indexed_at  # type: ignore
#     domain_doc._status = orm_doc.status  # type: ignore
#     return domain_doc


# def domain_to_orm_document(domain_doc: DomainDocument, orm_doc: ORMDocument) -> None:
#     """
#     Updates an existing ORM Document instance using the corresponding domain Document.

#     Maps the updated fields like status, processed_at, indexed_at, and metadata.

#     Args:
#         domain_doc (DomainDocument): The domain model instance with business logic applied.
#         orm_doc (ORMDocument): The ORM model instance to update.
#     """
#     orm_doc.status = domain_doc.status  # type: ignore
#     orm_doc.processed_at = domain_doc.processed_at  # type: ignore
#     orm_doc.indexed_at = domain_doc.indexed_at  # type: ignore
#     orm_doc.extra = domain_doc.metadata  # type: ignore


def orm_to_response_document(orm_doc: ORMDocument) -> DocumentResponse:
    """
    Converts an ORM Document instance into a DocumentResponse.

    The updated_at field is determined based on whether the document has been indexed or processed,
    and falls back to the creation time if not.

    Args:
        orm_doc (Document): The ORM Document instance.

    Returns:
        DocumentResponse: The API response object.
    """
    updated_at = orm_doc.indexed_at or orm_doc.processed_at or orm_doc.created_at
    return DocumentResponse(
        id=orm_doc.id,  # type: ignore
        status=orm_doc.status,  # type: ignore
        updated_at=updated_at,  # type: ignore
    )


# --- Query Conversion ---#


# def orm_to_domain_query(orm_query: ORMQuery) -> DomainQuery:
#     """
#     Converts an ORM Query instance to a domain Query instance.

#     Maps the essential fields including target document IDs (if stored in extra or as JSON).

#     Args:
#         orm_query (ORMQuery): The ORM model instance of Query.

#     Returns:
#         DomainQuery: A new domain model instance populated from the ORM model.
#     """
#     domain_query = DomainQuery(
#         query_id=orm_query.id,  # type: ignore
#         text=orm_query.text,  # type: ignore
#     )
#     domain_query.created_at = orm_query.created_at  # type: ignore
#     domain_query.processed_at = orm_query.processed_at  # type: ignore
#     domain_query.indexed_at = orm_query.indexed_at  # type: ignore
#     domain_query.context_retrieved_at = orm_query.context_retrieved_at  # type: ignore
#     domain_query.answered_at = orm_query.answered_at  # type: ignore
#     domain_query._status = orm_query.status  # type: ignore

#     return domain_query


# def domain_to_orm_query(domain_query: DomainQuery, orm_query: ORMQuery) -> None:
#     """
#     Updates an existing ORM Query instance using values from the domain Query instance.

#     This includes status, timestamps, metadata, and answer.

#     Args:
#         domain_query (DomainQuery): The domain model with business logic applied.
#         orm_query (ORMQuery): The ORM model instance to update.
#     """
#     orm_query.created_at = domain_query.created_at  # type: ignore
#     orm_query.processed_at = domain_query.processed_at  # type: ignore
#     orm_query.indexed_at = domain_query.indexed_at  # type: ignore
#     orm_query.context_retrieved_at = domain_query.context_retrieved_at  # type: ignore
#     orm_query.answered_at = domain_query.answered_at  # type: ignore
#     orm_query.status = domain_query.status  # type: ignore


def orm_to_response_query(orm_query: ORMQuery) -> QueryResponse:
    """
    Converts an ORM Query instance into a QueryResponse.

    The updated_at field is determined based on the latest timestamp (answered if available,
    then context_retrieved, indexed, processed, or created).

    Args:
        orm_query (ORMQuery): The ORM Query instance.

    Returns:
        QueryResponse: The API response object.
    """
    # Determine updated_at by choosing the most recent timestamp.
    updated_at = (
        orm_query.answered_at
        or orm_query.context_retrieved_at
        or orm_query.indexed_at
        or orm_query.processed_at
        or orm_query.created_at
    )
    return QueryResponse(
        id=orm_query.id,  # type: ignore
        status=orm_query.status,  # type: ignore
        updated_at=updated_at,  # type: ignore
    )
