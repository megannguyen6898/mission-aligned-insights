from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    outcome_id = Column(String, ForeignKey("outcomes.id"), nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    unit = Column(String, nullable=True)
    category = Column(String, nullable=True)
    aggregation_method = Column(String, nullable=True)
    source = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    is_library = Column(Boolean, nullable=False, server_default="false")
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    outcome = relationship("Outcome", back_populates="metrics")
    workspace = relationship("Workspace", back_populates="metrics")
    mappings = relationship("MetricMapping", back_populates="metric", cascade="all, delete-orphan")
    sdg_mappings = relationship("MetricSDGMapping", back_populates="metric", cascade="all, delete-orphan")
    correlations = relationship("CorrelationResult", back_populates="metric", cascade="all, delete-orphan")
    benchmarks = relationship("BenchmarkProject", back_populates="metric", cascade="all, delete-orphan")
    balance_entries = relationship("ImpactBalanceSheet", back_populates="metric", cascade="all, delete-orphan")


class MetricMapping(Base):
    __tablename__ = "metric_mappings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=False)
    metric_id = Column(Integer, ForeignKey("metrics.id"), nullable=False)
    column_name = Column(String, nullable=False)
    column_sample = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    suggested_by_ai = Column(Boolean, nullable=False, server_default="false")
    confirmed = Column(Boolean, nullable=False, server_default="false")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    dataset = relationship("Dataset", back_populates="metric_mappings")
    metric = relationship("Metric", back_populates="mappings")
