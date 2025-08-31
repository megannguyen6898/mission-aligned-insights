import os
import sys
from pathlib import Path
import types

from jose import jwt
from fastapi.testclient import TestClient

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
os.environ["database_url"] = "sqlite:///./test_reports.db"
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
from backend.app.database import Base, engine, SessionLocal
from backend.app.models import User, Project
from backend.app.api import deps as deps_module
from backend.app.routes import reports as reports_route


def setup_function(_):
    db_path = Path("test_reports.db")
    if db_path.exists():
        db_path.unlink()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(id=1, email="user@example.com", hashed_password="x", name="Test")
    db.add(user)
    db.add(
        Project(
            id="p1",
            owner_org_id="org1",
            project_id="p1",
            name="Project 1",
            source_system="excel",
            schema_version=1,
        )
    )
    db.commit()
    db.close()
    dummy = Path("dummy.pdf")
    dummy.write_text("dummy")

    def fake_generate(project_id: str, org_id: str, sections: list[str], db):
        if project_id != "p1" or org_id != "org1":
            raise ValueError("Project not found")
        return dummy

    reports_route.generate_pdf = fake_generate


client = TestClient(app)


def _fake_verify_token(token: str):
    try:
        return jwt.decode(token, os.environ["jwt_secret_key"], algorithms=["HS256"])
    except Exception:
        return None


deps_module.verify_token = _fake_verify_token
reports_route.verify_token = _fake_verify_token


def make_token(org_id="org1", roles=None):
    payload = {"sub": "1", "type": "access", "org_id": org_id}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, os.environ["jwt_secret_key"], algorithm="HS256")


def test_report_owner():
    token = make_token(roles=["org_member"])
    response = client.post(
        "/reports:generate",
        json={"project_id": "p1", "sections": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


def test_report_requires_role():
    token = make_token()
    response = client.post(
        "/reports:generate",
        json={"project_id": "p1", "sections": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_report_cross_org_blocked():
    token = make_token(org_id="org2", roles=["org_member"])
    response = client.post(
        "/reports:generate",
        json={"project_id": "p1", "sections": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


def test_report_admin_allowed():
    token = make_token(roles=["admin"])
    response = client.post(
        "/reports:generate",
        json={"project_id": "p1", "sections": []},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
