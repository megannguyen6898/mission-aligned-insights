from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from ..database import Base


class DashboardTopic(Base):
    __tablename__ = "dashboard_topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
