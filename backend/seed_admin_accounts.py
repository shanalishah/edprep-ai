#!/usr/bin/env python3
"""
Script to seed admin accounts for development and testing
"""

import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Override database URL for local development
os.environ["DATABASE_URL"] = "sqlite:///./ielts_master.db"

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, DatabaseManager, create_tables
from app.models.user import User, UserProgress
from app.core.security import get_password_hash


def seed_admin_accounts():
    """Create 5 admin accounts for testing"""
    
    # Admin account data
    admin_accounts = [
        {
            "email": "admin1@edprep.ai",
            "username": "admin1",
            "password": "admin123",
            "full_name": "Admin User 1",
            "role": "admin",
            "is_verified": True,
            "is_premium": True,
            "target_band_score": 9.0,
            "current_level": "advanced"
        },
        {
            "email": "admin2@edprep.ai", 
            "username": "admin2",
            "password": "admin123",
            "full_name": "Admin User 2",
            "role": "admin",
            "is_verified": True,
            "is_premium": True,
            "target_band_score": 8.5,
            "current_level": "advanced"
        },
        {
            "email": "admin3@edprep.ai",
            "username": "admin3", 
            "password": "admin123",
            "full_name": "Admin User 3",
            "role": "admin",
            "is_verified": True,
            "is_premium": True,
            "target_band_score": 8.0,
            "current_level": "intermediate"
        },
        {
            "email": "mentor1@edprep.ai",
            "username": "mentor1",
            "password": "admin123", 
            "full_name": "Mentor User 1",
            "role": "mentor",
            "is_verified": True,
            "is_premium": True,
            "target_band_score": 9.0,
            "current_level": "advanced"
        },
        {
            "email": "tutor1@edprep.ai",
            "username": "tutor1",
            "password": "admin123",
            "full_name": "Tutor User 1", 
            "role": "tutor",
            "is_verified": True,
            "is_premium": True,
            "target_band_score": 8.5,
            "current_level": "advanced"
        }
    ]
    
    # Ensure tables are created
    create_tables()
    
    db = SessionLocal()
    
    try:
        print("🌱 Seeding admin accounts...")
        
        for account_data in admin_accounts:
            # Check if user already exists
            existing_user = db.query(User).filter(User.email == account_data["email"]).first()
            if existing_user:
                print(f"⚠️  User {account_data['email']} already exists, skipping...")
                continue
            
            # Use a simple hash for admin accounts to avoid bcrypt issues
            import hashlib
            hashed_password = hashlib.sha256(account_data["password"].encode()).hexdigest()
            
            user = User(
                email=account_data["email"],
                username=account_data["username"],
                hashed_password=hashed_password,
                full_name=account_data["full_name"],
                role=account_data["role"],
                is_verified=account_data["is_verified"],
                is_premium=account_data["is_premium"],
                target_band_score=account_data["target_band_score"],
                current_level=account_data["current_level"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Create initial progress record
            progress = UserProgress(user_id=user.id)
            db.add(progress)
            db.commit()
            
            print(f"✅ Created {account_data['role']} account: {account_data['email']} / {account_data['password']}")
        
        print("\n🎉 Admin accounts seeded successfully!")
        print("\n📋 Test Admin Credentials:")
        print("=" * 50)
        for account in admin_accounts:
            print(f"Email: {account['email']}")
            print(f"Password: {account['password']}")
            print(f"Role: {account['role']}")
            print("-" * 30)
            
    except Exception as e:
        print(f"❌ Error seeding admin accounts: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_accounts()
