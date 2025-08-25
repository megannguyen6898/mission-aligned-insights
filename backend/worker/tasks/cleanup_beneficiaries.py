from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict

from ..worker import app


def _close_db(db) -> None:
    try:
        db.close()
    except Exception:
        pass


@app.task(bind=True)
def cleanup_beneficiaries(self) -> Dict[str, int]:
    """Remove beneficiary rows older than retention window for each org."""
    from backend.app.database import SessionLocal
    from backend.app.models import Beneficiary, Project

    retention_days = int(os.getenv("BENEFICIARY_RETENTION_DAYS", "365"))
    cutoff = datetime.utcnow() - timedelta(days=retention_days)

    db = SessionLocal()
    try:
        counts: Dict[str, int] = {}
        org_ids = [row[0] for row in db.query(Project.owner_org_id).distinct()]
        for org_id in org_ids:
            proj_ids = (
                db.query(Project.id)
                .filter(Project.owner_org_id == org_id)
                .subquery()
            )
            deleted = (
                db.query(Beneficiary)
                .filter(Beneficiary.project_fk.in_(proj_ids))
                .filter(Beneficiary.ingested_at < cutoff)
                .delete(synchronize_session=False)
            )
            counts[str(org_id)] = deleted
        db.commit()
        return counts
    finally:
        _close_db(db)
