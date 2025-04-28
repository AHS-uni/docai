# tests/unit/test_client_protocol.py
import pytest
from pathlib import Path
import httpx
from docai.storage.client import StorageClient


class DummyTransport(httpx.AsyncBaseTransport):
    """Always returns the next response in the list."""

    def __init__(self, responses):
        self._responses = responses

    async def handle_async_request(self, request):
        r = self._responses.pop(0)
        return httpx.Response(
            status_code=r["status"],
            json=r.get("json"),
            content=r.get("content", b""),
        )


@pytest.mark.asyncio
async def test_httpx_transport_retries(tmp_path):
    # write a dummy PDF
    pdf = tmp_path / "f.pdf"
    pdf.write_bytes(b"OK")

    # 2 failures, then success
    responses = [
        {"status": 500},
        {"status": 502},
        {"status": 200, "json": {"data": {"pdf_path": "f.pdf"}}},
    ]
    transport = DummyTransport(responses.copy())

    client = StorageClient("http://example.com")
    # swap in our dummy transport
    await client._client.aclose()
    client._client = httpx.AsyncClient(
        base_url=client.base_url,
        transport=transport,
        timeout=httpx.Timeout(1.0),
        limits=httpx.Limits(max_connections=2, max_keepalive_connections=1),
    )

    result = await client.save_pdf("docX", pdf)
    assert result == "f.pdf"
