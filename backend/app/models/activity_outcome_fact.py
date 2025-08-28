from __future__ import annotations

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String

from ..database import Base


class ActivityOutcomeFact(Base):
    """Denormalized facts combining activities, beneficiaries and spend."""

    __tablename__ = "facts_activity_outcomes"

    id = Column(String, primary_key=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False)
    activity_date = Column(Date, nullable=True)
    activities = Column(Integer, nullable=False, default=0)
    beneficiaries = Column(Integer, nullable=False, default=0)
    spend = Column(Float, nullable=False, default=0.0)
