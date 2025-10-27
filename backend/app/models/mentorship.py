"""
Mentorship and social interaction models
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey, Boolean, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any
import enum

# Import Base from user model to ensure consistency
from app.models.user import Base


class MentorshipStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageType(str, enum.Enum):
    TEXT = "text"
    FILE = "file"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    SYSTEM = "system"


class MentorshipConnection(Base):
    """Mentorship connection between mentor and mentee"""
    
    __tablename__ = "mentorship_connections"
    
    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Connection details
    status = Column(Enum(MentorshipStatus), default=MentorshipStatus.PENDING)
    connection_message = Column(Text, nullable=True)  # Initial message from mentee
    
    # Mentorship goals and objectives
    goals = Column(JSON, nullable=True)  # Learning objectives
    target_band_score = Column(Float, nullable=True)
    focus_areas = Column(JSON, nullable=True)  # ["writing", "speaking", etc.]
    
    # Session details
    session_frequency = Column(String(50), nullable=True)  # "weekly", "bi-weekly", etc.
    preferred_time = Column(String(100), nullable=True)  # "morning", "evening", etc.
    timezone = Column(String(50), nullable=True)
    
    # Progress tracking
    sessions_completed = Column(Integer, default=0)
    total_sessions = Column(Integer, nullable=True)
    progress_notes = Column(Text, nullable=True)
    
    # Ratings and feedback
    mentor_rating = Column(Float, nullable=True)  # Rating given by mentee to mentor
    mentee_rating = Column(Float, nullable=True)  # Rating given by mentor to mentee
    mentor_feedback = Column(Text, nullable=True)
    mentee_feedback = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    mentor = relationship("User", foreign_keys=[mentor_id], backref="mentor_connections")
    mentee = relationship("User", foreign_keys=[mentee_id], backref="mentee_connections")
    messages = relationship("MentorshipMessage", back_populates="connection", cascade="all, delete-orphan")
    sessions = relationship("MentorshipSession", back_populates="connection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MentorshipConnection(id={self.id}, mentor_id={self.mentor_id}, mentee_id={self.mentee_id}, status={self.status})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert mentorship connection to dictionary"""
        return {
            "id": self.id,
            "mentor_id": self.mentor_id,
            "mentee_id": self.mentee_id,
            "status": self.status.value if self.status else None,
            "connection_message": self.connection_message,
            "goals": self.goals,
            "target_band_score": self.target_band_score,
            "focus_areas": self.focus_areas,
            "session_frequency": self.session_frequency,
            "preferred_time": self.preferred_time,
            "timezone": self.timezone,
            "sessions_completed": self.sessions_completed,
            "total_sessions": self.total_sessions,
            "progress_notes": self.progress_notes,
            "mentor_rating": self.mentor_rating,
            "mentee_rating": self.mentee_rating,
            "mentor_feedback": self.mentor_feedback,
            "mentee_feedback": self.mentee_feedback,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class MentorshipMessage(Base):
    """Messages between mentor and mentee"""
    
    __tablename__ = "mentorship_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("mentorship_connections.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Message content
    message_type = Column(Enum(MessageType), default=MessageType.TEXT)
    content = Column(Text, nullable=True)  # Text content
    file_url = Column(String(500), nullable=True)  # File attachment URL
    file_name = Column(String(255), nullable=True)  # Original file name
    file_size = Column(Integer, nullable=True)  # File size in bytes
    
    # Message metadata
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    is_edited = Column(Boolean, default=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    connection = relationship("MentorshipConnection", back_populates="messages")
    sender = relationship("User", backref="sent_messages")
    
    def __repr__(self):
        return f"<MentorshipMessage(id={self.id}, connection_id={self.connection_id}, sender_id={self.sender_id}, type={self.message_type})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "sender_id": self.sender_id,
            "message_type": self.message_type.value if self.message_type else None,
            "content": self.content,
            "file_url": self.file_url,
            "file_name": self.file_name,
            "file_size": self.file_size,
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "is_edited": self.is_edited,
            "edited_at": self.edited_at.isoformat() if self.edited_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class MentorshipSession(Base):
    """Scheduled mentorship sessions"""
    
    __tablename__ = "mentorship_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    connection_id = Column(Integer, ForeignKey("mentorship_connections.id"), nullable=False, index=True)
    
    # Session details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    session_type = Column(String(50), nullable=False)  # "writing_feedback", "speaking_practice", "general", etc.
    
    # Scheduling
    scheduled_at = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50), nullable=True)
    
    # Session status
    status = Column(String(50), default="scheduled")  # "scheduled", "in_progress", "completed", "cancelled"
    meeting_url = Column(String(500), nullable=True)  # Video call URL
    
    # Session content
    agenda = Column(JSON, nullable=True)  # Session agenda items
    notes = Column(Text, nullable=True)  # Session notes
    homework = Column(Text, nullable=True)  # Assigned homework
    materials = Column(JSON, nullable=True)  # Shared materials
    
    # Feedback
    mentor_notes = Column(Text, nullable=True)
    mentee_notes = Column(Text, nullable=True)
    session_rating = Column(Float, nullable=True)  # Overall session rating
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    connection = relationship("MentorshipConnection", back_populates="sessions")
    
    def __repr__(self):
        return f"<MentorshipSession(id={self.id}, connection_id={self.connection_id}, title={self.title}, scheduled_at={self.scheduled_at})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "connection_id": self.connection_id,
            "title": self.title,
            "description": self.description,
            "session_type": self.session_type,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "duration_minutes": self.duration_minutes,
            "timezone": self.timezone,
            "status": self.status,
            "meeting_url": self.meeting_url,
            "agenda": self.agenda,
            "notes": self.notes,
            "homework": self.homework,
            "materials": self.materials,
            "mentor_notes": self.mentor_notes,
            "mentee_notes": self.mentee_notes,
            "session_rating": self.session_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None
        }


