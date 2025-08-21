import os
import sys
import pathlib
import pytest
import asyncio

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("XERO_CLIENT_ID", "test")
os.environ.setdefault("XERO_CLIENT_SECRET", "test")
os.environ.setdefault("XERO_REDIRECT_URI", "http://localhost")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost")
os.environ.setdefault("SECRET_KEY", "test")

from backend.app.services.dashboard_service import DashboardService
from backend.app.schemas.dashboard import DashboardCreate
from backend.app.models.project import Project


class DummyMetric:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class DummyOutcome:
    def __init__(self, metrics):
        self.metrics = metrics
class DummyActivity:
    def __init__(self, outcomes):
        self.outcomes = outcomes

class DummyProject:
    def __init__(self, user_id, activities):
        self.user_id = user_id
        self.activities = activities

class DummyQuery:
    def __init__(self, projects):
        self._projects = projects
    def filter_by(self, **kwargs):
        user_id = kwargs.get("user_id")
        if user_id is not None:
            self._projects = [p for p in self._projects if p.user_id == user_id]
        return self
    def all(self):
        return self._projects

class DummyDB:
    def __init__(self, projects):
        self.projects = projects
        self.added = []
    def query(self, model):
        assert model is Project
        return DummyQuery(self.projects)
    def add(self, obj):
        self.added.append(obj)
    def commit(self):
        pass
    def refresh(self, obj):
        pass

def test_generate_dashboard_aggregates_metrics_by_user():
    metric1 = DummyMetric("beneficiaries", 10)
    metric2 = DummyMetric("beneficiaries", 20)
    activity1 = DummyActivity([DummyOutcome([metric1, metric2])])
    project1 = DummyProject(user_id=1, activities=[activity1])

    metric3 = DummyMetric("beneficiaries", 5)
    activity2 = DummyActivity([DummyOutcome([metric3])])
    project2 = DummyProject(user_id=2, activities=[activity2])

    db = DummyDB([project1, project2])
    service = DashboardService()
    dashboard_data = DashboardCreate(title="Dash", topics=["impact"])

    dashboard = asyncio.run(service.generate_dashboard(1, dashboard_data, db))

    assert dashboard.chart_data["impact"][0]["value"] == 15
    assert db.added[0] is dashboard


def test_generate_dashboard_without_projects():
    db = DummyDB([])
    service = DashboardService()
    dashboard_data = DashboardCreate(title="Dash", topics=["impact"])

    with pytest.raises(ValueError, match="No project metrics found for dashboard generation"):
        asyncio.run(service.generate_dashboard(1, dashboard_data, db))

