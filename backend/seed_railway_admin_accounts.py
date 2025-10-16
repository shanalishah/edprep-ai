#!/usr/bin/env python3
"""
Seed admin accounts in Railway production database
"""

import requests
import json

def seed_railway_admin_accounts():
    """Create admin accounts in Railway database"""
    
    railway_url = 'https://web-production-4d7f.up.railway.app'
    
    # Admin account data
    admin_accounts = [
        {
            "email": "admin1@edprep.ai",
            "username": "admin1",
            "password": "admin123",
            "full_name": "Admin User 1",
            "role": "admin",
            "is_verified": True,
        },
        {
            "email": "admin2@edprep.ai",
            "username": "admin2", 
            "password": "admin123",
            "full_name": "Admin User 2",
            "role": "mentor",
            "is_verified": True,
        },
        {
            "email": "admin3@edprep.ai",
            "username": "admin3",
            "password": "admin123", 
            "full_name": "Admin User 3",
            "role": "tutor",
            "is_verified": True,
        }
    ]
    
    print("🌱 Seeding admin accounts in Railway database...")
    
    for account in admin_accounts:
        try:
            # Register the user
            response = requests.post(f'{railway_url}/api/v1/auth/register', data=account)
            
            if response.status_code == 200:
                print(f"✅ Created {account['email']} ({account['role']})")
            elif response.status_code == 400 and "already exists" in response.text:
                print(f"⚠️  {account['email']} already exists")
            else:
                print(f"❌ Failed to create {account['email']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {account['email']}: {e}")
    
    print("\n🧪 Testing login with admin1...")
    
    # Test login
    login_data = {
        'username': 'admin1@edprep.ai',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{railway_url}/api/v1/auth/login', data=login_data)
        if response.status_code == 200:
            print("✅ Login test successful!")
            result = response.json()
            print(f"   Access token received: {result.get('access_token', 'N/A')[:20]}...")
        else:
            print(f"❌ Login test failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login test error: {e}")

if __name__ == "__main__":
    seed_railway_admin_accounts()
