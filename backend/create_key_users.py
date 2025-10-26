import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "https://web-production-4d7f.up.railway.app")

def create_user(email, username, password, full_name, role, bio=None, teaching_experience=None, specializations=None, certifications=None, timezone=None, available_days=None, available_hours=None, is_available_for_mentorship=False, max_mentees=3):
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
        user_id = user_data["user_id"]
        
        if role in ["mentor", "tutor"]:
            profile_url = f"{BACKEND_URL}/api/v1/mentorship/profile"
            profile_payload = {
                "bio": bio or "No profile set up yet",
                "teaching_experience": teaching_experience or "Profile not completed",
                "specializations": json.dumps(specializations or []),
                "certifications": json.dumps(certifications or []),
                "timezone": timezone or "UTC",
                "available_days": json.dumps(available_days or []),
                "available_hours": json.dumps(available_hours or []),
                "is_available_for_mentorship": str(is_available_for_mentorship),
                "max_mentees": str(max_mentees)
            }
            # This part would ideally need an admin token or the user's own token
            # For this temporary script, we're assuming the admin endpoint handles it
            profile_response = requests.post(profile_url, data=profile_payload, headers=headers)
            if profile_response.status_code == 200:
                print(f"   - Profile created/updated for {full_name}")
            else:
                print(f"   - Failed to create/update profile for {full_name}: {profile_response.json()}")
        return True
    else:
        print(f"❌ Failed to create {full_name} ({email}): {user_data.get('error', user_data)}")
        return False

def main():
    print("🚀 Creating key users on Railway...")
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
    ]

    success_count = 0
    for user_data in users_to_create:
        if create_user(*user_data):
            success_count += 1

    print("-" * 50)
    print(f"📊 Results: {success_count}/{len(users_to_create)} users created successfully")
    print("\n🔑 Test Credentials:")
    print("Admin: admin@edprep.ai / admin123")
    print("Students: [email] / student123")
    print("Mentors: [email] / mentor123")
    print("Tutors: [email] / tutor123")

if __name__ == "__main__":
    main()
