from io import BytesIO
from pathlib import Path
import os
import sys

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR.parent))
from jose import jwt
import pandas as pd
from fastapi.testclient import TestClient

# Setup environment
os.environ.setdefault("database_url", "sqlite:///./uploads_api.db")
os.environ.setdefault("jwt_secret_key", "test")
os.environ.setdefault("secret_key", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("STORAGE_PROVIDER", "s3")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("S3_UPLOAD_PREFIX", "uploads/")
os.environ.setdefault("AUTH0_DOMAIN", "test")

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models.user import User
from backend.app.routes import uploads as uploads_route
from backend.app.ingest.validators import TEMPLATE_SHEETS
from backend.worker.tasks.ingest_excel_or_csv import ingest_excel_or_csv
from backend.app.api import deps as deps_module
object.__setattr__(deps_module.settings, "auth0_domain", "test")
object.__setattr__(deps_module.settings, "auth0_audience", "test")
def _fake_verify_token(token: str):
    try:
        return jwt.decode(token, os.environ["jwt_secret_key"], algorithms=["HS256"])
    except Exception:
        return None
deps_module.verify_token = _fake_verify_token
uploads_route.verify_token = _fake_verify_token

# Prepare database
_db_path = Path("uploads_api.db")
if _db_path.exists():
    _db_path.unlink()
Base.metadata.create_all(bind=engine)
_db = SessionLocal()
user = User(email="uploads@example.com", hashed_password="x", name="T")
_db.add(user)
_db.commit()
_db.refresh(user)
USER_ID = user.id
_db.close()

# Dummy S3 client
class DummyS3:
    def __init__(self):
        self.store = {}

    def put_object(self, Bucket, Key, Body, ContentType):
        self.store[Key] = Body

    def get_object(self, Bucket, Key):
        return {"Body": BytesIO(self.store[Key])}

dummy_s3 = DummyS3()
uploads_route.get_s3_client = lambda: dummy_s3

# Stub celery task
class DummyAsyncResult:
    def __init__(self, id):
        self.id = id

def _fake_delay(job_id):
    return DummyAsyncResult(job_id)

ingest_excel_or_csv.delay = _fake_delay

client = TestClient(app)


def make_token():
    payload = {"sub": str(USER_ID), "type": "access", "org_id": 123, "roles": ["org_member"]}
    return jwt.encode(payload, os.environ["jwt_secret_key"], algorithm="HS256")


def _build_valid_workbook():
    sheets = {}
    for name, cols in TEMPLATE_SHEETS.items():
        data = {}
        for col, typ in cols.items():
            if typ is int:
                data[col] = [1]
            elif typ is float:
                data[col] = [1.0]
            else:
                data[col] = ["x"]
        sheets[name] = pd.DataFrame(data)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    buf.seek(0)
    return buf.getvalue()


def _build_invalid_workbook():
    # Missing the 'Funding & Resources' sheet
    sheets = {}
    for name, cols in TEMPLATE_SHEETS.items():
        if name == "Funding & Resources":
            continue
        sheets[name] = pd.DataFrame({c: [] for c in cols.keys()})
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    buf.seek(0)
    return buf.getvalue()


def test_upload_validate_ingest_flow():
    token = make_token()
    files = {"file": ("data.xlsx", _build_valid_workbook(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/uploads", files=files, headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 201
    upload_id = res.json()["upload_id"]

    res = client.post(f"/api/uploads/{upload_id}/validate", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "validated"

    res = client.get(f"/api/uploads/{upload_id}", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["status"] == "validated"

    res = client.post(f"/api/uploads/{upload_id}/ingest", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 202
    assert "job_id" in res.json()


def test_upload_validation_failure():
    token = make_token()
    files = {"file": ("data.xlsx", _build_invalid_workbook(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    res = client.post("/api/uploads", files=files, headers={"Authorization": f"Bearer {token}"})
    upload_id = res.json()["upload_id"]

    res = client.post(f"/api/uploads/{upload_id}/validate", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "failed"
    assert body["errors"]
