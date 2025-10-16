"""
Teaching session persistence models for Writing Coach
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

# Use shared Base from user model to ensure one metadata
from app.models.user import Base


class TeachingSession(Base):
    __tablename__ = "teaching_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Session metadata
    role = Column(String(32), nullable=False)  # questioner | explainer | challenger
    task_type = Column(String(32), nullable=False, default="Task 2")
    goal = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="active")  # active | completed

    # Draft latest snapshot (redundant cache for quick reads)
    latest_draft_content = Column(Text, nullable=True)
    latest_draft_version = Column(Integer, nullable=False, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    turns = relationship("TeachingTurn", back_populates="session", cascade="all, delete-orphan")
    drafts = relationship("DraftVersion", back_populates="session", cascade="all, delete-orphan")


class TeachingTurn(Base):
    __tablename__ = "teaching_turns"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("teaching_sessions.id"), nullable=False, index=True)

    role = Column(String(32), nullable=False)
    user_input = Column(Text, nullable=True)
    agent_output = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("TeachingSession", back_populates="turns")


class DraftVersion(Base):
    __tablename__ = "draft_versions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("teaching_sessions.id"), nullable=False, index=True)

    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    session = relationship("TeachingSession", back_populates="drafts")


