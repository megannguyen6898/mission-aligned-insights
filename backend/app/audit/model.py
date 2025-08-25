from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func

from ..database import Base


class AuditEvent(Base):
    """Record of sensitive actions with minimal context."""

    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    action = Column(String, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    org_id = Column(Integer, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("ingestion_jobs.id"), nullable=True)
    batch_id = Column(String, ForeignKey("import_batches.id"), nullable=True)

    data = Column(JSON, nullable=True)
