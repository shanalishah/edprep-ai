"""
IELTS Master Platform - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException, Depends, status, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import uvicorn
from datetime import datetime
import os
from pathlib import Path

from app.core.config import settings
from app.core.security import verify_token, create_access_token, verify_password, get_password_hash, get_current_user
from app.services.production_multi_agent import ProductionMultiAgentScoringEngine
from app.services.optimized_multi_agent import OptimizedMultiAgentScoringEngine
from app.services.ai_feedback_generator import AdvancedAIFeedbackGenerator
from app.services.gibberish_detector import GibberishDetector
from app.services.voice_to_text import VoiceToTextService, VoiceTranscriptionRequest, VoiceTranscriptionResponse
from app.services.grammar_corrector import RealTimeGrammarCorrector, GrammarCorrectionRequest, GrammarCorrectionResponse
from app.services.study_planner import AIStudyPlanner, StudyPlanRequest, StudyPlanResponse
from app.services.analytics import PerformanceAnalytics, AnalyticsRequest, AnalyticsDashboard
from app.services.style_analyzer import WritingStyleAnalyzer, StyleAnalysisRequest, StyleAnalysisResponse
from app.services.gamification import GamificationSystem, GamificationRequest, GamificationResponse
from app.services.multilang import MultiLanguageSupport, LocalizationRequest, LocalizationResponse, LanguageDetectionRequest, LanguageDetectionResponse
from app.services.progress_tracker import ProgressTrackerAI, ProgressTrackingRequest, ProgressTrackingResponse
from app.services.personalized_coach import PersonalizedCoachAI, CoachingRequest, CoachingResponse
from app.services.adaptive_scoring import AdaptiveScoringSystem, AdaptiveScoringRequest, AdaptiveScoringResponse
from app.core.model_config import ModelConfig, ModelSpeed, PERFORMANCE_BENCHMARKS
from app.database import init_database, get_db, DatabaseManager
from app.models.user import User
from app.models.essay_submission import EssaySubmission
from sqlalchemy.orm import Session

# Import API routers
from app.api import mentorship
from app.api import speaking
from app.api import ai_speaking_bot
from app.api import progress

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
multi_agent_engine = None
optimized_multi_agent_engine = None
ai_feedback_generator = None
gibberish_detector = None
voice_to_text_service = None
grammar_corrector = None
study_planner = None
analytics_service = None
style_analyzer = None
gamification_system = None
multilang_service = None
progress_tracker = None
personalized_coach = None
adaptive_scoring = None
current_speed_config = ModelSpeed.BALANCED
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global multi_agent_engine, optimized_multi_agent_engine, ai_feedback_generator, gibberish_detector, voice_to_text_service, grammar_corrector, study_planner, analytics_service, style_analyzer, gamification_system, multilang_service, progress_tracker, personalized_coach, adaptive_scoring, current_speed_config
    
    # Startup
    logger.info("🚀 Starting IELTS Master Platform...")
    
    # Initialize database
    try:
        init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
    
    # Initialize gibberish detector
    try:
        gibberish_detector = GibberishDetector()
        logger.info("✅ Gibberish Detector initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Gibberish Detector: {e}")
        gibberish_detector = None
    
    # Initialize progress tracker
    try:
        progress_tracker = ProgressTrackerAI(
            openai_api_key=settings.OPENAI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        logger.info("✅ Progress Tracker AI initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Progress Tracker: {e}")
        progress_tracker = None
    
    # Initialize Personalized Coach AI
    try:
        personalized_coach = PersonalizedCoachAI(
            openai_api_key=settings.OPENAI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY
        )
        logger.info("✅ Personalized Coach AI initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Personalized Coach: {e}")
        personalized_coach = None
    
    # Initialize Adaptive Scoring System
    try:
        adaptive_scoring = AdaptiveScoringSystem()
        logger.info("✅ Adaptive Scoring System initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Adaptive Scoring: {e}")
        adaptive_scoring = None
    
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
    
    # Initialize optimized multi-agent scoring engine
    try:
        optimized_multi_agent_engine = OptimizedMultiAgentScoringEngine(
            openai_api_key=settings.OPENAI_API_KEY,
            anthropic_api_key=settings.ANTHROPIC_API_KEY,
            speed=current_speed_config
        )
        logger.info("✅ Optimized Multi-Agent Scoring Engine initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Optimized Multi-Agent Engine: {e}")
        optimized_multi_agent_engine = None
    
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
    
    logger.info("🎉 IELTS Master Platform started successfully! (v2.1.2 - Speed Optimized)")
    
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
        logger.info(f"🔍 Login attempt for username: {username}")
        
        # Try to find user by email or username
        user = DatabaseManager.get_user_by_email(db, username)
        if not user:
            user = DatabaseManager.get_user_by_username(db, username)
        
        if not user:
            logger.warning(f"❌ User not found: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        logger.info(f"✅ User found: {user.email}, is_active: {user.is_active}")
        
        if not verify_password(password, user.hashed_password):
            logger.warning(f"❌ Password verification failed for: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email/username or password"
            )
        
        if not user.is_active:
            logger.warning(f"❌ Account deactivated for: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        logger.info(f"✅ Login successful for: {username}")
        
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
        
        # Create new user with plain text password for Railway testing
        db_user = User(
            email=email,
            username=username,
            hashed_password=password,  # Store as plain text for Railway testing
            full_name=full_name,
            first_language=None,
            target_band_score=None,
            current_level="beginner",
            learning_goals=None,
            role=role
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {
            "message": f"Test user {email} created successfully",
            "user_id": db_user.id,
            "role": db_user.role,
            "password": password
        }
        
    except Exception as e:
        return {"error": f"Failed to create test user: {str(e)}"}


@app.post("/api/v1/admin/reset-password")
async def reset_user_password(
    email: str = Form(...),
    new_password: str = Form(...)
):
    """Reset password for existing users"""
    try:
        from app.database import get_db
        from app.models.user import User
        
        db = next(get_db())
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return {"error": f"User {email} not found"}
        
        # Update password (store as plain text for local development)
        user.hashed_password = new_password
        db.commit()
        
        return {
            "message": f"Password reset successfully for {email}",
            "user_id": user.id,
            "username": user.username,
            "new_password": new_password
        }
        
    except Exception as e:
        return {"error": f"Failed to reset password: {str(e)}"}


@app.post("/api/v1/admin/upload-file")
async def upload_file_to_volume(
    file: UploadFile = File(...),
    folder: str = Form("")
):
    """Upload files to the Railway volume for test data"""
    try:
        # Create data directory if it doesn't exist
        data_dir = Path("/data")
        if folder:
            data_dir = data_dir / folder
        
        data_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file to volume
        file_path = data_dir / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "message": f"File uploaded successfully",
            "filename": file.filename,
            "path": str(file_path),
            "size": len(content)
        }
        
    except Exception as e:
        return {"error": f"Failed to upload file: {str(e)}"}


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
        
        # Get word count for analysis
        word_count = len(essay.split())
        
        # Check for gibberish content
        gibberish_result = None
        if gibberish_detector:
            try:
                gibberish_result = gibberish_detector.detect_gibberish(essay)
                if gibberish_result['is_gibberish']:
                    logger.warning(f"🚨 Gibberish detected: {gibberish_result['reasons']}")
                    
                    # Return gibberish feedback immediately
                    gibberish_feedback = gibberish_detector.get_gibberish_feedback(gibberish_result)
                    
                    return {
                        "scores": {
                            "task_achievement": gibberish_result.get('score', 1.0),
                            "coherence_cohesion": gibberish_result.get('score', 1.0),
                            "lexical_resource": gibberish_result.get('score', 1.0),
                            "grammatical_range": gibberish_result.get('score', 1.0),
                            "overall_band_score": gibberish_result.get('score', 1.0)
                        },
                        "feedback": gibberish_feedback,
                        "assessment_metadata": {
                            "assessment_method": "gibberish_detection",
                            "processing_time_seconds": 0.1,
                            "word_count": word_count,
                            "gibberish_detection": gibberish_result
                        }
                    }
            except Exception as e:
                logger.error(f"❌ Gibberish detection failed: {e}")
                gibberish_result = None
        
        # Score the essay using optimized engine
        if optimized_multi_agent_engine:
            scoring_result = optimized_multi_agent_engine.score_essay(prompt, essay, task_type)
        elif multi_agent_engine:
            scoring_result = multi_agent_engine.score_essay(prompt, essay, task_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scoring engine not available"
            )
        
        # Generate feedback
        feedback_result = None
        if ai_feedback_generator:
            try:
                feedback_result = ai_feedback_generator.generate_comprehensive_feedback(
                    prompt=prompt,
                    essay=essay,
                    scores=scoring_result["scores"],
                    error_analysis=scoring_result.get("feedback", {}).get("error_analysis", []),
                    task_type=task_type
                )
                logger.info("✅ Feedback generated successfully")
            except Exception as e:
                logger.error(f"❌ Feedback generation failed: {e}")
                feedback_result = None
        
        # Always use enhanced fallback feedback for now (since AI feedback is having issues)
        if True:  # Force enhanced fallback for now
            # Enhanced fallback feedback using scoring results
            agent_results = scoring_result.get("agent_results", {})
            
            # Extract strengths and weaknesses from agent results
            all_strengths = []
            all_weaknesses = []
            all_suggestions = []
            
            for agent_name, result in agent_results.items():
                all_strengths.extend(result.get("strengths", []))
                all_weaknesses.extend(result.get("weaknesses", []))
                all_suggestions.extend(result.get("suggestions", []))
            
            # Create detailed feedback based on scores
            overall_score = scoring_result.get("overall_band_score", scoring_result.get("scores", {}).get("overall_band_score", 5.0))
            
            # Get individual scores
            task_score = scoring_result.get("scores", {}).get("task_achievement", 5.0)
            coherence_score = scoring_result.get("scores", {}).get("coherence_cohesion", 5.0)
            lexical_score = scoring_result.get("scores", {}).get("lexical_resource", 5.0)
            grammar_score = scoring_result.get("scores", {}).get("grammatical_range", 5.0)
            
            # Generate appropriate feedback based on scores
            def get_score_feedback(score, criterion):
                if score <= 2.0:
                    return f"Needs significant improvement in {criterion}"
                elif score <= 4.0:
                    return f"Limited performance in {criterion}"
                elif score <= 6.0:
                    return f"Adequate performance in {criterion}"
                elif score <= 8.0:
                    return f"Good performance in {criterion}"
                else:
                    return f"Excellent performance in {criterion}"
            
            detailed_feedback = f"""
