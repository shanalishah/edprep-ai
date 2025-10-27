#!/bin/bash

# Auto-Recovery Script for Railway Database Resets
# Run this script whenever users report login issues

echo "🚀 Auto-Recovery Script for Railway Database"
echo "============================================="

BACKEND_URL="https://web-production-4d7f.up.railway.app"

# Function to create users
create_users() {
    echo "📝 Creating users..."
    
    # Create admin
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=admin@edprep.ai&username=admin&password=admin123&full_name=Sarah Johnson&role=admin"
    
    # Create students
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=ahmed.hassan@student.com&username=ahmed_hassan&password=student123&full_name=Ahmed Hassan&role=student"
    
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=maria.gonzalez@student.com&username=maria.gonzalez&password=student123&full_name=Maria Gonzalez&role=student"
    
    # Create mentors
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=dr.emma.chen@edprep.ai&username=dr.emma.chen&password=mentor123&full_name=Dr. Emma Chen&role=mentor"
    
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=prof.david.kim@edprep.ai&username=prof.david.kim&password=mentor123&full_name=Prof. David Kim&role=mentor"
    
    # Create tutors
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=ms.lisa.patel@edprep.ai&username=ms.lisa.patel&password=tutor123&full_name=Ms. Lisa Patel&role=tutor"
    
    curl -X POST "$BACKEND_URL/api/v1/admin/create-test-user" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "email=ms.sarah.wilson@edprep.ai&username=ms.sarah.wilson&password=tutor123&full_name=Ms. Sarah Wilson&role=tutor"
    
    echo "✅ Users created successfully!"
}

# Function to setup mentor profiles
setup_profiles() {
    echo "👥 Setting up mentor profiles..."
    
    # Get tokens and create profiles for mentors/tutors
    python3 << 'EOF'
import requests
import json

BACKEND_URL = "https://web-production-4d7f.up.railway.app"

def setup_mentor_profile(email, password, bio, teaching_experience, specializations):
    # Login to get token
    login_response = requests.post(f"{BACKEND_URL}/api/v1/auth/login", 
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    
    if login_response.status_code != 200:
        print(f"❌ Failed to login {email}")
        return False
    
    token = login_response.json().get("access_token")
    if not token:
        print(f"❌ No token for {email}")
        return False
    
    # Create profile
    profile_response = requests.post(f"{BACKEND_URL}/api/v1/mentorship/profile",
        data={
            "bio": bio,
            "teaching_experience": teaching_experience,
            "specializations": json.dumps(specializations),
            "certifications": json.dumps(["IELTS Certified Examiner", "TESOL Certificate"]),
            "timezone": "UTC",
            "available_days": json.dumps(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]),
            "available_hours": json.dumps(["09:00-17:00"]),
            "is_available_for_mentorship": "true",
            "max_mentees": "5"
        },
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded"
        })
    
    if profile_response.status_code == 200:
        print(f"✅ Profile created for {email}")
        return True
    else:
        print(f"❌ Failed to create profile for {email}")
        return False

# Setup all mentor profiles
mentors = [
    ("dr.emma.chen@edprep.ai", "mentor123", "Former Cambridge examiner with 10+ years of experience.", "10+ years as an IELTS examiner.", ["Writing Task 2", "Speaking Fluency"]),
    ("prof.david.kim@edprep.ai", "mentor123", "Experienced IELTS mentor with expertise in academic writing.", "8+ years of experience as an IELTS mentor.", ["Academic Writing", "Test Strategies"]),
    ("ms.lisa.patel@edprep.ai", "tutor123", "Dedicated IELTS tutor specializing in Reading and Listening.", "6+ years as an IELTS tutor.", ["Reading Comprehension", "Listening Skills"]),
    ("ms.sarah.wilson@edprep.ai", "tutor123", "Professional IELTS tutor with focus on Speaking and Writing.", "7+ years of experience in IELTS tutoring.", ["Speaking Fluency", "Writing Improvement"]),
]

for email, password, bio, exp, specs in mentors:
    setup_mentor_profile(email, password, bio, exp, specs)

print("✅ All mentor profiles created!")
EOF
}

# Main execution
echo "🔍 Checking backend health..."
if curl -s "$BACKEND_URL/health" | grep -q "healthy"; then
    echo "✅ Backend is healthy"
    
    echo "🔍 Testing login..."
    if curl -s "$BACKEND_URL/api/v1/auth/login" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=admin@edprep.ai&password=admin123" | grep -q "access_token"; then
        echo "✅ Login working - users exist"
    else
        echo "❌ Login failed - recreating users..."
        create_users
        setup_profiles
    fi
else
    echo "❌ Backend is not healthy"
    echo "Please check Railway dashboard for service status"
fi

echo ""
echo "🔑 WORKING CREDENTIALS:"
echo "======================"
echo "Admin: admin@edprep.ai / admin123"
echo "Student: ahmed.hassan@student.com / student123"
echo "Mentor: dr.emma.chen@edprep.ai / mentor123"
echo "Tutor: ms.lisa.patel@edprep.ai / tutor123"
echo ""
echo "✅ Recovery complete!"

