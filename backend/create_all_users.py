import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "https://web-production-4d7f.up.railway.app")

def create_user(email, username, password, full_name, role):
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
        return True
    else:
        print(f"❌ Failed to create {full_name} ({email}): {user_data.get('error', user_data)}")
        return False

def main():
    print("🚀 Creating ALL users on Railway...")
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 50)

    users_to_create = [
        ("admin@edprep.ai", "admin", "admin123", "Sarah Johnson", "admin"),
        ("ahmed.hassan@student.com", "ahmed_hassan", "student123", "Ahmed Hassan", "student"),
        ("dr.emma.chen@edprep.ai", "dr.emma.chen", "mentor123", "Dr. Emma Chen", "mentor"),
        ("ms.lisa.patel@edprep.ai", "ms.lisa.patel", "tutor123", "Ms. Lisa Patel", "tutor"),
        ("maria.gonzalez@student.com", "maria.gonzalez", "student123", "Maria Gonzalez", "student"),
        ("wei.zhang@student.com", "wei.zhang", "student123", "Wei Zhang", "student"),
        ("priya.sharma@student.com", "priya.sharma", "student123", "Priya Sharma", "student"),
        ("john.smith@student.com", "john.smith", "student123", "John Smith", "student"),
        ("prof.david.kim@edprep.ai", "prof.david.kim", "mentor123", "Prof. David Kim", "mentor"),
        ("ms.sarah.wilson@edprep.ai", "ms.sarah.wilson", "tutor123", "Ms. Sarah Wilson", "tutor"),
    ]

    success_count = 0
    for user_data in users_to_create:
        if create_user(*user_data):
            success_count += 1

    print("-" * 50)
    print(f"📊 Results: {success_count}/{len(users_to_create)} users created successfully")
    print("\n🔑 ALL WORKING CREDENTIALS:")
    print("=" * 50)
    print("ADMIN ACCOUNTS:")
    print("  admin@edprep.ai / admin123")
    print("\nSTUDENT ACCOUNTS:")
    print("  ahmed.hassan@student.com / student123")
    print("  maria.gonzalez@student.com / student123")
    print("  wei.zhang@student.com / student123")
    print("  priya.sharma@student.com / student123")
    print("  john.smith@student.com / student123")
    print("\nMENTOR ACCOUNTS:")
    print("  dr.emma.chen@edprep.ai / mentor123")
    print("  prof.david.kim@edprep.ai / mentor123")
    print("\nTUTOR ACCOUNTS:")
    print("  ms.lisa.patel@edprep.ai / tutor123")
    print("  ms.sarah.wilson@edprep.ai / tutor123")
    print("=" * 50)

if __name__ == "__main__":
    main()

