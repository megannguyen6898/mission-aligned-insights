import json
from datetime import datetime, timedelta
import pytest

from backend.app.services.dashboard_service import DashboardService
from backend.app.schemas.dashboard import DashboardCreate
from backend.app.models.data_upload import DataUpload, UploadStatus

class DummyDataUpload:
    def __init__(self, user_id, created_at, metadata):
        self.user_id = user_id
        self.created_at = created_at
        self.status = UploadStatus.completed
        self.upload_metadata = metadata

class DummyQuery:
    def __init__(self, uploads):
        self.uploads = uploads
    def filter(self, *args, **kwargs):
        return self
    def order_by(self, *args, **kwargs):
        self.uploads = sorted(self.uploads, key=lambda u: u.created_at, reverse=True)
        return self
    def first(self):
        return self.uploads[0] if self.uploads else None

class DummyDB:
    def __init__(self, uploads):
        self.uploads = uploads
        self.added = None
    def query(self, model):
        assert model is DataUpload
        return DummyQuery(self.uploads)
    def add(self, obj):
        self.added = obj
    def commit(self):
        pass
    def refresh(self, obj):
        pass

@pytest.mark.asyncio
async def test_generate_dashboard_uses_latest_upload():
    old_metadata = json.dumps({"records": [{"A": 1}]})
    new_metadata = json.dumps({"records": [{"A": 10}]})
    old = DummyDataUpload(1, datetime.utcnow() - timedelta(days=1), old_metadata)
    new = DummyDataUpload(1, datetime.utcnow(), new_metadata)

    db = DummyDB([old, new])
    service = DashboardService()
    dashboard_data = DashboardCreate(title="Dash", topics=["impact"])

    dashboard = await service.generate_dashboard(1, dashboard_data, db)

    assert dashboard.chart_data["impact"][0]["value"] == 10
    assert db.added is dashboard