Your essay received an overall band score of {overall_score}.

**Task Achievement ({task_score}):** {get_score_feedback(task_score, "addressing the task requirements")}

**Coherence and Cohesion ({coherence_score}):** {get_score_feedback(coherence_score, "organizing ideas and using linking devices")}

**Lexical Resource ({lexical_score}):** {get_score_feedback(lexical_score, "vocabulary range and word choice")}

**Grammatical Range and Accuracy ({grammar_score}):** {get_score_feedback(grammar_score, "grammar accuracy and sentence variety")}
"""
            
            # Generate appropriate suggestions based on overall score
            if overall_score <= 2.0:
                default_suggestions = [
                    "Write a complete essay with at least 250 words",
                    "Address all parts of the task prompt",
                    "Use proper sentence structure",
                    "Include an introduction and conclusion",
                    "Practice basic English writing skills"
                ]
            elif overall_score <= 4.0:
                default_suggestions = [
                    "Develop your ideas more fully",
                    "Use linking words to connect ideas",
                    "Improve grammar and vocabulary",
                    "Follow proper essay structure",
                    "Practice writing longer essays"
                ]
            else:
                default_suggestions = [
                    "Review your essay for grammar and vocabulary errors",
                    "Ensure all parts of the task are addressed",
                    "Improve paragraph organization",
                    "Use more varied vocabulary",
                    "Practice complex sentence structures"
                ]
            
            feedback_result = {
                "detailed_feedback": detailed_feedback.strip(),
                "suggestions": all_suggestions[:5] if all_suggestions else default_suggestions,
                "improvement_plan": {
                    "immediate_focus": all_weaknesses[:3] if all_weaknesses else ["Practice writing more essays"],
                    "short_term_goals": ["Improve overall writing skills", "Focus on weak areas"],
                    "long_term_goals": ["Achieve target IELTS score"],
                    "recommended_resources": ["IELTS writing practice books", "Online writing courses"]
                },
                "strengths_weaknesses": {
                    "strengths": all_strengths[:3] if all_strengths else ["Attempted the task"],
                    "weaknesses": all_weaknesses[:3] if all_weaknesses else ["Needs improvement in all areas"]
                },
                "error_analysis": scoring_result.get("error_analysis", []),
                "feedback_type": "enhanced_fallback"
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

# Include test library API routes
from app.api import test_library
app.include_router(test_library.router)

# Include speaking test API routes
app.include_router(speaking.router, prefix="/api/v1/speaking", tags=["speaking"])
app.include_router(ai_speaking_bot.router, prefix="/api/v1/ai-speaking-bot", tags=["ai-speaking-bot"])
app.include_router(progress.router, prefix="/api/v1", tags=["progress"])

# Static file serving for audio files
@app.get("/api/v1/audio/{file_path:path}")
async def serve_audio_file(file_path: str):
    """Serve audio files from the ARCHIVE directory"""
    try:
        # Construct the full path to the audio file
        archive_path = Path("/Users/shan/Desktop/Work/Projects/EdPrep AI/ARCHIVE/test-data/IELTS")
        full_path = archive_path / file_path
        
        # Security check - ensure the path is within the archive directory
        if not str(full_path.resolve()).startswith(str(archive_path.resolve())):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Check if it's an audio file
        if not full_path.suffix.lower() in ['.mp3', '.wav', '.m4a']:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        return FileResponse(
            path=str(full_path),
            media_type="audio/mpeg",
            filename=full_path.name
        )
    except Exception as e:
        logger.error(f"Error serving audio file {file_path}: {e}")
        raise HTTPException(status_code=500, detail="Error serving audio file")


# Speed configuration endpoints
@app.get("/api/v1/config/speed")
async def get_speed_config():
    """Get current speed configuration"""
    global current_speed_config, optimized_multi_agent_engine
    
    config_info = ModelConfig.get_model_config(current_speed_config)
    benchmark = PERFORMANCE_BENCHMARKS.get(current_speed_config, PERFORMANCE_BENCHMARKS[ModelSpeed.BALANCED])
    
    return {
        "current_speed": current_speed_config.value,
        "description": config_info["description"],
        "models": {
            "openai": config_info["openai_model"],
            "anthropic": config_info["anthropic_model"]
        },
        "performance": benchmark,
        "available_speeds": ModelConfig.get_available_speeds(),
        "engine_status": "available" if optimized_multi_agent_engine else "unavailable"
    }

@app.post("/api/v1/config/speed")
async def set_speed_config(speed: str):
    """Set speed configuration"""
    global current_speed_config, optimized_multi_agent_engine
    
    try:
        # Validate speed configuration
        speed_enum = ModelSpeed(speed)
        config_info = ModelConfig.get_model_config(speed_enum)
        
        # Update global configuration
        current_speed_config = speed_enum
        
        # Reinitialize optimized engine with new speed
        if settings.OPENAI_API_KEY or settings.ANTHROPIC_API_KEY:
            optimized_multi_agent_engine = OptimizedMultiAgentScoringEngine(
                openai_api_key=settings.OPENAI_API_KEY,
                anthropic_api_key=settings.ANTHROPIC_API_KEY,
                speed=speed_enum
            )
            logger.info(f"✅ Speed configuration updated to: {speed_enum.value}")
        else:
            logger.warning("⚠️ No API keys available, cannot reinitialize engine")
        
        benchmark = PERFORMANCE_BENCHMARKS.get(speed_enum, PERFORMANCE_BENCHMARKS[ModelSpeed.BALANCED])
        
        return {
            "success": True,
            "message": f"Speed configuration updated to {speed_enum.value}",
            "new_config": {
                "speed": speed_enum.value,
                "description": config_info["description"],
                "models": {
                    "openai": config_info["openai_model"],
                    "anthropic": config_info["anthropic_model"]
                },
                "performance": benchmark
            }
        }
        
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid speed configuration. Available options: {ModelConfig.get_available_speeds()}"
        )
    except Exception as e:
        logger.error(f"❌ Failed to update speed configuration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update speed configuration"
        )

@app.get("/api/v1/config/performance")
async def get_performance_info():
    """Get detailed performance information"""
    global optimized_multi_agent_engine
    
    if optimized_multi_agent_engine:
        return optimized_multi_agent_engine.get_performance_info()
    else:
        return {
            "error": "Optimized engine not available",
            "available_speeds": ModelConfig.get_available_speeds(),
            "performance_benchmarks": PERFORMANCE_BENCHMARKS
        }


# Voice-to-Text endpoints
@app.post("/api/v1/voice/transcribe", response_model=VoiceTranscriptionResponse)
async def transcribe_voice(
    request: VoiceTranscriptionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Convert speech to text with AI-powered transcription"""
    
    if not voice_to_text_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice-to-text service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await voice_to_text_service.transcribe_audio(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Voice transcription completed in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Voice transcription failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice transcription failed"
        )


