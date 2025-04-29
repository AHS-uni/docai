import time
import asyncio
import pytest
import aiofiles
import aiofiles.os

from pathlib import Path
from docai.storage.storage import StorageService


@pytest.fixture
def svc(tmp_path, monkeypatch):
    service = StorageService(base_path=tmp_path / "data")

    # 1) Each doc_id uses its own lock (no contention)
    monkeypatch.setattr(service, "_get_lock", lambda doc_id: asyncio.Lock())

    # 2) Fake aiofiles.open → returns an async-context-manager with a 0.1s write delay
    def fake_open(path, mode):
        class FakeFile:
            async def write(self, data):
                await asyncio.sleep(0.1)

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                pass

        return FakeFile()

    monkeypatch.setattr(aiofiles, "open", fake_open)

    # 3) Fake exists/remove/listdir to each cost 0.1s
    async def fake_exists(path_str):
        await asyncio.sleep(0.1)
        return True

    async def fake_remove(path_str):
        await asyncio.sleep(0.1)

    async def fake_listdir(dir_str):
        await asyncio.sleep(0.1)
        return []

    monkeypatch.setattr(aiofiles.os.path, "exists", fake_exists)
    monkeypatch.setattr(aiofiles.os, "remove", fake_remove)
    monkeypatch.setattr(aiofiles.os, "listdir", fake_listdir)

    return service


# ── SAVE parallelism ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_save_pdf_parallelism(svc):
    start = time.monotonic()
    await asyncio.gather(
        svc.save_pdf("docA", b"X"),
        svc.save_pdf("docB", b"Y"),
    )
    elapsed = time.monotonic() - start
    assert 0.09 < elapsed < 0.15, f"PDF save not parallel: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_save_image_parallelism(svc):
    start = time.monotonic()
    await asyncio.gather(
        svc.save_image("imgA", 0, b"X"),
        svc.save_image("imgB", 1, b"Y"),
    )
    elapsed = time.monotonic() - start
    assert 0.09 < elapsed < 0.15, f"Image save not parallel: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_mixed_save_parallelism(svc):
    start = time.monotonic()
    await asyncio.gather(
        svc.save_pdf("mixed", b"P"),
        svc.save_image("mixed", 2, b"I"),
    )
    elapsed = time.monotonic() - start
    assert 0.09 < elapsed < 0.15, f"Mixed save not parallel: {elapsed:.3f}s"


# ── GET parallelism ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_pdf_parallelism(svc):
    start = time.monotonic()
    await asyncio.gather(
        svc.get_pdf_path("docA"),
        svc.get_pdf_path("docB"),
    )
    elapsed = time.monotonic() - start
    assert 0.09 < elapsed < 0.15, f"PDF get not parallel: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_get_image_parallelism(svc):
    start = time.monotonic()
    await asyncio.gather(
        svc.get_image_path("imgA", 0),
        svc.get_image_path("imgB", 1),
    )
    elapsed = time.monotonic() - start
    assert 0.09 < elapsed < 0.15, f"Image get not parallel: {elapsed:.3f}s"


# ── DELETE parallelism ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_delete_document_parallelism(svc, tmp_path):
    # Prepare two PDFs under distinct doc_ids
    for doc in ("docA", "docB"):
        pdfp = tmp_path / "data" / "pdfs" / f"{doc}.pdf"
        pdfp.parent.mkdir(parents=True, exist_ok=True)
        pdfp.write_bytes(b"x")

    start = time.monotonic()
    # delete runs three 0.1s sleeps in parallel → ~0.3s total
    await asyncio.gather(
        svc.delete_document("docA"),
        svc.delete_document("docB"),
    )
    elapsed = time.monotonic() - start
    assert 0.29 < elapsed < 0.35, f"Delete not parallel: {elapsed:.3f}s"


@pytest.mark.asyncio
async def test_mixed_get_delete_parallelism(svc):
    # Prepare one PDF for get, none for delete
    pdfp = svc.base_path / "pdfs" / "M1.pdf"
    pdfp.parent.mkdir(parents=True, exist_ok=True)
    pdfp.write_bytes(b"x")

    start = time.monotonic()
    results = await asyncio.gather(
        svc.get_pdf_path("M1"),
        svc.delete_document("M2"),
    )
    elapsed = time.monotonic() - start

    assert isinstance(results[0], Path)
    assert results[1] is None
    # get costs 0.1s, delete costs 0.3s → ~0.3s total
    assert 0.29 < elapsed < 0.35, f"Mixed get/delete not parallel: {elapsed:.3f}s"
