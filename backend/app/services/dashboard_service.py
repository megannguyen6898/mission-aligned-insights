
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import pandas as pd
import json
from ..models.dashboard import Dashboard
from ..models.data_upload import DataUpload
from ..schemas.dashboard import DashboardCreate

class DashboardService:
    async def generate_dashboard(self, user_id: int, dashboard_data: DashboardCreate, db: Session) -> Dashboard:
        """Generate a new dashboard based on user data and selected topics"""
        
        # Get user's uploaded data
        user_uploads = db.query(DataUpload).filter(
            DataUpload.user_id == user_id,
            DataUpload.status == "completed"
        ).all()
        
        if not user_uploads:
            raise ValueError("No completed data uploads found for dashboard generation")
        
        # Generate chart configuration based on topics
        chart_data = await self._generate_chart_data(dashboard_data.topics, user_uploads)
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
    
    async def _generate_chart_data(self, topics: List[str], uploads: List[DataUpload]) -> Dict[str, Any]:
        """Generate chart data based on selected topics and available data"""
        
        chart_data = {}
        
        df = pd.DataFrame()
        if uploads:
            meta = uploads[0].upload_metadata
            if meta:
                try:
                    parsed = json.loads(meta)
                    if "sample_data" in parsed:
                        df = pd.DataFrame(parsed["sample_data"])
                except json.JSONDecodeError:
                    pass

        for topic in topics:
            if topic == "Impact Overview" and not df.empty:
                bars = []
                for col in df.select_dtypes(include="number").columns:
                    bars.append({"name": col, "value": float(df[col].sum())})
                chart_data[topic] = {"type": "bar", "data": bars}
            elif topic == "Impact Overview":
                chart_data[topic] = {
                    "type": "summary_cards",
                    "data": [
                        {"label": "Total Beneficiaries", "value": 1250, "change": "+15%"},
                        {"label": "Programs Active", "value": 8, "change": "+2"},
                        {"label": "Impact Score", "value": 85, "change": "+5pts"}
                    ]
                }
            elif topic == "SDG Alignment":
                chart_data[topic] = {
                    "type": "sdg_wheel",
                    "data": [
                        {"sdg": 1, "name": "No Poverty", "score": 85},
                        {"sdg": 3, "name": "Good Health", "score": 72},
                        {"sdg": 4, "name": "Quality Education", "score": 90},
                        {"sdg": 8, "name": "Decent Work", "score": 68}
                    ]
                }
            elif topic == "Beneficiary Demographics":
                chart_data[topic] = {
                    "type": "demographics_chart",
                    "data": {
                        "age_groups": [
                            {"range": "18-25", "count": 320},
                            {"range": "26-35", "count": 450},
                            {"range": "36-50", "count": 380},
                            {"range": "50+", "count": 100}
                        ],
                        "gender": [
                            {"category": "Female", "count": 720},
                            {"category": "Male", "count": 480},
                            {"category": "Other", "count": 50}
                        ]
                    }
                }
            # Add more topic-specific chart generation logic
        
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