@app.get("/api/v1/voice/supported-formats")
async def get_supported_formats():
    """Get supported audio formats for voice transcription"""
    
    if not voice_to_text_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Voice-to-text service not available"
        )
    
    return {
        "formats": voice_to_text_service.get_supported_formats(),
        "languages": voice_to_text_service.get_supported_languages()
    }


# Grammar Correction endpoints
@app.post("/api/v1/grammar/correct", response_model=GrammarCorrectionResponse)
async def correct_grammar(
    request: GrammarCorrectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Real-time grammar correction"""
    
    if not grammar_corrector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grammar correction service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await grammar_corrector.correct_text(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Grammar correction completed in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Grammar correction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Grammar correction failed"
        )


@app.get("/api/v1/grammar/supported-features")
async def get_grammar_features():
    """Get supported grammar correction features"""
    
    if not grammar_corrector:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Grammar correction service not available"
        )
    
    return {
        "correction_types": grammar_corrector.get_correction_types(),
        "supported_languages": grammar_corrector.get_supported_languages(),
        "features": [
            "Real-time grammar checking",
            "Spelling correction",
            "Style improvements",
            "IELTS-specific vocabulary suggestions",
            "Punctuation fixes",
            "Structure analysis"
        ]
    }


# Study Planning endpoints
@app.post("/api/v1/study-plans/create", response_model=StudyPlanResponse)
async def create_study_plan(
    request: StudyPlanRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a personalized AI-powered study plan"""
    
    if not study_planner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Study planning service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await study_planner.create_study_plan(request)
        
        logger.info(f"✅ Study plan created in {time.time() - start_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Study plan creation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Study plan creation failed"
        )


@app.get("/api/v1/study-plans/types")
async def get_study_plan_types():
    """Get available study plan types"""
    
    if not study_planner:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Study planning service not available"
        )
    
    return {
        "plan_types": study_planner.get_plan_types(),
        "skill_areas": study_planner.get_skill_areas(),
        "features": [
            "AI-powered personalization",
            "Adaptive difficulty adjustment",
            "Progress tracking",
            "Milestone-based learning",
            "Resource recommendations",
            "Success probability calculation"
        ]
    }


