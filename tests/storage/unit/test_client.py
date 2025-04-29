import io
import time
from pathlib import Path

import pytest
import respx
import asyncio
import httpx
from httpx import ReadTimeout

from docai.storage.client import StorageClient

RESOURCES = Path(__file__).parent.parent.parent / "resources"


@pytest.mark.asyncio
async def test_client_init_parameters(monkeypatch):
    seen = {}

    class DummyAsyncClient:
        def __init__(self, *args, timeout=None, limits=None, **kwargs):
            seen["timeout"] = timeout
            seen["limits"] = limits

        async def aclose(self):
            pass

    monkeypatch.setattr(httpx, "AsyncClient", DummyAsyncClient)
    client = StorageClient(
        "http://testserver", timeout=2.5, max_connections=3, max_keepalive_connections=4
    )

    # httpx.Timeout stores our 2.5s in all four timeout slots:
    to: httpx.Timeout = seen["timeout"]
    assert isinstance(to, httpx.Timeout)
    assert to.read == pytest.approx(2.5)
    assert to.connect == pytest.approx(2.5)
    assert to.write == pytest.approx(2.5)
    assert to.pool == pytest.approx(2.5)

    limits: httpx.Limits = seen["limits"]
    assert limits.max_connections == 3
    assert limits.max_keepalive_connections == 4


@pytest.mark.asyncio
async def test_client_context_manager(monkeypatch):
    closed = {"flag": False}

    class DummyAsyncClient:
        async def aclose(self):
            closed["flag"] = True

    monkeypatch.setattr(httpx, "AsyncClient", lambda *args, **kw: DummyAsyncClient())
    async with StorageClient("http://testserver") as client:
        # inside context manager
        assert client is not None
        # on exit, our dummy aclose should have been called
    assert closed["flag"] is True


@respx.mock
@pytest.mark.asyncio
async def test_save_pdf_happy():
    pdf_path = "data/pdfs/sample_1.pdf"
    r = respx.post("http://testserver/pdf/save").mock(
        return_value=httpx.Response(200, json={"data": {"pdf_path": pdf_path}})
    )

    sample = RESOURCES / "sample_1.pdf"
    async with StorageClient("http://testserver") as client:
        result = await client.save_pdf("sample_1", sample)
        assert result == pdf_path
        assert r.called


@respx.mock
@pytest.mark.asyncio
async def test_save_pdf_http_error():
    respx.post("http://testserver/pdf/save").mock(return_value=httpx.Response(400))
    sample = RESOURCES / "sample_1.pdf"
    async with StorageClient("http://testserver") as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.save_pdf("bad", sample)


@respx.mock
@pytest.mark.asyncio
async def test_save_pdf_with_file_like():
    # also accept file-like object
    pdf_path = "data/pdfs/doc.pdf"
    respx.post("http://testserver/pdf/save").mock(
        return_value=httpx.Response(200, json={"data": {"pdf_path": pdf_path}})
    )
    sample_bytes = (RESOURCES / "sample_1.pdf").read_bytes()
    file_like = io.BytesIO(sample_bytes)
    file_like.name = "foobar.pdf"

    async with StorageClient("http://testserver") as client:
        result = await client.save_pdf("doc", file_like)
        assert result == pdf_path


@respx.mock
@pytest.mark.asyncio
async def test_save_image_happy():
    img_path = "data/images/sample_1_p1.jpg"
    respx.post("http://testserver/image/save").mock(
        return_value=httpx.Response(200, json={"data": {"image_path": img_path}})
    )
    sample = RESOURCES / "sample_1_p1.jpg"
    async with StorageClient("http://testserver") as client:
        result = await client.save_image("sample_1", 1, sample)
        assert result == img_path


@respx.mock
@pytest.mark.asyncio
async def test_save_image_http_error():
    respx.post("http://testserver/image/save").mock(return_value=httpx.Response(500))
    sample = RESOURCES / "sample_1_p1.jpg"
    async with StorageClient("http://testserver") as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.save_image("sample_1", 1, sample)


@respx.mock
@pytest.mark.asyncio
async def test_get_pdf_happy():
    content = (RESOURCES / "sample_2.pdf").read_bytes()
    respx.get("http://testserver/pdf/get").mock(
        return_value=httpx.Response(200, content=content)
    )
    async with StorageClient("http://testserver") as client:
        data = await client.get_pdf("sample_2")
        assert data == content


@respx.mock
@pytest.mark.asyncio
async def test_get_pdf_http_error():
    respx.get("http://testserver/pdf/get").mock(return_value=httpx.Response(404))
    async with StorageClient("http://testserver") as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_pdf("missing")


@respx.mock
@pytest.mark.asyncio
async def test_get_image_happy():
    content = (RESOURCES / "sample_1_p1.jpg").read_bytes()
    respx.get("http://testserver/image/get").mock(
        return_value=httpx.Response(200, content=content)
    )
    async with StorageClient("http://testserver") as client:
        data = await client.get_image("sample_1", 1)
        assert data == content


