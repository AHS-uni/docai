import pytest
import io
import httpx
from docai.storage.client import StorageClient

SAMPLE_PDF = b"%PDF-1.4\n%EOF"
SAMPLE_JPEG = b"\xff\xd8\xff\xd9"


@pytest.mark.asyncio
async def test_client_pdf_cycle(async_api_client):
    client = StorageClient("http://testserver")
    # route HTTPX calls into the same ASGI app
    client._client = async_api_client

    path = await client.save_pdf("xcd", io.BytesIO(SAMPLE_PDF))
    assert path.endswith("xcd.pdf")

    data = await client.get_pdf("xcd")
    assert data == SAMPLE_PDF


@pytest.mark.asyncio
async def test_client_image_cycle(async_api_client):
    client = StorageClient("http://testserver")
    client._client = async_api_client

    path = await client.save_image("ycd", 2, io.BytesIO(SAMPLE_JPEG))
    assert path.endswith("ycd_p2.jpg")

    data = await client.get_image("ycd", 2)
    assert data == SAMPLE_JPEG


@pytest.mark.asyncio
async def test_client_delete_behavior(async_api_client):
    client = StorageClient("http://testserver")
    client._client = async_api_client

    # create
    await client.save_pdf("delme", io.BytesIO(SAMPLE_PDF))
    # delete
    await client.delete_document("delme")

    # should raise on get
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_pdf("delme")
