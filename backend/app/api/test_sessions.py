from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.security import get_current_user
from app.services.test_data_service import test_data_service

router = APIRouter(prefix="/api/v1/test-sessions", tags=["test-sessions"])

class TestSessionRequest(BaseModel):
    test_id: str
    test_type: str  # listening, reading, writing, speaking
    user_answers: Optional[Dict[str, Any]] = None
    essay_content: Optional[str] = None
    time_spent: Optional[int] = None  # in seconds

class TestSessionResponse(BaseModel):
    session_id: str
    test_id: str
    test_type: str
    status: str  # in_progress, completed, abandoned
    score: Optional[float] = None
    feedback: Optional[Dict[str, Any]] = None
    time_spent: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

class TestSessionUpdate(BaseModel):
    user_answers: Optional[Dict[str, Any]] = None
    essay_content: Optional[str] = None
    time_spent: Optional[int] = None

# In-memory storage for test sessions (in production, use database)
_test_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/start", response_model=TestSessionResponse)
async def start_test_session(
    request: TestSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """Start a new test session"""
    try:
        # Get test details
        test = test_data_service.get_test_by_id(request.test_id)
        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test not found"
            )
        
        # Create session
        session_id = f"session_{len(_test_sessions) + 1}_{current_user['user_id']}"
        session = {
            "session_id": session_id,
            "test_id": request.test_id,
            "test_type": request.test_type,
            "user_id": current_user['user_id'],
            "status": "in_progress",
            "score": None,
            "feedback": None,
            "time_spent": 0,
            "user_answers": {},
            "essay_content": "",
            "created_at": datetime.now(),
            "completed_at": None
        }
        
        _test_sessions[session_id] = session
        
        return TestSessionResponse(
            session_id=session_id,
            test_id=request.test_id,
            test_type=request.test_type,
            status="in_progress",
            score=None,
            feedback=None,
            time_spent=0,
            created_at=session["created_at"],
            completed_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting test session: {str(e)}"
        )

@router.put("/{session_id}", response_model=TestSessionResponse)
async def update_test_session(
    session_id: str,
    update: TestSessionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a test session"""
    try:
        if session_id not in _test_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test session not found"
            )
        
        session = _test_sessions[session_id]
        
        # Check if user owns this session
        if session["user_id"] != current_user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update session
        if update.user_answers is not None:
            session["user_answers"].update(update.user_answers)
        if update.essay_content is not None:
            session["essay_content"] = update.essay_content
        if update.time_spent is not None:
            session["time_spent"] = update.time_spent
        
        _test_sessions[session_id] = session
        
        return TestSessionResponse(
            session_id=session_id,
            test_id=session["test_id"],
            test_type=session["test_type"],
            status=session["status"],
            score=session["score"],
            feedback=session["feedback"],
            time_spent=session["time_spent"],
            created_at=session["created_at"],
            completed_at=session["completed_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating test session: {str(e)}"
        )

@router.post("/{session_id}/complete", response_model=TestSessionResponse)
async def complete_test_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Complete a test session and generate feedback"""
    try:
        if session_id not in _test_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test session not found"
            )
        
        session = _test_sessions[session_id]
        
        # Check if user owns this session
        if session["user_id"] != current_user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Mark as completed
        session["status"] = "completed"
        session["completed_at"] = datetime.now()
        
        # Generate feedback based on test type
        feedback = await _generate_feedback(session)
        session["feedback"] = feedback
        session["score"] = feedback.get("overall_score", 0)
        
        _test_sessions[session_id] = session
        
        return TestSessionResponse(
            session_id=session_id,
            test_id=session["test_id"],
            test_type=session["test_type"],
            status="completed",
            score=session["score"],
            feedback=session["feedback"],
            time_spent=session["time_spent"],
            created_at=session["created_at"],
            completed_at=session["completed_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing test session: {str(e)}"
        )

@router.get("/", response_model=List[TestSessionResponse])
async def get_user_test_sessions(
    current_user: dict = Depends(get_current_user),
    status_filter: Optional[str] = None
):
    """Get all test sessions for the current user"""
    try:
        user_sessions = [
            session for session in _test_sessions.values()
            if session["user_id"] == current_user['user_id']
        ]
        
        if status_filter:
            user_sessions = [
                session for session in user_sessions
                if session["status"] == status_filter
            ]
        
        # Sort by created_at descending
        user_sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        return [
            TestSessionResponse(
                session_id=session["session_id"],
                test_id=session["test_id"],
                test_type=session["test_type"],
                status=session["status"],
                score=session["score"],
                feedback=session["feedback"],
                time_spent=session["time_spent"],
                created_at=session["created_at"],
                completed_at=session["completed_at"]
            )
            for session in user_sessions
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching test sessions: {str(e)}"
        )

@router.get("/{session_id}", response_model=TestSessionResponse)
async def get_test_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific test session"""
    try:
        if session_id not in _test_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Test session not found"
            )
        
        session = _test_sessions[session_id]
        
        # Check if user owns this session
        if session["user_id"] != current_user['user_id']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return TestSessionResponse(
            session_id=session_id,
            test_id=session["test_id"],
            test_type=session["test_type"],
            status=session["status"],
            score=session["score"],
            feedback=session["feedback"],
            time_spent=session["time_spent"],
            created_at=session["created_at"],
            completed_at=session["completed_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching test session: {str(e)}"
        )

async def _generate_feedback(session: Dict[str, Any]) -> Dict[str, Any]:
    """Generate feedback based on test type and user responses"""
    test_type = session["test_type"]
    
    if test_type == "writing":
        # Use existing essay assessment for writing tests
        essay_content = session.get("essay_content", "")
        if essay_content:
            # This would integrate with your existing essay assessment system
            return {
                "overall_score": 7.0,  # Placeholder
                "detailed_feedback": "Great essay! You've addressed the task well with clear arguments and good examples.",
                "strengths": ["Clear thesis statement", "Good use of examples", "Logical structure"],
                "weaknesses": ["Some grammar errors", "Could use more complex vocabulary"],
                "suggestions": ["Practice grammar exercises", "Read more academic texts"]
            }
    
    elif test_type == "listening":
        # Mock listening feedback
        return {
            "overall_score": 6.5,
            "detailed_feedback": "Good listening skills! You understood most of the content.",
            "strengths": ["Good comprehension", "Accurate answers"],
            "weaknesses": ["Missed some details", "Spelling errors"],
            "suggestions": ["Practice with different accents", "Focus on spelling"]
        }
    
    elif test_type == "reading":
        # Mock reading feedback
        return {
            "overall_score": 7.5,
            "detailed_feedback": "Excellent reading comprehension! You found the answers quickly and accurately.",
            "strengths": ["Fast reading", "Good understanding", "Accurate answers"],
            "weaknesses": ["Some vocabulary issues"],
            "suggestions": ["Expand vocabulary", "Practice skimming techniques"]
        }
    
    elif test_type == "speaking":
        # Mock speaking feedback
        return {
            "overall_score": 6.0,
            "detailed_feedback": "Good speaking practice! You communicated your ideas clearly.",
            "strengths": ["Clear pronunciation", "Good ideas"],
            "weaknesses": ["Some hesitation", "Limited vocabulary"],
            "suggestions": ["Practice fluency", "Expand vocabulary", "Record yourself"]
        }
    
    return {
        "overall_score": 0,
        "detailed_feedback": "No feedback available",
        "strengths": [],
        "weaknesses": [],
        "suggestions": []
    }


