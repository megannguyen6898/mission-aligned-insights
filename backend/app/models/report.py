
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from .user import User

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    framework = Column(String, nullable=False)  # e.g., "SDG", "ESG", "B Impact"
    report_url = Column(String, nullable=True)  # URL to generated report file
    report_content = Column(Text, nullable=True)  # Generated report content
    metrics = Column(JSON, nullable=True)  # Calculated metrics
    visualizations = Column(JSON, nullable=True)  # Chart configurations
    framework_mapping = Column(JSON, nullable=True)  # SDG/ESG mappings
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="reports")
