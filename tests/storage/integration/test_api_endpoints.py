# tests/integration/test_api_endpoints.py
import pytest
from pathlib import Path


@pytest.mark.integration
def test_full_pdf_flow(test_client, tmp_path):
    # Redirect the storage base dir
    from docai.storage.config import BASE_PATH as _old
    import docai.storage.config as cfg

    cfg.BASE_PATH = tmp_path
    # reload service binding
    from docai.storage.storage import StorageService
    import docai.storage.api as api_mod

    api_mod.s_service = StorageService(tmp_path)

    doc_id = "flow1"
    pdf_bytes = b"%PDF-1.0 test"
    # Save
    r = test_client.post(
        "/pdf/save",
        params={"doc_id": doc_id},
        files={"file": ("a.pdf", pdf_bytes, "application/pdf")},
    )
    assert r.status_code == 200

    # Get
    r2 = test_client.get(f"/pdf/get?doc_id={doc_id}")
    assert r2.status_code == 200
    assert r2.content == pdf_bytes

    # Delete
    r3 = test_client.delete(f"/document/delete?doc_id={doc_id}")
    assert r3.status_code == 200

    # Now 404
    r4 = test_client.get(f"/pdf/get?doc_id={doc_id}")
    assert r4.status_code == 404
