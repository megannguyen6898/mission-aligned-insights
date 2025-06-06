from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..models.investor import Investor, PitchSummary
from ..schemas.investor import InvestorMatchResponse, InvestorResponse


class InvestorService:
    """Service class for investor related operations."""

    async def match_investors(
        self,
        user_id: int,
        db: Session,
        region: Optional[str] = None,
        funding_type: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None,
    ) -> List[InvestorMatchResponse]:
        """Return investors matching the provided filters."""

        query = db.query(Investor)

        if region:
            query = query.filter(or_(Investor.region == region, Investor.region == "Global"))

        if funding_type:
            query = query.filter(Investor.funding_type == funding_type)

        if min_amount is not None:
            query = query.filter(Investor.ticket_size_max >= min_amount)

        if max_amount is not None:
            query = query.filter(Investor.ticket_size_min <= max_amount)

        investors = query.all()

        matches: List[InvestorMatchResponse] = []
        filters: Dict[str, Any] = {
            "region": region,
            "funding_type": funding_type,
            "min_amount": min_amount,
            "max_amount": max_amount,
        }
        for inv in investors:
            match = InvestorMatchResponse(
                investor=InvestorResponse.model_validate(inv, from_attributes=True),
                match_score=100.0,
                filters_applied={k: v for k, v in filters.items() if v is not None},
            )
            matches.append(match)

        return matches

    async def get_investor_profile(self, investor_id: int, db: Session) -> Optional[Investor]:
        """Return a single investor profile if it exists."""
        return db.query(Investor).filter(Investor.id == investor_id).first()

    async def generate_pitch_summary(
        self, user_id: int, investor_id: int, db: Session
    ) -> PitchSummary:
        """Generate a very basic pitch summary for the investor."""
        investor = await self.get_investor_profile(investor_id, db)
        if investor is None:
            raise ValueError("Investor not found")

        pitch_text = (
            f"Dear {investor.name}, we believe our mission aligns with your focus areas. "
            f"We would like to discuss potential opportunities." 
        )

        pitch = PitchSummary(
            user_id=user_id,
            investor_id=investor_id,
            pitch_text=pitch_text,
        )

        db.add(pitch)
        db.commit()
        db.refresh(pitch)
        return pitch

    async def request_introduction(
        self, user_id: int, investor_id: int, message: str, db: Session
    ) -> None:
        """Placeholder for introduction requests.

        In a real implementation this might send an email or store a request.
        """
        # For now we simply create a PitchSummary entry to log the request.
        pitch = PitchSummary(
            user_id=user_id,
            investor_id=investor_id,
            pitch_text=message,
        )
        db.add(pitch)
        db.commit()
        db.refresh(pitch)
