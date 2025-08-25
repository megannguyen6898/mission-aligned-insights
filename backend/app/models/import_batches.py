from __future__ import annotations

import enum
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, JSON, Enum

from ..database import Base


class BatchStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id = Column(String, primary_key=True)
    source_system = Column(String, nullable=False)  # e.g., 'excel'
    schema_version = Column(Integer, nullable=False, server_default="1")
    triggered_by_user_id = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    status = Column(
        Enum(BatchStatus, name="batchstatus"),
        default=BatchStatus.queued,
        nullable=False,
    )
    error_json = Column(JSON)

    def set_status(self, new_status: BatchStatus, error_json: dict | None = None) -> None:
        """Update status and record lifecycle timestamps."""
        now = datetime.now(timezone.utc)
        if new_status == BatchStatus.running:
            if self.started_at is None:
                self.started_at = now
        elif new_status in (BatchStatus.success, BatchStatus.failed):
            if self.started_at is None:
                self.started_at = now
            if self.finished_at is None:
                self.finished_at = now
        self.status = new_status
        if error_json is not None:
            self.error_json = error_json
