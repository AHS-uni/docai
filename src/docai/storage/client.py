import requests
from pathlib import Path
from typing import Union, IO


class StorageClient:
    """Client for interacting with the Storage Service API.

    Provides methods to upload/download PDFs and images, and to delete documents.

    Attributes:
        base_url (str): Base URL of the Storage Service (no trailing slash).
    """

    def __init__(self, base_url: str):
        """Initialize a new StorageClient.

        Args:
            base_url (str): Base URL of your storage service, e.g.
                "http://storage-service:8000".  A trailing slash will be stripped.
        """
        self.base_url = base_url.rstrip("/")

    def save_pdf(self, doc_id: str, pdf_file: Union[Path, IO[bytes]]) -> str:
        """Upload a PDF for a document.

        Args:
            doc_id (str): Unique identifier for the document.
            pdf_file (Union[Path, IO[bytes]]): Either a `Path` to the PDF on disk
                or any binary file-like object (e.g. `io.BytesIO`).

        Returns:
            str: The path (on the storage server) where the PDF was saved.

        Raises:
            requests.HTTPError: If the HTTP request fails (status code >= 400).
        """
        url = f"{self.base_url}/pdf/save"
        params = {"doc_id": doc_id}

        # Prepare the file payload
        if isinstance(pdf_file, Path):
            with open(pdf_file, "rb") as f:
                files = {"file": f}
                resp = requests.post(url, params=params, files=files)
        else:
            files = {"file": pdf_file}
            resp = requests.post(url, params=params, files=files)

        resp.raise_for_status()
        return resp.json()["pdf_path"]

    def save_image(
        self, doc_id: str, page_number: int, image_file: Union[Path, IO[bytes]]
    ) -> str:
        """Upload a page-image for a document.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page number.
            image_file (Union[Path, IO[bytes]]): Either a `Path` to the image on disk
                or any binary file-like object.

        Returns:
            str: The path (on the storage server) where the image was saved.

        Raises:
            requests.HTTPError: If the HTTP request fails (status code >= 400).
        """
        url = f"{self.base_url}/image/save"
        params = {"doc_id": doc_id, "page_number": page_number}

        if isinstance(image_file, Path):
            with open(image_file, "rb") as f:
                files = {"file": f}
                resp = requests.post(url, params=params, files=files)
        else:
            files = {"file": image_file}
            resp = requests.post(url, params=params, files=files)

        resp.raise_for_status()
        return resp.json()["image_path"]

    def get_pdf(self, doc_id: str) -> bytes:
        """Download the PDF bytes for a document.

        Args:
            doc_id (str): Unique identifier for the document.

        Returns:
            bytes: Raw PDF file contents.

        Raises:
            requests.HTTPError: If the HTTP request fails (status code >= 400).
        """
        url = f"{self.base_url}/pdf/get"
        params = {"doc_id": doc_id}

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.content

    def get_image(self, doc_id: str, page_number: int) -> bytes:
        """Download the image bytes for a given page of a document.

        Args:
            doc_id (str): Unique identifier for the document.
            page_number (int): Zero-based page number.

        Returns:
            bytes: Raw image file contents.

        Raises:
            requests.HTTPError: If the HTTP request fails (status code >= 400).
        """
        url = f"{self.base_url}/image/get"
        params = {"doc_id": doc_id, "page_number": page_number}

        resp = requests.get(url, params=params)
        resp.raise_for_status()
        return resp.content

    def delete_document(self, doc_id: str) -> None:
        """Delete a document and all its associated files (PDF + images).

        Args:
            doc_id (str): Unique identifier for the document to delete.

        Raises:
            requests.HTTPError: If the HTTP request fails (status code >= 400).
        """
        url = f"{self.base_url}/document/delete"
        params = {"doc_id": doc_id}

        resp = requests.delete(url, params=params)
        resp.raise_for_status()
