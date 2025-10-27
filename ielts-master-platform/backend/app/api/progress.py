"""
Progress Tracking and Analytics API Endpoints - Fixed Version
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/progress/test")
async def test_progress_endpoint(
    current_user: dict = Depends(get_current_user)
):
    """Test endpoint to debug progress API"""
    return {
        "message": "Progress API is working",
        "user": current_user,
        "user_id": current_user.get("user_id"),
        "isGuest": current_user.get("isGuest", False)
    }

@router.get("/progress/overview")
async def get_progress_overview(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive progress overview for a user"""
    
    # Handle guest users
    if current_user.get("isGuest", False):
        return {"message": "Guest users cannot access progress data", "isGuest": True}
    
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Convert user_id to integer for database queries
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    # Get user progress data
    progress_query = text("""
        SELECT essays_written, average_score, best_score, improvement_rate,
               task_achievement_avg, coherence_cohesion_avg, lexical_resource_avg,
               grammatical_range_avg, l1_errors_total, interlanguage_errors_total,
               discourse_errors_total, created_at, updated_at
        FROM user_progress 
        WHERE user_id = :user_id
    """)
    
    progress_result = db.execute(progress_query, {"user_id": user_id}).fetchone()
    
    # Get analytics data
    analytics_query = text("""
        SELECT metric_name, metric_value, metric_type, recorded_at
        FROM user_analytics 
        WHERE user_id = :user_id
        ORDER BY recorded_at DESC
    """)
    
    analytics_results = db.execute(analytics_query, {"user_id": user_id}).fetchall()
    
    # Get achievements
    achievements_query = text("""
        SELECT achievement_type, achievement_name, description, points, earned_at
        FROM user_achievements 
        WHERE user_id = :user_id
        ORDER BY earned_at DESC
    """)
    
    achievements_results = db.execute(achievements_query, {"user_id": user_id}).fetchall()
    
    # Get recent study sessions
    sessions_query = text("""
        SELECT session_type, duration_minutes, content_covered, started_at, ended_at, efficiency_score
        FROM user_study_sessions 
        WHERE user_id = :user_id
        ORDER BY started_at DESC
        LIMIT 10
    """)
    
    sessions_results = db.execute(sessions_query, {"user_id": user_id}).fetchall()
    
    # Get user email from users table
    user_query = text("SELECT email FROM users WHERE id = :user_id")
    user_result = db.execute(user_query, {"user_id": user_id}).fetchone()
    user_email = user_result.email if user_result else "unknown"
    
    # Format response
    response = {
        "user_id": user_id,
        "user_email": user_email,
        "progress": {
            "essays_written": progress_result.essays_written if progress_result else 0,
            "average_score": progress_result.average_score if progress_result else 0.0,
            "best_score": progress_result.best_score if progress_result else 0.0,
            "improvement_rate": progress_result.improvement_rate if progress_result else 0.0,
            "skill_breakdown": {
                "task_achievement": progress_result.task_achievement_avg if progress_result else 0.0,
                "coherence_cohesion": progress_result.coherence_cohesion_avg if progress_result else 0.0,
                "lexical_resource": progress_result.lexical_resource_avg if progress_result else 0.0,
                "grammatical_range": progress_result.grammatical_range_avg if progress_result else 0.0,
            },
            "error_analysis": {
                "l1_errors": progress_result.l1_errors_total if progress_result else 0,
                "interlanguage_errors": progress_result.interlanguage_errors_total if progress_result else 0,
                "discourse_errors": progress_result.discourse_errors_total if progress_result else 0,
            },
            "last_updated": progress_result.updated_at if progress_result and progress_result.updated_at else None
        },
        "analytics": {
            metric.metric_name: {
                "value": metric.metric_value,
                "type": metric.metric_type,
                "recorded_at": metric.recorded_at
            }
            for metric in analytics_results
        },
        "achievements": [
            {
                "type": achievement.achievement_type,
                "name": achievement.achievement_name,
                "description": achievement.description,
                "points": achievement.points,
                "earned_at": achievement.earned_at
            }
            for achievement in achievements_results
        ],
        "recent_sessions": [
            {
                "type": session.session_type,
                "duration_minutes": session.duration_minutes,
                "content": session.content_covered,
                "started_at": session.started_at,
                "ended_at": session.ended_at if session.ended_at else None,
                "efficiency_score": session.efficiency_score
            }
            for session in sessions_results
        ]
    }
    
    return response

