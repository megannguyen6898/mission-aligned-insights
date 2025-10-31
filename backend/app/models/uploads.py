import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    BigInteger,
    JSON,
    Text,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base
from .user import User


class UploadStatus(str, enum.Enum):
    """Lifecycle states for an uploaded workbook."""

    created = "created"
    uploaded = "uploaded"
    pending = "pending"
    validated = "validated"
    failed = "failed"
    ingested = "ingested"


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    object_key = Column(String, nullable=False)
    checksum = Column(String, nullable=True)
    status = Column(
        Enum(UploadStatus, name="uploadfilestatus"),
        default=UploadStatus.created,
        nullable=False,
    )
    template_version = Column(String, nullable=False, default="v1")
    errors_json = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
    workspace = relationship("Workspace", back_populates="uploads")
    workflows = relationship("Workflow", back_populates="upload", cascade="all, delete-orphan")
    dataset = relationship("Dataset", back_populates="upload", uselist=False)

    # Compatibility aliases for new API language
    @property
    def storage_key(self) -> str:
        return self.object_key

    @storage_key.setter
    def storage_key(self, value: str) -> None:
        self.object_key = value

    @property
    def size_bytes(self) -> int:
        return self.size

    @size_bytes.setter
    def size_bytes(self, value: int) -> None:
        self.size = value
