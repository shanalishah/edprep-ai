#!/usr/bin/env python3
"""
Vercel Database Population Script
Creates test users and mentor profiles for Vercel deployment
"""

import requests
import os
import json
import time

# Use the deployed Vercel URL
API_URL = os.getenv("API_URL", "https://edprep-ai.vercel.app")

def create_user(email, username, password, full_name, role):
    """Create a user account"""
    url = f"{API_URL}/api/v1/admin/create-test-user"
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
    
    try:
        response = requests.post(url, data=payload, headers=headers, timeout=30)
        user_data = response.json()

        if response.status_code == 200 and user_data.get("user_id"):
            print(f"✅ Created {full_name} ({role}): {email}")
            return user_data["user_id"]
        else:
            print(f"❌ Failed to create {full_name} ({email}): {user_data.get('error', user_data)}")
            return None
    except Exception as e:
        print(f"❌ Error creating {full_name}: {e}")
        return None

def main():
    """Create all test users"""
    print("🚀 Creating test users for Vercel deployment...")
    print(f"API URL: {API_URL}")
    print("-" * 50)
    
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
        user_id = create_user(**user_data)
        if user_id:
            created_count += 1
        time.sleep(0.5)  # Small delay
    
    print("-" * 50)
    print(f"📊 Results: {created_count}/{len(users)} users created successfully")
    print("\n🔑 Test Credentials:")
    print("   Student: ahmed.hassan@student.com / student123")
    print("   Mentor: dr.emma.chen@edprep.ai / mentor123")
    print("   Admin: admin@edprep.ai / admin123")
    print("\n📱 Your Vercel-only app is ready!")

if __name__ == "__main__":
    main()

