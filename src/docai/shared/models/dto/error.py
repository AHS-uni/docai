from typing import List
from pydantic import BaseModel, Field

from docai.shared.models.dto.meta import Meta


class ErrorDetail(BaseModel):
    """
    DTO representation for error information.

    Attributes:
        code (int): Numeric error code.
        message (str): A brief error message.
        detail (str): Detailed error description.
    """

    code: int = Field(..., description="Numeric error code", examples=[404])
    message: str = Field(
        ..., description="A brief error message", examples=["Not Found"]
    )
    detail: str = Field(
        ...,
        description="Detailed error description",
        examples=["The requested document was not found in the database."],
    )


class ErrorResponse(BaseModel):
    """Response model for all error responses."""

    errors: List[ErrorDetail] = Field(
        ...,
        description="List of one or more error objects.",
    )
    meta: Meta = Field(
        ..., description="Response metadata including timestamp, version, etc."
    )
