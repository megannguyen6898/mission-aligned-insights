
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ...schemas.investor import InvestorMatchResponse
from ...models.user import User
from ...api.deps import get_current_user
from ...services.investor_service import InvestorService

router = APIRouter(prefix="/investors", tags=["investors"])

@router.get("/match", response_model=List[InvestorMatchResponse])
async def get_matched_investors(
    region: Optional[str] = None,
    funding_type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investor_service = InvestorService()
    try:
        matches = await investor_service.match_investors(
            current_user.id, db, region, funding_type, min_amount, max_amount
        )
        return matches
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{investor_id}")
async def get_investor_profile(
    investor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investor_service = InvestorService()
    investor = await investor_service.get_investor_profile(investor_id, db)
    
    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")
    
    return investor

@router.post("/pitch-summary")
async def generate_pitch_summary(
    investor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investor_service = InvestorService()
    try:
        pitch = await investor_service.generate_pitch_summary(
            current_user.id, investor_id, db
        )
        return {"pitch_summary": pitch.pitch_text, "pitch_id": pitch.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/intro-request")
async def request_introduction(
    investor_id: int,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investor_service = InvestorService()
    try:
        result = await investor_service.request_introduction(
            current_user.id, investor_id, message, db
        )
        return {"message": "Introduction request sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
