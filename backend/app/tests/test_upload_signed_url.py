from pathlib import Path
from fastapi.testclient import TestClient
from jose import jwt
import os
import sys
import types

jinja2_stub = types.SimpleNamespace(
    Environment=lambda *a, **k: types.SimpleNamespace(
        get_template=lambda *a, **k: types.SimpleNamespace(render=lambda **kw: "")
    ),
    FileSystemLoader=lambda *a, **k: None,
    select_autoescape=lambda *a, **k: None,
)
sys.modules.setdefault("jinja2", jinja2_stub)

sys.path.append(str(Path(__file__).resolve().parents[3]))

# Required environment variables
os.environ["database_url"] = "sqlite:///./test_upload.db"
os.environ.setdefault("jwt_secret", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")

# Storage configuration
os.environ.setdefault("STORAGE_PROVIDER", "s3")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("S3_REGION", "us-east-1")
os.environ.setdefault("S3_UPLOAD_PREFIX", "raw/")
os.environ.setdefault("MAX_UPLOAD_MB", "25")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "test")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "test")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models.user import User
from backend.app.models.uploads import Upload, UploadStatus
from backend.app.api import deps as deps_module
from backend.app.routes.ingest import upload as upload_route

db_path = Path("test_upload.db")
if db_path.exists():
    db_path.unlink()

Base.metadata.create_all(bind=engine)

db = SessionLocal()
user = User(id=1, email="user@example.com", hashed_password="x", name="Test")
db.add(user)
db.commit()
db.close()


def _fake_verify_token(token: str):
    try:
        return jwt.decode(token, os.environ["jwt_secret"], algorithms=["HS256"])
    except Exception:
        return None


deps_module.verify_token = _fake_verify_token
upload_route.verify_token = _fake_verify_token

client = TestClient(app)


def make_token(roles=None):
    payload = {"sub": "1", "type": "access", "org_id": 123}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, os.environ["jwt_secret"], algorithm="HS256")


def test_signed_url_xlsx():
    token = make_token(roles=["org_member"])
    body = {
        "filename": "data.xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size": 1024,
    }
    response = client.post(
        "/ingest/uploads:signed-url",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["upload_id"] > 0
    assert "url" in data
    assert "fields" in data

    db = SessionLocal()
    upload = db.query(Upload).filter(Upload.id == data["upload_id"]).first()
    assert upload is not None
    assert upload.status == UploadStatus.pending
    assert upload.mime_type == body["mime"]
    assert upload.size == body["size"]
    assert upload.user_id == 1
    db.close()


def test_signed_url_csv():
    token = make_token(roles=["org_member"])
    body = {
        "filename": "data.csv",
        "mime": "text/csv",
        "size": 2048,
    }
    response = client.post(
        "/ingest/uploads:signed-url",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_signed_url_invalid_mime():
    token = make_token(roles=["org_member"])
    body = {
        "filename": "data.pdf",
        "mime": "application/pdf",
        "size": 100,
    }
    response = client.post(
        "/ingest/uploads:signed-url",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 415


def test_signed_url_requires_role():
    token = make_token()  # no roles
    body = {
        "filename": "data.xlsx",
        "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "size": 1024,
    }
    response = client.post(
        "/ingest/uploads:signed-url",
        json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403

