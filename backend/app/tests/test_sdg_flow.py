import os
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.app.main import app
from backend.app.database import Base, SessionLocal, engine
from backend.app.models import Dataset, Metric, Workspace
from backend.app.config import settings
from ops.seed_sdg import seed_sdg


class _FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def put_object(self, Bucket: str, Key: str, Body: bytes, ContentType: str) -> None:  # noqa: N803 - boto style
        self.objects[Key] = Body

    def generate_presigned_url(self, ClientMethod: str, Params: dict, ExpiresIn: int) -> str:  # noqa: N803
        return f"https://example.com/{Params['Key']}"


@pytest.fixture(autouse=True)
def setup_database(monkeypatch):
    os.environ.setdefault("STORAGE_BUCKET", "test-bucket")
    settings.storage_bucket = "test-bucket"

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    fake_client = _FakeS3Client()
    monkeypatch.setattr("backend.app.services.report.get_s3_client", lambda: fake_client)
    monkeypatch.setattr("backend.app.services.report.create_presigned_get", lambda key, expires_in=3600: f"https://example.com/{key}")

    session = SessionLocal()
    workspace = Workspace(id=1, name="Test Workspace", slug="test", description=None)
    session.add(workspace)
    dataset_id = uuid.uuid4()
    dataset = Dataset(
        id=dataset_id,
        workspace_id=workspace.id,
        schema=[
            {"name": "Completion Rate", "semantic_type": "numeric"},
            {"name": "Spend", "semantic_type": "numeric"},
        ],
        preview=[
            {"Completion Rate": 0.55, "Spend": 12000},
            {"Completion Rate": 0.62, "Spend": 15000},
            {"Completion Rate": 0.7, "Spend": 19000},
        ],
        row_count=3,
    )
    session.add(dataset)
    metric = Metric(
        name="Completion rate (primary education)",
        code="4.1.1",
        unit="ratio",
        category="Education",
        workspace_id=workspace.id,
        is_library=True,
        is_active=True,
    )
    session.add(metric)
    session.commit()
    seed_sdg()

    yield {
        "dataset_id": str(dataset_id),
        "metric_id": metric.id,
    }

    session.close()


def test_end_to_end_sdg_flow(setup_database):
    dataset_id = setup_database["dataset_id"]
    metric_id = setup_database["metric_id"]
    client = TestClient(app)

    suggest_resp = client.post(f"/datasets/{dataset_id}/metrics/suggest", json={"top_n": 2})
    assert suggest_resp.status_code == 200
    columns = suggest_resp.json()["columns"]
    completion_column = next((col for col in columns if col["column_name"] == "Completion Rate"), None)
    assert completion_column is not None
    assert completion_column["suggestions"]

    confirm_resp = client.post(
        f"/datasets/{dataset_id}/metrics/confirm",
        json={
            "mappings": [
                {
                    "column_name": "Completion Rate",
                    "metric_id": metric_id,
                    "confidence": 0.9,
                }
            ]
        },
    )
    assert confirm_resp.status_code == 200
    assert confirm_resp.json()["confirmed"] == ["Completion Rate"]

    sdg_resp = client.get(f"/datasets/{dataset_id}/sdg/suggest")
    assert sdg_resp.status_code == 200
    goals = sdg_resp.json()["goals"]
    assert isinstance(goals, list)

    run_resp = client.post(
        f"/datasets/{dataset_id}/analysis/run",
        json={"independent_variables": ["Spend"]},
    )
    assert run_resp.status_code == 200
    assert run_resp.json()["status"] in {"queued", "skipped"}

    results_resp = client.get(f"/datasets/{dataset_id}/analysis/results")
    assert results_resp.status_code == 200
    assert isinstance(results_resp.json()["results"], list)

    report_resp = client.post(
        "/reports/generate",
        json={
            "dataset_id": dataset_id,
            "selected_chart_ids": [],
            "narrative_blocks": [],
        },
    )
    assert report_resp.status_code == 200
    assert "download_url" in report_resp.json()
