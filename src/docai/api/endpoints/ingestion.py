from fastapi import APIRouter, HTTPException
from docai.api.models.schema import Document

router = APIRouter()

# TEMPORARY
DOCUMENT_STORE = {}


@router.post("/processed", status_code=200)
async def document_processed(document: Document):
    # Log the receipt
    print(f"Received document: {document.id} with {len(document.pages)} pages.")

    # Check for conflicts if the document exists
    if document.id in DOCUMENT_STORE:
        raise HTTPException(status_code=409, detail="Document already processed.")

    # Save to the in-memory store; add additional business logic as needed.
    DOCUMENT_STORE[document.id] = document
    return {"status": "ok", "message": f"Document {document.id} stored successfully."}
