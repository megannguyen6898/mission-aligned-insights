
import enum

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum
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


class ReportEngine(str, enum.Enum):
    html = "html"
    docx = "docx"


class ReportTemplate(Base):
    __tablename__ = "report_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    engine = Column(Enum(ReportEngine, name="reportengine"), nullable=False)
    object_key = Column(String, nullable=False)
    version = Column(Integer, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User")


class ReportJobStatus(str, enum.Enum):
    queued = "queued"
    running = "running"
    success = "success"
    failed = "failed"


class ReportJob(Base):
    __tablename__ = "report_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    org_id = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey("report_templates.id"), nullable=False)
    params_json = Column(JSON, nullable=True)
    status = Column(
        Enum(ReportJobStatus, name="reportjobstatus"),
        nullable=False,
        default=ReportJobStatus.queued,
    )
    output_object_key = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_json = Column(JSON, nullable=True)

    template = relationship("ReportTemplate")
    user = relationship("User")
