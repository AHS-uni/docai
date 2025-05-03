# tests/unit/test_storage_service.py
from pathlib import Path

import pytest

from docai.storage.exceptions import (
    DeleteDocumentError,
    ImageNotFoundError,
    PDFNotFoundError,
    SaveImageError,
    SavePDFError,
)
from docai.storage.service import StorageService


@pytest.fixture
def svc(tmp_path):
    # empty on‐disk under tmp_path
    yield StorageService(base_path=tmp_path)


@pytest.mark.asyncio
async def test_save_and_get_pdf(svc):
    data = b"PDFCONTENT"
    path = await svc.save_pdf("d1", data)
    assert path.exists()
    # retrieving path only
    path2 = await svc.get_pdf_path("d1")
    assert path2 == path


@pytest.mark.asyncio
async def test_get_pdf_not_found(svc):
    with pytest.raises(PDFNotFoundError):
        await svc.get_pdf_path("missing")


@pytest.mark.asyncio
async def test_save_and_get_image(svc):
    data = b"IMG"
    path = await svc.save_image("d2", 5, data)
    assert path.exists()
    p2 = await svc.get_image_path("d2", 5)
    assert p2 == path


@pytest.mark.asyncio
async def test_get_image_not_found(svc):
    with pytest.raises(ImageNotFoundError):
        await svc.get_image_path("x", 0)


@pytest.mark.asyncio
async def test_delete_document(svc):
    # create PDF+images
    await svc.save_pdf("d3", b"P")
    await svc.save_image("d3", 0, b"I0")
    await svc.save_image("d3", 1, b"I1")
    # delete
    await svc.delete_document("d3")
    with pytest.raises(PDFNotFoundError):
        await svc.get_pdf_path("d3")
    with pytest.raises(ImageNotFoundError):
        await svc.get_image_path("d3", 0)
    with pytest.raises(ImageNotFoundError):
        await svc.get_image_path("d3", 1)


@pytest.mark.asyncio
async def test_delete_nonexistent_is_noop(svc):
    # Should not raise
    await svc.delete_document("doesnotexist")
