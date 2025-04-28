import pytest
from docai.storage.exceptions import (
    StorageError,
    SavePDFError,
    PDFNotFoundError,
)


def test_hierarchy_and_message():
    assert issubclass(SavePDFError, StorageError)
    assert issubclass(PDFNotFoundError, StorageError)
    e = SavePDFError("oops")
    assert isinstance(e, StorageError)
    assert str(e) == "oops"
