#!/usr/bin/env python3
"""
Setup mentor profiles for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models.mentorship import UserProfile
from app.models.user import User
from sqlalchemy.orm import Session

def setup_mentor_profiles():
    """Set up mentor profiles for testing"""
    db = next(get_db())
    
    try:
        # Get all users with mentor/tutor roles
        mentors = db.query(User).filter(User.role.in_(["mentor", "tutor"])).all()
        
        print(f"Found {len(mentors)} mentors/tutors to set up...")
        
        for mentor in mentors:
            # Check if profile already exists
            existing_profile = db.query(UserProfile).filter(UserProfile.user_id == mentor.id).first()
            
            if existing_profile:
                print(f"Profile already exists for {mentor.username}")
                continue
            
            # Create profile based on role
            if mentor.role == "mentor":
                profile_data = {
                    "user_id": mentor.id,
                    "is_available_for_mentorship": True,
                    "mentorship_status": "available",
                    "max_mentees": 5,
                    "bio": f"Experienced IELTS mentor with expertise in {mentor.username} preparation. I help students achieve their target band scores through personalized guidance and practice.",
                    "teaching_experience": "5+ years of IELTS teaching experience",
                    "specializations": ["Writing Task 2", "Speaking", "Reading"],
                    "certifications": ["IELTS Teacher Training Certificate", "TESOL Certificate"],
                    "timezone": "UTC+8",
                    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "available_hours": ["morning", "afternoon", "evening"],
                    "total_mentees_helped": 0,
                    "average_rating": 0.0,
                    "total_sessions_conducted": 0
                }
            else:  # tutor
                profile_data = {
                    "user_id": mentor.id,
                    "is_available_for_mentorship": True,
                    "mentorship_status": "available",
                    "max_mentees": 3,
                    "bio": f"Professional IELTS tutor specializing in {mentor.username} preparation. I provide comprehensive support to help students excel in all IELTS components.",
                    "teaching_experience": "3+ years of IELTS tutoring experience",
                    "specializations": ["Writing", "Speaking", "Listening", "Reading"],
                    "certifications": ["IELTS Tutor Certificate", "English Teaching License"],
                    "timezone": "UTC+8",
                    "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
                    "available_hours": ["afternoon", "evening"],
                    "total_mentees_helped": 0,
                    "average_rating": 0.0,
                    "total_sessions_conducted": 0
                }
            
            # Create the profile
            profile = UserProfile(**profile_data)
            db.add(profile)
            print(f"Created profile for {mentor.username} ({mentor.role})")
        
        db.commit()
        print("✅ All mentor profiles created successfully!")
        
        # Verify the setup
        print("\n📊 Verification:")
        available_mentors = db.query(User, UserProfile).join(
            UserProfile, User.id == UserProfile.user_id
        ).filter(
            UserProfile.is_available_for_mentorship == True
        ).all()
        
        print(f"Total available mentors: {len(available_mentors)}")
        for user, profile in available_mentors:
            print(f"  - {user.username} ({user.role}): {profile.bio[:50]}...")
            
    except Exception as e:
        print(f"❌ Error setting up mentor profiles: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_mentor_profiles()