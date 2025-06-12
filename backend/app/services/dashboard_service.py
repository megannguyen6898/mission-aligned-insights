
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json
import pandas as pd
from ..models.dashboard import Dashboard
from ..models.data_upload import DataUpload
from ..schemas.dashboard import DashboardCreate

class DashboardService:
    async def generate_dashboard(self, user_id: int, dashboard_data: DashboardCreate, db: Session) -> Dashboard:
        """Generate a new dashboard based on user data and selected topics"""
        
        # Use the latest completed upload for dashboard generation
        latest_upload = (
            db.query(DataUpload)
            .filter(DataUpload.user_id == user_id, DataUpload.status == "completed")
            .order_by(DataUpload.created_at.desc())
            .first()
        )

        if not latest_upload:
            raise ValueError("No completed data uploads found for dashboard generation")

        # Generate chart configuration based on topics using the latest upload
        chart_data = await self._generate_chart_data(dashboard_data.topics, latest_upload)
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
        
        return dashboard
    
    async def _generate_chart_data(self, topics: List[str], upload: DataUpload) -> Dict[str, Any]:
        """Generate chart data based on selected topics and a data upload"""

        if not upload:
            return {}

        metadata = upload.upload_metadata
        if not metadata:
            return {}

        data = json.loads(metadata)
        records = data.get("records", [])
        df = pd.DataFrame(records)

        chart_data: Dict[str, Any] = {
            "impact": [],
            "sdg": [],
            "timeline": []
        }

        numeric_cols = df.select_dtypes(include="number").columns.tolist()
        for col in numeric_cols:
            chart_data["impact"].append({"name": col, "value": float(df[col].mean())})

        date_cols = [c for c in df.columns if "date" in c.lower() or "month" in c.lower()]
        if date_cols and numeric_cols:
            date_col = date_cols[0]
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            timeline = df.dropna(subset=[date_col])
            if not timeline.empty:
                group = timeline.groupby(timeline[date_col].dt.strftime("%b"))[numeric_cols[0]].mean().reset_index()
                group.columns = ["month", "value"]
                chart_data["timeline"] = group.to_dict("records")

        sdg_cols = [c for c in df.columns if c.lower() == "sdg"]
        if sdg_cols:
            sdg_col = sdg_cols[0]
            counts = df[sdg_col].value_counts(normalize=True) * 100
            for sdg_value, pct in counts.items():
                chart_data["sdg"].append({"sdg": sdg_value, "title": str(sdg_value), "score": round(pct, 2)})

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
