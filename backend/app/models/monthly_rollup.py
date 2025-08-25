from sqlalchemy import Column, Date, Float, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..database import Base

class MonthlyRollup(Base):
    __tablename__ = "monthly_rollups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_fk = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    month = Column(Date, nullable=False)
    total_received = Column(Float, nullable=False, default=0)
    total_spent = Column(Float, nullable=False, default=0)
    total_beneficiaries = Column(Integer, nullable=False, default=0)
    cost_per_beneficiary = Column(Float, nullable=True)
    source_system = Column(String, nullable=False, default="derived")

    project = relationship("Project", backref="monthly_rollups")

    __table_args__ = (
        UniqueConstraint("project_fk", "month", name="uq_rollup_project_month"),
    )
