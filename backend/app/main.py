"""
IELTS Master Platform - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import logging
import uvicorn

from app.core.config import settings
from app.core.security import verify_token, create_access_token, verify_password, get_password_hash, get_current_user
from app.services.production_multi_agent import ProductionMultiAgentScoringEngine
from app.services.ai_feedback_generator import AdvancedAIFeedbackGenerator
from app.database import init_database, get_db, DatabaseManager
from app.models.user import User
from app.models.essay_submission import EssaySubmission
from sqlalchemy.orm import Session

# Import mentorship API
from app.api import mentorship

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
multi_agent_engine = None
ai_feedback_generator = None
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global multi_agent_engine, ai_feedback_generator
    
    # Startup
    logger.info("🚀 Starting IELTS Master Platform...")
    
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    # Initialize production multi-agent scoring engine
    try:
        multi_agent_engine = ProductionMultiAgentScoringEngine(
            openai_api_key=settings.OPENAI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        logger.info("✅ Production Multi-Agent Scoring Engine initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Multi-Agent Engine: {e}")
        multi_agent_engine = None
    
    # Initialize AI feedback generator
    try:
        ai_feedback_generator = AdvancedAIFeedbackGenerator(
            openai_api_key=settings.OPENAI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        logger.info("✅ AI Feedback Generator initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI Feedback Generator: {e}")
        ai_feedback_generator = None
    
    logger.info("🎉 IELTS Master Platform started successfully!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down IELTS Master Platform...")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Advanced IELTS Writing Assessment Platform with AI-Powered Feedback",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# get_current_user is now imported from app.core.security


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "multi_agent_engine_loaded": multi_agent_engine is not None,
        "ai_feedback_available": ai_feedback_generator is not None
    }


# Authentication endpoints
@app.post("/api/v1/auth/register")
async def register_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    first_language: str = Form(None),
    target_band_score: float = Form(None),
    current_level: str = Form("beginner"),
    learning_goals: str = Form(None),
    role: str = Form("student"),
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = DatabaseManager.get_user_by_email(db, email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        existing_username = DatabaseManager.get_user_by_username(db, username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create new user
        user_data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name,
            "first_language": first_language,
            "target_band_score": target_band_score,
            "current_level": current_level,
            "learning_goals": learning_goals,
            "role": role
        }
        
        user = DatabaseManager.create_user(db, user_data)
        
        # Create access token
        access_token = create_access_token(subject=str(user.id))
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )


@app.post("/api/v1/auth/login")
async def login_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Login user"""
    try:
        # Try to find user by email or username
        user = DatabaseManager.get_user_by_email(db, username)
        if not user:
            user = DatabaseManager.get_user_by_username(db, username)
        
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create access token
        access_token = create_access_token(subject=str(user.id))
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


@app.post("/api/v1/auth/logout")
async def logout_user(current_user: dict = Depends(get_current_user)):
    """Logout user"""
    # TODO: Implement user logout
    return {"message": "User logged out successfully"}


@app.post("/api/v1/admin/create-test-user")
async def create_test_user(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(...),
    role: str = Form("student")
):
    """Temporary endpoint to create test admin accounts"""
    try:
        from app.database import get_db
        from app.models.user import User
        
        db = next(get_db())
        
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            return {"message": f"User {email} already exists", "status": "exists"}
        
        # Create new user - let DatabaseManager handle password hashing
        user_data = {
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name,
            "role": role
        }
        
        new_user = DatabaseManager.create_user(db, user_data)
        
        return {
            "message": f"Test user {email} created successfully",
            "user_id": new_user.id,
            "role": new_user.role,
            "password": password
        }
        
    except Exception as e:
        return {"error": f"Failed to create test user: {str(e)}"}


@app.get("/api/v1/admin/test-users")
async def get_test_users():
    """Get all test users for debugging"""
    try:
        from app.database import get_db
        from app.models.user import User
        
        db = next(get_db())
        users = db.query(User).filter(User.email.like('admin%@edprep.ai')).all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role,
                "is_verified": user.is_verified,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return {"users": user_list, "count": len(user_list)}
        
    except Exception as e:
        return {"error": f"Failed to get test users: {str(e)}"}


