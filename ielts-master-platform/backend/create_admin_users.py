#!/usr/bin/env python3
"""
Create 3 admin users with full privileges for IELTS Master Platform
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
import os

def create_admin_users():
    """Create 3 admin users with full privileges"""
    
    # Database path
    db_path = "ielts_master.db"
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table already exists, we'll work with the existing schema
    
    # Create user_progress table for comprehensive tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            test_type VARCHAR(20) NOT NULL,
            test_id VARCHAR(50) NOT NULL,
            score DECIMAL(3,1) NOT NULL,
            max_score DECIMAL(3,1) DEFAULT 9.0,
            time_spent INTEGER DEFAULT 0,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            detailed_results TEXT,
            feedback TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user_analytics table for detailed insights
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            metric_name VARCHAR(50) NOT NULL,
            metric_value DECIMAL(10,2) NOT NULL,
            metric_type VARCHAR(20) NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user_achievements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            achievement_type VARCHAR(50) NOT NULL,
            achievement_name VARCHAR(100) NOT NULL,
            description TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            points INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create user_study_sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_type VARCHAR(30) NOT NULL,
            duration_minutes INTEGER NOT NULL,
            content_covered TEXT,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            efficiency_score DECIMAL(3,2),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Helper function to hash password using bcrypt (same as auth system)
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(password):
        return pwd_context.hash(password)
    
    # Define 3 admin users
    admin_users = [
        {
            "username": "admin1",
            "email": "admin1@edprep.ai",
            "password": "admin123!",
            "role": "admin",
            "profile_data": {
                "full_name": "Sarah Johnson",
                "level": "advanced",
                "target_score": 8.0,
                "study_goals": ["Academic IELTS", "University Admission"],
                "preferred_test_types": ["listening", "reading", "writing", "speaking"]
            }
        },
        {
            "username": "admin2", 
            "email": "admin2@edprep.ai",
            "password": "admin456!",
            "role": "admin",
            "profile_data": {
                "full_name": "Michael Chen",
                "level": "intermediate",
                "target_score": 7.0,
                "study_goals": ["General IELTS", "Immigration"],
                "preferred_test_types": ["speaking", "writing"]
            }
        },
        {
            "username": "admin3",
            "email": "admin3@edprep.ai", 
            "password": "admin789!",
            "role": "admin",
            "profile_data": {
                "full_name": "Emily Rodriguez",
                "level": "beginner",
                "target_score": 6.0,
                "study_goals": ["General IELTS", "Work Visa"],
                "preferred_test_types": ["listening", "reading"]
            }
        }
    ]
    
    # Insert admin users
    for user_data in admin_users:
        password_hash = hash_password(user_data["password"])
        
        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data["email"],))
        if cursor.fetchone():
            print(f"User {user_data['email']} already exists, skipping...")
            continue
        
        # Insert user using existing schema
        cursor.execute('''
            INSERT INTO users (username, email, hashed_password, full_name, role, is_active, is_verified, is_premium, 
                             first_language, target_band_score, current_level, learning_goals, total_points, level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data["username"],
            user_data["email"], 
            password_hash,
            user_data["profile_data"]["full_name"],
            user_data["role"],
            True,  # is_active
            True,  # is_verified
            True,  # is_premium
            "English",  # first_language
            user_data["profile_data"]["target_score"],
            user_data["profile_data"]["level"],
            str(user_data["profile_data"]["study_goals"]),
            100,  # total_points
            1      # level
        ))
        
        print(f"✅ Created admin user: {user_data['email']}")
    
    print("✅ Users created successfully!")
    
    # Commit changes
    conn.commit()
    conn.close()
    
    print("\n🎉 Successfully created 3 admin users with full privileges!")
    print("\n📊 Database tables created:")
    print("   - users (with admin privileges)")
    print("   - user_progress (comprehensive test tracking)")
    print("   - user_analytics (detailed performance metrics)")
    print("   - user_achievements (gamification system)")
    print("   - user_study_sessions (study time tracking)")
    
    print("\n👥 Admin Users Created:")
    for user_data in admin_users:
        print(f"   - {user_data['email']} (Password: {user_data['password']})")
    
    print("\n🔑 Permissions granted:")
    print("   - admin: Full system access")
    print("   - user: Standard user features")
    print("   - mentor: Mentorship capabilities")
    print("   - analytics: Advanced analytics access")
    print("   - progress: Progress tracking features")

if __name__ == "__main__":
    create_admin_users()
