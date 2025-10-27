import requests
import os

BACKEND_URL = "https://web-production-4d7f.up.railway.app"

def create_test_connection():
    # First login as Ahmed (student)
    login_url = f"{BACKEND_URL}/api/v1/auth/login"
    login_payload = {
        "username": "ahmed.hassan@student.com",
        "password": "student123"
    }
    login_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    login_response = requests.post(login_url, data=login_payload, headers=login_headers)
    
    if not login_response.ok:
        print(f"Failed to login: {login_response.json()}")
        return False
    
    token = login_response.json()["access_token"]
    print("✅ Logged in as Ahmed Hassan")
    
    # Create connection with Dr. Emma
    connection_url = f"{BACKEND_URL}/api/v1/mentorship/connections"
    connection_payload = {
        "mentor_id": "3",
        "connection_message": "Hi Dr. Emma! I would like to connect with you for IELTS preparation.",
        "goals": "Improve IELTS score,Get personalized feedback",
        "target_band_score": "7.5",
        "focus_areas": "Writing,Speaking"
    }
    connection_headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {token}"
    }
    
    connection_response = requests.post(connection_url, data=connection_payload, headers=connection_headers)
    
    if connection_response.ok:
        connection_data = connection_response.json()
        print(f"✅ Created connection with ID: {connection_data.get('connection', {}).get('id', 'Unknown')}")
        return True
    else:
        print(f"❌ Failed to create connection: {connection_response.json()}")
        return False

if __name__ == "__main__":
    print("🚀 Creating test connection...")
    create_test_connection()

