import pytest
import requests
from pathlib import Path

from docai.storage.client import StorageClient


class DummyResponse:
    def __init__(self, status_code=200, json_data=None, content=b""):
        self.status_code = status_code
        self._json = json_data or {}
        self.content = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} Error")

    def json(self):
        return self._json


@pytest.fixture
def client():
    # instantiate with or without trailing slash
    return StorageClient(base_url="http://storage.test/")


def test_base_url_stripping(client):
    assert client.base_url == "http://storage.test"


def test_save_pdf_with_real_file(monkeypatch, client):
    sample_path = Path("tests/resources/sample.pdf")
    expected_bytes = sample_path.read_bytes()

    def fake_post(url, params, files):
        # Ensure we're hitting the correct endpoint
        assert url.endswith("/pdf/save")
        # Ensure doc_id is passed through
        assert params["doc_id"] == "real_doc"
        # The client should open the real file and pass its bytes
        file_obj = files["file"]
        data = file_obj.read()
        assert data == expected_bytes
        return DummyResponse(
            status_code=200, json_data={"pdf_path": "data/pdfs/real_doc.pdf"}
        )

    monkeypatch.setattr(requests, "post", fake_post)

    result = client.save_pdf("real_doc", sample_path)
    assert result == "data/pdfs/real_doc.pdf"


def test_save_image_with_real_file(monkeypatch, client):
    sample_img = Path("tests/resources/sample_page_p3.jpg")
    expected_bytes = sample_img.read_bytes()

    def fake_post(url, params, files):
        assert url.endswith("/image/save")
        assert params["doc_id"] == "real_doc"
        assert params["page_number"] == 3
        data = files["file"].read()
        assert data == expected_bytes
        return DummyResponse(
            status_code=200, json_data={"image_path": "data/images/real_doc_p3.jpg"}
        )

    monkeypatch.setattr(requests, "post", fake_post)

    result = client.save_image("real_doc", page_number=3, image_file=sample_img)
    assert result == "data/images/real_doc_p3.jpg"


def test_get_pdf_downloads_bytes(monkeypatch, client):
    fake_bytes = b"PDFCONTENT"

    def fake_get(url, params):
        assert url.endswith("/pdf/get")
        assert params["doc_id"] == "real_doc"
        return DummyResponse(status_code=200, content=fake_bytes)

    monkeypatch.setattr(requests, "get", fake_get)

    data = client.get_pdf("real_doc")
    assert data == fake_bytes


def test_get_image_downloads_bytes(monkeypatch, client):
    fake_bytes = b"IMAGECONTENT"

    def fake_get(url, params):
        assert url.endswith("/image/get")
        assert params["doc_id"] == "real_doc"
        assert params["page_number"] == 5
        return DummyResponse(status_code=200, content=fake_bytes)

    monkeypatch.setattr(requests, "get", fake_get)

    data = client.get_image("real_doc", page_number=5)
    assert data == fake_bytes


def test_delete_document_success(monkeypatch, client):
    def fake_delete(url, params):
        assert url.endswith("/document/delete")
        assert params["doc_id"] == "real_doc"
        return DummyResponse(status_code=200)

    monkeypatch.setattr(requests, "delete", fake_delete)

    # Should not raise
    client.delete_document("real_doc")


def test_delete_document_failure(monkeypatch, client):
    def fake_delete(url, params):
        return DummyResponse(status_code=500)

    monkeypatch.setattr(requests, "delete", fake_delete)

    with pytest.raises(requests.HTTPError):
        client.delete_document("real_doc")
