import enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Enum,
    BigInteger,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database import Base
from .user import User


class UploadStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


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
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
