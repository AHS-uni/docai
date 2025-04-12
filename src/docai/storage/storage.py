import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class StorageService:
    """
    A simple file system service used to store and retrieve files.

    This module supports:
      - Saving files (e.g., raw PDFs and converted page images)
      - Retrieving files by constructing paths
      - Deleting files
    """

    def __init__(self, base_path: Optional[Path] = None) -> None:
        """
        Initialize the file system service with directory paths.

        Args:
            base_path (Optional[Path]): Base directory for file storage. Defaults to './data'.
        """
        self.base_path = base_path or Path("./data")
        self.pdf_dir = self.base_path / "pdfs"
        self.image_dir = self.base_path / "images"
        self.ensure_directories()

    def ensure_directories(self) -> None:
        """
        Ensure that storage directories exist.
        """
        for directory in [self.pdf_dir, self.image_dir]:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info("Ensured directory exists: %s", directory)
            except Exception as e:
                logger.error(
                    "Failed to ensure directory %s exists: %s",
                    directory,
                    e,
                    exc_info=True,
                )
                raise

    # ----------------- File Saving Operations -----------------

    def save_pdf(self, doc_id: str, pdf_content: bytes) -> Path:
        """
        Saves PDF content to the designated PDFs directory.

        Args:
            doc_id (str): Unique identifier for the document.
            pdf_content (bytes): Raw bytes of the PDF file.

        Returns:
            Path: The absolute path to the saved PDF file.

        Raises:
            Exception: Propagates any exceptions encountered during the file write operation.
        """
        file_path = self.pdf_dir / f"{doc_id}.pdf"
        try:
            with open(file_path, "wb") as pdf_file:
                pdf_file.write(pdf_content)
                logger.info("PDF saved for doc_id %s at %s", doc_id, file_path)
        except Exception as e:
            logger.error(
                "Failed to save PDF for doc_id %s: %s", doc_id, e, exc_info=True
            )
            raise
        return file_path

    def save_image(self, doc_id: str, page_number: int, image_content: bytes) -> Path:
        """
        Save a page image to the designated images directory.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Page number of the image.
            image_content (bytes): Raw bytes of the image file.

        Returns:
            Path: The absolute path to the saved image file.

        Raises:
            Exception: Propagates any exceptions encountered during the file write operation.
        """
        file_path = self.image_dir / f"{doc_id}_p{page_number}.jpg"
        try:
            with open(file_path, "wb") as image_file:
                image_file.write(image_content)
                logger.info(
                    "Image saved for doc_id %s, page %d at %s",
                    doc_id,
                    page_number,
                    file_path,
                )
        except Exception as e:
            logger.error(
                "Failed to save image for doc_id %s, page %d: %s",
                doc_id,
                page_number,
                e,
                exc_info=True,
            )
            raise
        return file_path

    # ----------------- File Retrieval Operations -----------------

    def get_pdf_path(self, doc_id: str) -> Path:
        """
        Construct the file path for a given document's PDF.

        Args:
            doc_id (str): Unique identifier for the document.

        Returns:
            Path: The file path to the PDF.

        Raises:
            FileNotFoundError: If the PDF file does not exist.
        """
        file_path = self.pdf_dir / f"{doc_id}.pdf"
        if not file_path.exists():
            logger.error("PDF file for doc_id %s not found at %s", doc_id, file_path)
            raise FileNotFoundError(f"PDF file for doc_id {doc_id} does not exist.")
        logger.info("PDF path for doc_id %s is %s", doc_id, file_path)
        return file_path

    def get_image_path(self, doc_id: str, page_number: int) -> Path:
        """
        Construct the file path for a specific page image.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): The page number to retrieve.

        Returns:
            Path: The file path to the image.

        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        file_path = self.image_dir / f"{doc_id}_p{page_number}.jpg"
        if not file_path.exists():
            logger.error(
                "Image file for doc_id %s, page %d not found at %s",
                doc_id,
                page_number,
                file_path,
            )
            raise FileNotFoundError(
                f"Image file for doc_id {doc_id}, page {page_number} does not exist."
            )
        logger.info(
            "Image path for doc_id %s, page %d is %s", doc_id, page_number, file_path
        )
        return file_path

    # ----------------- File Deletion Operations -----------------

    def delete_document(self, doc_id: str) -> None:
        """
        Delete the PDF and all associated page images for a specified document.

        Args:
            doc_id (str): Unique identifier for the document.

        Raises:
            Exception: Propagates any exceptions encountered during file deletions.
        """
        pdf_file = self.pdf_dir / f"{doc_id}.pdf"
        if pdf_file.exists():
            try:
                pdf_file.unlink()
                logger.info("Deleted PDF for doc_id %s from %s", doc_id, pdf_file)
            except Exception as e:
                logger.error(
                    "Failed to delete PDF for doc_id %s: %s", doc_id, e, exc_info=True
                )
                raise

        # Delete associated images
        for image_file in self.image_dir.glob(f"{doc_id}_p*.jpg"):
            try:
                image_file.unlink()
                logger.info("Deleted image file %s for doc_id %s", image_file, doc_id)
            except Exception as e:
                logger.error(
                    "Failed to delete image file %s for doc_id %s: %s",
                    image_file,
                    doc_id,
                    e,
                    exc_info=True,
                )
                raise
