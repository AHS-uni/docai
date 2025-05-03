import importlib

import pytest
from httpx import ASGITransport, AsyncClient

import docai.storage.config as config_mod
from docai.storage.api import app
from docai.storage.client import StorageClient
from docai.storage.service import StorageService


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    # 1) Redirect BASE_PATH in config to a fresh tmp_path
    monkeypatch.setenv("STORAGE_BASE_PATH", str(tmp_path))
    importlib.reload(config_mod)

    # 2) Rebind the API’s global StorageService to our temp directory
    new_svc = StorageService(config_mod.BASE_PATH)
    import docai.storage.api as api_mod

    api_mod.s_service = new_svc

    yield
    # tmp_path is auto-cleaned, no teardown needed


@pytest.fixture
async def api_client():
    """
    An httpx.AsyncClient that dispatches to FastAPI via ASGITransport.
    No real HTTP server needed.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client


@pytest.fixture
async def storage_client():
    """
    A StorageClient pointed at our in-process API via ASGITransport.
    """
    # 1) Create the ASGI-backed HTTPX client
    transport = ASGITransport(app=app)
    asgi_httpx = AsyncClient(transport=transport, base_url="http://testserver")

    # 2) Instantiate your StorageClient against the same base_url
    client = StorageClient("http://testserver")
    # 3) Tear down its real _client, replace with our ASGI-backed one
    await client._client.aclose()  # close the real pool
    client._client = asgi_httpx

    # 4) Yield the patched StorageClient
    try:
        yield client
    finally:
        # 5) Clean up the ASGI client
        await client._client.aclose()
