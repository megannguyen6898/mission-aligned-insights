import enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.sql import func

from ..database import Base


class IngestionJobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=False)
    status = Column(
        Enum(IngestionJobStatus, name="ingestionjobstatus"),
        default=IngestionJobStatus.queued,
        nullable=False,
    )
    error_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
