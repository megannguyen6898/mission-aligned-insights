import os
import sys
import pathlib
import json
import asyncio

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))
os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("JWT_SECRET", "test")
os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("OPENAI_API_KEY", "test")
os.environ.setdefault("XERO_CLIENT_ID", "test")
os.environ.setdefault("XERO_CLIENT_SECRET", "test")
os.environ.setdefault("XERO_REDIRECT_URI", "http://localhost")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test")
os.environ.setdefault("GOOGLE_CLIENT_SECRET", "test")
os.environ.setdefault("GOOGLE_REDIRECT_URI", "http://localhost")

from backend.app.database import Base
from backend.app.models.data_upload import DataUpload, SourceType, UploadStatus
from backend.app.models.project import Project
from backend.app.services.ingestion_service import IngestionService


def test_ingest_upload_creates_records(tmp_path):
    engine = create_engine("sqlite://")
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    db = TestingSession()

    data = [
        {
            "name": "Project A",
            "activities": [
                {
                    "name": "Activity 1",
                    "outcomes": [
                        {
                            "name": "Outcome 1",
                            "metrics": [{"name": "beneficiaries", "value": 5}]
                        }
                    ]
                }
            ]
        }
    ]

    file_path = tmp_path / "upload.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    upload = DataUpload(
        user_id=1,
        file_name="upload.json",
        file_path=str(file_path),
        source_type=SourceType.manual,
        status=UploadStatus.pending,
    )
    db.add(upload)
    db.commit()
    db.refresh(upload)

    service = IngestionService()
    asyncio.run(service.ingest_upload(upload.id, db))
    db.refresh(upload)

    assert upload.status == UploadStatus.completed
    assert db.query(Project).count() == 1
