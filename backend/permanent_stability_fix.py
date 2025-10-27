import os
import sys
import sqlite3
import requests
import json
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.database import DatabaseManager, init_database, create_tables
from app.core.config import settings

class RailwayStabilityManager:
    """Permanent stability solution for Railway deployments"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.backend_url = "https://web-production-4d7f.up.railway.app"
        
    def ensure_database_stability(self):
        """Ensure database is stable and persistent"""
        print("🔧 Ensuring database stability...")
        
        try:
            # Initialize database
            init_database()
            create_tables()
            print("✅ Database initialized successfully")
            
            # Create persistent users
            self.create_persistent_users()
            
            # Verify system health
            return self.verify_system_health()
            
        except Exception as e:
            print(f"❌ Database stability check failed: {e}")
            return False
    
    def create_persistent_users(self):
        """Create users that persist across deployments"""
        print("👥 Creating persistent users...")
        
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
            },
            {
                "email": "ms.sarah.wilson@edprep.ai",
                "username": "ms.sarah.wilson", 
                "password": "tutor123",
                "full_name": "Ms. Sarah Wilson",
                "role": "tutor"
            }
        ]
        
        created_count = 0
        for user_data in users:
            try:
                # Check if user exists
                existing_user = self.db_manager.get_user_by_email(user_data["email"])
                if existing_user:
                    print(f"✅ User {user_data['email']} already exists")
                    continue
                
                # Create user
                user_id = self.db_manager.create_user(
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                    full_name=user_data["full_name"],
                    role=user_data["role"]
                )
                
                if user_id:
                    print(f"✅ Created user: {user_data['email']}")
                    created_count += 1
                    
                    # Create mentor profile if needed
                    if user_data["role"] in ["mentor", "tutor"]:
                        self.create_mentor_profile(user_id, user_data)
                        
            except Exception as e:
                print(f"❌ Failed to create user {user_data['email']}: {e}")
        
        print(f"📊 Created {created_count} new users")
        return created_count > 0
    
    def create_mentor_profile(self, user_id, user_data):
        """Create mentor profile for mentors/tutors"""
        try:
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
            
            # Create profile using database manager
            profile_id = self.db_manager.create_mentor_profile(**profile_data)
            if profile_id:
                print(f"✅ Created profile for {user_data['email']}")
                return True
            else:
                print(f"❌ Failed to create profile for {user_data['email']}")
                return False
                
        except Exception as e:
            print(f"❌ Error creating profile for {user_data['email']}: {e}")
            return False
    
    def verify_system_health(self):
        """Verify the entire system is working"""
        print("🔍 Verifying system health...")
        
        try:
            # Test database connection
            users = self.db_manager.get_all_users()
            print(f"✅ Database: {len(users)} users found")
            
            # Test mentor profiles
            mentors = self.db_manager.get_available_mentors()
            print(f"✅ Mentors: {len(mentors)} available")
            
            # Test API endpoints
            if self.test_api_endpoints():
                print("✅ API endpoints working")
                return True
            else:
                print("❌ API endpoints failed")
                return False
                
        except Exception as e:
            print(f"❌ System health check failed: {e}")
            return False
    
    def test_api_endpoints(self):
        """Test critical API endpoints"""
        try:
            # Test health endpoint
            response = requests.get(f"{self.backend_url}/health", timeout=10)
            if response.status_code != 200:
                return False
            
            # Test mentor search
            token = self.get_test_token()
            if not token:
                return False
                
            response = requests.get(
                f"{self.backend_url}/api/v1/mentorship/mentors",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"❌ API test failed: {e}")
            return False
    
    def get_test_token(self):
        """Get authentication token for testing"""
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                data={
                    "username": "ahmed.hassan@student.com",
                    "password": "student123"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()["access_token"]
            return None
            
        except Exception as e:
            print(f"❌ Token request failed: {e}")
            return None
    
    def run_permanent_fix(self):
        """Run the complete permanent stability fix"""
        print("🚀 Starting permanent stability fix...")
        print("=" * 60)
        
        # Step 1: Ensure database stability
        if not self.ensure_database_stability():
            print("❌ Database stability check failed")
            return False
        
        # Step 2: Wait for Railway to stabilize
        print("⏳ Waiting for Railway to stabilize...")
        time.sleep(5)
        
        # Step 3: Final verification
        if self.verify_system_health():
            print("=" * 60)
            print("✅ PERMANENT STABILITY FIX COMPLETED SUCCESSFULLY!")
            print("\n🔑 Test Credentials:")
            print("   Student: ahmed.hassan@student.com / student123")
            print("   Mentor: dr.emma.chen@edprep.ai / mentor123") 
            print("   Admin: admin@edprep.ai / admin123")
            print("\n📱 Your app should now be stable and working!")
            return True
        else:
            print("❌ Final verification failed")
            return False

def main():
    """Main entry point"""
    manager = RailwayStabilityManager()
    success = manager.run_permanent_fix()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()

