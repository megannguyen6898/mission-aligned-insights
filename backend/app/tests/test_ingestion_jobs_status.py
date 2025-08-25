from pathlib import Path
from fastapi.testclient import TestClient
from jose import jwt
import os
import sys

sys.path.append(str(Path(__file__).resolve().parents[3]))

# Required environment variables
os.environ["database_url"] = "sqlite:///./test.db"
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
from backend.app.models.ingestion_jobs import IngestionJob, IngestionJobStatus
from backend.app.api import deps as deps_module
from backend.app.routes.ingest import jobs as jobs_route

# Reset database
db_path = Path("test.db")
if db_path.exists():
    db_path.unlink()

Base.metadata.create_all(bind=engine)

# Seed user and upload
_db = SessionLocal()
user = User(id=2, email="user2@example.com", hashed_password="x", name="Test2")
upload = Upload(
    org_id=123,
    user_id=2,
    filename="data.csv",
    mime_type="text/csv",
    size=100,
    object_key="obj",
    status=UploadStatus.completed,
)
_db.add_all([user, upload])
_db.commit()
_db.close()


def _fake_verify_token(token: str):
    try:
        return jwt.decode(token, os.environ["jwt_secret"], algorithms=["HS256"])
    except Exception:
        return None


deps_module.verify_token = _fake_verify_token
jobs_route.verify_token = _fake_verify_token

client = TestClient(app)


def make_token(org_id=123):
    payload = {"sub": "2", "type": "access", "org_id": org_id}
    return jwt.encode(payload, os.environ["jwt_secret"], algorithm="HS256")


def test_create_and_get_job():
    token = make_token()
    response = client.post(
        "/ingest/jobs",
        json={"upload_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    db = SessionLocal()
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    assert job is not None
    assert job.status == IngestionJobStatus.queued
    assert job.org_id == 123
    db.close()

    response = client.get(
        f"/ingest/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "queued", "error": None}


def test_org_scoped_visibility():
    token1 = make_token(org_id=123)
    token2 = make_token(org_id=999)
    response = client.post(
        "/ingest/jobs",
        json={"upload_id": 1},
        headers={"Authorization": f"Bearer {token1}"},
    )
    job_id = response.json()["job_id"]

    response = client.get(
        f"/ingest/jobs/{job_id}", headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 404


def test_status_and_error_returned():
    token = make_token()
    response = client.post(
        "/ingest/jobs",
        json={"upload_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    job_id = response.json()["job_id"]

    db = SessionLocal()
    job = db.query(IngestionJob).filter(IngestionJob.id == job_id).first()
    job.status = IngestionJobStatus.failed
    job.error_json = {"row": 1, "msg": "bad"}
    db.commit()
    db.close()

    response = client.get(
        f"/ingest/jobs/{job_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {"status": "failed", "error": {"row": 1, "msg": "bad"}}
