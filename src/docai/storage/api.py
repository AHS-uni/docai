import uvicorn
import logging

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse

from docai.storage.storage import StorageService
from docai.storage.config import BASE_PATH, HOST, PORT, LOG_FILE
from docai.storage.schemas import (
    SavePDFResponse,
    SaveImageResponse,
    DeleteDocumentResponse,
    ErrorResponse,
)
from docai.shared.utils.logging_utils import setup_logging


setup_logging(LOG_FILE)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Storage Service",
    description="Service to handle file storage operations.",
    version="1.0.0",
)

s_service = StorageService(BASE_PATH)


@app.post(
    "/pdf/save",
    response_model=SavePDFResponse,
    responses={500: {"model": ErrorResponse}},
)
async def save_pdf(doc_id: str, file: UploadFile = File(...)):
    """
    Save a PDF file to the storage service.

    Args:
        doc_id (str): Unique identifier for the document.
        file (UploadFile): The uploaded PDF file.

    Returns:
        SavePDFResponse: An object containing the document ID and the path to the saved PDF.

    Raises:
        HTTPException: If saving the file fails.
    """
    try:
        content = await file.read()
        file_path = s_service.save_pdf(doc_id, content)
        return SavePDFResponse(doc_id=doc_id, pdf_path=str(file_path))
    except Exception as e:
        logger.error("Error saving PDF for doc_id %s: %s", doc_id, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to save PDF file.")


@app.get(
    "/pdf/get", responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
def get_pdf(doc_id: str):
    """
    Retrieve the PDF file for a specific document.

    Args:
        doc_id (str): Unique identifier for the document.

    Returns:
        FileResponse: A file response containing the PDF file.

    Raises:
        HTTPException: If the file is not found or retrieval fails.
    """
    try:
        file_path = s_service.get_pdf_path(doc_id)
        return FileResponse(
            path=str(file_path), media_type="application/pdf", filename=f"{doc_id}.pdf"
        )
    except FileNotFoundError as e:
        logger.error("PDF not found for doc_id %s: %s", doc_id, e, exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error retrieving PDF for doc_id %s: %s",
            doc_id,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve PDF file.")


@app.post(
    "/image/save",
    response_model=SaveImageResponse,
    responses={500: {"model": ErrorResponse}},
)
async def save_image(
    doc_id: str, page_number: int = Query(..., ge=0), file: UploadFile = File(...)
):
    """
    Save an image file for a specific page of a document.

    Args:
        doc_id (str): Unique identifier for the document.
        page_number (int): The page number of the image.
        file (UploadFile): The uploaded image file.

    Returns:
        SaveImageResponse: An object containing the document ID, page number, and the path to the saved image.

    Raises:
        HTTPException: If saving the image fails.
    """
    try:
        content = await file.read()
        file_path = s_service.save_image(doc_id, page_number, content)
        return SaveImageResponse(
            doc_id=doc_id, page_number=page_number, image_path=str(file_path)
        )
    except Exception as e:
        logger.error(
            "Error saving image for doc_id %s, page %d: %s",
            doc_id,
            page_number,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to save image file.")


@app.get(
    "/image/get",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
def get_image(doc_id: str, page_number: int = Query(..., ge=0)):
    """
    Retrieve the image file for a specific page of a document.

    Args:
        doc_id (str): Unique identifier for the document.
        page_number (int): The page number of the desired image.

    Returns:
        FileResponse: A file response containing the image file.

    Raises:
        HTTPException: If the image file is not found or retrieval fails.
    """
    try:
        file_path = s_service.get_image_path(doc_id, page_number)
        return FileResponse(
            path=str(file_path),
            media_type="image/jpeg",
            filename=f"{doc_id}_p{page_number}.jpg",
        )
    except FileNotFoundError as e:
        logger.error(
            "Image not found for doc_id %s, page %d: %s",
            doc_id,
            page_number,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            "Unexpected error retrieving image for doc_id %s, page %d: %s",
            doc_id,
            page_number,
            e,
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve image file.")


@app.delete(
    "/document/delete",
    response_model=DeleteDocumentResponse,
    responses={500: {"model": ErrorResponse}},
)
def delete_document(doc_id: str):
    """
    Delete a document and all its associated files (PDF and images).

    Args:
        doc_id (str): Unique identifier for the document to be deleted.

    Returns:
        DeleteDocumentResponse: Confirmation of successful deletion.

    Raises:
        HTTPException: If deletion fails.
    """
    try:
        s_service.delete_document(doc_id)
        return DeleteDocumentResponse(
            doc_id=doc_id, detail="Document deleted successfully."
        )
    except Exception as e:
        logger.error(
            "Error deleting document for doc_id %s: %s", doc_id, e, exc_info=True
        )
        raise HTTPException(status_code=500, detail="Failed to delete document.")


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
