from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from ..database import Base
from .user import User


class AuditAction(str, enum.Enum):
    upload = "upload"
    delete = "delete"
    login = "login"
    dashboard = "dashboard"
    report = "report"


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(Enum(AuditAction), nullable=False)
    target_type = Column(String, nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="audit_logs")
