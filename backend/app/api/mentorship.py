"""
Mentorship API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json

from app.database import get_db
from app.models.user import User
from app.services.mentorship_service import MentorshipService
from app.models.mentorship import MessageType
from app.core.security import get_current_user

router = APIRouter(prefix="/api/v1/mentorship", tags=["mentorship"])


@router.post("/profile")
async def create_or_update_profile(
    bio: str = Form(None),
    teaching_experience: str = Form(None),
    specializations: str = Form(None),  # JSON string
    certifications: str = Form(None),  # JSON string
    timezone: str = Form(None),
    available_days: str = Form(None),  # JSON string
    available_hours: str = Form(None),  # JSON string
    is_available_for_mentorship: bool = Form(False),
    max_mentees: int = Form(3),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update user profile for mentorship"""
    try:
        profile_data = {
            "bio": bio,
            "teaching_experience": teaching_experience,
            "timezone": timezone,
            "is_available_for_mentorship": is_available_for_mentorship,
            "max_mentees": max_mentees
        }
        
        # Parse JSON fields
        if specializations:
            try:
                profile_data["specializations"] = json.loads(specializations)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid specializations format")
        
        if certifications:
            try:
                profile_data["certifications"] = json.loads(certifications)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid certifications format")
        
        if available_days:
            try:
                profile_data["available_days"] = json.loads(available_days)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid available_days format")
        
        if available_hours:
            try:
                profile_data["available_hours"] = json.loads(available_hours)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid available_hours format")
        
        profile = MentorshipService.create_user_profile(db, current_user["user_id"], profile_data)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": profile.to_dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mentors")
