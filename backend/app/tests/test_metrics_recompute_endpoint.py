# flake8: noqa
import os
import sys
import uuid
from pathlib import Path
from datetime import date
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
os.environ["database_url"] = "sqlite:///./test_metrics.db"
os.environ.setdefault("jwt_secret", "test")
os.environ.setdefault("openai_api_key", "test")
os.environ.setdefault("xero_client_id", "test")
os.environ.setdefault("xero_client_secret", "test")
os.environ.setdefault("xero_redirect_uri", "http://localhost")
os.environ.setdefault("google_client_id", "test")
os.environ.setdefault("google_client_secret", "test")
os.environ.setdefault("google_redirect_uri", "http://localhost")
os.environ.setdefault("secret_key", "test")

from fastapi.testclient import TestClient
from jose import jwt

from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.models import (
    User,
    Project,
    FundingResource,
    Beneficiary,
    Outcome,
    ProjectSummary,
    MonthlyRollup,
    MetricsSummary,
)
from backend.app.api import deps as deps_module
from backend.app.routes.metrics import recompute as recompute_route


def setup_function(_):
    db_path = Path("test_metrics.db")
    if db_path.exists():
        db_path.unlink()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = User(id=1, email="user@example.com", hashed_password="x", name="Test")
    db.add(user)
    project_id = "p1"
    db.add(
        Project(
            id=project_id,
            owner_org_id="org1",
            project_id="p1",
            name="Project 1",
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        FundingResource(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 4, 1),
            funding_source="donor",
            received=100.0,
            spent=80.0,
            volunteer_hours=0,
            staff_hours=0,
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        Beneficiary(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 5, 1),
            group="g1",
            count=20,
            demographic_info="info",
            location="loc",
            notes="b",
            source_system="excel",
            schema_version=1,
        )
    )
    db.add(
        Outcome(
            id=str(uuid.uuid4()),
            project_fk=project_id,
            date=date(2024, 3, 1),
            outcome_metric="metric",
            value=5.0,
            unit="u",
            method="m",
            notes="o",
            source_system="excel",
            schema_version=1,
        )
    )
    db.commit()
    db.close()


client = TestClient(app)


def _fake_verify_token(token: str):
    try:
        return jwt.decode(token, os.environ["jwt_secret"], algorithms=["HS256"])
    except Exception:
        return None


deps_module.verify_token = _fake_verify_token
recompute_route.verify_token = _fake_verify_token


def make_token(org_id="org1", roles=None):
    payload = {"sub": "1", "type": "access", "org_id": org_id}
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, os.environ["jwt_secret"], algorithm="HS256")


def test_recompute_requires_admin_for_org():
    token = make_token(roles=["org_member"])
    response = client.post(
        "/metrics:recompute",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_recompute_metrics_org_admin():
    token = make_token(roles=["admin"])
    response = client.post(
        "/metrics:recompute",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    counts = response.json()
    assert counts == {
        "projects": 1,
        "project_summaries": 1,
        "monthly_rollups": 2,
        "metrics_summary": 1,
    }
    db = SessionLocal()
    ms = db.query(MetricsSummary).filter_by(project_fk="p1", metric_name="metric").one()
    assert ms.total_value == 5.0
    db.close()


def test_recompute_metrics_project_owner():
    token = make_token(roles=["org_member"])
    response = client.post(
        "/metrics:recompute",
        json={"project_id": "p1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    counts = response.json()
    assert counts["projects"] == 1


def test_recompute_cross_org_blocked():
    token = make_token(org_id="org2", roles=["org_member"])
    response = client.post(
        "/metrics:recompute",
        json={"project_id": "p1"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

