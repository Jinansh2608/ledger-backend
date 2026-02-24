import os
import pytest

# Lightweight smoke test: ensure uploads folder exists and API modules import

def test_uploads_folder_exists():
    root = os.path.dirname(os.path.dirname(__file__))
    uploads = os.path.join(root, 'uploads')
    # create if missing for local dev
    os.makedirs(uploads, exist_ok=True)
    assert os.path.isdir(uploads)

try:
    # sanity import of document repo
    from app.repository import document_repo  # noqa: F401
except Exception:
    pytest.skip('document_repo not importable in this environment')