async def get_available_mentors(
    specializations: Optional[str] = None,
    target_band_score: Optional[float] = None,
    timezone: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of available mentors"""
    try:
        filters = {}
        if specializations:
            filters["specializations"] = specializations
        if target_band_score:
            filters["target_band_score"] = target_band_score
        if timezone:
            filters["timezone"] = timezone
        
        mentors = MentorshipService.get_available_mentors(db, current_user["user_id"], filters)
        
        return {
            "success": True,
            "mentors": mentors,
            "count": len(mentors)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def send_connection_request(
    mentor_id: int = Form(...),
    message: str = Form(None),
    goals: str = Form(None),  # JSON string
    target_band_score: float = Form(None),
    focus_areas: str = Form(None),  # JSON string
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a mentorship connection request"""
    try:
        # Parse JSON fields
        goals_list = None
        if goals:
            try:
                goals_list = json.loads(goals)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid goals format")
        
        focus_areas_list = None
        if focus_areas:
            try:
                focus_areas_list = json.loads(focus_areas)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid focus_areas format")
        
        connection = MentorshipService.send_connection_request(
            db=db,
            mentee_id=current_user["user_id"],
            mentor_id=mentor_id,
            message=message,
            goals=goals_list,
            target_band_score=target_band_score,
            focus_areas=focus_areas_list
        )
        
        return {
            "success": True,
            "message": "Connection request sent successfully",
            "connection": connection.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connections/{connection_id}/accept")
async def accept_connection_request(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept a mentorship connection request"""
    try:
        connection = MentorshipService.accept_connection_request(db, connection_id, current_user["user_id"])
        
        return {
            "success": True,
            "message": "Connection request accepted",
            "connection": connection.to_dict()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connections/{connection_id}/reject")
async def reject_connection_request(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reject a mentorship connection request"""
    try:
        success = MentorshipService.reject_connection_request(db, connection_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=404, detail="Connection request not found")
        
        return {
            "success": True,
            "message": "Connection request rejected"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_user_connections(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all connections for the current user"""
    try:
        connections = MentorshipService.get_user_connections(db, current_user["user_id"], status)
        
        return {
            "success": True,
            "connections": connections,  # Already converted to dict with user details
            "count": len(connections)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}")
async def get_connection_details(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific connection"""
    try:
        connection = MentorshipService.get_connection_by_id(db, connection_id, current_user["user_id"])
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return {
            "success": True,
            "connection": connection
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}/messages")
async def get_connection_messages(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all messages for a specific connection"""
    try:
        messages = MentorshipService.get_connection_messages(db, connection_id, current_user["user_id"])
        
        return {
            "success": True,
            "messages": messages
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a mentorship connection"""
    try:
        # Check if connection exists and user has permission to delete it
        connection = MentorshipService.get_connection_by_id(db, connection_id, current_user["user_id"])
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Delete the connection (this will also delete associated messages due to cascade)
        success = MentorshipService.delete_connection(db, connection_id, current_user["user_id"])
        
        if not success:
            raise HTTPException(status_code=403, detail="You don't have permission to delete this connection")
        
        return {
            "success": True,
            "message": "Connection deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connections/{connection_id}/messages")
async def send_message(
    connection_id: int,
    content: str = Form(None),
    message_type: str = Form("text"),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send a message in a mentorship connection"""
    try:
        # Handle file upload
        file_url = None
        file_name = None
        file_size = None
        
        if file:
            # In a real implementation, you would upload to cloud storage
            # For now, we'll just store the filename
            file_name = file.filename
            file_size = file.size
            file_url = f"/uploads/{file.filename}"  # Placeholder URL
        
        # Convert message type
        msg_type = MessageType.TEXT
        if message_type == "file":
            msg_type = MessageType.FILE
        elif message_type == "image":
            msg_type = MessageType.IMAGE
        elif message_type == "audio":
            msg_type = MessageType.AUDIO
        elif message_type == "video":
            msg_type = MessageType.VIDEO
        
        message = MentorshipService.send_message(
            db=db,
            connection_id=connection_id,
            sender_id=current_user["user_id"],
            content=content,
            message_type=msg_type,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size
        )
        
        # Get the sender information
        from app.models.user import User
        sender = db.query(User).filter(User.id == current_user["user_id"]).first()
        
        # Create response with sender information
        message_data = message.to_dict()
        if sender:
            message_data['sender'] = {
                'id': sender.id,
                'username': sender.username,
                'full_name': sender.full_name,
                'email': sender.email,
                'role': sender.role
            }
        
        return {
            "success": True,
            "message": "Message sent successfully",
            "data": message_data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}/messages")
async def get_messages(
    connection_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get messages for a connection"""
    try:
        messages = MentorshipService.get_messages(db, connection_id, current_user["user_id"], limit, offset)
        
        return {
            "success": True,
            "messages": [msg.to_dict() for msg in messages],
            "count": len(messages)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_session(
    connection_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(None),
    session_type: str = Form("general"),
    scheduled_at: str = Form(...),  # ISO datetime string
    duration_minutes: int = Form(60),
    agenda: str = Form(None),  # JSON string
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a mentorship session"""
    try:
        # Parse scheduled_at
        try:
            scheduled_datetime = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")
        
        # Parse agenda
        agenda_list = None
        if agenda:
            try:
                agenda_list = json.loads(agenda)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid agenda format")
        
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
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/upcoming")
async def get_upcoming_sessions(
    days_ahead: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get upcoming sessions for the current user"""
    try:
        sessions = MentorshipService.get_upcoming_sessions(db, current_user["user_id"], days_ahead)
        
        return {
            "success": True,
            "sessions": [session.to_dict() for session in sessions],
            "count": len(sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/complete")
async def complete_session(
    session_id: int,
    notes: str = Form(None),
    rating: float = Form(None),
    homework: str = Form(None),
    current_user: User = Depends(get_current_user),
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


@router.post("/connections/{connection_id}/rate")
async def rate_mentorship(
    connection_id: int,
    rating: float = Form(...),
    feedback: str = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Rate a mentorship relationship"""
    try:
        if not 1.0 <= rating <= 5.0:
            raise HTTPException(status_code=400, detail="Rating must be between 1.0 and 5.0")
        
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
