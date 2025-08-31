import os
import sys
import io
import importlib
from pathlib import Path
from jose import jwt
from fastapi.testclient import TestClient

# Setup environment variables
os.environ["DATABASE_URL"] = "sqlite://"
os.environ.setdefault("JWT_SECRET_KEY", "test")
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("XERO_CLIENT_ID", "test")
os.environ.setdefault("XERO_CLIENT_SECRET", "test")
os.environ.setdefault("XERO_REDIRECT_URI", "http://localhost")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost")
os.environ.setdefault("S3_BUCKET", "testbucket")

sys.path.append(str(Path(__file__).resolve().parents[3]))

from backend.app.api import deps as deps_module
from backend.worker.tasks import render_report as render_task
from backend.app.storage import s3_client as s3_module

client: TestClient


class DummyS3:
    def __init__(self):
        self.store = {}

    def put_object(self, Bucket, Key, Body, ContentType=None):
        if isinstance(Body, bytes):
            data = Body
        else:
            data = Body.read()
        self.store[Key] = data

    def download_file(self, Bucket, Key, Filename):
        with open(Filename, "wb") as f:
            f.write(self.store[Key])

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.store[Key])}


def setup_function(_):
    os.environ["DATABASE_URL"] = "sqlite:///./test_report_gen.db"
    db_path = Path("test_report_gen.db")
    if db_path.exists():
        db_path.unlink()

    import backend.app.main as main_module
    import backend.app.database as db_module
    import backend.app.models as models

    importlib.reload(main_module)
    importlib.reload(db_module)
    importlib.reload(models)

    global client
    client = TestClient(main_module.app)

    db_module.Base.metadata.drop_all(bind=db_module.engine)
    db_module.Base.metadata.create_all(bind=db_module.engine)
    db = db_module.SessionLocal()
    db.add(models.User(id=1, email="user@example.com", hashed_password="x", name="Test"))
    db.commit()
    db.close()

    s3_instance = DummyS3()
    s3_module.get_s3_client = lambda: s3_instance

    def _run(job_id: int):
        try:
            render_task.render_report_job(job_id)
        except Exception:
            pass

    render_task.render_report_job.delay = _run

    def _fake_verify(token: str):
        try:
            return jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        except Exception:
            return None

    deps_module.verify_token = _fake_verify


def make_token(org_id="org1"):
    payload = {"sub": "1", "type": "access", "org_id": org_id}
    return jwt.encode(payload, os.environ["JWT_SECRET_KEY"], algorithm="HS256")


def test_template_upload_and_report_generation():
    token = make_token()
    template_path = Path(__file__).resolve().parents[2] / "app/reports/templates/pilot_overview.html.j2"
    files = {"file": (template_path.name, template_path.read_bytes(), "text/jinja2")}
    data = {"name": "Pilot", "description": "", "engine": "html", "version": "1"}
    resp = client.post(
        "/api/v1/report-templates",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    template_id = resp.json()["template_id"]

    resp = client.get("/api/v1/report-templates")
    assert resp.status_code == 200
    assert any(t["id"] == template_id for t in resp.json()["templates"])

    payload = {
        "template_id": template_id,
        "params": {"title": "Hello", "kpis": [{"name": "Impact", "value": 5}], "outcomes": []},
    }
    resp = client.post(
        "/api/v1/reports",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    report_id = resp.json()["report_id"]

    resp = client.get(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.json()["status"] == "success"

    resp = client.get(
        f"/api/v1/reports/{report_id}/download",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert len(resp.content) > 0


def test_variable_mismatch_produces_error():
    token = make_token()
    template_path = Path(__file__).resolve().parents[2] / "app/reports/templates/pilot_overview.html.j2"
    files = {"file": (template_path.name, template_path.read_bytes(), "text/jinja2")}
    data = {"name": "Pilot", "description": "", "engine": "html", "version": "1"}
    resp = client.post(
        "/api/v1/report-templates",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    template_id = resp.json()["template_id"]

    payload = {"template_id": template_id, "params": {"title": "Hi"}}
    resp = client.post(
        "/api/v1/reports",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    report_id = resp.json()["report_id"]

    resp = client.get(
        f"/api/v1/reports/{report_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.json()["status"] == "failed"
    assert "error" in resp.json()["error"]
