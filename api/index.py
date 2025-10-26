from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Vercel backend is working"}

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
                "is_available": True
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
                "content": "Hello Dr. Emma!",
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
            }
        ]
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