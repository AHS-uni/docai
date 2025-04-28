"""
FastAPI service for handling PDF and image storage operations.

This module defines endpoints for saving, retrieving, and deleting PDF files and
page images associated with documents. It uses an asynchronous file storage service.
"""

import uvicorn
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse

from docai.storage.config import BASE_PATH, HOST, PORT, LOG_FILE
from docai.shared.models.dto.meta import Meta
from docai.storage.schemas import (
    SavePDFResponse,
    SavePDFData,
    SaveImageResponse,
    SaveImageData,
    DeleteDocumentResponse,
    DeleteDocumentData,
    ErrorResponse,
)
from docai.storage.storage import StorageService
from docai.storage.exceptions import (
    SavePDFError,
    SaveImageError,
    PDFNotFoundError,
    ImageNotFoundError,
    DeleteDocumentError,
)
from docai.shared.utils.logging_utils import setup_logging
from docai.storage.config import VERSION


# Initialize logging
setup_logging(LOG_FILE)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Storage Service",
    description="Async file storage service for PDFs and images.",
    version=VERSION,
)

s_service = StorageService(BASE_PATH)


def _response_meta() -> Meta:
    """Generate a fresh Meta object."""
    return Meta(timestamp=datetime.now(timezone.utc), version="1.0.0")


@app.post(
    "/pdf/save",
    response_model=SavePDFResponse,
    responses={500: {"model": ErrorResponse}},
)
async def save_pdf(doc_id: str, file: UploadFile = File(...)) -> SavePDFResponse:
    """
    Save a PDF file asynchronously.

    Args:
        doc_id (str): Unique document identifier.
        file (UploadFile): Uploaded PDF file.

    Returns:
        SavePDFResponse: Response containing saved‐PDF details and meta.
    """
    content = await file.read()
    try:
        path = await s_service.save_pdf(doc_id, content)
        data = SavePDFData(doc_id=doc_id, pdf_path=str(path))
        return SavePDFResponse(data=data, meta=_response_meta())
    except SavePDFError as e:
        logger.error("Error saving PDF for %s: %s", doc_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/pdf/get",
    responses={
        200: {"content": {"application/pdf": {}}, "description": "The PDF file"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_pdf(doc_id: str) -> FileResponse:
    """
    Retrieve a stored PDF file asynchronously.

    Args:
        doc_id (str): Unique document identifier.

    Returns:
        FileResponse: The PDF file stream.
    """
    try:
        path = await s_service.get_pdf_path(doc_id)
        return FileResponse(
            path=str(path), media_type="application/pdf", filename=f"{doc_id}.pdf"
        )
    except PDFNotFoundError as e:
        logger.warning("PDF not found for %s: %s", doc_id, e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error retrieving PDF for %s: %s", doc_id, e, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve PDF.")


@app.post(
    "/image/save",
    response_model=SaveImageResponse,
    responses={500: {"model": ErrorResponse}},
)
async def save_image(
    doc_id: str,
    page_number: int = Query(..., ge=0),
    file: UploadFile = File(...),
) -> SaveImageResponse:
    """
    Save a page image asynchronously.

    Args:
        doc_id (str): Unique document identifier.
        page_number (int): Zero‐based page index.
        file (UploadFile): Uploaded JPEG file.

    Returns:
        SaveImageResponse: Response containing saved‐image details and meta.
    """
    content = await file.read()
    try:
        path = await s_service.save_image(doc_id, page_number, content)
        data = SaveImageData(
            doc_id=doc_id, page_number=page_number, image_path=str(path)
        )
        return SaveImageResponse(data=data, meta=_response_meta())
    except SaveImageError as e:
        logger.error(
            "Error saving image for %s page %d: %s",
            doc_id,
            page_number,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/image/get",
    responses={
        200: {"content": {"image/jpeg": {}}, "description": "The JPEG image"},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def get_image(doc_id: str, page_number: int = Query(..., ge=0)) -> FileResponse:
    """
    Retrieve a stored page image asynchronously.

    Args:
        doc_id (str): Unique document identifier.
        page_number (int): Zero‐based page index.

    Returns:
        FileResponse: The JPEG image stream.
    """
    try:
        path = await s_service.get_image_path(doc_id, page_number)
        return FileResponse(
            path=str(path),
            media_type="image/jpeg",
            filename=f"{doc_id}_p{page_number}.jpg",
        )
    except ImageNotFoundError as e:
        logger.warning("Image not found for %s page %d: %s", doc_id, page_number, e)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error retrieving image for %s page %d: %s",
            doc_id,
            page_number,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve image.")


@app.delete(
    "/document/delete",
    response_model=DeleteDocumentResponse,
    responses={500: {"model": ErrorResponse}},
)
async def delete_document(doc_id: str) -> DeleteDocumentResponse:
    """
    Delete a document and all its associated files asynchronously.

    Args:
        doc_id (str): Document identifier.

    Returns:
        DeleteDocumentResponse: Response containing deletion confirmation and meta.
    """
    try:
        await s_service.delete_document(doc_id)
        data = DeleteDocumentData(
            doc_id=doc_id, detail="Document deleted successfully."
        )
        return DeleteDocumentResponse(data=data, meta=_response_meta())
    except DeleteDocumentError as e:
        logger.error("Error deleting document %s: %s", doc_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("docai.storage.api:app", host=HOST, port=PORT, reload=True)
