import os
import sys
import pathlib
from io import BytesIO

import pandas as pd
import pytest
from fastapi.testclient import TestClient

# Ensure project root on path
sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

# Minimal environment for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_mvp.sqlite3")
os.environ.setdefault("JWT_SECRET_KEY", "test")
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("STORAGE_BUCKET", "test-bucket")
os.environ.setdefault("STORAGE_ACCESS_KEY", "test")
os.environ.setdefault("STORAGE_SECRET_KEY", "test")
os.environ.setdefault("STORAGE_ENDPOINT", "http://localhost:9000")
os.environ.setdefault("PUBLIC_UPLOAD_MAX_MB", "10")
os.environ.setdefault("SERVER_UPLOAD_MAX_MB", "25")
os.environ.setdefault("USE_LOCAL_MODEL", "true")
os.environ.setdefault("MODEL_NAME", "llama3.1:8b-instruct")
os.environ.setdefault("OLLAMA_ENDPOINT", "http://ollama:11434")

from backend.app.database import Base, engine, SessionLocal  # noqa: E402
from backend.app.main import app  # noqa: E402
from backend.app.jobs import validate_upload, ingest_dataset  # noqa: E402
from backend.app.models import Dataset, User  # noqa: E402
from backend.app.storage import presign as storage_presign  # noqa: E402


class FakeS3Client:
    def __init__(self):
        self.objects = {}
        self.cors_called = False

    def put_object(self, Bucket, Key, Body, ContentType=None):
        payload = Body if isinstance(Body, (bytes, bytearray)) else Body.read()
        self.objects[(Bucket, Key)] = bytes(payload)

    def get_object(self, Bucket, Key):
        data = self.objects[(Bucket, Key)]
        return {"Body": BytesIO(data)}

    def generate_presigned_url(self, ClientMethod, Params, ExpiresIn):  # noqa: D401
        return f"https://fake-s3.local/{Params['Key']}"

    def put_bucket_cors(self, Bucket, CORSConfiguration):
        self.cors_called = True

    def head_bucket(self, Bucket):  # pragma: no cover - used in health check
        if (Bucket, None) not in self.objects:
            self.objects[(Bucket, None)] = b""
        return {}


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def fake_s3(monkeypatch):
    client = FakeS3Client()
    monkeypatch.setattr("backend.app.storage.s3_client.get_s3_client", lambda: client)
    storage_presign._cors_configured = False  # reset between tests
    return client


@pytest.fixture()
def fastapi_client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def force_sync_jobs(monkeypatch):
    def _immediate_validation(upload_id: int, workflow_id: str):
        validate_upload(upload_id, workflow_id)
        return type("Job", (), {"id": workflow_id})

    def _immediate_ingest(dataset_id: str, workflow_id: str):
        ingest_dataset(dataset_id, workflow_id)
        return type("Job", (), {"id": workflow_id})

    monkeypatch.setattr("backend.app.jobs.enqueue_validation", _immediate_validation)
    monkeypatch.setattr("backend.app.jobs.enqueue_ingest", _immediate_ingest)
    monkeypatch.setattr("backend.app.routes.mvp.uploads.enqueue_validation", _immediate_validation)
    monkeypatch.setattr("backend.app.routes.mvp.workflows.enqueue_ingest", _immediate_ingest)


def ensure_user():
    session = SessionLocal()
    exists = session.query(User).first()
    if not exists:
        user = User(email="demo@example.com", hashed_password="hashed", name="Demo User")
        session.add(user)
        session.commit()
    session.close()


def create_sample_workbook() -> bytes:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=5, freq="D"),
            "region": ["North", "South", "East", "West", "North"],
            "impact": [10, 20, 15, 18, 30],
        }
    )
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.read()


def get_first_dataset():
    session = SessionLocal()
    dataset = session.query(Dataset).first()
    session.close()
    return dataset


