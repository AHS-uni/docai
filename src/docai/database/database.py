import logging
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text

from docai.database.session import SessionLocal
from docai.database.models import (
    Document as ORMDocument,
    Query as ORMQuery,
    Page as ORMPage,
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Encapsulates all database operations for the DocAI application.

    This service class provides methods for creating, retrieving, updating, and listing
    Document, Page and Query records. Each method manages its own database session and
    handles transactions and error reporting.
    """

    def __init__(self) -> None:
        """
        Initializes the DatabaseService with a session factory.
        """
        self.Session = SessionLocal

    def get_session(self) -> Session:
        """
        Creates and returns a new SQLAlchemy session.

        Returns:
            Session: A new database session instance.
        """
        return self.Session()

    # --- Document CRUD Operations --- #

    def create_document(self, document: ORMDocument) -> ORMDocument:
        """
        Persists a new Document record to the database.

        Args:
            document (ORMDocument): The ORM Document instance to save.

        Returns:
            ORMDocument: The persisted document with any auto-generated fields.
        """
        session: Session = self.get_session()
        try:
            session.add(document)
            session.commit()
            session.refresh(document)
            logger.info("Created document with ID: %s", document.id)
            return document
        except Exception as e:
            session.rollback()
            logger.error("Error creating document: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def get_document(self, doc_id: str) -> Optional[ORMDocument]:
        """
        Retrieves a Document record by its ID.

        Args:
            doc_id (str): The unique identifier for the document.

        Returns:
            Optional[ORMDocument]: The document if found, otherwise None.
        """
        session: Session = self.get_session()
        try:
            document = (
                session.query(ORMDocument).filter(ORMDocument.id == doc_id).first()
            )
            if document:
                logger.info("Retrieved document with ID: %s", doc_id)
            else:
                logger.warning("Document with ID %s not found", doc_id)
            return document
        except Exception as e:
            logger.error("Error retrieving document %s: %s", doc_id, e, exc_info=True)
            raise
        finally:
            session.close()

    def get_documents_by_ids(self, document_ids: List[str]) -> List[ORMDocument]:
        """
        Retrieves Document records that match the provided list of document IDs.

        Args:
            document_ids (List[str]): The list of document IDs to retrieve.

        Returns:
            List[ORMDocument]: A list of matching ORM Document instances.

        Raises:
            ValueError: If one or more document IDs cannot be found.
        """
        session: Session = self.get_session()
        try:
            documents = (
                session.query(ORMDocument)
                .filter(ORMDocument.id.in_(document_ids))
                .all()
            )

            # Validate that the expected documents were found
            found_ids = {doc.id for doc in documents}
            missing_ids = set(document_ids) - found_ids  # type: ignore
            if missing_ids:
                error_message = (
                    f"Documents with IDs {missing_ids} not found in the database."
                )
                logger.error(error_message)
                raise ValueError(error_message)

            return documents
        except Exception as e:
            logger.error("Error fetching documents by IDs: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def list_documents(self) -> List[ORMDocument]:
        """
        Lists all Document records.

        Returns:
            List[ORMDocument]: A list of all Document records.
        """
        session: Session = self.get_session()
        try:
            documents = session.query(ORMDocument).all()
            logger.info("Listed %d documents", len(documents))
            return documents
        except Exception as e:
            logger.error("Error listing documents: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def delete_document(self, doc_id: str) -> None:
        """
        Deletes a Document record (and related pages) by its ID.

        Args:
            doc_id (str): The unique identifier for the document.

        Raises:
            ValueError: If the document is not found.
        """
        session: Session = self.get_session()
        try:
            document = (
                session.query(ORMDocument).filter(ORMDocument.id == doc_id).first()
            )
            if document is None:
                logger.error("Document with ID %s not found for deletion", doc_id)
                raise ValueError("Document not found")
            session.delete(document)
            session.commit()
            logger.info("Deleted document with ID: %s", doc_id)
        except Exception as e:
            session.rollback()
            logger.error("Error deleting document: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    # --- Page Retrieval Operations --- #

    def get_page(self, page_id: str) -> Optional[ORMPage]:
        """
        Retrieves a Page record by its ID.

        Args:
            page_id (str): The unique identifier for the page image.

        Returns:
            Optional[ORMPage]: The page image if found, else None.
        """
        session: Session = self.get_session()
        try:
            page = session.query(ORMPage).filter(ORMPage.id == page_id).first()
            if page:
                logger.info("Retrieved page with ID: %s", page_id)
            else:
                logger.warning("Page with ID %s not found", page_id)
            return page
        except Exception as e:
            logger.error("Error retrieving page %s: %s", page_id, e, exc_info=True)
            raise
        finally:
            session.close()

    def get_pages_by_ids(self, page_ids: List[str]) -> List[ORMPage]:
        """
        Retrieves Page records that match the provided list of page IDs.

        Args:
            page_ids (List[str]): The list of page IDs to retrieve.

        Returns:
            List[ORMPage]: A list of matching ORM Page instances.

        Raises:
            ValueError: If one or more page IDs cannot be found.
        """
        session: Session = self.get_session()
        try:
            pages = session.query(ORMPage).filter(ORMPage.id.in_(page_ids)).all()
            found_ids = {page.id for page in pages}
            missing_ids = set(page_ids) - found_ids  # type: ignore
            if missing_ids:
                error_message = (
                    f"Pages with IDs {missing_ids} not found in the database."
                )
                logger.error(error_message)
                raise ValueError(error_message)
            return pages
        except Exception as e:
            logger.error("Error fetching pages by IDs: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def list_pages(self) -> List[ORMPage]:
        """
        Retrieves all Page records from the database.

        Returns:
            List[ORMPage]: A list of page image records.
        """
        session: Session = self.get_session()
        try:
            pages = session.query(ORMPage).all()
            logger.info("Listed %d pages", len(pages))
            return pages
        except Exception as e:
            logger.error("Error listing pages: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    # --- Query CRUD Operations --- #

    def create_query(self, query: ORMQuery) -> ORMQuery:
        """
        Persists a new Query record to the database.

        Args:
            query (ORMQuery): The ORM Query instance to save.

        Returns:
            ORMQuery: The persisted query with updated fields.
        """
        session: Session = self.get_session()
        try:
            session.add(query)
            session.commit()
            session.refresh(query)
            logger.info("Created query with ID: %s", query.id)
            return query
        except Exception as e:
            session.rollback()
            logger.error("Error creating query: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def get_query(self, query_id: str) -> Optional[ORMQuery]:
        """
        Retrieves a Query record by its ID.

        Args:
            query_id (str): The unique identifier for the query.

        Returns:
            Optional[ORMQuery]: The query record if found, otherwise None.
        """
        session: Session = self.get_session()
        try:
            query = session.query(ORMQuery).filter(ORMQuery.id == query_id).first()
            if query:
                logger.info("Retrieved query with ID: %s", query_id)
            else:
                logger.warning("Query with ID %s not found", query_id)
            return query
        except Exception as e:
            logger.error("Error retrieving query %s: %s", query_id, e, exc_info=True)
            raise
        finally:
            session.close()

    def get_queries_by_ids(self, query_ids: List[str]) -> List[ORMQuery]:
        """
        Fetches ORM Query records that match the provided list of query IDs.

        Args:
            query_ids (List[str]): The list of query IDs to retrieve.

        Returns:
            List[ORMQuery]: A list of matching ORM Query instances.

        Raises:
            ValueError: If one or more query IDs cannot be found.
        """
        session: Session = self.get_session()
        try:
            queries = session.query(ORMQuery).filter(ORMQuery.id.in_(query_ids)).all()
            found_ids = {query.id for query in queries}
            missing_ids = set(query_ids) - found_ids  # type: ignore
            if missing_ids:
                error_message = (
                    f"Queries with IDs {missing_ids} not found in the database."
                )
                logger.error(error_message)
                raise ValueError(error_message)
            return queries
        except Exception as e:
            logger.error("Error fetching queries by IDs: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def list_queries(self) -> List[ORMQuery]:
        """
        Lists all Query records.

        Returns:
            List[ORMQuery]: A list of all Query records.
        """
        session: Session = self.get_session()
        try:
            queries = session.query(ORMQuery).all()
            logger.info("Listed %d queries", len(queries))
            return queries
        except Exception as e:
            logger.error("Error listing queries: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    def delete_query(self, query_id: str) -> None:
        """
        Deletes a Query record by its ID.

        Args:
            query_id (str): The unique identifier for the query.

        Raises:
            ValueError: If the query is not found.
        """
        session: Session = self.get_session()
        try:
            query = session.query(ORMQuery).filter(ORMQuery.id == query_id).first()
            if query is None:
                logger.error("Query with ID %s not found for deletion", query_id)
                raise ValueError("Query not found")
            session.delete(query)
            session.commit()
            logger.info("Deleted query with ID: %s", query_id)
        except Exception as e:
            session.rollback()
            logger.error("Error deleting query: %s", e, exc_info=True)
            raise
        finally:
            session.close()

    # --- Raw SQL Operations ---#

    def execute_raw_sql(
        self, sql_query: str, params: Optional[dict] = None
    ) -> List[Any]:
        """
        Executes a raw SQL query and returns the result.

        This function allows executing arbitrary SQL commands for flexibility (e.g., advanced reporting).

        Args:
            sql_query (str): The raw SQL query to execute.
            params (Optional[dict]): Optional dictionary of parameters to bind to the query.

        Returns:
            List[Any]: A list of rows resulting from the query.
        """
        session: Session = self.get_session()
        try:
            result = session.execute(text(sql_query), params).fetchall()
            logger.info("Executed raw SQL query")
            return result  # type: ignore
        except Exception as e:
            logger.error("Error executing raw SQL query: %s", e, exc_info=True)
            raise
        finally:
            session.close()
