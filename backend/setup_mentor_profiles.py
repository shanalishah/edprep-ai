import requests
import os
import json

BACKEND_URL = os.getenv("BACKEND_URL", "https://web-production-4d7f.up.railway.app")

def setup_mentor_profile(email, password, bio, teaching_experience, specializations):
    # First login to get token
    login_url = f"{BACKEND_URL}/api/v1/auth/login"
    login_payload = {
        "username": email,
        "password": password
    }
    login_response = requests.post(login_url, data=login_payload, headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login {email}")
        return False
    
    token = login_response.json().get("access_token")
    if not token:
        print(f"❌ No token for {email}")
        return False
    
    # Create mentor profile
    profile_url = f"{BACKEND_URL}/api/v1/mentorship/profile"
    profile_payload = {
        "bio": bio,
        "teaching_experience": teaching_experience,
        "specializations": json.dumps(specializations),
        "certifications": json.dumps(["IELTS Certified Examiner", "TESOL Certificate"]),
        "timezone": "UTC",
        "available_days": json.dumps(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
        "available_hours": json.dumps(["09:00-17:00"]),
        "is_available_for_mentorship": "true",
        "max_mentees": "5"
    }
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    profile_response = requests.post(profile_url, data=profile_payload, headers=headers)
    
    if profile_response.status_code == 200:
        print(f"✅ Profile created for {email}")
        return True
    else:
        print(f"❌ Failed to create profile for {email}: {profile_response.json()}")
        return False

def main():
    print("🚀 Setting up mentor/tutor profiles on Railway...")
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 50)

    mentors_to_setup = [
        ("dr.emma.chen@edprep.ai", "mentor123", "Former Cambridge examiner with 10+ years of experience. Specializes in IELTS Writing Task 2 and Speaking fluency.", "10+ years as an IELTS examiner and tutor.", ["Writing Task 2", "Speaking Fluency"]),
        ("prof.david.kim@edprep.ai", "mentor123", "Experienced IELTS mentor with expertise in academic writing and test strategies.", "8+ years of experience as an IELTS mentor.", ["Academic Writing", "Test Strategies"]),
        ("ms.lisa.patel@edprep.ai", "tutor123", "Dedicated IELTS tutor specializing in Reading and Listening comprehension.", "6+ years as an IELTS tutor.", ["Reading Comprehension", "Listening Skills"]),
        ("ms.sarah.wilson@edprep.ai", "tutor123", "Professional IELTS tutor with focus on Speaking and Writing improvement.", "7+ years of experience in IELTS tutoring.", ["Speaking Fluency", "Writing Improvement"]),
    ]

    success_count = 0
    
    for email, password, bio, teaching_experience, specializations in mentors_to_setup:
        if setup_mentor_profile(email, password, bio, teaching_experience, specializations):
            success_count += 1

    print("-" * 50)
    print(f"📊 Results: {success_count}/{len(mentors_to_setup)} mentor profiles created successfully")
    print("\n🔍 Now test the mentor search functionality!")

if __name__ == "__main__":
    main()