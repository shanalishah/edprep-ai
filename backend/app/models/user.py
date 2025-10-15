"""
User model for IELTS Master Platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class User(Base):
    """User model for authentication and profile management"""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Profile information
    first_language = Column(String(100), nullable=True)
    target_band_score = Column(Float, nullable=True)
    current_level = Column(String(50), nullable=True)  # beginner, intermediate, advanced
    learning_goals = Column(Text, nullable=True)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), nullable=True)
    
    # Preferences
    preferred_ai_role = Column(String(50), nullable=True)  # questionnaire, explainer, challenger
    notification_preferences = Column(JSON, nullable=True)
    
    # Relationships
    essay_submissions = relationship("EssaySubmission", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', username='{self.username}')>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "first_language": self.first_language,
            "target_band_score": self.target_band_score,
            "current_level": self.current_level,
            "learning_goals": self.learning_goals,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "total_points": self.total_points,
            "level": self.level,
            "streak_days": self.streak_days,
            "preferred_ai_role": self.preferred_ai_role,
            "notification_preferences": self.notification_preferences
        }


class UserProgress(Base):
    """User progress tracking model"""
    
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    
    # Progress metrics
    essays_written = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    best_score = Column(Float, nullable=True)
    improvement_rate = Column(Float, nullable=True)
    
    # Skill-specific progress
    task_achievement_avg = Column(Float, nullable=True)
    coherence_cohesion_avg = Column(Float, nullable=True)
    lexical_resource_avg = Column(Float, nullable=True)
    grammatical_range_avg = Column(Float, nullable=True)
    
    # Error tracking
    l1_errors_total = Column(Integer, default=0)
    interlanguage_errors_total = Column(Integer, default=0)
    discourse_errors_total = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, essays_written={self.essays_written})>"


class UserSession(Base):
    """User session tracking for analytics"""
    
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    session_id = Column(String(255), nullable=False, index=True)
    
    # Session data
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Activity tracking
    essays_assessed = Column(Integer, default=0)
    learning_sessions = Column(Integer, default=0)
    pages_visited = Column(JSON, nullable=True)
    
    # Device and location
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    
    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, session_id='{self.session_id}')>"