@app.get("/api/v1/study-plans/{plan_id}")
async def get_study_plan(
    plan_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific study plan"""
    
    # TODO: Implement study plan retrieval from database
    return {
        "plan_id": plan_id,
        "message": "Study plan retrieval not yet implemented",
        "user_id": current_user.get("user_id", "unknown")
    }


@app.put("/api/v1/study-plans/{plan_id}/progress")
async def update_study_progress(
    plan_id: str,
    progress_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update study plan progress"""
    
    # TODO: Implement progress tracking
    return {
        "plan_id": plan_id,
        "message": "Progress tracking not yet implemented",
        "updated_data": progress_data
    }


# Analytics Dashboard endpoints
@app.post("/api/v1/analytics/dashboard", response_model=AnalyticsDashboard)
async def get_analytics_dashboard(
    request: AnalyticsRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive performance analytics dashboard"""
    
    if not analytics_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await analytics_service.generate_dashboard(request)
        
        logger.info(f"✅ Analytics dashboard generated in {time.time() - start_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Analytics dashboard generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Analytics dashboard generation failed"
        )


@app.get("/api/v1/analytics/features")
async def get_analytics_features():
    """Get available analytics features"""
    
    if not analytics_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics service not available"
        )
    
    return {
        "available_periods": analytics_service.get_available_periods(),
        "features": analytics_service.get_analytics_features(),
        "capabilities": [
            "Real-time performance tracking",
            "Skill-specific analysis",
            "Trend identification and prediction",
            "Goal progress monitoring",
            "Peer comparison analysis",
            "Personalized insights generation",
            "Weakness and strength identification",
            "Study pattern analysis",
            "Success probability calculation",
            "Actionable recommendations"
        ]
    }


@app.get("/api/v1/analytics/performance-summary")
async def get_performance_summary(
    user_id: str,
    period: str = "monthly",
    current_user: dict = Depends(get_current_user)
):
    """Get quick performance summary"""
    
    if not analytics_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Analytics service not available"
        )
    
    try:
        # Create a quick analytics request
        request = AnalyticsRequest(
            user_id=user_id,
            period=period,
            include_comparisons=False,
            include_predictions=False
        )
        
        dashboard = await analytics_service.generate_dashboard(request)
        
        return {
            "user_id": user_id,
            "period": period,
            "current_score": dashboard.overall_performance.get("current_score", 0.0),
            "improvement_rate": dashboard.overall_performance.get("improvement_rate", 0.0),
            "practice_hours": dashboard.overall_performance.get("practice_hours", 0.0),
            "top_insights": [insight.title for insight in dashboard.insights[:3]],
            "key_recommendations": dashboard.recommendations[:5]
        }
        
    except Exception as e:
        logger.error(f"❌ Performance summary generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Performance summary generation failed"
        )


# Writing Style Analysis endpoints
@app.post("/api/v1/style/analyze", response_model=StyleAnalysisResponse)
async def analyze_writing_style(
    request: StyleAnalysisRequest,
    current_user: dict = Depends(get_current_user)
):
    """Analyze writing style comprehensively"""
    
    if not style_analyzer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Style analysis service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await style_analyzer.analyze_style(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Style analysis completed in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Style analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Style analysis failed"
        )


@app.get("/api/v1/style/features")
async def get_style_features():
    """Get available style analysis features"""
    
    if not style_analyzer:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Style analysis service not available"
        )
    
    return {
        "available_styles": style_analyzer.get_available_styles(),
        "complexity_levels": style_analyzer.get_complexity_levels(),
        "analysis_features": [
            "Writing style detection",
            "Complexity level assessment",
            "Style metrics calculation",
            "Pattern identification",
            "Strengths and weaknesses analysis",
            "Consistency scoring",
            "Improvement recommendations",
            "Peer comparison analysis",
            "Performance predictions",
            "Personalized feedback"
        ],
        "metrics_analyzed": [
            "Sentence Variety",
            "Vocabulary Diversity", 
            "Transition Usage",
            "Passive Voice Usage",
            "Complexity Level",
            "Consistency Score",
            "Academic Tone",
            "Coherence Patterns"
        ]
    }


@app.get("/api/v1/style/user-profile/{user_id}")
async def get_user_style_profile(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's writing style profile"""
    
    # TODO: Implement user style profile retrieval from database
    return {
        "user_id": user_id,
        "message": "Style profile retrieval not yet implemented",
        "features": [
            "Personal writing style trends",
            "Historical style analysis",
            "Improvement tracking",
            "Style consistency over time",
            "Personalized recommendations"
        ]
    }


# Gamification endpoints
@app.post("/api/v1/gamification/process-action", response_model=GamificationResponse)
async def process_gamification_action(
    request: GamificationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Process a user action and return gamification rewards"""
    
    if not gamification_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification system not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await gamification_system.process_action(request)
        
        logger.info(f"✅ Gamification action processed in {time.time() - start_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Gamification processing failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gamification processing failed"
        )


@app.get("/api/v1/gamification/leaderboard")
async def get_leaderboard(
    period: str = "weekly",  # daily, weekly, monthly, all_time
    limit: int = 50
):
    """Get leaderboard"""
    
    if not gamification_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification system not available"
        )
    
    try:
        leaderboard = await gamification_system.get_leaderboard(period, limit)
        return leaderboard
        
    except Exception as e:
        logger.error(f"❌ Leaderboard generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Leaderboard generation failed"
        )


@app.get("/api/v1/gamification/achievements")
async def get_user_achievements(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user achievements"""
    
    if not gamification_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification system not available"
        )
    
    try:
        achievements = await gamification_system.get_user_achievements(user_id)
        return achievements
        
    except Exception as e:
        logger.error(f"❌ Achievements retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Achievements retrieval failed"
        )


@app.get("/api/v1/gamification/system-info")
async def get_gamification_info():
    """Get gamification system information"""
    
    if not gamification_system:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gamification system not available"
        )
    
    return {
        "available_achievements": gamification_system.get_available_achievements(),
        "points_system": gamification_system.get_points_system(),
        "xp_system": gamification_system.get_xp_system(),
        "level_requirements": gamification_system.get_level_requirements(),
        "features": [
            "Points and XP system",
            "Achievement unlocking",
            "Level progression",
            "Streak tracking",
            "Leaderboards",
            "Milestone rewards",
            "Social features",
            "Progress tracking",
            "Badge system",
            "Ranking system"
        ]
    }


# Multi-Language Support endpoints
@app.post("/api/v1/multilang/translate", response_model=LocalizationResponse)
async def translate_text(
    request: LocalizationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Translate text between languages"""
    
    if not multilang_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-language service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await multilang_service.translate_text(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Text translated in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Translation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Translation failed"
        )


@app.post("/api/v1/multilang/detect", response_model=LanguageDetectionResponse)
async def detect_language(
    request: LanguageDetectionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Detect the language of given text"""
    
    if not multilang_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-language service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await multilang_service.detect_language(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Language detected in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Language detection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Language detection failed"
        )


@app.get("/api/v1/multilang/supported-languages")
async def get_supported_languages():
    """Get all supported languages"""
    
    if not multilang_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-language service not available"
        )
    
    return {
        "supported_languages": multilang_service.get_supported_languages(),
        "features": [
            "Text translation",
            "Language detection",
            "UI localization",
            "IELTS-specific translations",
            "RTL language support",
            "Date and number formatting",
            "Language family classification",
            "Cultural adaptation"
        ]
    }


@app.get("/api/v1/multilang/translations/{language_code}")
async def get_translations(language_code: str):
    """Get translations for a specific language"""
    
    if not multilang_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-language service not available"
        )
    
    if not multilang_service.validate_language_code(language_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language code: {language_code}"
        )
    
    return {
        "language_code": language_code,
        "language_info": multilang_service.get_language_info(language_code),
        "ui_translations": multilang_service.translations.get(language_code, {}),
        "ielts_translations": multilang_service.get_ielts_specific_translations(language_code),
        "is_rtl": multilang_service.is_rtl_language(language_code),
        "date_format": multilang_service.get_date_format(language_code),
        "number_format": multilang_service.get_number_format(language_code),
        "language_family": multilang_service.get_language_family(language_code)
    }


