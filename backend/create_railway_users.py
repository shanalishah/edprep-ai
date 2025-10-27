#!/usr/bin/env python3
"""
Script to create admin users on Railway with plain text passwords
This bypasses the bcrypt password hashing issue
"""

import requests
import json

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

def create_user(user_data):
    """Create a single user"""
    try:
        # Try the admin endpoint first
        response = requests.post(
            f"{RAILWAY_URL}/api/v1/admin/create-test-user",
            data=user_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created {user_data['email']}: {result.get('message', 'Success')}")
            return True
        else:
            print(f"❌ Failed to create {user_data['email']}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating {user_data['email']}: {e}")
        return False

def main():
    print("🚀 Creating admin users on Railway...")
    print(f"Backend URL: {RAILWAY_URL}")
    print("-" * 50)
    
    success_count = 0
    total_count = len(ADMIN_USERS)
    
    for user_data in ADMIN_USERS:
        if create_user(user_data):
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

