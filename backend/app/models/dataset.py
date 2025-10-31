import uuid
from sqlalchemy import Column, Integer, ForeignKey, DateTime, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    schema = Column(JSON, nullable=True)
    preview = Column(JSON, nullable=True)
    row_count = Column(Integer, nullable=True)
    table_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="datasets")
    upload = relationship("Upload", back_populates="dataset")
    workflows = relationship("Workflow", back_populates="dataset")
    ai_events = relationship("AIEvent", back_populates="dataset")
