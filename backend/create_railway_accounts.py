#!/usr/bin/env python3
"""
Create Railway admin accounts with working passwords
"""

import requests

def create_railway_accounts():
    """Create admin accounts in Railway with simple passwords"""
    
    railway_url = 'https://web-production-4d7f.up.railway.app'
    
    # Admin accounts with simple passwords
    admin_accounts = [
        {
            "email": "admin1@edprep.ai",
            "username": "admin1",
            "password": "test",
            "full_name": "Admin User 1",
            "role": "admin",
        },
        {
            "email": "admin2@edprep.ai",
            "username": "admin2", 
            "password": "test",
            "full_name": "Admin User 2",
            "role": "mentor",
        },
        {
            "email": "admin3@edprep.ai",
            "username": "admin3",
            "password": "test", 
            "full_name": "Admin User 3",
            "role": "tutor",
        }
    ]
    
    print("🌱 Creating Railway admin accounts...")
    
    for account in admin_accounts:
        try:
            response = requests.post(f'{railway_url}/api/v1/admin/create-test-user', data=account)
            
            if response.status_code == 200:
                print(f"✅ Created {account['email']} ({account['role']})")
            elif "already exists" in response.text:
                print(f"⚠️  {account['email']} already exists")
            else:
                print(f"❌ Failed to create {account['email']}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error creating {account['email']}: {e}")
    
    print("\n🧪 Testing login with admin1...")
    
    # Test login with the simple password
    login_data = {
        'username': 'admin1@edprep.ai',
        'password': 'test'
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
    create_railway_accounts()





