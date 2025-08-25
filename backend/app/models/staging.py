from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func

from ..database import Base


class _StagingBase(Base):
    __abstract__ = True

    id = Column(String, primary_key=True)
    upload_id = Column(String, nullable=False)
    row_num = Column(Integer, nullable=False)
    raw_json = Column(JSON, nullable=False)
    parse_errors = Column(JSON, nullable=True)
    source_system = Column(String, nullable=False, server_default="excel")
    external_id = Column(String, nullable=True)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())
    row_hash = Column(String, nullable=True)
    import_batch_id = Column(String, ForeignKey("import_batches.id"))
    schema_version = Column(Integer, nullable=False, server_default="1")


class StgProjectInfo(_StagingBase):
    __tablename__ = "stg_project_info"


class StgActivity(_StagingBase):
    __tablename__ = "stg_activities"


class StgOutcome(_StagingBase):
    __tablename__ = "stg_outcomes"


class StgFundingResource(_StagingBase):
    __tablename__ = "stg_funding_resources"


class StgBeneficiary(_StagingBase):
    __tablename__ = "stg_beneficiaries"
