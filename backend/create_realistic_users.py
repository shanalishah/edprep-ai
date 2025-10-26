#!/usr/bin/env python3
"""
Create realistic users for the IELTS Master Platform
"""

import requests
import json
from typing import List, Dict

# Configuration
BACKEND_URL = "http://localhost:8001"

def create_user(email: str, username: str, password: str, full_name: str, role: str, 
                first_language: str = None, target_band_score: float = None, 
                current_level: str = None, learning_goals: str = None):
    """Create a user account"""
    url = f"{BACKEND_URL}/api/v1/admin/create-test-user"
    payload = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name,
        "role": role,
        "first_language": first_language,
        "target_band_score": target_band_score,
        "current_level": current_level,
        "learning_goals": learning_goals
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.status_code, response.json()

def create_mentor_profile(user_id: int, bio: str, specializations: List[str], 
                         certifications: List[str], timezone: str, 
                         available_days: List[str], available_hours: List[str]):
    """Create a mentor profile"""
    url = f"{BACKEND_URL}/api/v1/mentorship/profile"
    payload = {
        "bio": bio,
        "teaching_experience": f"{len(specializations)}+ years of IELTS teaching experience",
        "specializations": json.dumps(specializations),
        "certifications": json.dumps(certifications),
        "timezone": timezone,
        "available_days": json.dumps(available_days),
        "available_hours": json.dumps(available_hours),
        "is_available_for_mentorship": "true",
        "max_mentees": "5"
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    return response.status_code, response.json()

def main():
    print("🚀 Creating realistic users for IELTS Master Platform...")
    print(f"Backend URL: {BACKEND_URL}")
    print("-" * 60)

    # Define realistic users
    users_to_create = [
        # Administrators
        {
            "email": "admin@edprep.ai",
            "username": "admin",
            "password": "admin123",
            "full_name": "Sarah Johnson",
            "role": "admin",
            "first_language": "English",
            "target_band_score": 9.0,
            "current_level": "expert",
            "learning_goals": "Platform management and user support"
        },
        
        # IELTS Mentors/Tutors
        {
            "email": "dr.emma.chen@edprep.ai",
            "username": "emma_chen",
            "password": "mentor123",
            "full_name": "Dr. Emma Chen",
            "role": "mentor",
            "first_language": "English",
            "target_band_score": 9.0,
            "current_level": "expert",
            "learning_goals": "Help students achieve their target scores"
        },
        {
            "email": "prof.michael.rodriguez@edprep.ai",
            "username": "michael_rodriguez",
            "password": "mentor123",
            "full_name": "Prof. Michael Rodriguez",
            "role": "mentor",
            "first_language": "English",
            "target_band_score": 8.5,
            "current_level": "advanced",
            "learning_goals": "Specialized in Writing and Speaking"
        },
        {
            "email": "ms.lisa.patel@edprep.ai",
            "username": "lisa_patel",
            "password": "tutor123",
            "full_name": "Ms. Lisa Patel",
            "role": "tutor",
            "first_language": "English",
            "target_band_score": 8.0,
            "current_level": "advanced",
            "learning_goals": "Focus on Reading and Listening strategies"
        },
        {
            "email": "mr.james.kim@edprep.ai",
            "username": "james_kim",
            "password": "tutor123",
            "full_name": "Mr. James Kim",
            "role": "tutor",
            "first_language": "English",
            "target_band_score": 8.5,
            "current_level": "advanced",
            "learning_goals": "Academic Writing specialist"
        },
        
        # Students/Mentees
        {
            "email": "ahmed.hassan@student.com",
            "username": "ahmed_hassan",
            "password": "student123",
            "full_name": "Ahmed Hassan",
            "role": "student",
            "first_language": "Arabic",
            "target_band_score": 7.0,
            "current_level": "intermediate",
            "learning_goals": "Improve Writing Task 2 and Speaking fluency"
        },
        {
            "email": "maria.gonzalez@student.com",
            "username": "maria_gonzalez",
            "password": "student123",
            "full_name": "Maria Gonzalez",
            "role": "student",
            "first_language": "Spanish",
            "target_band_score": 6.5,
            "current_level": "intermediate",
            "learning_goals": "Achieve band 7 for university admission"
        },
        {
            "email": "wei.zhang@student.com",
            "username": "wei_zhang",
            "password": "student123",
            "full_name": "Wei Zhang",
            "role": "student",
            "first_language": "Mandarin",
            "target_band_score": 7.5,
            "current_level": "upper-intermediate",
            "learning_goals": "Focus on Academic Writing and Reading"
        },
        {
            "email": "priya.sharma@student.com",
            "username": "priya_sharma",
            "password": "student123",
            "full_name": "Priya Sharma",
            "role": "student",
            "first_language": "Hindi",
            "target_band_score": 8.0,
            "current_level": "advanced",
            "learning_goals": "Perfect all four skills for immigration"
        },
        {
            "email": "john.smith@student.com",
            "username": "john_smith",
            "password": "student123",
            "full_name": "John Smith",
            "role": "student",
            "first_language": "English",
            "target_band_score": 6.0,
            "current_level": "intermediate",
            "learning_goals": "Improve overall IELTS performance"
        }
    ]

    # Mentor profiles data
    mentor_profiles = [
        {
            "user_id": 2,  # Dr. Emma Chen
            "bio": "Experienced IELTS examiner with 8+ years of teaching experience. Specialized in helping students achieve band 7+ scores. Former Cambridge English examiner.",
            "specializations": ["Writing Task 2", "Speaking Fluency", "Academic Writing"],
            "certifications": ["Cambridge CELTA", "IELTS Examiner Certification", "TESOL Advanced"],
            "timezone": "UTC+8",
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "available_hours": ["09:00-12:00", "14:00-17:00", "19:00-21:00"]
        },
        {
            "user_id": 3,  # Prof. Michael Rodriguez
            "bio": "IELTS specialist focusing on Writing and Speaking strategies. Uses data-driven approaches to help students improve their performance.",
            "specializations": ["Writing Task 1", "Writing Task 2", "Speaking Part 2", "Speaking Part 3"],
            "certifications": ["IELTS Teacher Training Certificate", "Cambridge Assessment English"],
            "timezone": "UTC-5",
            "available_days": ["Tuesday", "Thursday", "Sunday"],
            "available_hours": ["10:00-13:00", "15:00-18:00", "20:00-22:00"]
        },
        {
            "user_id": 4,  # Ms. Lisa Patel
            "bio": "Reading and Listening specialist with expertise in test-taking strategies. Helps students improve comprehension and time management.",
            "specializations": ["Reading Strategies", "Listening Techniques", "Test Preparation"],
            "certifications": ["IELTS Teacher Training Certificate", "English Teaching License"],
            "timezone": "UTC+5:30",
            "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "available_hours": ["morning", "afternoon", "evening"]
        },
        {
            "user_id": 5,  # Mr. James Kim
            "bio": "Academic Writing specialist with focus on Task 1 and Task 2. Helps students develop strong arguments and improve coherence.",
            "specializations": ["Academic Writing", "Task 1 Reports", "Task 2 Essays", "Grammar"],
            "certifications": ["IELTS Tutor Certificate", "Academic Writing Certificate"],
            "timezone": "UTC+9",
            "available_days": ["Monday", "Wednesday", "Friday", "Saturday"],
            "available_hours": ["afternoon", "evening"]
        }
    ]

    # Create users
    success_count = 0
    for user_data in users_to_create:
        status_code, response_data = create_user(**user_data)
        if status_code == 200 and response_data.get("message"):
            print(f"✅ Created {user_data['full_name']} ({user_data['role']}): {user_data['email']}")
            success_count += 1
        else:
            print(f"❌ Failed to create {user_data['full_name']}: {response_data.get('error', response_data)}")
        print("")

    print("-" * 60)
    print(f"📊 User Creation Results: {success_count}/{len(users_to_create)} users created successfully")
    
    # Note: Mentor profiles will be created when mentors log in and set up their profiles
    print("\n🎯 Next Steps:")
    print("1. Mentors should log in and complete their profiles")
    print("2. Students can now search for mentors")
    print("3. All users have realistic names and backgrounds")
    
    print("\n🔑 Login Credentials:")
    print("Admin: admin@edprep.ai / admin123")
    print("Mentors: [email] / mentor123")
    print("Tutors: [email] / tutor123") 
    print("Students: [email] / student123")

if __name__ == "__main__":
    main()
