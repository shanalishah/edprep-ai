#!/usr/bin/env python3
"""
Vercel Database Setup Script
Creates users and mentor profiles for Vercel deployment
"""

import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
sys.path.insert(0, backend_path)

from app.database import DatabaseManager, init_database, create_tables

def setup_vercel_database():
    """Set up database for Vercel deployment"""
    print("🚀 Setting up Vercel database...")
    
    try:
        # Initialize database
        init_database()
        create_tables()
        print("✅ Database initialized")
        
        # Create database manager
        db_manager = DatabaseManager()
        
        # Create users
        users = [
            {
                "email": "admin@edprep.ai",
                "username": "admin",
                "password": "admin123",
                "full_name": "Sarah Johnson",
                "role": "admin"
            },
            {
                "email": "ahmed.hassan@student.com",
                "username": "ahmed_hassan",
                "password": "student123",
                "full_name": "Ahmed Hassan",
                "role": "student"
            },
            {
                "email": "dr.emma.chen@edprep.ai",
                "username": "dr.emma.chen",
                "password": "mentor123",
                "full_name": "Dr. Emma Chen",
                "role": "mentor"
            },
            {
                "email": "prof.david.kim@edprep.ai",
                "username": "prof.david.kim",
                "password": "mentor123",
                "full_name": "Prof. David Kim",
                "role": "mentor"
            },
            {
                "email": "ms.lisa.patel@edprep.ai",
                "username": "ms.lisa.patel",
                "password": "tutor123",
                "full_name": "Ms. Lisa Patel",
                "role": "tutor"
            }
        ]
        
        created_count = 0
        for user_data in users:
            try:
                # Check if user exists
                existing_user = db_manager.get_user_by_email(user_data["email"])
                if existing_user:
                    print(f"✅ User {user_data['email']} already exists")
                    continue
                
                # Create user
                user_id = db_manager.create_user(
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                
                if user_id:
                    print(f"✅ Created user: {user_data['email']}")
                    created_count += 1
                    
                    # Create mentor profile for mentors/tutors
                    if user_data["role"] in ["mentor", "tutor"]:
                        profile_data = {
                            "user_id": user_id,
                            "bio": f"Experienced IELTS {user_data['role']} with expertise in test preparation.",
                            "teaching_experience": f"5+ years as an IELTS {user_data['role']}.",
                            "specializations": ["IELTS Preparation", "Test Strategies"],
                            "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
                            "timezone": "UTC",
                            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                            "available_hours": ["09:00-17:00"],
                            "is_available_for_mentorship": True,
                            "max_mentees": 5,
                            "mentorship_status": "available"
                        }
                        
                        profile_id = db_manager.create_mentor_profile(**profile_data)
                        if profile_id:
                            print(f"✅ Created profile for {user_data['email']}")
                        
            except Exception as e:
                print(f"❌ Error creating user {user_data['email']}: {e}")
        
        print(f"📊 Created {created_count} new users")
        print("✅ Vercel database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_vercel_database()
    sys.exit(0 if success else 1)
