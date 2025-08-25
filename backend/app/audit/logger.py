from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from .model import AuditEvent


def log_event(
    db: Session,
    action: str,
    *,
    user_id: int | None = None,
    org_id: int | None = None,
    project_id: str | None = None,
    upload_id: int | None = None,
    job_id: int | None = None,
    batch_id: str | None = None,
    data: dict[str, Any] | None = None,
) -> None:
    """Persist an audit event. Errors are swallowed."""
    event = AuditEvent(
        action=action,
        user_id=user_id,
        org_id=org_id,
        project_id=project_id,
        upload_id=upload_id,
        job_id=job_id,
        batch_id=batch_id,
        data=data or {},
    )
    try:
        db.add(event)
        db.commit()
    except Exception:
        db.rollback()
