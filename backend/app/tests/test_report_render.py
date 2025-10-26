import uuid

from fastapi.testclient import TestClient

from .test_analytics_api import _stage_and_load, setup_function as setup_analytics_db


def setup_function(fn):
    setup_analytics_db(fn)


def test_render_report_pdf():
    batch = str(uuid.uuid4())
    _stage_and_load(batch)

    from backend.app.main import app

    client = TestClient(app)
    resp = client.post(
        "/report/render",
        json={"space_id": "org1", "template": "sdg", "inputs": {"prepared_by": "QA"}},
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/pdf"
    assert len(resp.content) > 100
