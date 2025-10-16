"""
Database configuration and connection management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator

# Database URL - using SQLite for development, can be changed to PostgreSQL for production
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ielts_master.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific configuration
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False  # Set to True for SQL query logging
    )
else:
    # PostgreSQL or other database configuration
    engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables
    """
    # Import all models to ensure they are registered
    from app.models.user import User, UserProgress, UserSession, Base
    from app.models.essay_submission import EssaySubmission, UserMistake, StudyPlan, LearningSession
    from app.models.teaching import TeachingSession, TeachingTurn, DraftVersion, Checkpoint
    from app.models.mentorship import MentorshipConnection, MentorshipMessage, MentorshipSession, UserProfile
    
    # Create tables using single Base class
    Base.metadata.create_all(bind=engine)


def init_database():
    """
    Initialize database with tables and default data
    """
    create_tables()
    print("✅ Database tables created successfully")


# Database utility functions
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int):
        """Get user by ID"""
        from app.models.user import User
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str):
        """Get user by email"""
        from app.models.user import User
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str):
        """Get user by username"""
        from app.models.user import User
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def create_user(db: Session, user_data: dict):
        """Create a new user"""
        from app.models.user import User
        from app.core.security import get_password_hash
        
        # Hash the password
        hashed_password = get_password_hash(user_data["password"])
        
        # Create user object
        db_user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hashed_password,
            full_name=user_data.get("full_name"),
            first_language=user_data.get("first_language"),
            target_band_score=user_data.get("target_band_score"),
            current_level=user_data.get("current_level", "beginner"),
            learning_goals=user_data.get("learning_goals"),
            role=user_data.get("role", "student")
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Create initial progress record
        from app.models.user import UserProgress
        progress = UserProgress(user_id=db_user.id)
        db.add(progress)
        db.commit()
        
        return db_user
    
    @staticmethod
    def save_essay_submission(db: Session, user_id: int, submission_data: dict):
        """Save essay submission and assessment results"""
        from app.models.essay_submission import EssaySubmission
        
        submission = EssaySubmission(
            user_id=user_id,
            prompt=submission_data["prompt"],
            essay_text=submission_data["essay"],
            task_type=submission_data["task_type"],
            word_count=submission_data["word_count"],
            scores=submission_data["scores"],
            overall_band_score=submission_data["overall_band_score"],
            confidence=submission_data["confidence"],
            assessment_method=submission_data["assessment_method"],
            feedback=submission_data.get("feedback"),
            error_analysis=submission_data.get("error_analysis"),
            suggestions=submission_data.get("suggestions"),
            is_gibberish=submission_data.get("is_gibberish", False),
            processing_time_seconds=submission_data.get("processing_time_seconds")
        )
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        
        # Update user progress
        DatabaseManager.update_user_progress(db, user_id, submission)
        
        return submission
    
    @staticmethod
    def update_user_progress(db: Session, user_id: int, submission):
        """Update user progress based on new submission"""
        from app.models.user import UserProgress, User
        
        # Get or create user progress
        progress = db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
        if not progress:
            progress = UserProgress(user_id=user_id)
            db.add(progress)
        
        # Update progress metrics
        progress.essays_written += 1
        
        # Update average scores
        if progress.average_score is None:
            progress.average_score = submission.overall_band_score
        else:
            # Calculate new average
            total_score = progress.average_score * (progress.essays_written - 1) + submission.overall_band_score
            progress.average_score = total_score / progress.essays_written
        
        # Update best score
        if progress.best_score is None or submission.overall_band_score > progress.best_score:
            progress.best_score = submission.overall_band_score
        
        # Update skill-specific averages
        scores = submission.scores
        if scores:
            if progress.task_achievement_avg is None:
                progress.task_achievement_avg = scores.get("task_achievement", 0)
            else:
                total_ta = progress.task_achievement_avg * (progress.essays_written - 1) + scores.get("task_achievement", 0)
                progress.task_achievement_avg = total_ta / progress.essays_written
            
            if progress.coherence_cohesion_avg is None:
                progress.coherence_cohesion_avg = scores.get("coherence_cohesion", 0)
            else:
                total_cc = progress.coherence_cohesion_avg * (progress.essays_written - 1) + scores.get("coherence_cohesion", 0)
                progress.coherence_cohesion_avg = total_cc / progress.essays_written
            
            if progress.lexical_resource_avg is None:
                progress.lexical_resource_avg = scores.get("lexical_resource", 0)
            else:
                total_lr = progress.lexical_resource_avg * (progress.essays_written - 1) + scores.get("lexical_resource", 0)
                progress.lexical_resource_avg = total_lr / progress.essays_written
            
            if progress.grammatical_range_avg is None:
                progress.grammatical_range_avg = scores.get("grammatical_range", 0)
            else:
                total_gr = progress.grammatical_range_avg * (progress.essays_written - 1) + scores.get("grammatical_range", 0)
                progress.grammatical_range_avg = total_gr / progress.essays_written
        
        # Update error counts
        if submission.error_analysis:
            error_analysis = submission.error_analysis
            progress.l1_errors_total += error_analysis.get("l1_errors", 0)
            progress.interlanguage_errors_total += error_analysis.get("interlanguage_errors", 0)
            progress.discourse_errors_total += error_analysis.get("discourse_errors", 0)
        
        # Update user points and streak
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            # Award points based on score
            points_earned = max(1, int(submission.overall_band_score * 2))  # 2 points per band score
            user.total_points += points_earned
            
            # Update level based on points
            user.level = min(10, (user.total_points // 100) + 1)  # Level up every 100 points, max level 10
            
            # Update streak (simplified - just increment for now)
            user.streak_days += 1
            user.last_activity_date = submission.submitted_at
        
        db.commit()
        return progress
    
    @staticmethod
    def get_user_essays(db: Session, user_id: int, limit: int = 10):
        """Get user's recent essays"""
        from app.models.essay_submission import EssaySubmission
        return db.query(EssaySubmission).filter(
            EssaySubmission.user_id == user_id
        ).order_by(EssaySubmission.submitted_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_user_progress(db: Session, user_id: int):
        """Get user's progress summary"""
        from app.models.user import UserProgress
        return db.query(UserProgress).filter(UserProgress.user_id == user_id).first()
