"""
Asynchronous, file‐based storage service.

Uses aiofiles for non‐blocking I/O and per‐document asyncio locks
to coordinate concurrent access to the same document’s files.
"""

import asyncio
import logging
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiofiles.os

from docai.storage.config import LOCK_STRIPES
from docai.storage.exceptions import (
    DeleteDocumentError,
    ImageNotFoundError,
    PDFNotFoundError,
    SaveImageError,
    SavePDFError,
)

logger = logging.getLogger(__name__)


class StorageService:
    """Async file‐system storage service for PDFs and page images."""

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """
        Initialize storage directories and per‐document locks.

        Args:
            base_path (Optional[Path]): Base directory for storage (defaults to './data').
        """
        self.base_path: Path = base_path or Path("./data")
        self.pdf_dir: Path = self.base_path / "pdfs"
        self.image_dir: Path = self.base_path / "images"
        # Bounded “striped” lock pool — prevents unbounded growth
        self._num_stripes: int = LOCK_STRIPES
        self._locks: List[asyncio.Lock] = [
            asyncio.Lock() for _ in range(self._num_stripes)
        ]
        self._ensure_directories()

    def _get_lock(self, doc_id: str) -> asyncio.Lock:
        """
        Map a document ID to one of a fixed set of locks.

        This bounds the total number of Lock objects in memory.

        Args:
            doc_id (str): Unique document identifier.

        Returns:
            asyncio.Lock: One of the striped locks.
        """
        idx = hash(doc_id) % self._num_stripes
        return self._locks[idx]

    def _ensure_directories(self) -> None:
        """Ensure that both PDF and image directories exist on disk."""
        for directory in (self.pdf_dir, self.image_dir):
            directory.mkdir(parents=True, exist_ok=True)
            logger.info("Storage directory ensured: %s", directory)

    async def save_pdf(self, doc_id: str, pdf_content: bytes) -> Path:
        """
        Asynchronously save PDF bytes to disk under a per‐document lock.

        Args:
            doc_id (str): Unique identifier for the document.
            pdf_content (bytes): Raw bytes of the PDF file.

        Returns:
            Path: Path to the saved PDF file.

        Raises:
            SavePDFError: If writing the file fails.
        """
        file_path = self.pdf_dir / f"{doc_id}.pdf"
        lock = self._get_lock(doc_id)
        logger.debug(
            "Attempting save_pdf: doc_id=%s path=%s size=%dB",
            doc_id,
            file_path,
            len(pdf_content),
        )
        async with lock:
            try:
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(pdf_content)
                    logger.info("PDF saved: doc_id=%s path=%s", doc_id, file_path)
                return file_path
            except Exception as e:
                logger.error(
                    "Error saving PDF: doc_id=%s path=%s error=%s",
                    doc_id,
                    file_path,
                    e,
                    exc_info=True,
                )
                raise SavePDFError(f"Could not save PDF for {doc_id}") from e

    async def save_image(
        self, doc_id: str, page_number: int, image_content: bytes
    ) -> Path:
        """
        Asynchronously save image bytes to disk under a per‐document lock.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page index.
            image_content (bytes): Raw bytes of the JPEG image.

        Returns:
            Path: Path to the saved image file.

        Raises:
            SaveImageError: If writing the file fails.
        """
        file_path = self.image_dir / f"{doc_id}_p{page_number}.jpg"
        lock = self._get_lock(doc_id)
        logger.debug(
            "Attempting save_image: doc_id=%s page=%d path=%s size=%dB",
            doc_id,
            page_number,
            file_path,
            len(image_content),
        )
        async with lock:
            try:
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(image_content)
                    logger.info(
                        "Image saved: doc_id=%s page=%d path=%s",
                        doc_id,
                        page_number,
                        file_path,
                    )
                return file_path
            except Exception as e:
                logger.error(
                    "Error saving image: doc_id=%s page=%d path=%s error=%s",
                    doc_id,
                    page_number,
                    file_path,
                    e,
                    exc_info=True,
                )
                raise SaveImageError(
                    f"Could not save image {page_number} for {doc_id}"
                ) from e

    async def get_pdf_path(self, doc_id: str) -> Path:
        """
        Asynchronously check that the PDF exists and return its path.

        Args:
            doc_id (str): Unique identifier for the document.

        Returns:
            Path: Path to the PDF file.

        Raises:
            PDFNotFoundError: If the file does not exist.
        """
        file_path = self.pdf_dir / f"{doc_id}.pdf"
        logger.debug("Checking PDF existence: doc_id=%s path=%s", doc_id, file_path)
        exists = await aiofiles.os.path.exists(str(file_path))
        if not exists:
            logger.warning("PDF not found: doc_id=%s path=%s", doc_id, file_path)
            raise PDFNotFoundError(f"PDF for {doc_id} does not exist")
        logger.info("PDF exists: doc_id=%s path=%s", doc_id, file_path)
        return file_path

    async def get_image_path(self, doc_id: str, page_number: int) -> Path:
        """
        Asynchronously check that the image exists and return its path.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page index.

        Returns:
            Path: Path to the image file.

        Raises:
            ImageNotFoundError: If the file does not exist.
        """
        file_path = self.image_dir / f"{doc_id}_p{page_number}.jpg"
        logger.debug(
            "Checking image existence: doc_id=%s page=%d path=%s",
            doc_id,
            page_number,
            file_path,
        )
        exists = await aiofiles.os.path.exists(str(file_path))
        if exists:
            logger.info(
                "Image exists: doc_id=%s page=%d path=%s",
                doc_id,
                page_number,
                file_path,
            )
            return file_path
        else:
            logger.warning(
                "Image not found: doc_id=%s page=%d path=%s",
                doc_id,
                page_number,
                file_path,
            )
            raise ImageNotFoundError(f"Image {page_number} for {doc_id} does not exist")

    async def delete_document(self, doc_id: str) -> None:
        """
        Asynchronously delete the PDF and all associated images for a document.

        Args:
            doc_id (str): Unique identifier for the document.

        Raises:
            DeleteDocumentError: If any part of deletion fails.
        """
        lock = self._get_lock(doc_id)
        logger.debug("Starting delete_document: doc_id=%s", doc_id)
        async with lock:
            # Delete PDF
            pdf_file = self.pdf_dir / f"{doc_id}.pdf"
            if await aiofiles.os.path.exists(str(pdf_file)):
                try:
                    await aiofiles.os.remove(str(pdf_file))
                    logger.info("Deleted PDF: doc_id=%s path=%s", doc_id, pdf_file)
                except Exception as e:
                    logger.error(
                        "Error deleting PDF: doc_id=%s path=%s error=%s",
                        doc_id,
                        pdf_file,
                        e,
                        exc_info=True,
                    )
                    raise DeleteDocumentError(
                        f"Could not delete PDF for {doc_id}"
                    ) from e
            else:
                logger.debug("No PDF to delete for doc_id=%s", doc_id)

            # Delete images
            try:
                entries = await aiofiles.os.listdir(str(self.image_dir))
                for name in entries:
                    if name.startswith(f"{doc_id}_p") and name.endswith(".jpg"):
                        img_path = self.image_dir / name
                        await aiofiles.os.remove(str(img_path))
                        logger.info("Deleted image: %s", img_path)
                        logger.debug(
                            "Finished image deletion scan for doc_id=%s", doc_id
                        )
            except Exception as e:
                logger.error(
                    "Error deleting images for doc_id=%s error=%s",
                    doc_id,
                    e,
                    exc_info=True,
                )
                raise DeleteDocumentError(
                    f"Could not delete images for {doc_id}"
                ) from e

        logger.debug("Completed delete_document: doc_id=%s", doc_id)
