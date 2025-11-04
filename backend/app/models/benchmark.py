from __future__ import annotations

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class BenchmarkProject(Base):
    __tablename__ = "benchmark_projects"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String, nullable=False, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    mean_value = Column(Float, nullable=False)
    std_dev = Column(Float, nullable=True)
    sample_size = Column(Integer, nullable=True)
    source = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    metric = relationship("Metric", back_populates="benchmarks")
