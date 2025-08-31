from pathlib import Path
from hashlib import sha256
from fastapi.testclient import TestClient

import os
import sys
sys.path.append(str(Path(__file__).resolve().parents[3]))
os.environ.setdefault("database_url", "sqlite://")
os.environ.setdefault("jwt_secret_key", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")
from backend.app.main import app

client = TestClient(app)


def compute_file_hash(path: Path) -> str:
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def test_template_download():
    response = client.get("/public/template")
    assert response.status_code == 200
    assert (
        response.headers["content-type"]
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert int(response.headers["content-length"]) > 5000
    assert len(response.content) > 5000

    etag = response.headers.get("etag")
    assert etag
    assert response.headers.get("cache-control") == "public, max-age=86400"

    # ETag should remain the same across requests
    response2 = client.get("/public/template")
    assert response2.headers.get("etag") == etag

    # ETag should match actual file hash
    template_path = Path(__file__).resolve().parents[1] / "assets" / "templates" / "universal_template.xlsx"
    assert etag == compute_file_hash(template_path)
