
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from ..database import Base

class SourceType(str, enum.Enum):
    manual = "manual"
    xero = "xero"
    google_sheets = "google_sheets"
    google_docs = "google_docs"

class UploadStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class DataUpload(Base):
    __tablename__ = "data_uploads"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    source_type = Column(Enum(SourceType), nullable=False)
    status = Column(Enum(UploadStatus), default=UploadStatus.pending)
    row_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    upload_metadata = Column(Text, nullable=True)  # JSON string for additional data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="data_uploads")
    projects = relationship("Project", back_populates="data_upload")