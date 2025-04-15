import logging
from typing import List, Optional, Any

from fastapi import FastAPI, HTTPException, Query

from docai.database.database import DatabaseService
from docai.database.schemas import (
    DocumentResponse,
    QueryResponse,
    ErrorResponse,
    SQLQueryResponse,
)
from docai.database.utils import orm_to_response_document, orm_to_response_query

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Database Service",
    description="API endpoints to manage documents and queries in the DocAI system.",
    version="1.0.0",
)

db_service = DatabaseService()

# --- Document Related Endpoints --- #


@app.get(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_document(doc_id: str):
    """
    Retrieve a document by its ID.

    Args:
        doc_id (str): Unique identifier for the document.

    Returns:
        DocumentResponse: The document response containing its ID, status, and update timestamp.

    Raises:
        HTTPException: If the document is not found.
    """
    try:
        doc = db_service.get_document(doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return orm_to_response_document(doc)
    except Exception as e:
        logger.error("Error in get_document: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get(
    "/documents",
    response_model=List[DocumentResponse],
    responses={500: {"model": ErrorResponse}},
)
def list_documents():
    """
    List all documents.

    Returns:
        List[DocumentResponse]: A list of document responses.
    """
    try:
        docs = db_service.list_documents()
        return [orm_to_response_document(doc) for doc in docs]
    except Exception as e:
        logger.error("Error in list_documents: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete(
    "/documents/{doc_id}",
    response_model=DocumentResponse,
    responses={404: {"model": ErrorResponse}},
)
def delete_document(doc_id: str):
    """
    Delete a document by its ID.

    Args:
        doc_id (str): Unique identifier for the document.

    Returns:
        DocumentResponse: The response representing the deleted document record.

    Raises:
        HTTPException: If the document is not found or deletion fails.
    """
    try:
        # Retrieve the document first (to return details if needed)
        doc = db_service.get_document(doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail="Document not found")
        db_service.delete_document(doc_id)
        return orm_to_response_document(doc)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        logger.error("Error deleting document: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete document")


@app.get(
    "/queries/{query_id}",
    response_model=QueryResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_query(query_id: str):
    """
    Retrieve a query record by its ID.

    Args:
        query_id (str): Unique identifier for the query.

    Returns:
        QueryResponse: The query response containing its ID, status, and update timestamp.

    Raises:
        HTTPException: If the query is not found.
    """
    try:
        query = db_service.get_query(query_id)
        if query is None:
            raise HTTPException(status_code=404, detail="Query not found")
        return orm_to_response_query(query)
    except Exception as e:
        logger.error("Error in get_query: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.patch(
    "/queries/{query_id}/status",
    response_model=QueryResponse,
    responses={404: {"model": ErrorResponse}},
)
def update_query_status(
    query_id: str, new_status: QueryStatus = Query(..., description="New query status")
):
    """
    Update the status of a query.

    Args:
        query_id (str): Unique identifier for the query.
        new_status (QueryStatus): New query status to be applied.

    Returns:
        QueryResponse: The updated query response.

    Raises:
        HTTPException: If the query is not found or if the update fails.
    """
    try:
        updated_query = db_service.update_query_status(query_id, new_status)
        return orm_to_response_query(updated_query)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Error updating query status: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to update query status")
