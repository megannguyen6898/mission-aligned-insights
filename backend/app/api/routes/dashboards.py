
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ...database import get_db
from ...schemas.dashboard import DashboardCreate, DashboardResponse
from ...models.user import User
from ...api.deps import get_current_user
from ...services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

@router.get("/topics")
async def get_dashboard_topics(db: Session = Depends(get_db)):
    service = DashboardService()
    topics = await service.get_topics(db)
    return {"topics": topics}

@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(
    dashboard_data: DashboardCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard_service = DashboardService()
    try:
        dashboard = await dashboard_service.generate_dashboard(
            current_user.id, dashboard_data, db
        )
        return dashboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{dashboard_id}", response_model=DashboardResponse)
async def get_dashboard(
    dashboard_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard_service = DashboardService()
    dashboard = await dashboard_service.get_dashboard(dashboard_id, current_user.id, db)
    
    if not dashboard:
        raise HTTPException(status_code=404, detail="Dashboard not found")
    
    return dashboard

@router.get("/", response_model=List[DashboardResponse])
async def get_user_dashboards(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    dashboard_service = DashboardService()
    dashboards = await dashboard_service.get_user_dashboards(current_user.id, db)
    return dashboards
