from sqlalchemy import Column, Float, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base

class ProjectSummary(Base):
    __tablename__ = "project_summary"

    project_fk = Column(String, ForeignKey("projects.id"), primary_key=True)
    total_received = Column(Float, nullable=False, default=0)
    total_spent = Column(Float, nullable=False, default=0)
    total_beneficiaries = Column(Integer, nullable=False, default=0)
    cost_per_beneficiary = Column(Float, nullable=True)

    project = relationship("Project", backref="summary")
