
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
from .user import User

class Investor(Base):
    __tablename__ = "investors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # List of focus areas
    funding_type = Column(String, nullable=False)  # "grant", "equity", "debt"
    region = Column(String, nullable=True)
    sdg_tags = Column(JSON, nullable=True)  # List of SDG numbers
    ticket_size_min = Column(Float, nullable=True)
    ticket_size_max = Column(Float, nullable=True)
    website_url = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    requirements = Column(JSON, nullable=True)  # Investment criteria
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InvestorMatch(Base):
    __tablename__ = "investor_matches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    filters_applied = Column(JSON, nullable=True)  # Matching criteria used
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    investor = relationship("Investor")

class PitchSummary(Base):
    __tablename__ = "pitch_summaries"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False)
    pitch_text = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    investor = relationship("Investor")
