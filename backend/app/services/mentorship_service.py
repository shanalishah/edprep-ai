"""
Mentorship service for handling mentor-mentee interactions
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import json

from app.models.mentorship import (
    MentorshipConnection, 
    MentorshipMessage, 
    MentorshipSession, 
    UserProfile,
    MentorshipStatus,
    MessageType
)
from app.models.user import User


class MentorshipService:
    """Service for managing mentorship relationships and interactions"""
    
    @staticmethod
    def create_user_profile(db: Session, user_id: int, profile_data: Dict[str, Any]) -> UserProfile:
        """Create or update user profile for mentorship"""
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)
        
        # Update profile data
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        
        db.commit()
        db.refresh(profile)
        return profile
    
    @staticmethod
    def get_available_mentors(db: Session, mentee_id: int, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get list of available mentors with matching criteria"""
        # Use LEFT JOIN to include mentors without profiles
        query = db.query(User, UserProfile).outerjoin(
            UserProfile, User.id == UserProfile.user_id
        ).filter(
            and_(
                User.role.in_(["mentor", "tutor"]),
                User.id != mentee_id,
                # Show mentors if they have no profile OR if their profile allows mentorship
                or_(
                    UserProfile.is_available_for_mentorship == True,
                    UserProfile.is_available_for_mentorship.is_(None)
                )
            )
        )
        
        # Apply filters
        if filters:
            if filters.get("specializations"):
                specializations = filters["specializations"]
                query = query.filter(
                    or_(
                        UserProfile.specializations.contains(specializations),
                        UserProfile.specializations.is_(None)
                    )
                )
            
            if filters.get("target_band_score"):
                target_score = filters["target_band_score"]
                # Find mentors who have achieved higher scores
                query = query.filter(User.target_band_score >= target_score)
            
            if filters.get("timezone"):
                timezone = filters["timezone"]
                query = query.filter(
                    or_(
                        UserProfile.timezone == timezone,
                        UserProfile.timezone.is_(None)
                    )
                )
        
        mentors = query.limit(20).all()
        
        result = []
        for user, profile in mentors:
            mentor_data = {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "email": user.email,
                "role": user.role,
                "target_band_score": user.target_band_score,
                "current_level": user.current_level,
                "profile": profile.to_dict() if profile else {
                    "bio": "No profile set up yet",
                    "teaching_experience": "Profile not completed",
                    "specializations": [],
                    "average_rating": 0.0,
                    "total_mentees_helped": 0,
                    "is_available_for_mentorship": True
                },
                "is_available": profile.is_available_for_mentorship if profile else True
            }
            result.append(mentor_data)
        
        return result
    
    @staticmethod
    def send_connection_request(
        db: Session, 
        mentee_id: int, 
        mentor_id: int, 
        message: str = None,
        goals: List[str] = None,
        target_band_score: float = None,
        focus_areas: List[str] = None
    ) -> MentorshipConnection:
        """Send a mentorship connection request"""
        
        # Check if connection already exists
        existing = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.mentee_id == mentee_id,
                MentorshipConnection.mentor_id == mentor_id
            )
        ).first()
        
        if existing:
            raise ValueError("Connection request already exists")
        
        # Create new connection request
        connection = MentorshipConnection(
            mentor_id=mentor_id,
            mentee_id=mentee_id,
            status=MentorshipStatus.PENDING,
            connection_message=message,
            goals=goals,
            target_band_score=target_band_score,
            focus_areas=focus_areas
        )
        
        db.add(connection)
        db.commit()
        db.refresh(connection)
        
        return connection

    @staticmethod
    def get_connection_by_id(db: Session, connection_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific connection by ID with user details"""
        from sqlalchemy.orm import joinedload
        
        connection = db.query(MentorshipConnection).options(
            joinedload(MentorshipConnection.mentor),
            joinedload(MentorshipConnection.mentee)
        ).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            return None
        
        conn_dict = connection.to_dict()
        conn_dict['mentor'] = {
            'id': connection.mentor.id,
            'username': connection.mentor.username,
            'full_name': connection.mentor.full_name,
            'email': connection.mentor.email,
            'role': connection.mentor.role
        }
        conn_dict['mentee'] = {
            'id': connection.mentee.id,
            'username': connection.mentee.username,
            'full_name': connection.mentee.full_name,
            'email': connection.mentee.email,
            'role': connection.mentee.role
        }
        
        return conn_dict

    @staticmethod
    def get_connection_messages(db: Session, connection_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all messages for a specific connection"""
        from sqlalchemy.orm import joinedload
        from app.models.user import User
        
        # First verify user has access to this connection
        connection = db.query(MentorshipConnection).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Get messages without joinedload first
        messages = db.query(MentorshipMessage).filter(
            MentorshipMessage.connection_id == connection_id
        ).order_by(MentorshipMessage.created_at.asc()).all()
        
        result = []
        for msg in messages:
            msg_dict = msg.to_dict()
            
            # Get sender details separately
            try:
                sender = db.query(User).filter(User.id == msg.sender_id).first()
                if sender:
                    msg_dict['sender'] = {
                        'id': sender.id,
                        'username': sender.username,
                        'full_name': sender.full_name,
                        'email': sender.email,
                        'role': sender.role
                    }
                else:
                    # If sender doesn't exist, create a placeholder
                    msg_dict['sender'] = {
                        'id': msg.sender_id,
                        'username': f'user_{msg.sender_id}',
                        'full_name': f'User {msg.sender_id}',
                        'email': f'user{msg.sender_id}@example.com',
                        'role': 'unknown'
                    }
            except Exception as e:
                print(f"Error fetching sender {msg.sender_id}: {e}")
                msg_dict['sender'] = {
                    'id': msg.sender_id,
                    'username': f'user_{msg.sender_id}',
                    'full_name': f'User {msg.sender_id}',
                    'email': f'user{msg.sender_id}@example.com',
                    'role': 'unknown'
                }
            
            result.append(msg_dict)
        
        return result
    
    @staticmethod
    def accept_connection_request(db: Session, connection_id: int, mentor_id: int) -> MentorshipConnection:
        """Accept a mentorship connection request"""
        connection = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.id == connection_id,
                MentorshipConnection.mentor_id == mentor_id,
                MentorshipConnection.status == MentorshipStatus.PENDING
            )
        ).first()
        
        if not connection:
            raise ValueError("Connection request not found or already processed")
        
        connection.status = MentorshipStatus.ACTIVE
        connection.started_at = datetime.utcnow()
        
        # Update mentor's status
        mentor_profile = db.query(UserProfile).filter(UserProfile.user_id == mentor_id).first()
        if mentor_profile:
            mentor_profile.mentorship_status = "mentoring"
        
        # Update mentee's status
        mentee_profile = db.query(UserProfile).filter(UserProfile.user_id == connection.mentee_id).first()
        if mentee_profile:
            mentee_profile.mentorship_status = "mentored"
        
        db.commit()
        db.refresh(connection)
        
        return connection

    @staticmethod
    def get_connection_by_id(db: Session, connection_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific connection by ID with user details"""
        from sqlalchemy.orm import joinedload
        
        connection = db.query(MentorshipConnection).options(
            joinedload(MentorshipConnection.mentor),
            joinedload(MentorshipConnection.mentee)
        ).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            return None
        
        conn_dict = connection.to_dict()
        conn_dict['mentor'] = {
            'id': connection.mentor.id,
            'username': connection.mentor.username,
            'full_name': connection.mentor.full_name,
            'email': connection.mentor.email,
            'role': connection.mentor.role
        }
        conn_dict['mentee'] = {
            'id': connection.mentee.id,
            'username': connection.mentee.username,
            'full_name': connection.mentee.full_name,
            'email': connection.mentee.email,
            'role': connection.mentee.role
        }
        
        return conn_dict

    @staticmethod
    def get_connection_messages(db: Session, connection_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all messages for a specific connection"""
        from sqlalchemy.orm import joinedload
        from app.models.user import User
        
        # First verify user has access to this connection
        connection = db.query(MentorshipConnection).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Get messages without joinedload first
        messages = db.query(MentorshipMessage).filter(
            MentorshipMessage.connection_id == connection_id
        ).order_by(MentorshipMessage.created_at.asc()).all()
        
        result = []
        for msg in messages:
            msg_dict = msg.to_dict()
            
            # Get sender details separately
            try:
                sender = db.query(User).filter(User.id == msg.sender_id).first()
                if sender:
                    msg_dict['sender'] = {
                        'id': sender.id,
                        'username': sender.username,
                        'full_name': sender.full_name,
                        'email': sender.email,
                        'role': sender.role
                    }
                else:
                    # If sender doesn't exist, create a placeholder
                    msg_dict['sender'] = {
                        'id': msg.sender_id,
                        'username': f'user_{msg.sender_id}',
                        'full_name': f'User {msg.sender_id}',
                        'email': f'user{msg.sender_id}@example.com',
                        'role': 'unknown'
                    }
            except Exception as e:
                print(f"Error fetching sender {msg.sender_id}: {e}")
                msg_dict['sender'] = {
                    'id': msg.sender_id,
                    'username': f'user_{msg.sender_id}',
                    'full_name': f'User {msg.sender_id}',
                    'email': f'user{msg.sender_id}@example.com',
                    'role': 'unknown'
                }
            
            result.append(msg_dict)
        
        return result
    
    @staticmethod
    def reject_connection_request(db: Session, connection_id: int, mentor_id: int) -> bool:
        """Reject a mentorship connection request"""
        connection = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.id == connection_id,
                MentorshipConnection.mentor_id == mentor_id,
                MentorshipConnection.status == MentorshipStatus.PENDING
            )
        ).first()
        
        if not connection:
            return False
        
        connection.status = MentorshipStatus.CANCELLED
        db.commit()
        
        return True
    
    @staticmethod
    def get_user_connections(db: Session, user_id: int, status: str = None) -> List[Dict[str, Any]]:
        """Get all connections for a user with user details"""
        from sqlalchemy.orm import joinedload
        from app.models.user import User
        
        # First get the connection IDs
        query = db.query(MentorshipConnection).filter(
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        )
        
        if status:
            query = query.filter(MentorshipConnection.status == status)
        
        connections = query.order_by(MentorshipConnection.created_at.desc()).all()
        
        # Convert to dict with user details
        result = []
        for conn in connections:
            conn_dict = conn.to_dict()
            
            # Get mentor details - with better error handling
            try:
                mentor = db.query(User).filter(User.id == conn.mentor_id).first()
                if mentor:
                    conn_dict['mentor'] = {
                        'id': mentor.id,
                        'username': mentor.username,
                        'full_name': mentor.full_name,
                        'email': mentor.email,
                        'role': mentor.role
                    }
                else:
                    # If mentor doesn't exist, create a placeholder
                    conn_dict['mentor'] = {
                        'id': conn.mentor_id,
                        'username': f'user_{conn.mentor_id}',
                        'full_name': f'User {conn.mentor_id}',
                        'email': f'user{conn.mentor_id}@example.com',
                        'role': 'unknown'
                    }
            except Exception as e:
                print(f"Error fetching mentor {conn.mentor_id}: {e}")
                conn_dict['mentor'] = {
                    'id': conn.mentor_id,
                    'username': f'user_{conn.mentor_id}',
                    'full_name': f'User {conn.mentor_id}',
                    'email': f'user{conn.mentor_id}@example.com',
                    'role': 'unknown'
                }
            
            # Get mentee details - with better error handling
            try:
                mentee = db.query(User).filter(User.id == conn.mentee_id).first()
                if mentee:
                    conn_dict['mentee'] = {
                        'id': mentee.id,
                        'username': mentee.username,
                        'full_name': mentee.full_name,
                        'email': mentee.email,
                        'role': mentee.role
                    }
                else:
                    # If mentee doesn't exist, create a placeholder
                    conn_dict['mentee'] = {
                        'id': conn.mentee_id,
                        'username': f'user_{conn.mentee_id}',
                        'full_name': f'User {conn.mentee_id}',
                        'email': f'user{conn.mentee_id}@example.com',
                        'role': 'unknown'
                    }
            except Exception as e:
                print(f"Error fetching mentee {conn.mentee_id}: {e}")
                conn_dict['mentee'] = {
                    'id': conn.mentee_id,
                    'username': f'user_{conn.mentee_id}',
                    'full_name': f'User {conn.mentee_id}',
                    'email': f'user{conn.mentee_id}@example.com',
                    'role': 'unknown'
                }
            
            result.append(conn_dict)
        
        return result
    
    @staticmethod
    def send_message(
        db: Session,
        connection_id: int,
        sender_id: int,
        content: str = None,
        message_type: MessageType = MessageType.TEXT,
        file_url: str = None,
        file_name: str = None,
        file_size: int = None
    ) -> MentorshipMessage:
        """Send a message in a mentorship connection"""
        
        # Verify user is part of the connection
        connection = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.id == connection_id,
                or_(
                    MentorshipConnection.mentor_id == sender_id,
                    MentorshipConnection.mentee_id == sender_id
                )
            )
        ).first()
        
        if not connection:
            raise ValueError("Connection not found or user not authorized")
        
        message = MentorshipMessage(
            connection_id=connection_id,
            sender_id=sender_id,
            message_type=message_type,
            content=content,
            file_url=file_url,
            file_name=file_name,
            file_size=file_size
        )
        
        db.add(message)
        db.commit()
        db.refresh(message)
        
        return message
    
    @staticmethod
    def get_messages(db: Session, connection_id: int, user_id: int, limit: int = 50, offset: int = 0) -> List[MentorshipMessage]:
        """Get messages for a connection"""
        
        # Verify user is part of the connection
        connection = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.id == connection_id,
                or_(
                    MentorshipConnection.mentor_id == user_id,
                    MentorshipConnection.mentee_id == user_id
                )
            )
        ).first()
        
        if not connection:
            raise ValueError("Connection not found or user not authorized")
        
        messages = db.query(MentorshipMessage).filter(
            MentorshipMessage.connection_id == connection_id
        ).order_by(MentorshipMessage.created_at.desc()).offset(offset).limit(limit).all()
        
        # Mark messages as read
        for message in messages:
            if message.sender_id != user_id and not message.is_read:
                message.is_read = True
                message.read_at = datetime.utcnow()
        
        db.commit()
        
        return list(reversed(messages))  # Return in chronological order
    
    @staticmethod
    def create_session(
        db: Session,
        connection_id: int,
        title: str,
        description: str = None,
        session_type: str = "general",
        scheduled_at: datetime = None,
        duration_minutes: int = 60,
        agenda: List[str] = None
    ) -> MentorshipSession:
        """Create a mentorship session"""
        
        if not scheduled_at:
            scheduled_at = datetime.utcnow() + timedelta(days=1)
        
        session = MentorshipSession(
            connection_id=connection_id,
            title=title,
            description=description,
            session_type=session_type,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            agenda=agenda
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def get_upcoming_sessions(db: Session, user_id: int, days_ahead: int = 30) -> List[MentorshipSession]:
        """Get upcoming sessions for a user"""
        end_date = datetime.utcnow() + timedelta(days=days_ahead)
        
        sessions = db.query(MentorshipSession).join(
            MentorshipConnection,
            MentorshipSession.connection_id == MentorshipConnection.id
        ).filter(
            and_(
                or_(
                    MentorshipConnection.mentor_id == user_id,
                    MentorshipConnection.mentee_id == user_id
                ),
                MentorshipSession.scheduled_at >= datetime.utcnow(),
                MentorshipSession.scheduled_at <= end_date,
                MentorshipSession.status.in_(["scheduled", "in_progress"])
            )
        ).order_by(MentorshipSession.scheduled_at.asc()).all()
        
        return sessions
    
    @staticmethod
    def complete_session(
        db: Session,
        session_id: int,
        user_id: int,
        notes: str = None,
        rating: float = None,
        homework: str = None
    ) -> MentorshipSession:
        """Complete a mentorship session"""
        
        session = db.query(MentorshipSession).join(
            MentorshipConnection,
            MentorshipSession.connection_id == MentorshipConnection.id
        ).filter(
            and_(
                MentorshipSession.id == session_id,
                or_(
                    MentorshipConnection.mentor_id == user_id,
                    MentorshipConnection.mentee_id == user_id
                )
            )
        ).first()
        
        if not session:
            raise ValueError("Session not found or user not authorized")
        
        session.status = "completed"
        session.ended_at = datetime.utcnow()
        
        if notes:
            if MentorshipConnection.mentor_id == user_id:
                session.mentor_notes = notes
            else:
                session.mentee_notes = notes
        
        if rating:
            session.session_rating = rating
        
        if homework:
            session.homework = homework
        
        # Update connection session count
        connection = session.connection
        connection.sessions_completed += 1
        
        db.commit()
        db.refresh(session)
        
        return session
    
    @staticmethod
    def rate_mentorship(
        db: Session,
        connection_id: int,
        user_id: int,
        rating: float,
        feedback: str = None
    ) -> MentorshipConnection:
        """Rate a mentorship relationship"""
        
        connection = db.query(MentorshipConnection).filter(
            and_(
                MentorshipConnection.id == connection_id,
                or_(
                    MentorshipConnection.mentor_id == user_id,
                    MentorshipConnection.mentee_id == user_id
                )
            )
        ).first()
        
        if not connection:
            raise ValueError("Connection not found or user not authorized")
        
        if connection.mentor_id == user_id:
            connection.mentee_rating = rating
            connection.mentee_feedback = feedback
        else:
            connection.mentor_rating = rating
            connection.mentor_feedback = feedback
        
        db.commit()
        db.refresh(connection)
        
        return connection

    @staticmethod
    def get_connection_by_id(db: Session, connection_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific connection by ID with user details"""
        from sqlalchemy.orm import joinedload
        
        connection = db.query(MentorshipConnection).options(
            joinedload(MentorshipConnection.mentor),
            joinedload(MentorshipConnection.mentee)
        ).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            return None
        
        conn_dict = connection.to_dict()
        conn_dict['mentor'] = {
            'id': connection.mentor.id,
            'username': connection.mentor.username,
            'full_name': connection.mentor.full_name,
            'email': connection.mentor.email,
            'role': connection.mentor.role
        }
        conn_dict['mentee'] = {
            'id': connection.mentee.id,
            'username': connection.mentee.username,
            'full_name': connection.mentee.full_name,
            'email': connection.mentee.email,
            'role': connection.mentee.role
        }
        
        return conn_dict

    @staticmethod
    def get_connection_messages(db: Session, connection_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all messages for a specific connection"""
        from sqlalchemy.orm import joinedload
        from app.models.user import User
        
        # First verify user has access to this connection
        connection = db.query(MentorshipConnection).filter(
            MentorshipConnection.id == connection_id,
            or_(
                MentorshipConnection.mentor_id == user_id,
                MentorshipConnection.mentee_id == user_id
            )
        ).first()
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        # Get messages without joinedload first
        messages = db.query(MentorshipMessage).filter(
            MentorshipMessage.connection_id == connection_id
        ).order_by(MentorshipMessage.created_at.asc()).all()
        
        result = []
        for msg in messages:
            msg_dict = msg.to_dict()
            
            # Get sender details separately
            try:
                sender = db.query(User).filter(User.id == msg.sender_id).first()
                if sender:
                    msg_dict['sender'] = {
                        'id': sender.id,
                        'username': sender.username,
                        'full_name': sender.full_name,
                        'email': sender.email,
                        'role': sender.role
                    }
                else:
                    # If sender doesn't exist, create a placeholder
                    msg_dict['sender'] = {
                        'id': msg.sender_id,
                        'username': f'user_{msg.sender_id}',
                        'full_name': f'User {msg.sender_id}',
                        'email': f'user{msg.sender_id}@example.com',
                        'role': 'unknown'
                    }
            except Exception as e:
                print(f"Error fetching sender {msg.sender_id}: {e}")
                msg_dict['sender'] = {
                    'id': msg.sender_id,
                    'username': f'user_{msg.sender_id}',
                    'full_name': f'User {msg.sender_id}',
                    'email': f'user{msg.sender_id}@example.com',
                    'role': 'unknown'
                }
            
            result.append(msg_dict)
        
        return result

    @staticmethod
    def delete_connection(db: Session, connection_id: int, user_id: int) -> bool:
        """Delete a mentorship connection"""
        try:
            # First verify user has access to this connection
            connection = db.query(MentorshipConnection).filter(
                MentorshipConnection.id == connection_id,
                or_(
                    MentorshipConnection.mentor_id == user_id,
                    MentorshipConnection.mentee_id == user_id
                )
            ).first()
            
            if not connection:
                return False
            
            # Delete the connection (messages will be deleted due to cascade)
            db.delete(connection)
            db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error deleting connection {connection_id}: {e}")
            db.rollback()
            return False