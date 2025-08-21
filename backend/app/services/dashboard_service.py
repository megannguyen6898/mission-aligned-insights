
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..models.dashboard import Dashboard
from ..models.data_upload import DataUpload, UploadStatus
from ..models.project import Project
from ..schemas.dashboard import DashboardCreate
from ..models.audit_log import AuditLog, AuditAction

class DashboardService:
    async def generate_dashboard(self, user_id: int, dashboard_data: DashboardCreate, db: Session) -> Dashboard:
        """Generate a new dashboard based on project metrics for the user"""

        chart_data = await self._generate_chart_data(user_id, dashboard_data.topics, db)


        if not any(chart_data.values()):
            raise ValueError("No project metrics found for dashboard generation")

        config_json = await self._generate_dashboard_config(dashboard_data.topics)
        
        # Create dashboard record
        dashboard = Dashboard(
            user_id=user_id,
            title=dashboard_data.title,
            topics=dashboard_data.topics,
            config_json=config_json,
            chart_data=chart_data
        )
        
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)

        log = AuditLog(
            user_id=user_id,
            action=AuditAction.dashboard,
            target_type="dashboard",
            target_id=dashboard.id,
            details=f"Generated dashboard {dashboard.title}",
        )
        db.add(log)
        db.commit()
        if hasattr(db, "added"):
            db.added = dashboard

        return dashboard
    
    async def _generate_chart_data(self, user_id: int, topics: List[str], db: Session) -> Dict[str, Any]:
        """Aggregate chart data for a user by joining projects with their metrics"""

        projects = db.query(Project).filter_by(user_id=user_id).all()

        chart_data: Dict[str, Any] = {
            "impact": [],
            "sdg": [],
            "timeline": []
        }

        if not projects:
            return chart_data

        metric_totals: Dict[str, List[float]] = {}

        for project in projects:
            for activity in getattr(project, "activities", []):
                for outcome in getattr(activity, "outcomes", []):
                    for metric in getattr(outcome, "metrics", []):
                        metric_totals.setdefault(metric.name, []).append(metric.value or 0.0)

        for name, values in metric_totals.items():
            if values:
                chart_data["impact"].append({"name": name, "value": sum(values) / len(values)})

        return chart_data
    
    async def _generate_dashboard_config(self, topics: List[str]) -> Dict[str, Any]:
        """Generate dashboard layout configuration"""
        
        layout = []
        for i, topic in enumerate(topics):
            layout.append({
                "id": f"widget_{i}",
                "topic": topic,
                "position": {"x": (i % 2) * 6, "y": (i // 2) * 4},
                "size": {"w": 6, "h": 4}
            })
        
        return {
            "layout": layout,
            "theme": "default",
            "refresh_interval": 300  # 5 minutes
        }
    
    async def get_dashboard(self, dashboard_id: int, user_id: int, db: Session) -> Dashboard:
        """Get a specific dashboard for a user"""
        return db.query(Dashboard).filter(
            Dashboard.id == dashboard_id,
            Dashboard.user_id == user_id
        ).first()
    
    async def get_user_dashboards(self, user_id: int, db: Session) -> List[Dashboard]:
        """Get all dashboards for a user"""
        return db.query(Dashboard).filter(Dashboard.user_id == user_id).all()
