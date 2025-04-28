from pathlib import Path

from docai.storage.config import StorageSettings, BASE_PATH, HOST, PORT, LOG_FILE


def test_defaults(monkeypatch):
    # clear any STORAGE_* environment
    for k in ("STORAGE_BASE_PATH", "STORAGE_HOST", "STORAGE_PORT", "STORAGE_LOG_FILE"):
        monkeypatch.delenv(k, raising=False)

    settings = StorageSettings()
    assert settings.base_path == BASE_PATH
    assert settings.host == HOST
    assert settings.port == PORT
    assert settings.log_file == LOG_FILE


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("STORAGE_BASE_PATH", "/tmp/foo")
    monkeypatch.setenv("STORAGE_HOST", "1.2.3.4")
    monkeypatch.setenv("STORAGE_PORT", "9999")
    monkeypatch.setenv("STORAGE_LOG_FILE", "/tmp/logs/x.log")

    settings = StorageSettings()
    assert settings.base_path == Path("/tmp/foo")
    assert settings.host == "1.2.3.4"
    assert settings.port == 9999
    assert settings.log_file == Path("/tmp/logs/x.log")
