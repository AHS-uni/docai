from pydantic import BaseModel, Field
from typing import List

from docai.shared.models.dto.meta import Meta


class Page(BaseModel):
    """
    DTO representation of a page.

    Attributes:
        id (str): Unique identifier for the page.
        page_number (int): The page number within the document.
        image_path (str): The file path to the page image.
    """

    id: str = Field(
        ..., description="Unique identifier for the page", examples=["page_001"]
    )
    page_number: int = Field(
        ..., description="Page number in the document", examples=[1]
    )
    image_path: str = Field(
        ...,
        description="Filesystem path to the page image",
        examples=["/images/page1.jpg"],
    )


class PageResponse(BaseModel):
    """
    Response model for page-related endpoints.

    Attributes:
        data (List[Page]): Array of Page DTO objects.
        meta (dict): Metadata for the response including timestamp and version.
    """

    data: List[Page] = Field(
        ...,
        description="List of page records",
        examples=[
            [{"id": "page_001", "page_number": 1, "image_path": "/images/page1.jpg"}]
        ],
    )
    meta: Meta = Field(
        ..., description="Response metadata including timestamp, version, etc."
    )
