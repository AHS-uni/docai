import logging
from pathlib import Path
from typing import IO, Optional, Union

import httpx
from httpx import AsyncHTTPTransport

from docai.storage.config import (
    CLIENT_MAX_CONNECTIONS,
    CLIENT_MAX_KEEPALIVE_CONNECTIONS,
    CLIENT_REQUEST_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class StorageClient:
    """
    Async client for interacting with the Storage Service API using httpx.

    Example:
        async with StorageClient("http://storage:8000") as client:
            pdf_path = await client.save_pdf("doc123", Path("foo.pdf"))

    Attributes:
        base_url (str): Base URL of the Storage Service (no trailing slash).
        _client (httpx.AsyncClient): Underlying HTTPX async client.
    """

    def __init__(
        self,
        base_url: str,
        timeout: Optional[float] = None,
        max_connections: Optional[int] = None,
        max_keepalive_connections: Optional[int] = None,
    ) -> None:
        """
        Args:
            base_url (str): URL of the storage API (no trailing slash).
            timeout (float | None): Seconds to wait for each request.
            max_connections (int | None): Max concurrent TCP connections.
            max_keepalive_connections (int | None): Max idle keep-alive connections.
        """
        self.base_url = base_url.rstrip("/")
        t = timeout or CLIENT_REQUEST_TIMEOUT_SECONDS
        limits = httpx.Limits(
            max_connections=max_connections or CLIENT_MAX_CONNECTIONS,
            max_keepalive_connections=max_keepalive_connections
            or CLIENT_MAX_KEEPALIVE_CONNECTIONS,
        )
        logger.debug(
            "Initializing AsyncClient(base_url=%r, timeout=%.1fs, limits=%r)",
            self.base_url,
            t,
            limits,
        )

        transport = AsyncHTTPTransport(retries=3)

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(t),
            limits=limits,
            transport=transport,
        )

    async def __aenter__(self) -> "StorageClient":
        return self

    async def __aexit__(self, *args) -> None:
        """
        Close the underlying HTTPX connection pool.
        """
        logger.debug("Closing AsyncClient pool")
        await self._client.aclose()

    async def save_pdf(self, doc_id: str, pdf_file: Union[Path, IO[bytes]]) -> str:
        """
        Upload a PDF for a document asynchronously.

        Args:
            doc_id (str): Unique identifier for the document.
            pdf_file (Path | IO[bytes]): Either a `Path` to the PDF on disk,
                or any binary file-like object.

        Returns:
            str: The path (on the storage server) where the PDF was saved.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails (status_code >= 400).
        """
        if isinstance(pdf_file, Path):
            content = pdf_file.read_bytes()
            filename = pdf_file.name
        else:
            content = pdf_file.read()
            filename = getattr(pdf_file, "name", "file")

        files = {"file": (filename, content, "application/pdf")}
        logger.debug(
            "save_pdf start: doc_id=%s filename=%s size=%dB",
            doc_id,
            filename,
            len(content),
        )
        resp = await self._client.post(
            "/pdf/save", params={"doc_id": doc_id}, files=files
        )
        resp.raise_for_status()
        saved = resp.json()["data"]["pdf_path"]
        logger.info("save_pdf success: doc_id=%s → %s", doc_id, saved)
        return saved

    async def save_image(
        self, doc_id: str, page_number: int, image_file: Union[Path, IO[bytes]]
    ) -> str:
        """
        Upload a page-image for a document asynchronously.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page number.
            image_file (Path | IO[bytes]): Either a `Path` to the image on disk,
                or any binary file-like object.

        Returns:
            str: The path (on the storage server) where the image was saved.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails (status_code >= 400).
        """
        if isinstance(image_file, Path):
            content = image_file.read_bytes()
            filename = image_file.name
        else:
            content = image_file.read()
            filename = getattr(image_file, "name", "file")

        files = {"file": (filename, content, "image/jpeg")}
        logger.debug(
            "save_image start: doc_id=%s page=%d filename=%s size=%dB",
            doc_id,
            page_number,
            filename,
            len(content),
        )
        resp = await self._client.post(
            "/image/save",
            params={"doc_id": doc_id, "page_number": page_number},
            files=files,
        )
        resp.raise_for_status()
        saved = resp.json()["data"]["image_path"]
        logger.info(
            "save_image success: doc_id=%s page=%d → %s",
            doc_id,
            page_number,
            saved,
        )
        return saved

    async def get_pdf(self, doc_id: str) -> bytes:
        """
        Download the raw PDF bytes for a document asynchronously.

        Args:
            doc_id (str): Unique identifier for the document.

        Returns:
            bytes: Raw PDF file contents.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails (status_code >= 400).
        """
        logger.debug("get_pdf start: doc_id=%s", doc_id)
        resp = await self._client.get("/pdf/get", params={"doc_id": doc_id})
        resp.raise_for_status()
        logger.info("get_pdf success: doc_id=%s size=%dB", doc_id, len(resp.content))
        return resp.content

    async def get_image(self, doc_id: str, page_number: int) -> bytes:
        """
        Download the raw JPEG bytes for a page image asynchronously.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page number.

        Returns:
            bytes: Raw image file contents.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails (status_code >= 400).
        """
        logger.debug("get_image start: doc_id=%s page=%d", doc_id, page_number)
        resp = await self._client.get(
            "/image/get", params={"doc_id": doc_id, "page_number": page_number}
        )
        resp.raise_for_status()
        logger.info(
            "get_image success: doc_id=%s page=%d size=%dB",
            doc_id,
            page_number,
            len(resp.content),
        )
        return resp.content

    async def delete_document(self, doc_id: str) -> None:
        """
        Delete a document and all its associated files (PDF + images) asynchronously.

        Args:
            doc_id (str): Unique identifier for the document to delete.

        Raises:
            httpx.HTTPStatusError: If the HTTP request fails (status_code >= 400).
        """
        logger.debug("delete_document start: doc_id=%s", doc_id)
        resp = await self._client.delete("/document/delete", params={"doc_id": doc_id})
        resp.raise_for_status()
        logger.info("delete_document success: doc_id=%s", doc_id)
