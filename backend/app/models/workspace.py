import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    uploads = relationship("Upload", back_populates="workspace")
    datasets = relationship("Dataset", back_populates="workspace")
    members = relationship("WorkspaceMember", back_populates="workspace", cascade="all, delete-orphan")
    ai_events = relationship("AIEvent", back_populates="workspace")


class WorkspaceRole(str, enum.Enum):
    admin = "admin"
    member = "member"
    viewer = "viewer"


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(WorkspaceRole, name="workspacerole"), nullable=False, default=WorkspaceRole.member)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")
