from pydantic import BaseModel, Field

# --- Request Schemas ---


class SavePDFResponse(BaseModel):
    doc_id: str = Field(..., description="Unique identifier for the document")
    pdf_path: str = Field(..., description="Filesystem path where the PDF is stored")


class SaveImageResponse(BaseModel):
    doc_id: str = Field(..., description="Unique identifier for the document")
    page_number: int = Field(..., description="Page number of the saved image")
    image_path: str = Field(
        ..., description="Filesystem path where the image is stored"
    )


class DeleteDocumentResponse(BaseModel):
    doc_id: str = Field(..., description="Unique identifier for the deleted document")
    detail: str = Field(..., description="Confirmation message")


# --- Error Schema ---


class ErrorResponse(BaseModel):
    detail: str
