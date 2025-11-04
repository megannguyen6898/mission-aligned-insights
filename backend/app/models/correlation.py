from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class CorrelationResult(Base):
    __tablename__ = "correlations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    sdg_indicator_id = Column(Integer, ForeignKey("sdg_indicators.id"), nullable=True)
    independent_variable = Column(String, nullable=False)
    r_value = Column(Float, nullable=False)
    p_value = Column(Float, nullable=True)
    direction = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())

    dataset = relationship("Dataset", back_populates="correlations")
    metric = relationship("Metric", back_populates="correlations")
    indicator = relationship("SDGIndicator", back_populates="correlations")
