"""
Session Management API endpoints for mentorship system
"""

from fastapi import APIRouter, Depends, HTTPException, Form, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from datetime import datetime

from app.database import get_db
from app.core.security import get_current_user
from app.services.mentorship_service import MentorshipService
from app.models.mentorship import MentorshipConnection

router = APIRouter()

# Session Management Endpoints
@router.post("/connections/{connection_id}/sessions")
async def create_session(
    connection_id: int,
    title: str = Form(...),
    description: str = Form(None),
    session_type: str = Form("general"),
    scheduled_at: str = Form(...),
    duration_minutes: int = Form(60),
    agenda: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new mentorship session"""
    try:
        # Parse scheduled_at
        scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        
        # Parse agenda if provided
        agenda_list = None
        if agenda:
            try:
                agenda_list = json.loads(agenda)
            except:
                agenda_list = [agenda]
        
        session = MentorshipService.create_session(
            db=db,
            connection_id=connection_id,
            title=title,
            description=description,
            session_type=session_type,
            scheduled_at=scheduled_datetime,
            duration_minutes=duration_minutes,
            agenda=agenda_list
        )
        
        return {
            "success": True,
            "message": "Session created successfully",
            "session": session.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/upcoming")
async def get_upcoming_sessions(
    days_ahead: int = 30,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming sessions for the current user"""
    try:
        sessions = MentorshipService.get_upcoming_sessions(db, current_user["user_id"], days_ahead)
        
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            # Add connection details
            connection = db.query(MentorshipConnection).filter(
                MentorshipConnection.id == session.connection_id
            ).first()
            if connection:
                session_dict['connection'] = {
                    'id': connection.id,
                    'mentor_id': connection.mentor_id,
                    'mentee_id': connection.mentee_id,
                    'status': connection.status
                }
            sessions_data.append(session_dict)
        
        return {
            "success": True,
            "sessions": sessions_data,
            "count": len(sessions_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    notes: str = Form(None),
    rating: float = Form(None),
    homework: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a mentorship session"""
    try:
        session = MentorshipService.complete_session(
            db=db,
            session_id=session_id,
            user_id=current_user["user_id"],
            notes=notes,
            rating=rating,
            homework=homework
        )
        
        return {
            "success": True,
            "message": "Session completed successfully",
            "session": session.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Rating System Endpoints
@router.post("/connections/{connection_id}/rate")
async def rate_mentorship(
    connection_id: int,
    rating: float = Form(...),
    feedback: str = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a mentorship relationship"""
    try:
        connection = MentorshipService.rate_mentorship(
            db=db,
            connection_id=connection_id,
            user_id=current_user["user_id"],
            rating=rating,
            feedback=feedback
        )
        
        return {
            "success": True,
            "message": "Rating submitted successfully",
            "connection": connection.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
