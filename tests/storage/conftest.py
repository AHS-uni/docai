# tests/conftest.py
import importlib
import pytest
from fastapi.testclient import TestClient

import docai.storage.config as config_mod
from docai.storage.storage import StorageService
from docai.storage.api import app


@pytest.fixture(scope="session")
def test_client():
    """A TestClient against the live FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch):
    """
    Redirect BASE_PATH → a fresh tmp_path for every test,
    reload config & rebind the service in api.py.
    """
    # point STORAGE_BASE_PATH env var (so config picks it up if ever reloaded)
    monkeypatch.setenv("STORAGE_BASE_PATH", str(tmp_path))
    # reload the config module
    importlib.reload(config_mod)
    # rebind the global StorageService in the API module
    import docai.storage.api as api_mod

    api_mod.s_service = StorageService(config_mod.BASE_PATH)
    yield
    # cleanup happens automatically with tmp_path
