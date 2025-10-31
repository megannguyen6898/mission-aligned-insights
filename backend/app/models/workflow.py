import enum
import uuid
from sqlalchemy import (
    Column,
    String,
    Enum,
    ForeignKey,
    DateTime,
    Text,
    Integer,
    JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class WorkflowStep(str, enum.Enum):
    upload = "upload"
    validate = "validate"
    ingest = "ingest"


class WorkflowState(str, enum.Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    upload_id = Column(Integer, ForeignKey("uploads.id"), nullable=True)
    dataset_id = Column(UUID(as_uuid=True), ForeignKey("datasets.id"), nullable=True)
    step = Column(Enum(WorkflowStep, name="workflowstep"), nullable=False)
    state = Column(Enum(WorkflowState, name="workflowstate"), nullable=False, default=WorkflowState.queued)
    error = Column(Text, nullable=True)
    progress = Column(Integer, nullable=True)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace")
    upload = relationship("Upload", back_populates="workflows")
    dataset = relationship("Dataset", back_populates="workflows")
