#!/usr/bin/env python3
"""
Railway Database Recovery Script
Automatically recreates users and mentor profiles when Railway database resets.
"""

import requests
import os
import json
import time
import sys

BACKEND_URL = os.getenv("BACKEND_URL", "https://web-production-4d7f.up.railway.app")

def create_user(email, username, password, full_name, role):
    """Create a user account"""
    url = f"{BACKEND_URL}/api/v1/admin/create-test-user"
    payload = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": role
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    user_data = response.json()

    if response.status_code == 200 and user_data.get("user_id"):
        print(f"✅ Created {full_name} ({role}): {email}")
        return user_data["user_id"]
    else:
        print(f"❌ Failed to create {full_name} ({email}): {user_data.get('error', user_data)}")
        return None

def login_user(email, password):
    """Login and get token"""
    url = f"{BACKEND_URL}/api/v1/auth/login"
    payload = {
        "username": email,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    if response.ok:
        return response.json()["access_token"]
    return None

def create_mentor_profile(email, password, profile_data):
    """Create mentor profile"""
    token = login_user(email, password)
    if not token:
        print(f"❌ Failed to login {email}")
        return False

    profile_url = f"{BACKEND_URL}/api/v1/mentorship/profile"
    profile_payload = {
        "bio": profile_data["bio"],
        "teaching_experience": profile_data["teaching_experience"],
        "specializations": json.dumps(profile_data["specializations"]),
        "certifications": json.dumps(profile_data["certifications"]),
        "timezone": profile_data["timezone"],
        "available_days": json.dumps(profile_data["available_days"]),
        "available_hours": json.dumps(profile_data["available_hours"]),
        "is_available_for_mentorship": str(profile_data["is_available_for_mentorship"]).lower(),
        "max_mentees": str(profile_data["max_mentees"])
    }
    profile_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}"
    }
    profile_response = requests.post(profile_url, data=profile_payload, headers=profile_headers)
    if profile_response.status_code == 200:
        print(f"✅ Profile created for {email}")
        return True
    else:
        print(f"❌ Failed to create profile for {email}: {profile_response.json()}")
        return False

def verify_mentors():
    """Verify mentors are available"""
    try:
        # Login as a student to check mentors
        token = login_user("ahmed.hassan@student.com", "student123")
        if not token:
            print("❌ Cannot verify mentors - student login failed")
            return False
        
        mentors_url = f"{BACKEND_URL}/api/v1/mentorship/mentors"
        response = requests.get(mentors_url, headers={"Authorization": f"Bearer {token}"})
        
        if response.ok:
            data = response.json()
            mentor_count = data.get("count", 0)
            print(f"✅ Found {mentor_count} mentors available")
            return mentor_count > 0
        else:
            print(f"❌ Failed to verify mentors: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Error verifying mentors: {e}")
        return False

def main():
    print("🚀 Starting Railway Database Recovery...")
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 60)

    # Define all users to create
    users_to_create = [
        {"email": "admin@edprep.ai", "username": "admin", "password": "admin123", "full_name": "Sarah Johnson", "role": "admin"},
        {"email": "ahmed.hassan@student.com", "username": "ahmed_hassan", "password": "student123", "full_name": "Ahmed Hassan", "role": "student"},
        {"email": "maria.gonzalez@student.com", "username": "maria.gonzalez", "password": "student123", "full_name": "Maria Gonzalez", "role": "student"},
        {"email": "wei.zhang@student.com", "username": "wei.zhang", "password": "student123", "full_name": "Wei Zhang", "role": "student"},
        {"email": "priya.sharma@student.com", "username": "priya.sharma", "password": "student123", "full_name": "Priya Sharma", "role": "student"},
        {"email": "john.smith@student.com", "username": "john.smith", "password": "student123", "full_name": "John Smith", "role": "student"},
        
        # Mentors with profiles
        {"email": "dr.emma.chen@edprep.ai", "username": "dr.emma.chen", "password": "mentor123", "full_name": "Dr. Emma Chen", "role": "mentor",
         "profile": {
             "bio": "Former Cambridge examiner with 10+ years of experience. Specializes in IELTS Writing Task 2 and Speaking fluency.",
             "teaching_experience": "10+ years as an IELTS examiner and tutor.",
             "specializations": ["Writing Task 2", "Speaking Fluency"],
             "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
             "timezone": "UTC", "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "available_hours": ["09:00-17:00"], "is_available_for_mentorship": True, "max_mentees": 5
         }},
        
        {"email": "prof.david.kim@edprep.ai", "username": "prof.david.kim", "password": "mentor123", "full_name": "Prof. David Kim", "role": "mentor",
         "profile": {
             "bio": "Experienced IELTS mentor with expertise in academic writing and test strategies.",
             "teaching_experience": "8+ years of experience as an IELTS mentor.",
             "specializations": ["Academic Writing", "Test Strategies"],
             "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
             "timezone": "UTC", "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "available_hours": ["09:00-17:00"], "is_available_for_mentorship": True, "max_mentees": 5
         }},
        
        # Tutors with profiles
        {"email": "ms.lisa.patel@edprep.ai", "username": "ms.lisa.patel", "password": "tutor123", "full_name": "Ms. Lisa Patel", "role": "tutor",
         "profile": {
             "bio": "Dedicated IELTS tutor specializing in Reading and Listening comprehension.",
             "teaching_experience": "6+ years as an IELTS tutor.",
             "specializations": ["Reading Comprehension", "Listening Skills"],
             "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
             "timezone": "UTC", "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "available_hours": ["09:00-17:00"], "is_available_for_mentorship": True, "max_mentees": 5
         }},
        
        {"email": "ms.sarah.wilson@edprep.ai", "username": "ms.sarah.wilson", "password": "tutor123", "full_name": "Ms. Sarah Wilson", "role": "tutor",
         "profile": {
             "bio": "Professional IELTS tutor with focus on Speaking and Writing improvement.",
             "teaching_experience": "7+ years of experience in IELTS tutoring.",
             "specializations": ["Speaking Fluency", "Writing Improvement"],
             "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
             "timezone": "UTC", "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "available_hours": ["09:00-17:00"], "is_available_for_mentorship": True, "max_mentees": 5
         }},
    ]

    # Create users
    created_users = 0
    created_profiles = 0
    
    for user_data in users_to_create:
        user_id = create_user(user_data["email"], user_data["username"], user_data["password"], user_data["full_name"], user_data["role"])
        if user_id:
            created_users += 1
            
            # Create profile for mentors/tutors
            if user_data["role"] in ["mentor", "tutor"] and "profile" in user_data:
                time.sleep(0.5)  # Small delay to avoid rate limiting
                if create_mentor_profile(user_data["email"], user_data["password"], user_data["profile"]):
                    created_profiles += 1

    print("-" * 60)
    print(f"📊 Recovery Results:")
    print(f"   Users created: {created_users}/{len(users_to_create)}")
    print(f"   Profiles created: {created_profiles}")
    
    # Verify everything is working
    print("\n🔍 Verifying system...")
    if verify_mentors():
        print("✅ Railway database recovery completed successfully!")
        print("\n🔑 Test Credentials:")
        print("   Student: ahmed.hassan@student.com / student123")
        print("   Mentor: dr.emma.chen@edprep.ai / mentor123")
        print("   Admin: admin@edprep.ai / admin123")
        return True
    else:
        print("❌ Recovery completed but verification failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

