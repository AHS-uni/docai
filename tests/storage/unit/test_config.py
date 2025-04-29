from pathlib import Path
import importlib
from pathlib import Path

from docai.storage import config


def test_host_default(monkeypatch):
    monkeypatch.delenv("STORAGE_HOST", raising=False)
    importlib.reload(config)
    assert config.HOST == "0.0.0.0"


def test_host_override(monkeypatch):
    monkeypatch.setenv("STORAGE_HOST", "127.231.19.9")
    importlib.reload(config)
    assert config.HOST == "127.231.19.9"


def test_port_default(monkeypatch):
    monkeypatch.delenv("STORAGE_PORT", raising=False)
    importlib.reload(config)
    assert config.PORT == 8000


def test_port_override(monkeypatch):
    monkeypatch.setenv("STORAGE_PORT", "8080")
    importlib.reload(config)
    assert config.PORT == 8080


def test_client_limits_positive():
    assert config.CLIENT_REQUEST_TIMEOUT_SECONDS > 0.0
    assert config.CLIENT_MAX_CONNECTIONS > 0
    assert config.CLIENT_MAX_KEEPALIVE_CONNECTIONS > 0


def test_base_path_default(monkeypatch):
    monkeypatch.delenv("STORAGE_BASE_PATH", raising=False)
    importlib.reload(config)
    assert config.BASE_PATH == Path("data")


def test_base_path_override(monkeypatch):
    monkeypatch.setenv("STORAGE_BASE_PATH", "/tmp/foo")
    importlib.reload(config)
    assert config.BASE_PATH == Path("/tmp/foo")
