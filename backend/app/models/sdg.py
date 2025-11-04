from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class SDGGoal(Base):
    __tablename__ = "sdg_goals"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True, nullable=False)
    title = Column(String, nullable=False)
    short_title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    color = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    targets = relationship("SDGTarget", back_populates="goal", cascade="all, delete-orphan")


class SDGTarget(Base):
    __tablename__ = "sdg_targets"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("sdg_goals.id"), nullable=False)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    goal = relationship("SDGGoal", back_populates="targets")
    indicators = relationship("SDGIndicator", back_populates="target", cascade="all, delete-orphan")


class SDGIndicator(Base):
    __tablename__ = "sdg_indicators"

    id = Column(Integer, primary_key=True, index=True)
    target_id = Column(Integer, ForeignKey("sdg_targets.id"), nullable=False)
    code = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    guidance = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    target = relationship("SDGTarget", back_populates="indicators")
    metric_mappings = relationship("MetricSDGMapping", back_populates="indicator", cascade="all, delete-orphan")
    correlations = relationship("CorrelationResult", back_populates="indicator", cascade="all, delete-orphan")


class MetricSDGMapping(Base):
    __tablename__ = "metric_sdg_mapping"
    __table_args__ = (
        UniqueConstraint("metric_id", "indicator_id", name="uq_metric_indicator"),
    )

    id = Column(Integer, primary_key=True, index=True)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("sdg_indicators.id"), nullable=False)
    relevance_score = Column(Float, nullable=False, default=0.0)
    rationale = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    metric = relationship("Metric", back_populates="sdg_mappings")
    indicator = relationship("SDGIndicator", back_populates="metric_mappings")
