"""
Essay submission and assessment tracking model
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any

# Import Base from user model to ensure consistency
from app.models.user import Base


class EssaySubmission(Base):
    """Essay submission and assessment tracking"""
    
    __tablename__ = "essay_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Essay content
    prompt = Column(Text, nullable=False)
    essay_text = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=False)  # Task 1, Task 2
    word_count = Column(Integer, nullable=False)
    
    # Assessment results
    scores = Column(JSON, nullable=False)  # {"task_achievement": 6.0, "coherence_cohesion": 7.0, ...}
    overall_band_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    assessment_method = Column(String(50), nullable=False)  # multi_agent, rule_based, etc.
    
    # Feedback and analysis
    feedback = Column(JSON, nullable=True)  # Complete feedback object
    error_analysis = Column(JSON, nullable=True)  # Error categorization
    suggestions = Column(JSON, nullable=True)  # Improvement suggestions
    
    # Metadata
    is_gibberish = Column(Boolean, default=False)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    assessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships - commented out to avoid circular import issues
    # user = relationship("User", back_populates="essay_submissions")
    
    def __repr__(self):
        return f"<EssaySubmission(id={self.id}, user_id={self.user_id}, score={self.overall_band_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert essay submission to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prompt": self.prompt,
            "essay_text": self.essay_text,
            "task_type": self.task_type,
            "word_count": self.word_count,
            "scores": self.scores,
            "overall_band_score": self.overall_band_score,
            "confidence": self.confidence,
            "assessment_method": self.assessment_method,
            "feedback": self.feedback,
            "error_analysis": self.error_analysis,
            "suggestions": self.suggestions,
            "is_gibberish": self.is_gibberish,
            "processing_time_seconds": self.processing_time_seconds,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "assessed_at": self.assessed_at.isoformat() if self.assessed_at else None
        }


class UserMistake(Base):
    """Track specific mistakes made by users"""
    
    __tablename__ = "user_mistakes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    essay_submission_id = Column(Integer, ForeignKey("essay_submissions.id"), nullable=False, index=True)
    
    # Mistake details
    mistake_type = Column(String(100), nullable=False)  # l1_influenced, interlanguage, discourse, grammar, vocabulary
    mistake_category = Column(String(100), nullable=False)  # specific category within type
    mistake_description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Context
    sentence_context = Column(Text, nullable=True)
    suggested_correction = Column(Text, nullable=True)
    
    # Tracking
    frequency = Column(Integer, default=1)  # How many times this mistake was made
    is_corrected = Column(Boolean, default=False)
    correction_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    essay_submission = relationship("EssaySubmission")
    
    def __repr__(self):
        return f"<UserMistake(id={self.id}, user_id={self.user_id}, type='{self.mistake_type}')>"


class StudyPlan(Base):
    """Personalized study plans for users"""
    
    __tablename__ = "study_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Plan details
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(String(50), nullable=False)  # weekly, monthly, custom
    target_band_score = Column(Float, nullable=False)
    current_band_score = Column(Float, nullable=False)
    
    # Plan content
    goals = Column(JSON, nullable=False)  # List of specific goals
    activities = Column(JSON, nullable=False)  # List of activities and exercises
    resources = Column(JSON, nullable=True)  # Recommended resources
    timeline = Column(JSON, nullable=False)  # Timeline and milestones
    
    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<StudyPlan(id={self.id}, user_id={self.user_id}, name='{self.plan_name}')>"


class LearningSession(Base):
    """Track individual learning sessions"""
    
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session details
    session_type = Column(String(50), nullable=False)  # essay_writing, grammar_practice, vocabulary, etc.
    duration_minutes = Column(Integer, nullable=False)
    activities_completed = Column(JSON, nullable=True)
    
    # Performance metrics
    accuracy_score = Column(Float, nullable=True)
    improvement_areas = Column(JSON, nullable=True)
    strengths_demonstrated = Column(JSON, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<LearningSession(id={self.id}, user_id={self.user_id}, type='{self.session_type}')>"
