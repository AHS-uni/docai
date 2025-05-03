# queue_service/schemas.py

from typing import Any, Dict, List

from pydantic import BaseModel, Field

from docai.shared.models.dto.error import ErrorResponse
from docai.shared.models.dto.meta import Meta

__all__ = [
    "EnqueueItem",
    "EnqueueRequest",
    "EnqueueResponse",
    "FetchResponse",
    "FetchItem",
    "AckRequest",
    "AckResponse",
    "NackRequest",
    "NackResponse",
    "ErrorResponse",
]


class EnqueueItem(BaseModel):
    """
    A single task to enqueue.

    Attributes:
        task_id (str): Unique identifier for the task.
        payload (Dict[str, Any]): Arbitrary JSON payload for processing.
    """

    task_id: str = Field(
        ..., description="Unique identifier for the task", examples=["task_123456"]
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Payload containing task-specific data",
        examples=[{"doc_id": "doc_123", "path": "/tmp/doc.pdf"}],
    )


class EnqueueRequest(BaseModel):
    """
    Request model for enqueuing one or more tasks.

    Attributes:
        queue_name (str): Logical queue to push into.
        items (List[EnqueueItem]): The batch of tasks to enqueue.
    """

    queue_name: str = Field(
        ..., description="Name of the target queue", examples=["document_processing"]
    )
    items: List[EnqueueItem] = Field(..., description="List of tasks to enqueue")


class EnqueueResponse(BaseModel):
    """
    Response model for enqueue operations.

    Attributes:
        data (Dict[str, int]): Number of items enqueued.
        meta (Meta): Response metadata.
    """

    data: Dict[str, int] = Field(
        ..., description="Counts of enqueued items", examples=[{"enqueued": 3}]
    )
    meta: Meta = Field(..., description="Response metadata")


class FetchItem(BaseModel):
    """
    A single fetched task.

    Attributes:
        task_id (str): The identifier of the task.
        payload (Dict[str, Any]): The task payload.
        receipt_handle (str): Opaque handle for ack/nack.
    """

    task_id: str = Field(
        ..., description="Identifier of the fetched task", examples=["task_123456"]
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Payload for processing",
        examples=[{"doc_id": "doc_123", "path": "/tmp/doc.pdf"}],
    )
    receipt_handle: str = Field(
        ...,
        description="Opaque broker handle for acknowledgment",
        examples=["AQEBwJnKyrHigUMZj6rY..."],
    )


class FetchResponse(BaseModel):
    """
    Response model for fetch operations.

    Attributes:
        data (List[FetchItem]): The list of fetched tasks.
        meta (Meta): Response metadata.
    """

    data: List[FetchItem] = Field(..., description="Fetched tasks")
    meta: Meta = Field(..., description="Response metadata")


class AckRequest(BaseModel):
    """
    Request model for acknowledging successful processing.

    Attributes:
        queue_name (str): Logical queue of the tasks.
        receipt_handles (List[str]): Handles to ack.
    """

    queue_name: str = Field(
        ..., description="Name of the queue", examples=["document_processing"]
    )
    receipt_handles: List[str] = Field(
        ...,
        description="List of receipt handles to acknowledge",
        examples=[["AQEBw...", "AQEBx..."]],
    )


class AckResponse(BaseModel):
    """
    Response model for acknowledgments.

    Attributes:
        data (Dict[str, int]): Number of items acknowledged.
        meta (Meta): Response metadata.
    """

    data: Dict[str, int] = Field(
        ..., description="Counts of acknowledgments", examples=[{"acked": 2}]
    )
    meta: Meta = Field(..., description="Response metadata")


class NackRequest(BaseModel):
    """
    Request model for negative acknowledgments (failures).

    Attributes:
        queue_name (str): Logical queue of the tasks.
        receipt_handles (List[str]): Handles to nack.
        requeue (bool): Whether to requeue or send to DLQ.
    """

    queue_name: str = Field(
        ..., description="Name of the queue", examples=["document_processing"]
    )
    receipt_handles: List[str] = Field(
        ...,
        description="List of receipt handles to negative-acknowledge",
        examples=[["AQEBw...", "AQEBx..."]],
    )
    requeue: bool = Field(
        True, description="Whether to requeue failed tasks", examples=[True]
    )


class NackResponse(BaseModel):
    """
    Response model for negative acknowledgments.

    Attributes:
        data (Dict[str, int]): Number of items nacked.
        meta (Meta): Response metadata.
    """

    data: Dict[str, int] = Field(
        ..., description="Counts of nacks", examples=[{"nacked": 2}]
    )
    meta: Meta = Field(..., description="Response metadata")
