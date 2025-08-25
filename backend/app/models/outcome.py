from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
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


class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(String, primary_key=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False)
    date = Column(Date, nullable=True)
    outcome_metric = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    method = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # lineage fields
    source_system = Column(String, nullable=False, server_default="excel")
    external_id = Column(String, nullable=True)
    ingested_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    row_hash = Column(String, nullable=True)
    import_batch_id = Column(String, ForeignKey("import_batches.id"), nullable=True)
    schema_version = Column(Integer, nullable=False, server_default="1")

    __table_args__ = (
        UniqueConstraint(
            "project_fk", "outcome_metric", "date", name="uq_outcome_natural"
        ),
    )

    project = relationship("Project", back_populates="outcomes")
    metrics = relationship("Metric", back_populates="outcome", cascade="all, delete-orphan")

