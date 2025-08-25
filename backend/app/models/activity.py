from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base
from .outcome import Outcome


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    source_system = Column(String, nullable=False, server_default="excel")
    external_id = Column(String, nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    row_hash = Column(String, nullable=True)
    import_batch_id = Column(String, ForeignKey("import_batches.id"), nullable=True)
    schema_version = Column(Integer, nullable=False, server_default="1")

    project = relationship("Project", back_populates="activities")
    outcomes = relationship("Outcome", back_populates="activity", cascade="all, delete-orphan")