@app.post("/api/v1/admin/setup-mentor-profiles")
async def setup_mentor_profiles():
    """Set up mentor profiles for Railway testing"""
    try:
        from app.database import get_db
        from app.models.user import User
        from app.models.mentorship import UserProfile
        import json
        
        db = next(get_db())
        
        # Set up mentor profiles for admin2 and admin3
        mentor_profiles = [
            {
                "user_id": 2,  # admin2
                "is_available_for_mentorship": True,
                "mentorship_status": "available",
                "max_mentees": 3,
                "bio": "Professional IELTS mentor specializing in writing and speaking. I provide comprehensive support to help students excel in all IELTS components.",
                "teaching_experience": "5+ years of IELTS mentoring experience",
                "specializations": ["Writing", "Speaking", "Listening", "Reading"],
                "certifications": ["IELTS Mentor Certificate", "English Teaching License"],
                "timezone": "UTC+8",
                "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
                "available_hours": ["afternoon", "evening"]
            },
            {
                "user_id": 3,  # admin3
                "is_available_for_mentorship": True,
                "mentorship_status": "available",
                "max_mentees": 2,
                "bio": "Experienced IELTS tutor with expertise in academic writing and test strategies. I help students achieve their target band scores.",
                "teaching_experience": "3+ years of IELTS tutoring experience",
                "specializations": ["Writing", "Reading", "Test Strategies"],
                "certifications": ["IELTS Tutor Certificate", "TESOL Certificate"],
                "timezone": "UTC+5",
                "available_days": ["Tuesday", "Thursday", "Sunday"],
                "available_hours": ["morning", "afternoon"]
            }
        ]
        
        created_profiles = []
        for profile_data in mentor_profiles:
            # Check if profile already exists
            existing_profile = db.query(UserProfile).filter(UserProfile.user_id == profile_data["user_id"]).first()
            
            if existing_profile:
                # Update existing profile
                for key, value in profile_data.items():
                    if hasattr(existing_profile, key):
                        setattr(existing_profile, key, value)
                created_profiles.append(f"Updated profile for user {profile_data['user_id']}")
            else:
                # Create new profile
                profile = UserProfile(**profile_data)
                db.add(profile)
                created_profiles.append(f"Created profile for user {profile_data['user_id']}")
        
        db.commit()
        
        return {
            "message": "Mentor profiles set up successfully",
            "profiles": created_profiles
        }
        
    except Exception as e:
        return {"error": f"Failed to set up mentor profiles: {str(e)}"}


