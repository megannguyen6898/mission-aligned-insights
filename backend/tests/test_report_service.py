import os
import sys
import pathlib
import asyncio

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET_KEY", "test")
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("XERO_CLIENT_ID", "test")
os.environ.setdefault("XERO_CLIENT_SECRET", "test")
os.environ.setdefault("XERO_REDIRECT_URI", "http://localhost")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost")

from backend.app.database import Base
from backend.app.models.project import Project
from backend.app.models.activity import Activity
from backend.app.models.outcome import Outcome
from backend.app.models.metric import Metric
from backend.app.services.report_service import ReportService


def test_generate_report_aggregates_metrics_and_charts():
    engine = create_engine("sqlite://")
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()

    project = Project(user_id=1, name="Proj")
    db.add(project)
    db.flush()
    activity = Activity(project_id=project.id, name="Act")
    db.add(activity)
    db.flush()
    outcome = Outcome(activity_id=activity.id, name="Out")
    db.add(outcome)
    db.flush()
    metric = Metric(outcome_id=outcome.id, name="beneficiaries", value=5)
    db.add(metric)
    db.commit()

    service = ReportService()
    report = asyncio.run(service.generate_report(1, "custom", "Title", db))
    db.refresh(report)

    assert report.metrics["beneficiaries"] == 5
    assert report.visualizations["impact"][0]["value"] == 5