class UserProfile(Base):
    """Extended user profile for mentorship features"""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Mentorship preferences
    is_available_for_mentorship = Column(Boolean, default=False)
    mentorship_status = Column(String(50), default="available")  # "available", "mentoring", "mentored", "busy"
    max_mentees = Column(Integer, default=3)  # Maximum number of mentees a mentor can handle
    
    # Profile information
    bio = Column(Text, nullable=True)
    teaching_experience = Column(Text, nullable=True)
    specializations = Column(JSON, nullable=True)  # ["writing", "speaking", "listening", "reading"]
    certifications = Column(JSON, nullable=True)  # IELTS certifications, teaching certificates
    
    # Availability
    timezone = Column(String(50), nullable=True)
    available_days = Column(JSON, nullable=True)  # ["monday", "tuesday", etc.]
    available_hours = Column(JSON, nullable=True)  # ["morning", "afternoon", "evening"]
    
    # Social features
    profile_image_url = Column(String(500), nullable=True)
    social_links = Column(JSON, nullable=True)  # LinkedIn, Twitter, etc.
    
    # Statistics
    total_mentees_helped = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_sessions_conducted = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="profile")
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, is_available={self.is_available_for_mentorship})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_available_for_mentorship": self.is_available_for_mentorship,
            "mentorship_status": self.mentorship_status,
            "max_mentees": self.max_mentees,
            "bio": self.bio,
            "teaching_experience": self.teaching_experience,
            "specializations": self.specializations,
            "certifications": self.certifications,
            "timezone": self.timezone,
            "available_days": self.available_days,
            "available_hours": self.available_hours,
            "profile_image_url": self.profile_image_url,
            "social_links": self.social_links,
            "total_mentees_helped": self.total_mentees_helped,
            "average_rating": self.average_rating,
            "total_sessions_conducted": self.total_sessions_conducted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }






