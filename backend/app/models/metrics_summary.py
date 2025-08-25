from sqlalchemy import Column, Float, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base

class MetricsSummary(Base):
    __tablename__ = "metrics_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)
    total_value = Column(Float, nullable=True)

    project = relationship("Project", backref="metrics_summary")

    __table_args__ = (
        UniqueConstraint("project_fk", "metric_name", name="uq_metric_project_name"),
    )