@router.get("/progress/analytics")
async def get_detailed_analytics(
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get detailed analytics data"""
    
    # Handle guest users
    if current_user.get("isGuest", False):
        return {"message": "Guest users cannot access analytics data", "isGuest": True}
    
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Convert user_id to integer for database queries
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    # Build query with optional filters
    query = text("""
        SELECT metric_name, metric_value, metric_type, recorded_at, metadata
        FROM user_analytics 
        WHERE user_id = :user_id AND recorded_at >= :start_date
    """)
    params = {"user_id": user_id, "start_date": datetime.now() - timedelta(days=days)}
    
    if metric_type:
        query = text("""
            SELECT metric_name, metric_value, metric_type, recorded_at, metadata
            FROM user_analytics 
            WHERE user_id = :user_id AND recorded_at >= :start_date AND metric_type = :metric_type
        """)
        params["metric_type"] = metric_type
    
    query = text(str(query) + " ORDER BY recorded_at DESC")
    
    results = db.execute(query, params).fetchall()
    
    # Group metrics by type
    metrics_by_type = {}
    for result in results:
        metric_type = result.metric_type
        if metric_type not in metrics_by_type:
            metrics_by_type[metric_type] = []
        
        metrics_by_type[metric_type].append({
            "name": result.metric_name,
            "value": result.metric_value,
            "recorded_at": result.recorded_at,
            "metadata": json.loads(result.metadata) if result.metadata else None
        })
    
    return {
        "user_id": user_id,
        "period_days": days,
        "metrics_by_type": metrics_by_type,
        "summary": {
            "total_metrics": len(results),
            "metric_types": list(metrics_by_type.keys()),
            "date_range": {
                "from": str(datetime.now() - timedelta(days=days)),
                "to": str(datetime.now())
            }
        }
    }

@router.get("/progress/achievements")
async def get_achievements(
    achievement_type: Optional[str] = Query(None, description="Filter by achievement type"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get user achievements"""
    
    # Handle guest users
    if current_user.get("isGuest", False):
        return {"message": "Guest users cannot access achievements", "isGuest": True}
    
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Convert user_id to integer for database queries
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    query = text("""
        SELECT achievement_type, achievement_name, description, points, earned_at
        FROM user_achievements 
        WHERE user_id = :user_id
    """)
    params = {"user_id": user_id}
    
    if achievement_type:
        query = text("""
            SELECT achievement_type, achievement_name, description, points, earned_at
            FROM user_achievements 
            WHERE user_id = :user_id AND achievement_type = :achievement_type
        """)
        params["achievement_type"] = achievement_type
    
    query = text(str(query) + " ORDER BY earned_at DESC")
    
    results = db.execute(query, params).fetchall()
    
    # Calculate total points
    total_points = sum(achievement.points for achievement in results)
    
    return {
        "user_id": user_id,
        "total_achievements": len(results),
        "total_points": total_points,
        "achievements": [
            {
                "type": achievement.achievement_type,
                "name": achievement.achievement_name,
                "description": achievement.description,
                "points": achievement.points,
                "earned_at": achievement.earned_at
            }
            for achievement in results
        ]
    }

@router.get("/progress/study-sessions")
async def get_study_sessions(
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get study session history"""
    
    # Handle guest users
    if current_user.get("isGuest", False):
        return {"message": "Guest users cannot access study sessions", "isGuest": True}
    
    user_id = current_user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user")
    
    # Convert user_id to integer for database queries
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid user ID")
    
    query = text("""
        SELECT session_type, duration_minutes, content_covered, started_at, ended_at, efficiency_score
        FROM user_study_sessions 
        WHERE user_id = :user_id AND started_at >= :start_date
    """)
    params = {"user_id": user_id, "start_date": datetime.now() - timedelta(days=days)}
    
    if session_type:
        query = text("""
            SELECT session_type, duration_minutes, content_covered, started_at, ended_at, efficiency_score
            FROM user_study_sessions 
            WHERE user_id = :user_id AND started_at >= :start_date AND session_type = :session_type
        """)
        params["session_type"] = session_type
    
    query = text(str(query) + " ORDER BY started_at DESC")
    
    results = db.execute(query, params).fetchall()
    
    # Calculate statistics
    total_duration = sum(session.duration_minutes for session in results)
    avg_efficiency = sum(session.efficiency_score for session in results if session.efficiency_score) / len([s for s in results if s.efficiency_score]) if results else 0
    
    # Group by session type
    sessions_by_type = {}
    for session in results:
        session_type = session.session_type
        if session_type not in sessions_by_type:
            sessions_by_type[session_type] = []
        
        sessions_by_type[session_type].append({
            "duration_minutes": session.duration_minutes,
            "content": session.content_covered,
            "started_at": session.started_at,
            "ended_at": session.ended_at if session.ended_at else None,
            "efficiency_score": session.efficiency_score
        })
    
    return {
        "user_id": user_id,
        "period_days": days,
        "statistics": {
            "total_sessions": len(results),
            "total_duration_minutes": total_duration,
            "total_duration_hours": round(total_duration / 60, 2),
            "average_efficiency": round(avg_efficiency, 2),
            "sessions_by_type": {k: len(v) for k, v in sessions_by_type.items()}
        },
        "sessions_by_type": sessions_by_type
    }
