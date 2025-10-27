#!/usr/bin/env python3
"""
Temporary script to add admin account creation endpoint to Railway backend
"""

import requests
import json

def create_admin_accounts_via_endpoint():
    """Create admin accounts using a temporary endpoint"""
    
    railway_url = 'https://web-production-4d7f.up.railway.app'
    
    # Admin account data
    admin_accounts = [
        {
            "email": "admin1@edprep.ai",
            "username": "admin1",
            "password": "admin123",
            "full_name": "Admin User 1",
            "role": "admin",
        },
        {
            "email": "admin2@edprep.ai",
            "username": "admin2", 
            "password": "admin123",
            "full_name": "Admin User 2",
            "role": "mentor",
        },
        {
            "email": "admin3@edprep.ai",
            "username": "admin3",
            "password": "admin123", 
            "full_name": "Admin User 3",
            "role": "tutor",
        }
    ]
    
    print("🌱 Creating admin accounts via direct database endpoint...")
    
    for account in admin_accounts:
        try:
            # Try to create via a direct database endpoint (if it exists)
            response = requests.post(f'{railway_url}/api/v1/admin/create-test-user', json=account)
            
            if response.status_code == 200:
                print(f"✅ Created {account['email']} ({account['role']})")
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
    create_admin_accounts_via_endpoint()






