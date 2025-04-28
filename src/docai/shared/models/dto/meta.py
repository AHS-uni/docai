from typing import List, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class Meta(BaseModel):
    """Metadata common to all API responses."""

    timestamp: datetime = Field(
        ...,
        description="Time when the response was generated (ISO8601).",
        examples=["2025-04-12T17:00:00Z"],
    )
    version: str = Field(
        ...,
        description="API version string.",
        examples=["1.0.0"],
    )
