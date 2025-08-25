from __future__ import annotations

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id = Column(String, primary_key=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False)
    date = Column(Date, nullable=True)
    group = Column(String, nullable=True)
    count = Column(Integer, nullable=True)
    demographic_info = Column(String, nullable=True)
    location = Column(String, nullable=True)
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
        UniqueConstraint("project_fk", "group", "date", name="uq_beneficiary_natural"),
    )

    project = relationship("Project", back_populates="beneficiaries")

