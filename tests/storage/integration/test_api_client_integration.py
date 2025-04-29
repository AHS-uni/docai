import asyncio
from pathlib import Path

import pytest
import httpx

# fixtures from tests/storage/conftest.py:
#  - storage_client
#  - api_client

RESOURCES = Path(__file__).parent.parent.parent / "resources"


# ── Single‐item PDF flows ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pdf_lifecycle_success(storage_client):
    doc_id = "intg_pdf"
    sample = RESOURCES / "sample_1.pdf"

    # save
    saved_path = await storage_client.save_pdf(doc_id, sample)
    assert saved_path.endswith(f"{doc_id}.pdf")

    # get
    data = await storage_client.get_pdf(doc_id)
    assert data == sample.read_bytes()

    # delete
    await storage_client.delete_document(doc_id)

    # get again → 404
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await storage_client.get_pdf(doc_id)
        assert exc.value.response.status_code == 404


@pytest.mark.asyncio
async def test_pdf_get_without_save_returns_404(storage_client):
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await storage_client.get_pdf("no_such_pdf")
        assert exc.value.response.status_code == 404


@pytest.mark.asyncio
async def test_pdf_delete_without_save_is_noop(storage_client):
    await storage_client.delete_document("no_pdf")
    with pytest.raises(httpx.HTTPStatusError):
        await storage_client.get_pdf("no_pdf")


# ── Single‐item Image flows ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_image_lifecycle_success(storage_client):
    doc_id, page = "intg_img", 1
    sample = RESOURCES / "sample_1_p1.jpg"

    # save
    saved_path = await storage_client.save_image(doc_id, page, sample)
    assert saved_path.endswith(f"{doc_id}_p{page}.jpg")

    # get
    data = await storage_client.get_image(doc_id, page)
    assert data == sample.read_bytes()

    # delete
    await storage_client.delete_document(doc_id)

    # get again → 404
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await storage_client.get_image(doc_id, page)
        assert exc.value.response.status_code == 404


@pytest.mark.asyncio
async def test_image_get_without_save_returns_404(storage_client):
    with pytest.raises(httpx.HTTPStatusError) as exc:
        await storage_client.get_image("no_such_img", 1)
        assert exc.value.response.status_code == 404


@pytest.mark.asyncio
async def test_image_delete_without_save_is_noop(storage_client):
    await storage_client.delete_document("no_img")
    with pytest.raises(httpx.HTTPStatusError):
        await storage_client.get_image("no_img", 1)


# ── Batch flows ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_batch_save_and_get_pdfs(storage_client):
    doc_ids = ["sample_1", "sample_2", "sample_5"]
    samples = [RESOURCES / f"{d}.pdf" for d in doc_ids]

    # batch save
    save_paths = await asyncio.gather(
        *(storage_client.save_pdf(d, p) for d, p in zip(doc_ids, samples))
    )
    assert all(sp.endswith(f"{d}.pdf") for d, sp in zip(doc_ids, save_paths))

    # batch get
    contents = await asyncio.gather(*(storage_client.get_pdf(d) for d in doc_ids))
    assert all(c == p.read_bytes() for p, c in zip(samples, contents))


@pytest.mark.asyncio
async def test_batch_get_multiple_pdfs_mixed(storage_client):
    # only sample_1 & sample_2 exist
    for d in ("sample_1", "sample_2"):
        src = RESOURCES / f"{d}.pdf"
        await storage_client._client.post(
            "/pdf/save",
            params={"doc_id": d},
            files={"file": (src.name, src.read_bytes(), "application/pdf")},
        )

    doc_ids = ["sample_1", "missing1", "missing2"]
    results = await asyncio.gather(
        *(storage_client.get_pdf(d) for d in doc_ids),
        return_exceptions=True,
    )
    assert isinstance(results[0], bytes)
    assert (
        isinstance(results[1], httpx.HTTPStatusError)
        and results[1].response.status_code == 404
    )
    assert (
        isinstance(results[2], httpx.HTTPStatusError)
        and results[2].response.status_code == 404
    )


@pytest.mark.asyncio
async def test_batch_delete_multiple_pdfs(storage_client):
    # copy in two PDFs
    for d in ("sample_1", "sample_2"):
        src = RESOURCES / f"{d}.pdf"
        await storage_client._client.post(
            "/pdf/save",
            params={"doc_id": d},
            files={"file": (src.name, src.read_bytes(), "application/pdf")},
        )

    # batch delete
    await asyncio.gather(
        *(storage_client.delete_document(d) for d in ("sample_1", "sample_2"))
    )

    for d in ("sample_1", "sample_2"):
        with pytest.raises(httpx.HTTPStatusError):
            await storage_client.get_pdf(d)


