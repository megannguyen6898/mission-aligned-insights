import os
import sys
import pathlib
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))


def test_cleanup_beneficiaries(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("JWT_SECRET", "test")
    monkeypatch.setenv("SECRET_KEY", "test")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("XERO_CLIENT_ID", "test")
    monkeypatch.setenv("XERO_CLIENT_SECRET", "test")
    monkeypatch.setenv("XERO_REDIRECT_URI", "http://localhost")
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test")
    monkeypatch.setenv("GOOGLE_REDIRECT_URI", "http://localhost")

    from backend.app.database import Base
    from backend.app.models.project import Project
    from backend.app.models.beneficiary import Beneficiary

    engine = create_engine("sqlite://")
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    monkeypatch.setattr("backend.app.database.SessionLocal", TestingSession)

    db = TestingSession()
    old = datetime.utcnow() - timedelta(days=60)
    recent = datetime.utcnow() - timedelta(days=10)

    p1 = Project(id="p1", owner_org_id="org1", project_id="p1")
    p2 = Project(id="p2", owner_org_id="org2", project_id="p2")
    db.add_all([p1, p2])
    db.commit()

    b1 = Beneficiary(id="b1", project_fk="p1", ingested_at=old)
    b2 = Beneficiary(id="b2", project_fk="p1", ingested_at=recent)
    b3 = Beneficiary(id="b3", project_fk="p2", ingested_at=old)
    db.add_all([b1, b2, b3])
    db.commit()
    db.close()

    monkeypatch.setenv("BENEFICIARY_RETENTION_DAYS", "30")
    from backend.worker.tasks.cleanup_beneficiaries import cleanup_beneficiaries

    result = cleanup_beneficiaries()
    assert result["org1"] == 1
    assert result["org2"] == 1

    db = TestingSession()
    remaining = {b.id for b in db.query(Beneficiary.id).all()}
    assert remaining == {"b2"}