# User dashboard and progress endpoints
@app.get("/api/v1/user/profile")
async def get_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile and progress"""
    try:
        if current_user.get("isGuest", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Guest users cannot access profile"
            )
        
        user_id = int(current_user["user_id"])
        user = DatabaseManager.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get user progress
        progress = DatabaseManager.get_user_progress(db, user_id)
        
        # Get recent essays
        recent_essays = DatabaseManager.get_user_essays(db, user_id, limit=5)
        
        return {
            "user": user.to_dict(),
            "progress": {
                "essays_written": progress.essays_written if progress else 0,
                "average_score": progress.average_score if progress else 0,
                "best_score": progress.best_score if progress else 0,
                "improvement_rate": progress.improvement_rate if progress else 0,
                "task_achievement_avg": progress.task_achievement_avg if progress else 0,
                "coherence_cohesion_avg": progress.coherence_cohesion_avg if progress else 0,
                "lexical_resource_avg": progress.lexical_resource_avg if progress else 0,
                "grammatical_range_avg": progress.grammatical_range_avg if progress else 0,
                "l1_errors_total": progress.l1_errors_total if progress else 0,
                "interlanguage_errors_total": progress.interlanguage_errors_total if progress else 0,
                "discourse_errors_total": progress.discourse_errors_total if progress else 0
            },
            "recent_essays": [essay.to_dict() for essay in recent_essays],
            "stats": {
                "total_points": user.total_points,
                "level": user.level,
                "streak_days": user.streak_days,
                "current_level": user.current_level
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/api/v1/user/essays")
async def get_user_essays(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's essay history"""
    try:
        if current_user.get("isGuest", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Guest users cannot access essay history"
            )
        
        user_id = int(current_user["user_id"])
        essays = DatabaseManager.get_user_essays(db, user_id, limit=limit)
        
        return {
            "essays": [essay.to_dict() for essay in essays],
            "total_count": len(essays)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user essays: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/api/v1/user/progress")
async def get_user_progress(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed user progress analytics"""
    try:
        if current_user.get("isGuest", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Guest users cannot access progress data"
            )
        
        user_id = int(current_user["user_id"])
        progress = DatabaseManager.get_user_progress(db, user_id)
        user = DatabaseManager.get_user_by_id(db, user_id)
        
        if not progress:
            return {
                "message": "No progress data available yet",
                "progress": {
                    "essays_written": 0,
                    "average_score": 0,
                    "best_score": 0,
                    "improvement_rate": 0
                }
            }
        
        # Calculate improvement rate (simplified)
        improvement_rate = 0
        if progress.essays_written > 1:
            # This would need more sophisticated calculation in production
            improvement_rate = 0.1  # Placeholder
        
        return {
            "progress": {
                "essays_written": progress.essays_written,
                "average_score": round(progress.average_score, 1) if progress.average_score else 0,
                "best_score": round(progress.best_score, 1) if progress.best_score else 0,
                "improvement_rate": round(improvement_rate, 2),
                "skill_breakdown": {
                    "task_achievement": round(progress.task_achievement_avg, 1) if progress.task_achievement_avg else 0,
                    "coherence_cohesion": round(progress.coherence_cohesion_avg, 1) if progress.coherence_cohesion_avg else 0,
                    "lexical_resource": round(progress.lexical_resource_avg, 1) if progress.lexical_resource_avg else 0,
                    "grammatical_range": round(progress.grammatical_range_avg, 1) if progress.grammatical_range_avg else 0
                },
                "error_analysis": {
                    "l1_errors": progress.l1_errors_total,
                    "interlanguage_errors": progress.interlanguage_errors_total,
                    "discourse_errors": progress.discourse_errors_total
                }
            },
            "user_stats": {
                "total_points": user.total_points if user else 0,
                "level": user.level if user else 1,
                "streak_days": user.streak_days if user else 0,
                "current_level": user.current_level if user else "beginner"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting user progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Essay assessment endpoints
@app.post("/api/v1/essays/assess")
async def assess_essay(
    essay_data: dict,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assess an essay using advanced ML models and save to database"""
    
    try:
        # Extract essay data
        prompt = essay_data.get("prompt", "")
        essay = essay_data.get("essay", "")
        task_type = essay_data.get("task_type", "Task 2")
        
        if not essay.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Essay text is required"
            )
        
        # Score the essay
        if multi_agent_engine:
            scoring_result = multi_agent_engine.score_essay(prompt, essay, task_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Multi-agent scoring engine not available"
            )
        
        # Generate feedback
        if ai_feedback_generator:
            feedback_result = ai_feedback_generator.generate_comprehensive_feedback(
                prompt=prompt,
                essay=essay,
                scores=scoring_result["scores"],
                error_analysis=scoring_result["error_analysis"],
                task_type=task_type
            )
        else:
            # Fallback feedback
            feedback_result = {
                "detailed_feedback": "Feedback generation not available",
                "suggestions": ["Please try again later"],
                "improvement_plan": {"immediate_focus": ["Practice writing more essays"]},
                "strengths_weaknesses": {"strengths": [], "weaknesses": ["Needs improvement"]},
                "error_analysis": scoring_result["error_analysis"],
                "feedback_type": "fallback"
            }
        
        # Save essay and assessment to database (only for real users, not guests)
        submission_id = None
        if not current_user.get("isGuest", False):
            try:
                submission_data = {
                    "prompt": prompt,
                    "essay": essay,
                    "task_type": task_type,
                    "word_count": len(essay.split()),
                    "scores": scoring_result["scores"],
                    "overall_band_score": scoring_result["scores"]["overall_band_score"],
                    "confidence": scoring_result.get("confidence", 0.8),
                    "assessment_method": scoring_result.get("assessment_method", "multi_agent"),
                    "feedback": feedback_result,
                    "error_analysis": scoring_result.get("error_analysis", {}),
                    "suggestions": feedback_result.get("suggestions", []),
                    "is_gibberish": scoring_result.get("is_gibberish", False)
                }
                
                submission = DatabaseManager.save_essay_submission(
                    db, 
                    int(current_user["user_id"]), 
                    submission_data
                )
                submission_id = submission.id
                logger.info(f"✅ Essay submission saved with ID: {submission_id}")
                
            except Exception as e:
                logger.error(f"❌ Error saving essay submission: {e}")
                # Continue without failing the assessment
        
        return {
            "scores": scoring_result["scores"],
            "feedback": feedback_result,
            "assessment_metadata": {
                "is_gibberish": scoring_result.get("is_gibberish", False),
                "confidence": scoring_result.get("confidence", 0.8),
                "word_count": len(essay.split()),
                "assessment_method": scoring_result.get("assessment_method", "multi_agent"),
                "submission_id": submission_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error assessing essay: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during essay assessment"
        )


@app.get("/api/v1/essays/prompts")
async def get_essay_prompts(
    task_type: str = "Task 2",
    difficulty: str = "intermediate",
    limit: int = 10
):
    """Get available essay prompts"""
    
    # TODO: Implement database query for prompts
    sample_prompts = [
        {
            "id": 1,
            "prompt": "Some people believe that technology has made our lives more complicated, while others think it has made life easier. Discuss both views and give your opinion.",
            "task_type": "Task 2",
            "topic_category": "technology",
            "difficulty_level": "intermediate"
        },
        {
            "id": 2,
            "prompt": "Many people believe that social media has a negative impact on society. To what extent do you agree or disagree?",
            "task_type": "Task 2",
            "topic_category": "social_media",
            "difficulty_level": "intermediate"
        },
        {
            "id": 3,
            "prompt": "The chart below shows the percentage of households in different income brackets in a city from 2010 to 2020. Summarize the information by selecting and reporting the main features, and make comparisons where relevant.",
            "task_type": "Task 1",
            "topic_category": "economics",
            "difficulty_level": "beginner"
        }
    ]
    
    # Filter by task type and difficulty
    filtered_prompts = [
        p for p in sample_prompts 
        if p["task_type"] == task_type and p["difficulty_level"] == difficulty
    ]
    
    return {
        "prompts": filtered_prompts[:limit],
        "total": len(filtered_prompts)
    }


@app.get("/api/v1/essays/history")
async def get_essay_history(
    current_user: dict = Depends(get_current_user),
    limit: int = 20,
    offset: int = 0
):
    """Get user's essay history"""
    
    # TODO: Implement database query for user's essays
    return {
        "essays": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }


# Analytics endpoints
@app.get("/api/v1/analytics/progress")
async def get_user_progress(
    current_user: dict = Depends(get_current_user)
):
    """Get user's progress analytics"""
    
    # TODO: Implement progress analytics
    return {
        "overall_progress": {
            "essays_written": 0,
            "average_score": 0.0,
            "best_score": 0.0,
            "improvement_rate": 0.0
        },
        "skill_breakdown": {
            "task_achievement": {"current": 0.0, "target": 7.0, "trend": "stable"},
            "coherence_cohesion": {"current": 0.0, "target": 7.0, "trend": "stable"},
            "lexical_resource": {"current": 0.0, "target": 7.0, "trend": "stable"},
            "grammatical_range": {"current": 0.0, "target": 7.0, "trend": "stable"}
        },
        "error_analysis": {
            "l1_errors": {"total": 0, "trend": "decreasing"},
            "interlanguage_errors": {"total": 0, "trend": "decreasing"},
            "discourse_errors": {"total": 0, "trend": "decreasing"}
        },
        "achievements": [],
        "streak_days": 0,
        "total_points": 0
    }


@app.get("/api/v1/analytics/performance")
async def get_performance_analytics(
    current_user: dict = Depends(get_current_user),
    period: str = "30d"  # 7d, 30d, 90d, 1y
):
    """Get detailed performance analytics"""
    
    # TODO: Implement performance analytics
    return {
        "period": period,
        "score_trend": [],
        "error_trend": [],
        "improvement_areas": [],
        "strengths": [],
        "recommendations": []
    }


# Learning endpoints
@app.post("/api/v1/learning/assess-level")
async def assess_user_level(
    assessment_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Assess user's current writing level"""
    
    # TODO: Implement level assessment
    return {
        "current_level": "intermediate",
        "recommended_ai_role": "explainer",
        "learning_path": [],
        "target_band_score": 7.0
    }


@app.get("/api/v1/learning/sessions")
async def get_learning_sessions(
    current_user: dict = Depends(get_current_user),
    ai_role: str = "explainer"
):
    """Get personalized learning sessions"""
    
    # TODO: Implement learning session generation
    return {
        "sessions": [],
        "recommended_role": ai_role,
        "progress": {
            "completed_sessions": 0,
            "total_sessions": 0,
            "current_streak": 0
        }
    }


@app.post("/api/v1/learning/sessions/{session_id}/complete")
async def complete_learning_session(
    session_id: int,
    session_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Complete a learning session"""
    
    # TODO: Implement session completion
    return {
        "session_id": session_id,
        "completed": True,
        "points_earned": 10,
        "next_session": None
    }


# Gamification endpoints
@app.get("/api/v1/gamification/leaderboard")
async def get_leaderboard(
    period: str = "weekly",  # daily, weekly, monthly, all_time
    limit: int = 50
):
    """Get leaderboard"""
    
    # TODO: Implement leaderboard
    return {
        "period": period,
        "leaderboard": [],
        "user_rank": None,
        "user_points": 0
    }


@app.get("/api/v1/gamification/achievements")
async def get_user_achievements(
    current_user: dict = Depends(get_current_user)
):
    """Get user achievements"""
    
    # TODO: Implement achievements
    return {
        "achievements": [],
        "total_achievements": 0,
        "recent_achievements": []
    }


# Include mentorship API routes
app.include_router(mentorship.router)

# Include mentorship sessions API routes
from app.api import mentorship_sessions
app.include_router(mentorship_sessions.router, prefix="/api/v1/mentorship", tags=["mentorship-sessions"])

# Include learning sessions API routes (Writing Coach M1 skeleton)
from app.api import learning_sessions
app.include_router(learning_sessions.router)


# Admin endpoints
@app.get("/api/v1/admin/stats")
async def get_admin_stats():
    """Get platform statistics (admin only)"""
    
    # TODO: Implement admin statistics
    return {
        "total_users": 0,
        "total_essays": 0,
        "active_users_today": 0,
        "average_score": 0.0,
        "system_health": "healthy"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