@pytest.mark.asyncio
async def test_batch_save_and_get_images(storage_client):
    doc = "batchimg"
    pages = [1, 2, 3]
    samples = [RESOURCES / f"sample_1_p{p}.jpg" for p in pages]

    # batch save
    save_paths = await asyncio.gather(
        *(storage_client.save_image(doc, p, s) for p, s in zip(pages, samples))
    )
    assert all(sp.endswith(f"{doc}_p{p}.jpg") for p, sp in zip(pages, save_paths))

    # batch get
    contents = await asyncio.gather(*(storage_client.get_image(doc, p) for p in pages))
    assert all(c == s.read_bytes() for s, c in zip(samples, contents))


@pytest.mark.asyncio
async def test_batch_get_multiple_images_mixed(storage_client):
    doc = "miximg"
    # only pages 1 & 3
    for p in (1, 3):
        src = RESOURCES / f"sample_1_p{p}.jpg"
        await storage_client.save_image(doc, p, src)

    tasks = [storage_client.get_image(doc, p) for p in (1, 2, 3)] + [
        storage_client.get_image("no_doc", 1)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    assert isinstance(results[0], bytes)
    assert (
        isinstance(results[1], httpx.HTTPStatusError)
        and results[1].response.status_code == 404
    )
    assert isinstance(results[2], bytes)
    assert (
        isinstance(results[3], httpx.HTTPStatusError)
        and results[3].response.status_code == 404
    )


@pytest.mark.asyncio
async def test_batch_delete_multiple_images(storage_client):
    doc = "delimg"
    for p in (1, 2):
        src = RESOURCES / f"sample_1_p{p}.jpg"
        await storage_client.save_image(doc, p, src)

    await storage_client.delete_document(doc)

    for p in (1, 2):
        with pytest.raises(httpx.HTTPStatusError):
            await storage_client.get_image(doc, p)


# ── Race‐conditions ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_race_save_pdf_same_doc(storage_client):
    a = RESOURCES / "sample_1.pdf"
    b = RESOURCES / "sample_2.pdf"
    paths = await asyncio.gather(
        storage_client.save_pdf("racepdf", a),
        storage_client.save_pdf("racepdf", b),
    )
    assert paths[0] == paths[1]
    final = await storage_client.get_pdf("racepdf")
    assert final in (a.read_bytes(), b.read_bytes())


@pytest.mark.asyncio
async def test_race_get_delete_pdf(storage_client):
    doc = "racepd2"
    sample = RESOURCES / "sample_1.pdf"
    await storage_client.save_pdf(doc, sample)

    results = await asyncio.gather(
        storage_client.get_pdf(doc),
        storage_client.delete_document(doc),
        return_exceptions=True,
    )

    # delete must return None
    r_get, r_del = results
    assert r_del is None

    # get either gives bytes or raises 404
    assert isinstance(r_get, (bytes, httpx.HTTPStatusError))
    if isinstance(r_get, httpx.HTTPStatusError):
        assert r_get.response.status_code == 404
    else:
        assert r_get == sample.read_bytes()


@pytest.mark.asyncio
async def test_race_save_image_same_page(storage_client):
    sample = RESOURCES / "sample_1_p1.jpg"
    paths = await asyncio.gather(
        storage_client.save_image("raceimg", 1, sample),
        storage_client.save_image("raceimg", 1, sample),
    )
    assert paths[0] == paths[1]
    content = await storage_client.get_image("raceimg", 1)
    assert content == sample.read_bytes()


@pytest.mark.asyncio
async def test_race_get_delete_image(storage_client):
    doc, page = "raceimg2", 2
    sample = RESOURCES / f"sample_1_p{page}.jpg"
    await storage_client.save_image(doc, page, sample)

    results = await asyncio.gather(
        storage_client.get_image(doc, page),
        storage_client.delete_document(doc),
        return_exceptions=True,
    )

    r_get, r_del = results
    assert r_del is None

    assert isinstance(r_get, (bytes, httpx.HTTPStatusError))
    if isinstance(r_get, httpx.HTTPStatusError):
        assert r_get.response.status_code == 404
    else:
        assert r_get == sample.read_bytes()


# ── Validation & error‐path tests ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_save_pdf_missing_file_param(api_client):
    r = await api_client.post("/pdf/save", params={"doc_id": "x"})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_save_image_missing_params(api_client):
    r1 = await api_client.post("/image/save", params={"doc_id": "x"})
    assert r1.status_code == 422

    r2 = await api_client.post(
        "/image/save",
        params={"doc_id": "x", "page_number": -1},
        files={"file": ("f.jpg", b"data", "image/jpeg")},
    )
    assert r2.status_code == 422


@pytest.mark.asyncio
async def test_delete_response_schema(storage_client):
    doc = "schemadoc"
    sample = RESOURCES / "sample_1.pdf"
    await storage_client.save_pdf(doc, sample)

    r = await storage_client._client.delete("/document/delete", params={"doc_id": doc})
    payload = r.json()
    assert payload["data"]["doc_id"] == doc
    assert "deleted successfully" in payload["data"]["detail"].lower()
    assert "version" in payload["meta"]
