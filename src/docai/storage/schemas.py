from typing import List

from pydantic import BaseModel, Field

from docai.shared.models.dto.meta import Meta
from docai.shared.models.dto.error import ErrorResponse

__all__ = ["ErrorResponse"]


class SavePDFData(BaseModel):
    """
    The payload for a successful PDF‐save response.

    Attributes:
        doc_id (str): Unique identifier for the document.
        pdf_path (str): Filesystem path where the PDF is stored.
    """

    doc_id: str = Field(
        ...,
        description="Unique identifier for the document",
        examples=["doc_123456789"],
    )
    pdf_path: str = Field(
        ...,
        description="Filesystem path where the PDF is stored",
        examples=["data/pdfs/doc_123456789.pdf"],
    )


class SavePDFResponse(BaseModel):
    """
    Response model for saving a PDF, with metadata.

    Attributes:
        data (SavePDFData): The saved‐PDF payload.
        meta (Meta): Metadata about the response (timestamp, version, etc.).
    """

    data: SavePDFData = Field(..., description="Saved PDF details")
    meta: Meta = Field(..., description="Response metadata")


class SaveImageData(BaseModel):
    """
    The payload for a successful image‐save response.

    Attributes:
        doc_id (str): Unique identifier for the document.
        page_number (int): The page number of the saved image.
        image_path (str): Filesystem path where the image is stored.
    """

    doc_id: str = Field(
        ...,
        description="Unique identifier for the document",
        examples=["doc_123456789"],
    )
    page_number: int = Field(
        ..., description="Page number of the saved image", examples=[0]
    )
    image_path: str = Field(
        ...,
        description="Filesystem path where the image is stored",
        examples=["data/images/doc_123456789_p0.jpg"],
    )


class SaveImageResponse(BaseModel):
    """
    Response model for saving an image, with metadata.

    Attributes:
        data (SaveImageData): The saved‐image payload.
        meta (Meta): Metadata about the response (timestamp, version, etc.).
    """

    data: SaveImageData = Field(..., description="Saved image details")
    meta: Meta = Field(..., description="Response metadata")


class DeleteDocumentData(BaseModel):
    """
    The payload for a successful document deletion response.

    Attributes:
        doc_id (str): Unique identifier for the deleted document.
        detail (str): A confirmation message.
    """

    doc_id: str = Field(
        ...,
        description="Unique identifier for the deleted document",
        examples=["doc_123456789"],
    )
    detail: str = Field(
        ...,
        description="Confirmation message",
        examples=["Document deleted successfully."],
    )


class DeleteDocumentResponse(BaseModel):
    """
    Response model for deleting a document, with metadata.

    Attributes:
        data (DeleteDocumentData): The deleted‐document payload.
        meta (Meta): Metadata about the response (timestamp, version, etc.).
    """

    data: DeleteDocumentData = Field(..., description="Deleted document details")
    meta: Meta = Field(..., description="Response metadata")
