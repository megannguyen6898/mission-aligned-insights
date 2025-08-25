from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Integer,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Project(Base):
    """Core project table.

    Projects are uniquely identified by the tuple
    ``(owner_org_id, project_id)``.  The ``id`` column is a surrogate
    primary key used by child tables.
    """

    __tablename__ = "projects"

    id = Column(String, primary_key=True)
    owner_org_id = Column(String, nullable=False)
    project_id = Column(String, nullable=False)
    name = Column(String, nullable=True)
    org_name = Column(String, nullable=True)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    country = Column(String, nullable=True)
    region = Column(String, nullable=True)
    sdg_goal = Column(String, nullable=True)
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
        UniqueConstraint("owner_org_id", "project_id", name="uq_project_org_pid"),
    )

    activities = relationship(
        "Activity", back_populates="project", cascade="all, delete-orphan"
    )
    outcomes = relationship(
        "Outcome", back_populates="project", cascade="all, delete-orphan"
    )
    funding_resources = relationship(
        "FundingResource", back_populates="project", cascade="all, delete-orphan"
    )
    beneficiaries = relationship(
        "Beneficiary", back_populates="project", cascade="all, delete-orphan"
    )