@app.get("/api/v1/multilang/format-text")
async def format_text_for_language(
    text: str,
    language_code: str,
    current_user: dict = Depends(get_current_user)
):
    """Format text according to language-specific rules"""
    
    if not multilang_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Multi-language service not available"
        )
    
    if not multilang_service.validate_language_code(language_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language code: {language_code}"
        )
    
    formatted_text = multilang_service.format_text_for_language(text, language_code)
    
    return {
        "original_text": text,
        "formatted_text": formatted_text,
        "language_code": language_code,
        "is_rtl": multilang_service.is_rtl_language(language_code)
    }


# Progress Tracking endpoints
@app.post("/api/v1/progress/track", response_model=ProgressTrackingResponse)
async def track_progress(
    request: ProgressTrackingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Generate comprehensive progress tracking report"""
    
    if not progress_tracker:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Progress tracking service not available"
        )
    
    try:
        import time
        start_time = time.time()
        
        result = await progress_tracker.generate_progress_report(request)
        result.processing_time = time.time() - start_time
        
        logger.info(f"✅ Progress report generated in {result.processing_time:.2f}s")
        return result
        
    except Exception as e:
        logger.error(f"❌ Progress tracking failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Progress tracking failed"
        )


@app.get("/api/v1/progress/features")
async def get_progress_features():
    """Get available progress tracking features"""
    
    if not progress_tracker:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Progress tracking service not available"
        )
    
    return {
        "available_metrics": progress_tracker.get_available_metrics(),
        "learning_patterns": progress_tracker.get_learning_patterns(),
        "tracking_features": progress_tracker.get_tracking_features(),
        "capabilities": [
            "AI-powered progress analysis",
            "Learning pattern recognition",
            "Performance predictions",
            "Milestone tracking",
            "Personalized insights generation",
            "Goal achievement monitoring",
            "Study effectiveness analysis",
            "Weakness and strength identification",
            "Recommendation generation",
            "Trend analysis and forecasting"
        ]
    }


@app.get("/api/v1/progress/milestones/{user_id}")
async def get_user_milestones(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get user's learning milestones"""
    
    if not progress_tracker:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Progress tracking service not available"
        )
    
    try:
        # Create a progress tracking request
        request = ProgressTrackingRequest(
            user_id=user_id,
            period_days=90,  # 3 months
            include_predictions=False,
            include_insights=False
        )
        
        result = await progress_tracker.generate_progress_report(request)
        milestones = result.report.milestones
        
        return {
            "user_id": user_id,
            "milestones": milestones,
            "total_milestones": len(milestones),
            "achieved_milestones": len([m for m in milestones if m.achieved_at is not None]),
            "completion_percentage": (len([m for m in milestones if m.achieved_at is not None]) / len(milestones)) * 100 if milestones else 0
        }
        
    except Exception as e:
        logger.error(f"❌ Milestones retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Milestones retrieval failed"
        )


