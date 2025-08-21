from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    outcome_id = Column(Integer, ForeignKey("outcomes.id"), nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

    outcome = relationship("Outcome", back_populates="metrics")
