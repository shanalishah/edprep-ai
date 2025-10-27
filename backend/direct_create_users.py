#!/usr/bin/env python3
"""
Direct database insertion script for Railway
This creates users with plain text passwords for testing
"""

import os
import sys
import requests
import json

# Add the app directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# Railway backend URL
RAILWAY_URL = "https://web-production-4d7f.up.railway.app"

# Admin users to create
ADMIN_USERS = [
    {
        "email": "admin1@edprep.ai",
        "username": "admin1", 
        "password": "test",
        "full_name": "Admin User 1",
        "role": "admin"
    },
    {
        "email": "admin2@edprep.ai",
        "username": "admin2",
        "password": "test", 
        "full_name": "Admin User 2",
        "role": "mentor"
    },
    {
        "email": "admin3@edprep.ai",
        "username": "admin3",
        "password": "test",
        "full_name": "Admin User 3", 
        "role": "tutor"
    },
    {
        "email": "admin4@edprep.ai",
        "username": "admin4",
        "password": "test",
        "full_name": "Admin User 4",
        "role": "admin"
    },
    {
        "email": "admin5@edprep.ai", 
        "username": "admin5",
        "password": "test",
        "full_name": "Admin User 5",
        "role": "mentor"
    }
]

def create_user_direct(user_data):
    """Create user by directly calling the database endpoint"""
    try:
        # Try to create user with a very simple approach
        # First, let's try to register with minimal data
        response = requests.post(
            f"{RAILWAY_URL}/api/v1/auth/register",
            data={
                "email": user_data["email"],
                "username": user_data["username"], 
                "password": user_data["password"],
                "full_name": user_data["full_name"],
                "role": user_data["role"]
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        print(f"Response for {user_data['email']}: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            print(f"✅ Created {user_data['email']}")
            return True
        else:
            print(f"❌ Failed to create {user_data['email']}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {user_data['email']}: {e}")
        return False

def main():
    print("🚀 Creating admin users on Railway (Direct Method)...")
    print(f"Backend URL: {RAILWAY_URL}")
    print("-" * 50)
    
    success_count = 0
    total_count = len(ADMIN_USERS)
    
    for user_data in ADMIN_USERS:
        if create_user_direct(user_data):
            success_count += 1
        print()
    
    print("-" * 50)
    print(f"📊 Results: {success_count}/{total_count} users created successfully")
    
    if success_count > 0:
        print("\n🎉 Test credentials:")
        for user_data in ADMIN_USERS:
            print(f"  • {user_data['email']} / {user_data['password']}")
    
    return success_count > 0

if __name__ == "__main__":
    main()

