import pytest
from pydantic import ValidationError
from docai.storage.schemas import (
    SavePDFData,
    SavePDFResponse,
    SaveImageData,
    SaveImageResponse,
    DeleteDocumentData,
    DeleteDocumentResponse,
)
from docai.shared.models.dto.meta import Meta


def test_save_pdf_data_and_response():
    data = SavePDFData(doc_id="123", pdf_path="out/123.pdf")
    assert data.doc_id == "123"
    assert data.pdf_path.endswith("123.pdf")

    meta = Meta(timestamp="2025-01-01T00:00:00Z", version="v1")
    resp = SavePDFResponse(data=data, meta=meta)
    assert resp.data == data
    assert resp.meta == meta


def test_save_image_data_and_response():
    data = SaveImageData(doc_id="docA", page_number=0, image_path="img/docA_0.jpg")
    assert data.page_number == 0

    meta = Meta(timestamp="2025-01-01T00:00:00Z", version="v2")
    resp = SaveImageResponse(data=data, meta=meta)
    assert resp.data.page_number == 0
    assert resp.meta.version == "v2"


def test_delete_document_data_and_response():
    data = DeleteDocumentData(doc_id="del1", detail="deleted ok")
    assert "deleted" in data.detail

    meta = Meta(timestamp="2025-01-01T00:00:00Z", version="v3")
    resp = DeleteDocumentResponse(data=data, meta=meta)
    assert resp.data == data
    assert resp.meta == meta


def test_invalid_schema_inputs_raise():
    with pytest.raises(ValidationError):
        SavePDFData(doc_id=None, pdf_path="x.pdf")
    with pytest.raises(ValidationError):
        SaveImageData(doc_id="x", page_number="not-an-int", image_path="y.jpg")
