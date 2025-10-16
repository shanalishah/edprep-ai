#!/usr/bin/env python3
"""
Script to set up mentor profiles for Railway deployment
"""

import requests
import os
import json

# Railway URL
RAILWAY_URL = "https://web-production-4d7f.up.railway.app"

def setup_mentor_profiles():
    """Set up mentor profiles for Railway deployment"""
    
    # First, login as admin1 to get a token
    login_data = {
        "username": "admin1@edprep.ai",
        "password": "test"
    }
    
    print("🔐 Logging in as admin1...")
    login_response = requests.post(f'{RAILWAY_URL}/api/v1/auth/login', data=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code} - {login_response.text}")
        return
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("✅ Login successful!")
    
    # Set up mentor profiles for admin2 and admin3
    mentor_profiles = [
        {
            "user_id": 2,  # admin2
            "is_available_for_mentorship": True,
            "mentorship_status": "available",
            "max_mentees": 3,
            "bio": "Professional IELTS mentor specializing in writing and speaking. I provide comprehensive support to help students excel in all IELTS components.",
            "teaching_experience": "5+ years of IELTS mentoring experience",
            "specializations": ["Writing", "Speaking", "Listening", "Reading"],
            "certifications": ["IELTS Mentor Certificate", "English Teaching License"],
            "timezone": "UTC+8",
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "available_hours": ["afternoon", "evening"]
        },
        {
            "user_id": 3,  # admin3
            "is_available_for_mentorship": True,
            "mentorship_status": "available",
            "max_mentees": 2,
            "bio": "Experienced IELTS tutor with expertise in academic writing and test strategies. I help students achieve their target band scores.",
            "teaching_experience": "3+ years of IELTS tutoring experience",
            "specializations": ["Writing", "Reading", "Test Strategies"],
            "certifications": ["IELTS Tutor Certificate", "TESOL Certificate"],
            "timezone": "UTC+5",
            "available_days": ["Tuesday", "Thursday", "Sunday"],
            "available_hours": ["morning", "afternoon"]
        }
    ]
    
    for profile_data in mentor_profiles:
        print(f"👨‍🏫 Setting up mentor profile for user {profile_data['user_id']}...")
        
        # Create mentor profile using Form data
        form_data = {
            "bio": profile_data["bio"],
            "teaching_experience": profile_data["teaching_experience"],
            "specializations": json.dumps(profile_data["specializations"]),
            "certifications": json.dumps(profile_data["certifications"]),
            "timezone": profile_data["timezone"],
            "available_days": json.dumps(profile_data["available_days"]),
            "available_hours": json.dumps(profile_data["available_hours"]),
            "is_available_for_mentorship": profile_data["is_available_for_mentorship"],
            "max_mentees": profile_data["max_mentees"]
        }
        
        response = requests.post(
            f'{RAILWAY_URL}/api/v1/mentorship/profile',
            data=form_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ Mentor profile created successfully for user {profile_data['user_id']}")
        else:
            print(f"❌ Failed to create mentor profile: {response.status_code} - {response.text}")
    
    # Test the mentors endpoint
    print("\n🧪 Testing mentors endpoint...")
    mentors_response = requests.get(f'{RAILWAY_URL}/api/v1/mentorship/mentors', headers=headers)
    
    if mentors_response.status_code == 200:
        mentors_data = mentors_response.json()
        print(f"✅ Found {mentors_data['count']} mentors available")
        for mentor in mentors_data['mentors']:
            print(f"   - {mentor['full_name']} ({mentor['role']})")
    else:
        print(f"❌ Failed to get mentors: {mentors_response.status_code} - {mentors_response.text}")

if __name__ == "__main__":
    setup_mentor_profiles()
