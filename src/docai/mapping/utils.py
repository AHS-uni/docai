import logging
from typing import List

from docai.database.models import Query as ORMQuery
from docai.database.database import DatabaseService

logger = logging.getLogger(__name__)


def link_documents_to_query(
    db_service: DatabaseService, orm_query: ORMQuery, document_ids: List[str]
) -> ORMQuery:
    """
    Associates ORM Document instances with the provided ORM Query using the
    DatabaseService to retrieve the documents by their IDs.

    Args:
        db_service (DatabaseService): The database service used for fetching documents.
        orm_query (ORMQuery): The ORM Query instance to be updated.
        document_ids (List[str]): A list of document IDs to link to the query.
        session (Optional[Session], optional): An optional SQLAlchemy session to be passed to the
            DatabaseService. If None, the DatabaseService will manage its own session.

    Returns:
        ORMQuery: The updated ORM Query instance with the associated documents.

    Raises:
        ValueError: If one or more of the specified document IDs do not correspond to an existing document.
        Exception: Propagates any unexpected errors encountered during document retrieval or linking.
    """
    try:
        documents = db_service.get_documents_by_ids(document_ids)

        orm_query.documents = documents
        logger.info(
            "Linked %d document(s) to Query with ID: %s", len(documents), orm_query.id
        )

        return orm_query
    except Exception as e:
        logger.error(
            "Error linking documents to query with ID %s: %s",
            orm_query.id,
            e,
            exc_info=True,
        )
        raise
