from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "IELTS Master Platform API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "IELTS Master Platform", "version": "2.1.2"}

@app.get("/api/health")
async def api_health():
    return {"status": "healthy", "service": "IELTS Master Platform", "version": "2.1.2"}

@app.get("/api/v1/mentorship/mentors")
async def get_mentors():
    return {
        "success": True,
        "mentors": [
            {
                "id": 1,
                "username": "dr.emma.chen",
                "full_name": "Dr. Emma Chen",
                "email": "dr.emma.chen@edprep.ai",
                "role": "mentor",
                "is_available": True,
                "profile": {
                    "bio": "Former Cambridge examiner with 10+ years of experience.",
                    "teaching_experience": "10+ years as an IELTS examiner and tutor.",
                    "specializations": ["Writing Task 2", "Speaking Fluency"],
                    "certifications": ["IELTS Certified Examiner", "TESOL Certificate"],
                    "timezone": "UTC",
                    "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "available_hours": ["09:00-17:00"],
                    "is_available_for_mentorship": True,
                    "max_mentees": 5,
                    "mentorship_status": "available"
                }
            }
        ],
        "count": 1
    }

@app.get("/api/v1/mentorship/connections/{connection_id}")
async def get_connection(connection_id: int):
    return {
        "connection": {
            "id": connection_id,
            "mentor_id": 1,
            "mentee_id": 2,
            "status": "active",
            "connection_message": "Test connection",
            "goals": ["Improve IELTS score"],
            "target_band_score": 7.5,
            "focus_areas": ["Writing"],
            "mentor": {
                "id": 1,
                "username": "dr.emma.chen",
                "full_name": "Dr. Emma Chen",
                "email": "dr.emma.chen@edprep.ai",
                "role": "mentor"
            },
            "mentee": {
                "id": 2,
                "username": "ahmed_hassan",
                "full_name": "Ahmed Hassan",
                "email": "ahmed.hassan@student.com",
                "role": "student"
            },
            "created_at": "2025-01-01T00:00:00"
        }
    }

@app.get("/api/v1/mentorship/connections/{connection_id}/messages")
async def get_messages(connection_id: int):
    return {
        "messages": [
            {
                "id": 1,
                "connection_id": connection_id,
                "sender_id": 2,
                "message_type": "text",
                "content": "Hello Dr. Emma! I'm excited to start our mentorship journey.",
                "is_read": False,
                "is_edited": False,
                "created_at": "2025-01-01T00:00:00",
                "sender": {
                    "id": 2,
                    "username": "ahmed_hassan",
                    "full_name": "Ahmed Hassan",
                    "email": "ahmed.hassan@student.com",
                    "role": "student"
                }
            },
            {
                "id": 2,
                "connection_id": connection_id,
                "sender_id": 1,
                "message_type": "text",
                "content": "Hello Ahmed! Welcome to our mentorship program. I'm here to help you achieve your IELTS goals.",
                "is_read": False,
                "is_edited": False,
                "created_at": "2025-01-01T00:05:00",
                "sender": {
                    "id": 1,
                    "username": "dr.emma.chen",
                    "full_name": "Dr. Emma Chen",
                    "email": "dr.emma.chen@edprep.ai",
                    "role": "mentor"
                }
            }
        ]
    }

@app.post("/api/v1/mentorship/connections/{connection_id}/messages")
async def send_message(connection_id: int, content: str, message_type: str = "text"):
    return {
        "data": {
            "id": 3,
            "connection_id": connection_id,
            "sender_id": 2,
            "message_type": message_type,
            "content": content,
            "is_read": False,
            "is_edited": False,
            "created_at": "2025-01-01T00:10:00",
            "sender": {
                "id": 2,
                "username": "ahmed_hassan",
                "full_name": "Ahmed Hassan",
                "email": "ahmed.hassan@student.com",
                "role": "student"
            }
        }
    }

@app.post("/api/v1/auth/login")
async def login(username: str, password: str):
    if username == "ahmed.hassan@student.com" and password == "student123":
        return {
            "access_token": "test-token-123",
            "token_type": "bearer",
            "user": {
                "id": 2,
                "email": "ahmed.hassan@student.com",
                "username": "ahmed_hassan",
                "full_name": "Ahmed Hassan",
                "role": "student"
            }
        }
    return {"error": "Invalid credentials"}

# Export for Vercel
handler = app