@app.get("/api/v1/progress/summary/{user_id}")
async def get_progress_summary(
    user_id: str,
    period_days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get quick progress summary"""
    
    if not progress_tracker:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Progress tracking service not available"
        )
    
    try:
        # Create a quick progress tracking request
        request = ProgressTrackingRequest(
            user_id=user_id,
            period_days=period_days,
            include_predictions=False,
            include_insights=False
        )
        
        result = await progress_tracker.generate_progress_report(request)
        report = result.report
        
        return {
            "user_id": user_id,
            "period_days": period_days,
            "overall_progress": report.overall_progress,
            "learning_pattern": report.learning_pattern.value,
            "milestones_count": len(report.milestones),
            "achieved_milestones": len([m for m in report.milestones if m.achieved_at is not None]),
            "top_insights": [insight.title for insight in report.insights[:3]],
            "key_recommendations": report.recommendations[:5]
        }
        
    except Exception as e:
        logger.error(f"❌ Progress summary generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Progress summary generation failed"
        )


# Personalized Coach AI endpoints
@app.post("/api/v1/coaching/session", response_model=CoachingResponse)
async def create_coaching_session(
    request: CoachingRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create a personalized AI coaching session"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        start_time = datetime.now()
        response = await personalized_coach.provide_coaching(request)
        response.processing_time = (datetime.now() - start_time).total_seconds()
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Personalized coaching failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Personalized coaching failed"
        )

@app.get("/api/v1/coaching/coaches")
async def get_available_coaches():
    """Get all available coach personalities"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        coaches = personalized_coach.get_available_coaches()
        return {"coaches": [coach.dict() for coach in coaches]}
        
    except Exception as e:
        logger.error(f"❌ Failed to get available coaches: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get available coaches"
        )

@app.get("/api/v1/coaching/styles")
async def get_coaching_styles():
    """Get available coaching styles"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        styles = personalized_coach.get_coaching_styles()
        return {"coaching_styles": styles}
        
    except Exception as e:
        logger.error(f"❌ Failed to get coaching styles: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get coaching styles"
        )

@app.get("/api/v1/coaching/learning-preferences")
async def get_learning_preferences():
    """Get available learning preferences"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        preferences = personalized_coach.get_learning_preferences()
        return {"learning_preferences": preferences}
        
    except Exception as e:
        logger.error(f"❌ Failed to get learning preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get learning preferences"
        )

@app.get("/api/v1/coaching/features")
async def get_coaching_features():
    """Get available coaching features"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        features = personalized_coach.get_coaching_features()
        return {"coaching_features": features}
        
    except Exception as e:
        logger.error(f"❌ Failed to get coaching features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get coaching features"
        )

@app.post("/api/v1/coaching/recommend-coach")
async def recommend_coach(
    user_id: str,
    user_preferences: dict,
    current_user: dict = Depends(get_current_user)
):
    """Recommend the best coach personality for a user"""
    
    if not personalized_coach:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Personalized coaching service not available"
        )
    
    try:
        recommended_coach = await personalized_coach.get_coach_recommendation(user_id, user_preferences)
        return {"recommended_coach": recommended_coach.dict()}
        
    except Exception as e:
        logger.error(f"❌ Failed to recommend coach: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recommend coach"
        )


# Adaptive Scoring System endpoints
@app.post("/api/v1/scoring/adaptive", response_model=AdaptiveScoringResponse)
async def score_essay_adaptive(
    request: AdaptiveScoringRequest,
    current_user: dict = Depends(get_current_user)
):
    """Score essay using adaptive methodology"""
    
    if not adaptive_scoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive scoring service not available"
        )
    
    try:
        response = await adaptive_scoring.score_essay_adaptive(request)
        return response
        
    except Exception as e:
        logger.error(f"❌ Adaptive scoring failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Adaptive scoring failed"
        )

@app.get("/api/v1/scoring/modes")
async def get_scoring_modes():
    """Get available scoring modes"""
    
    if not adaptive_scoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive scoring service not available"
        )
    
    try:
        modes = adaptive_scoring.get_scoring_modes()
        return {"scoring_modes": modes}
        
    except Exception as e:
        logger.error(f"❌ Failed to get scoring modes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get scoring modes"
        )

@app.get("/api/v1/scoring/difficulty-levels")
async def get_difficulty_levels():
    """Get available difficulty levels"""
    
    if not adaptive_scoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive scoring service not available"
        )
    
    try:
        levels = adaptive_scoring.get_difficulty_levels()
        return {"difficulty_levels": levels}
        
    except Exception as e:
        logger.error(f"❌ Failed to get difficulty levels: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get difficulty levels"
        )

@app.get("/api/v1/scoring/adaptive-features")
async def get_adaptive_features():
    """Get available adaptive features"""
    
    if not adaptive_scoring:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Adaptive scoring service not available"
        )
    
    try:
        features = adaptive_scoring.get_adaptive_features()
        return {"adaptive_features": features}
        
    except Exception as e:
        logger.error(f"❌ Failed to get adaptive features: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get adaptive features"
        )


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
# Railway redeployment trigger
