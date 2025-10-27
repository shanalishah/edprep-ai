#!/usr/bin/env python3
"""
Supabase User Seeding Script
Creates test users and mentor profiles in Supabase for development/testing
"""

import os
import asyncio
from supabase import create_client, Client
from typing import List, Dict, Any

# Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://your-project.supabase.co')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY', 'your-service-key-here')

def get_supabase_client() -> Client:
    """Create Supabase client with service key for admin operations"""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Test users data
TEST_USERS = [
    {
        "email": "admin1@edprep.ai",
        "password": "test123",
        "full_name": "Admin User 1",
        "role": "admin",
        "username": "admin1"
    },
    {
        "email": "admin2@edprep.ai", 
        "password": "test123",
        "full_name": "Admin User 2",
        "role": "admin",
        "username": "admin2"
    },
    {
        "email": "dr.emma.chen@edprep.ai",
        "password": "test123",
        "full_name": "Dr. Emma Chen",
        "role": "mentor",
        "username": "dr.emma.chen",
        "bio": "IELTS expert with 10+ years experience",
        "teaching_experience": "10+ years teaching IELTS",
        "specializations": ["Writing", "Speaking"],
        "is_available_for_mentorship": True,
        "max_mentees": 5
    },
    {
        "email": "prof.john.smith@edprep.ai",
        "password": "test123", 
        "full_name": "Prof. John Smith",
        "role": "mentor",
        "username": "prof.john.smith",
        "bio": "University professor specializing in English language assessment",
        "teaching_experience": "15+ years in language assessment",
        "specializations": ["Reading", "Writing"],
        "is_available_for_mentorship": True,
        "max_mentees": 3
    },
    {
        "email": "ahmed.hassan@student.com",
        "password": "test123",
        "full_name": "Ahmed Hassan", 
        "role": "student",
        "username": "ahmed_hassan"
    },
    {
        "email": "sarah.johnson@student.com",
        "password": "test123",
        "full_name": "Sarah Johnson",
        "role": "student", 
        "username": "sarah_johnson"
    },
    {
        "email": "maria.rodriguez@student.com",
        "password": "test123",
        "full_name": "Maria Rodriguez",
        "role": "student",
        "username": "maria_rodriguez"
    }
]

async def create_users_and_profiles():
    """Create users in Supabase Auth and their profiles"""
    supabase = get_supabase_client()
    
    print("🚀 Starting Supabase user seeding...")
    
    created_users = []
    
    for user_data in TEST_USERS:
        try:
            print(f"📝 Creating user: {user_data['email']}")
            
            # Create user in Supabase Auth
            auth_response = supabase.auth.admin.create_user({
                "email": user_data["email"],
                "password": user_data["password"],
                "email_confirm": True,
                "user_metadata": {
                    "full_name": user_data["full_name"],
                    "role": user_data["role"],
                    "username": user_data["username"]
                }
            })
            
            if auth_response.user:
                user_id = auth_response.user.id
                print(f"✅ User created: {user_data['email']} (ID: {user_id})")
                
                # Create profile in public.profiles
                profile_data = {
                    "id": user_id,
                    "email": user_data["email"],
                    "username": user_data["username"],
                    "full_name": user_data["full_name"],
                    "role": user_data["role"]
                }
                
                # Add mentor-specific fields if applicable
                if user_data["role"] == "mentor":
                    profile_data.update({
                        "bio": user_data.get("bio", ""),
                        "teaching_experience": user_data.get("teaching_experience", ""),
                        "specializations": user_data.get("specializations", []),
                        "is_available_for_mentorship": user_data.get("is_available_for_mentorship", False),
                        "max_mentees": user_data.get("max_mentees", 3)
                    })
                
                # Insert profile
                profile_response = supabase.table("profiles").insert(profile_data).execute()
                
                if profile_response.data:
                    print(f"✅ Profile created for: {user_data['email']}")
                    created_users.append({
                        "email": user_data["email"],
                        "role": user_data["role"],
                        "user_id": user_id
                    })
                else:
                    print(f"❌ Failed to create profile for: {user_data['email']}")
                    
            else:
                print(f"❌ Failed to create user: {user_data['email']}")
                
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {str(e)}")
    
    print(f"\n🎉 User seeding completed! Created {len(created_users)} users:")
    for user in created_users:
        print(f"  - {user['email']} ({user['role']})")
    
    return created_users

async def verify_mentors():
    """Verify that mentors are available for mentorship"""
    supabase = get_supabase_client()
    
    print("\n🔍 Verifying mentors...")
    
    try:
        mentors_response = supabase.table("profiles").select("*").eq("role", "mentor").execute()
        
        if mentors_response.data:
            print(f"✅ Found {len(mentors_response.data)} mentors:")
            for mentor in mentors_response.data:
                status = "Available" if mentor.get("is_available_for_mentorship") else "Not Available"
                print(f"  - {mentor['full_name']} ({mentor['email']}) - {status}")
        else:
            print("❌ No mentors found")
            
    except Exception as e:
        print(f"❌ Error verifying mentors: {str(e)}")

async def main():
    """Main seeding function"""
    print("=" * 60)
    print("🎓 IELTS Master Platform - Supabase User Seeding")
    print("=" * 60)
    
    # Check if Supabase is configured
    if SUPABASE_URL == 'https://your-project.supabase.co':
        print("❌ Please configure SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
        print("   Get these from your Supabase project settings")
        return
    
    try:
        # Create users and profiles
        await create_users_and_profiles()
        
        # Verify mentors
        await verify_mentors()
        
        print("\n" + "=" * 60)
        print("✅ Supabase seeding completed successfully!")
        print("=" * 60)
        print("\n📋 Test Credentials:")
        print("  Admin: admin1@edprep.ai / test123")
        print("  Mentor: dr.emma.chen@edprep.ai / test123")
        print("  Student: ahmed.hassan@student.com / test123")
        
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())

