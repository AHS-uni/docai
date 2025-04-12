from fastapi import APIRouter, HTTPException
from typing import Dict

from docai.api.models.schema import Document, DocumentStatus

router = APIRouter()

# TEMPORARY
DOCUMENT_STORE: Dict[str, Document] = {}


@router.post("/", response_model=Document)
def post_document(document: Document):
    """
    Adds a processed document to an document store.

    Args:
        document (Document): The document to be stored.

    Returns:
        Document: The added document, as confirmation.

    Raises:
        HTTPException: If the document is not processed or already in the store.
    """
    if document.status != DocumentStatus.PROCESSED:
        raise HTTPException(
            status_code=400, detail="Document has not been processed yet."
        )

    if document.id in DOCUMENT_STORE:
        raise HTTPException(
            status_code=400, detail="Document already processed and added to the store."
        )

    DOCUMENT_STORE[document.id] = document
    return document


@router.get("/", response_model=list[Document])
def list_documents():
    """Retrieves all processed documents from the document store.

    Returns:
        List[Document]: A list of all documents in the store.
    """
    return list(DOCUMENT_STORE.values())
