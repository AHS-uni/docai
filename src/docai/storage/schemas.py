from pydantic import BaseModel, Field

# --- Request Response Models ---


class SavePDFResponse(BaseModel):
    """
    Response model for saving a PDF file in the storage service.

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


class SaveImageResponse(BaseModel):
    """
    Response model for saving an image file (a page) in the storage service.

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


class DeleteDocumentResponse(BaseModel):
    """
    Response model for deleting a document and its associated files.

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


# --- Error Response Models ---


class ErrorResponse(BaseModel):
    """
    Error response model for storage service endpoints.

    Attributes:
        detail (str): A description of the encountered error.
    """

    detail: str = Field(
        ..., description="Error message", examples=["Document not found"]
    )
