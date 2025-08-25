from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    organization_name = Column(String, nullable=True)
    mission = Column(Text, nullable=True)
    audience = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    region = Column(String, nullable=True)
    organization_size = Column(String, nullable=True)
    key_goals = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    data_uploads = relationship("DataUpload", back_populates="user")
    dashboards = relationship("Dashboard", back_populates="user")
    integrations = relationship("Integration", back_populates="user")
    reports = relationship("Report", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")