def run_upload_flow(fastapi_client, fake_s3):
    ensure_user()
    workbook_bytes = create_sample_workbook()
    presign_resp = fastapi_client.post(
        "/uploads/presign",
        json={
            "workspace_id": 1,
            "filename": "impact.xlsx",
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "size_bytes": len(workbook_bytes),
        },
    )
    assert presign_resp.status_code == 200
    data = presign_resp.json()
    upload_id = data["upload_id"]
    storage_key = data["storage_key"]

    fake_s3.put_object(
        Bucket=os.environ["STORAGE_BUCKET"],
        Key=storage_key,
        Body=workbook_bytes,
        ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    complete_resp = fastapi_client.post(f"/uploads/{upload_id}/complete")
    assert complete_resp.status_code == 200
    summary = complete_resp.json()
    assert summary["upload"]["state"] == "succeeded"

    workflow_resp = fastapi_client.get(f"/uploads/{upload_id}/workflow")
    dataset_id = workflow_resp.json()["validate"].get("dataset_id")
    assert dataset_id

    ingest_resp = fastapi_client.post(f"/workflows/{dataset_id}/ingest")
    assert ingest_resp.status_code == 200
    assert ingest_resp.json()["state"] in {"queued", "succeeded"}

    dataset_resp = fastapi_client.get(f"/datasets/{dataset_id}")
    assert dataset_resp.status_code == 200
    payload = dataset_resp.json()
    assert payload["row_count"] == 5
    assert len(payload["schema"]) >= 3
    return dataset_id


def test_upload_validate_ingest_flow(fastapi_client, fake_s3):
    dataset_id = run_upload_flow(fastapi_client, fake_s3)
    assert dataset_id is not None


def test_dashboards_generation_returns_specs(fastapi_client, fake_s3):
    run_upload_flow(fastapi_client, fake_s3)
    dataset = get_first_dataset()
    assert dataset is not None

    resp = fastapi_client.post("/dashboards/generate", json={"dataset_id": str(dataset.id)})
    assert resp.status_code == 200
    charts = resp.json()["charts"]
    assert charts, "Expected at least one chart"
    for chart in charts:
        assert "spec" in chart
        assert "data" in chart["spec"]


def test_ai_route_returns_answer(monkeypatch, fastapi_client, fake_s3):
    run_upload_flow(fastapi_client, fake_s3)
    dataset = get_first_dataset()
    assert dataset is not None

    class DummyResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "- Efficiency is high in North\n- West trails behind"}}

    monkeypatch.setattr("backend.app.services.ai.httpx.post", lambda *args, **kwargs: DummyResponse())

    resp = fastapi_client.post(
        "/ai/ask",
        json={"workspace_id": 1, "dataset_id": str(dataset.id), "question": "Which regions"},
    )
    assert resp.status_code == 200
    assert "Efficiency" in resp.json()["answer"]


def test_report_generation_persists_pdf(fastapi_client, fake_s3):
    run_upload_flow(fastapi_client, fake_s3)
    dataset = get_first_dataset()
    assert dataset is not None

    charts_resp = fastapi_client.post("/dashboards/generate", json={"dataset_id": str(dataset.id)})
    chart_ids = [chart["id"] for chart in charts_resp.json()["charts"]]

    resp = fastapi_client.post(
        "/reports/generate",
        json={
            "dataset_id": str(dataset.id),
            "selected_chart_ids": chart_ids,
            "narrative_blocks": [{"heading": "Highlights", "body": "Great performance."}],
        },
    )
    assert resp.status_code == 200
    download_url = resp.json()["download_url"]
    assert download_url.startswith("https://fake-s3.local/")

    stored = [blob for (bucket, key), blob in fake_s3.objects.items() if key and key.startswith("reports/")]
    assert stored, "Report bytes missing"
    assert len(stored[0]) > 10 * 1024


def test_healthz_returns_green(monkeypatch, fastapi_client, fake_s3):
    class DummyRedis:
        def ping(self):  # pragma: no cover - simple stub
            return True

    monkeypatch.setattr("redis.Redis", lambda *args, **kwargs: DummyRedis())

    class DummyHTTPResponse:
        def raise_for_status(self):
            return None

    monkeypatch.setattr("backend.app.routes.mvp.health.httpx.get", lambda *args, **kwargs: DummyHTTPResponse())

    resp = fastapi_client.get("/healthz")
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {
        "database": True,
        "redis": True,
        "storage": True,
        "ai": True,
    }
