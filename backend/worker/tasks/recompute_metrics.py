from __future__ import annotations

from typing import Any, Dict, List

from ..worker import app


def _close_db(db) -> None:
    try:
        db.close()
    except Exception:
        pass


@app.task(bind=True)
def recompute_metrics(self, org_id: str, project_id: str | None = None) -> Dict[str, int]:
    """Recompute summary metrics for an organization or single project."""
    from backend.app.database import SessionLocal
    from backend.app.metrics.compute import recompute_for_project
    from backend.app.models import (
        Project,
        ProjectSummary,
        MonthlyRollup,
        MetricsSummary,
    )

    db = SessionLocal()
    try:
        if project_id:
            project_ids: List[str] = [project_id]
        else:
            project_ids = [
                p.id for p in db.query(Project).filter(Project.owner_org_id == str(org_id)).all()
            ]
        totals = {
            "projects": 0,
            "project_summaries": 0,
            "monthly_rollups": 0,
            "metrics_summary": 0,
        }
        for pid in project_ids:
            recompute_for_project(db, pid)
            totals["projects"] += 1
            totals["project_summaries"] += db.query(ProjectSummary).filter_by(project_fk=pid).count()
            totals["monthly_rollups"] += db.query(MonthlyRollup).filter_by(project_fk=pid).count()
            totals["metrics_summary"] += db.query(MetricsSummary).filter_by(project_fk=pid).count()
        return totals
    finally:
        _close_db(db)
