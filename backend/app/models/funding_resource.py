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


class FundingResource(Base):
    __tablename__ = "funding_resources"

    id = Column(String, primary_key=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False)
    date = Column(Date, nullable=True)
    funding_source = Column(String, nullable=True)
    received = Column(Float, nullable=True)
    spent = Column(Float, nullable=True)
    volunteer_hours = Column(Float, nullable=True)
    staff_hours = Column(Float, nullable=True)
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
            "project_fk", "funding_source", "date", name="uq_funding_natural"
        ),
    )

    project = relationship("Project", back_populates="funding_resources")

