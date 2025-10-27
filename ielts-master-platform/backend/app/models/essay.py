"""
Essay assessment models for IELTS Master Platform
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()


class Essay(Base):
    """Essay model for storing user essays and assessments"""
    
    __tablename__ = "essays"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Essay content
    prompt = Column(Text, nullable=False)
    essay_text = Column(Text, nullable=False)
    task_type = Column(String(20), nullable=False)  # Task 1, Task 2
    word_count = Column(Integer, nullable=True)
    
    # Assessment scores
    task_achievement = Column(Float, nullable=True)
    coherence_cohesion = Column(Float, nullable=True)
    lexical_resource = Column(Float, nullable=True)
    grammatical_range = Column(Float, nullable=True)
    overall_band_score = Column(Float, nullable=True)
    
    # Error analysis
    l1_errors = Column(Integer, default=0)
    interlanguage_errors = Column(Integer, default=0)
    discourse_errors = Column(Integer, default=0)
    total_errors = Column(Integer, default=0)
    
    # Assessment metadata
    is_gibberish = Column(Boolean, default=False)
    confidence_score = Column(Float, nullable=True)
    assessment_method = Column(String(50), nullable=True)  # ml_model, rule_based, hybrid
    
    # Feedback
    detailed_feedback = Column(Text, nullable=True)
    suggestions = Column(JSON, nullable=True)
    improvement_plan = Column(JSON, nullable=True)
    strengths_weaknesses = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Essay(id={self.id}, user_id={self.user_id}, score={self.overall_band_score})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert essay to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "prompt": self.prompt,
            "essay_text": self.essay_text,
            "task_type": self.task_type,
            "word_count": self.word_count,
            "task_achievement": self.task_achievement,
            "coherence_cohesion": self.coherence_cohesion,
            "lexical_resource": self.lexical_resource,
            "grammatical_range": self.grammatical_range,
            "overall_band_score": self.overall_band_score,
            "l1_errors": self.l1_errors,
            "interlanguage_errors": self.interlanguage_errors,
            "discourse_errors": self.discourse_errors,
            "total_errors": self.total_errors,
            "is_gibberish": self.is_gibberish,
            "confidence_score": self.confidence_score,
            "assessment_method": self.assessment_method,
            "detailed_feedback": self.detailed_feedback,
            "suggestions": self.suggestions,
            "improvement_plan": self.improvement_plan,
            "strengths_weaknesses": self.strengths_weaknesses,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EssayPrompt(Base):
    """Essay prompt model for storing available prompts"""
    
    __tablename__ = "essay_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Prompt content
    prompt_text = Column(Text, nullable=False)
    task_type = Column(String(20), nullable=False)  # Task 1, Task 2
    topic_category = Column(String(100), nullable=True)  # education, technology, environment, etc.
    difficulty_level = Column(String(20), nullable=True)  # beginner, intermediate, advanced
    
    # Metadata
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    average_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<EssayPrompt(id={self.id}, task_type='{self.task_type}', topic='{self.topic_category}')>"


class LearningSession(Base):
    """Learning session model for tracking user learning activities"""
    
    __tablename__ = "learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session details
    session_type = Column(String(50), nullable=False)  # writing_practice, grammar_lesson, vocabulary_building
    ai_role = Column(String(50), nullable=True)  # questionnaire, explainer, challenger
    topic = Column(String(100), nullable=True)
    
    # Session content
    content = Column(Text, nullable=True)
    exercises = Column(JSON, nullable=True)
    user_responses = Column(JSON, nullable=True)
    
    # Progress tracking
    completed_exercises = Column(Integer, default=0)
    total_exercises = Column(Integer, default=0)
    score = Column(Float, nullable=True)
    time_spent_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<LearningSession(id={self.id}, user_id={self.user_id}, type='{self.session_type}')>"


class UserAchievement(Base):
    """User achievements and badges model"""
    
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Achievement details
    achievement_type = Column(String(50), nullable=False)  # streak, score, essays_written, etc.
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    # Achievement data
    points_earned = Column(Integer, default=0)
    badge_icon = Column(String(100), nullable=True)
    
    # Timestamps
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement='{self.achievement_name}')>"
