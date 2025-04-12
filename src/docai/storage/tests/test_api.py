import time
from pathlib import Path

from fastapi.testclient import TestClient

from docai.storage.api import app
from docai.storage.config import BASE_PATH

SAMPLE_PDF_PATH = Path("tests/resources/sample.pdf")
PAGE_COUNT = 9  # adjust to the actual number of pages in your sample PDF
SAMPLE_IMAGE_PATHS = [
    Path(f"tests/resources/sample_page_p{i}.jpg") for i in range(PAGE_COUNT)
]

client = TestClient(app)

# Use a fixed document ID for testing.
TEST_DOC_ID = "integration_test_doc"


def load_file_content(file_path: Path) -> bytes:
    """Load binary content from the given file path."""
    with file_path.open("rb") as f:
        return f.read()


def measure_time(func):
    """
    Decorator to measure the elapsed time of a test function and print a message.
    """

    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} completed in {elapsed:.4f} seconds")
        return result

    return wrapper


@measure_time
def test_save_and_get_pdf():
    """
    Test saving a PDF and then retrieving it.
    """
    pdf_content = load_file_content(SAMPLE_PDF_PATH)

    # Save the PDF.
    response = client.post(
        "/pdf/save",
        params={"doc_id": TEST_DOC_ID},
        files={"file": (SAMPLE_PDF_PATH.name, pdf_content, "application/pdf")},
    )
    assert response.status_code == 200, response.text
    json_resp = response.json()
    assert json_resp["doc_id"] == TEST_DOC_ID
    saved_pdf_path = Path(json_resp["pdf_path"])
    # Verify that the file exists.
    assert saved_pdf_path.exists(), f"PDF not found at {saved_pdf_path}"

    # Retrieve the PDF.
    response = client.get(f"/pdf/get?doc_id={TEST_DOC_ID}")
    assert response.status_code == 200, response.text
    assert response.headers.get("content-type") == "application/pdf"
    retrieved_pdf = response.content
    assert (
        retrieved_pdf == pdf_content
    ), "Retrieved PDF does not match the original sample."


@measure_time
def test_save_and_get_images():
    """
    Test saving multiple image files (one per page) and then retrieving each image.
    """
    # Save each page image.
    for page_number, image_path in enumerate(SAMPLE_IMAGE_PATHS):
        image_content = load_file_content(image_path)
        response = client.post(
            "/image/save",
            params={"doc_id": TEST_DOC_ID, "page_number": page_number},
            files={"file": (image_path.name, image_content, "image/jpeg")},
        )
        assert response.status_code == 200, response.text
        json_resp = response.json()
        assert json_resp["doc_id"] == TEST_DOC_ID
        assert json_resp["page_number"] == page_number
        saved_image_path = Path(json_resp["image_path"])
        assert (
            saved_image_path.exists()
        ), f"Image for page {page_number} not found at {saved_image_path}"

        # Retrieve the image.
        response = client.get(
            f"/image/get?doc_id={TEST_DOC_ID}&page_number={page_number}"
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("content-type") == "image/jpeg"
        retrieved_image = response.content
        assert (
            retrieved_image == image_content
        ), f"Retrieved image for page {page_number} does not match."


@measure_time
def test_get_nonexistent_pdf():
    """
    Test that attempting to retrieve a PDF that does not exist returns a 404 error.
    """
    nonexisting_id = "nonexistent_pdf"
    response = client.get(f"/pdf/get?doc_id={nonexisting_id}")
    assert response.status_code == 404, response.text
    json_resp = response.json()
    assert "does not exist" in json_resp["detail"]


@measure_time
def test_get_nonexistent_image():
    """
    Test that attempting to retrieve an image that does not exist returns a 404 error.
    """
    nonexisting_id = "nonexistent_image"
    response = client.get(f"/image/get?doc_id={nonexisting_id}&page_number=0")
    assert response.status_code == 404, response.text
    json_resp = response.json()
    assert "does not exist" in json_resp["detail"]


@measure_time
def test_delete_document():
    """
    Test deletion of the document to clean up all created files (PDF and images).

    This test is used as cleanup, ensuring the document's files are removed from the storage.
    """
    # Delete the document.
    response = client.delete(f"/document/delete?doc_id={TEST_DOC_ID}")
    assert response.status_code == 200, response.text
    json_resp = response.json()
    assert json_resp["doc_id"] == TEST_DOC_ID
    assert json_resp["detail"] == "Document deleted successfully."

    # Verify that the PDF no longer exists.
    pdf_file = Path(BASE_PATH) / "pdfs" / f"{TEST_DOC_ID}.pdf"
    assert not pdf_file.exists(), f"PDF file {pdf_file} still exists after deletion."

    # Verify that each image file no longer exists.
    for page_number in range(len(SAMPLE_IMAGE_PATHS)):
        image_file = Path(BASE_PATH) / "images" / f"{TEST_DOC_ID}_p{page_number}.jpg"
        assert (
            not image_file.exists()
        ), f"Image file {image_file} still exists after deletion."


if __name__ == "__main__":
    # Running the tests manually will print timing statistics.
    test_save_and_get_pdf()
    test_save_and_get_images()
    test_get_nonexistent_pdf()
    test_get_nonexistent_image()
    test_delete_document()
