import pytest
from datetime import datetime, timezone
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


# ––– SavePDFData –––
def test_savepdfdata_valid():
    obj = SavePDFData(
        doc_id="doc_123456789",
        pdf_path="data/pdfs/doc_123456789.pdf",
    )
    assert obj.doc_id.startswith("doc_")
    assert obj.pdf_path.endswith(".pdf")


def test_savepdfdata_invalid():
    with pytest.raises(ValidationError):
        # wrong types for both fields
        SavePDFData(doc_id=123, pdf_path=456)


# ––– SavePDFResponse –––
def test_savepdfresponse_valid():
    data = SavePDFData(
        doc_id="doc_123",
        pdf_path="some/path.pdf",
    )
    meta = Meta(timestamp=datetime.now(timezone.utc), version="1.0.0")
    resp = SavePDFResponse(data=data, meta=meta)
    assert resp.data == data
    assert resp.meta.version == "1.0.0"


def test_savepdfresponse_invalid():
    with pytest.raises(ValidationError):
        # missing both .data and .meta or wrong types
        SavePDFResponse(data={}, meta=None)


# ––– SaveImageData –––
def test_saveimagedata_valid():
    obj = SaveImageData(
        doc_id="doc_img",
        page_number=0,
        image_path="data/images/doc_img_p0.jpg",
    )
    assert obj.page_number == 0
    assert obj.image_path.endswith(".jpg")


def test_saveimagedata_invalid():
    with pytest.raises(ValidationError):
        # None doc_id, negative page_number, wrong image_path type
        SaveImageData(doc_id=None, page_number=-1, image_path=123)


# ––– SaveImageResponse –––
def test_saveimageresponse_valid():
    data = SaveImageData(
        doc_id="doc_img2",
        page_number=2,
        image_path="img2.jpg",
    )
    meta = Meta(timestamp=datetime.now(timezone.utc), version="2.0")
    resp = SaveImageResponse(data=data, meta=meta)
    assert resp.data.doc_id == "doc_img2"
    assert resp.meta.timestamp <= datetime.now(timezone.utc)


def test_saveimageresponse_invalid():
    with pytest.raises(ValidationError):
        SaveImageResponse(data={}, meta={})


# ––– DeleteDocumentData –––
def test_deletedocumentdata_valid():
    obj = DeleteDocumentData(doc_id="doc_del", detail="Document deleted successfully.")
    assert "deleted" in obj.detail.lower()


def test_deletedocumentdata_invalid():
    with pytest.raises(ValidationError):
        # doc_id wrong type, missing detail
        DeleteDocumentData(doc_id=123)


# ––– DeleteDocumentResponse –––
def test_deletedocumentresponse_valid():
    data = DeleteDocumentData(doc_id="doc_del2", detail="OK")
    meta = Meta(timestamp=datetime.now(timezone.utc), version="v1")
    resp = DeleteDocumentResponse(data=data, meta=meta)
    assert resp.data.doc_id == "doc_del2"


def test_deletedocumentresponse_invalid():
    with pytest.raises(ValidationError):
        DeleteDocumentResponse(data=None, meta=None)