@respx.mock
@pytest.mark.asyncio
async def test_get_image_http_error():
    respx.get("http://testserver/image/get").mock(return_value=httpx.Response(500))
    async with StorageClient("http://testserver") as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_image("sample_1", 1)


@respx.mock
@pytest.mark.asyncio
async def test_delete_document_happy():
    respx.delete("http://testserver/document/delete").mock(
        return_value=httpx.Response(200, json={})
    )
    async with StorageClient("http://testserver") as client:
        # should complete without error
        await client.delete_document("whatever")


@respx.mock
@pytest.mark.asyncio
async def test_delete_document_http_error():
    respx.delete("http://testserver/document/delete").mock(
        return_value=httpx.Response(500)
    )
    async with StorageClient("http://testserver") as client:
        with pytest.raises(httpx.HTTPStatusError):
            await client.delete_document("whatever")


@respx.mock
@pytest.mark.asyncio
async def test_full_pdf_flow_unit():
    # stub save
    respx.post("http://testserver/pdf/save").mock(
        return_value=httpx.Response(200, json={"data": {"pdf_path": "p.pdf"}})
    )
    # stub get
    pdf_bytes = (RESOURCES / "sample_5.pdf").read_bytes()
    respx.get("http://testserver/pdf/get").mock(
        return_value=httpx.Response(200, content=pdf_bytes)
    )
    # stub delete
    respx.delete("http://testserver/document/delete").mock(
        return_value=httpx.Response(200, json={})
    )

    sample = RESOURCES / "sample_5.pdf"
    async with StorageClient("http://testserver") as client:
        p = await client.save_pdf("doc5", sample)
        assert p == "p.pdf"
        b = await client.get_pdf("doc5")
        assert b == pdf_bytes
        await client.delete_document("doc5")


@respx.mock
@pytest.mark.asyncio
async def test_full_image_flow_unit():
    # stub save
    respx.post("http://testserver/image/save").mock(
        return_value=httpx.Response(200, json={"data": {"image_path": "i.jpg"}})
    )
    # stub get
    img_bytes = (RESOURCES / "sample_1_p1.jpg").read_bytes()
    respx.get("http://testserver/image/get").mock(
        return_value=httpx.Response(200, content=img_bytes)
    )
    # stub delete
    respx.delete("http://testserver/document/delete").mock(
        return_value=httpx.Response(200, json={})
    )

    sample = RESOURCES / "sample_1_p1.jpg"
    async with StorageClient("http://testserver") as client:
        i = await client.save_image("docimg", 1, sample)
        assert i == "i.jpg"
        b = await client.get_image("docimg", 1)
        assert b == img_bytes
        await client.delete_document("docimg")


@respx.mock
@pytest.mark.asyncio
async def test_base_url_trailing_slash():
    # route without double-slash
    called = respx.post("http://svc/pdf/save").mock(
        return_value=httpx.Response(200, json={"data": {"pdf_path": "p"}})
    )

    async with StorageClient("http://svc/") as client:
        await client.save_pdf("d", Path("tests/resources/sample_1.pdf"))
        assert called.called


@respx.mock
@pytest.mark.asyncio
async def test_save_pdf_file_like_no_name():
    route = respx.post("http://svc/pdf/save").mock(
        return_value=httpx.Response(200, json={"data": {"pdf_path": "pdf1"}})
    )

    bio = io.BytesIO(b"PDF")
    # remove name attribute if any
    if hasattr(bio, "name"):
        delattr(bio, "name")

    async with StorageClient("http://svc") as client:
        await client.save_pdf("d1", bio)

    # ensure the multipart used 'file' as filename
    assert b'filename="file"' in route.calls[0].request.content


@respx.mock
@pytest.mark.asyncio
async def test_save_pdf_missing_data_raises():
    respx.post("http://svc/pdf/save").mock(return_value=httpx.Response(200, json={}))
    async with StorageClient("http://svc") as client:
        with pytest.raises(KeyError):
            await client.save_pdf("d", Path("tests/resources/sample_1.pdf"))


@pytest.mark.asyncio
async def test_save_pdf_timeout(monkeypatch):
    async def timeout_post(*args, **kwargs):
        raise ReadTimeout("timed out")

    monkeypatch.setattr("httpx.AsyncClient.post", timeout_post)

    async with StorageClient("http://svc", timeout=0.01) as client:
        with pytest.raises(ReadTimeout):
            await client.save_pdf("d", Path("tests/resources/sample_1.pdf"))


@respx.mock
@pytest.mark.asyncio
async def test_client_concurrent_requests():
    # simulate a 0.1s delay in response
    async def delayed_response(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json={"data": {"pdf_path": "p"}})

    respx.post("http://svc/pdf/save").mock(side_effect=delayed_response)

    async with StorageClient("http://svc", max_connections=2) as client:
        start = time.monotonic()
        await asyncio.gather(
            client.save_pdf("a", Path("tests/resources/sample_1.pdf")),
            client.save_pdf("b", Path("tests/resources/sample_2.pdf")),
        )
        elapsed = time.monotonic() - start
        # with 2 max_connections, both should run in parallel -> ~0.1s
        assert elapsed < 0.15
