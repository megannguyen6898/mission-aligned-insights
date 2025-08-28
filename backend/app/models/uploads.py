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
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base
from .user import User


class UploadStatus(str, enum.Enum):
    """Lifecycle states for an uploaded workbook."""

    pending = "pending"
    validated = "validated"
    failed = "failed"
    ingested = "ingested"


class Upload(Base):
    __tablename__ = "uploads"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size = Column(BigInteger, nullable=False)
    object_key = Column(String, nullable=False)
    status = Column(
        Enum(UploadStatus, name="uploadfilestatus"),
        default=UploadStatus.pending,
        nullable=False,
    )
    template_version = Column(String, nullable=False, default="v1")
    errors_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User")
