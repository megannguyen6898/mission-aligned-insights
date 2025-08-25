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
from backend.app.models.ingestion_jobs import IngestionJob
from backend.app.models.import_batches import ImportBatch, BatchStatus
from backend.app.api import deps as deps_module
from backend.app.routes.ingest import jobs as jobs_route

# Reset database
_db_path = Path("test.db")
if _db_path.exists():
    _db_path.unlink()

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


def test_batch_created_and_lifecycle_recorded():
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
    assert job.import_batch_id is not None

    batch = db.query(ImportBatch).filter(ImportBatch.id == job.import_batch_id).first()
    assert batch is not None
    assert batch.status == BatchStatus.queued
    assert batch.triggered_by_user_id == "2"
    assert batch.started_at is None
    assert batch.finished_at is None

    batch.set_status(BatchStatus.running)
    db.commit()
    db.refresh(batch)
    assert batch.status == BatchStatus.running
    assert batch.started_at is not None
    assert batch.finished_at is None

    batch.set_status(BatchStatus.success)
    db.commit()
    db.refresh(batch)
    assert batch.status == BatchStatus.success
    assert batch.finished_at is not None
    db.close()
