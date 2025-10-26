from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import sqlite3
import hashlib
import jwt
import os
from datetime import datetime, timedelta
from typing import List, Optional
import json

# Initialize FastAPI app
app = FastAPI(title="IELTS Master Platform API", version="2.1.2")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ielts_master.db")

# Pydantic models
class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ConnectionResponse(BaseModel):
    id: int
    mentor_id: int
    mentee_id: int
    status: str
    connection_message: str
    goals: List[str]
    target_band_score: float
    focus_areas: List[str]
    mentor: UserResponse
    mentee: UserResponse
    created_at: str

class MessageResponse(BaseModel):
    id: int
    connection_id: int
    sender_id: int
    message_type: str
    content: str
    is_read: bool
    is_edited: bool
    created_at: str
    sender: Optional[UserResponse] = None

# Database functions
def get_db():
    conn = sqlite3.connect("ielts_master.db")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    conn = sqlite3.connect("ielts_master.db")
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            is_premium BOOLEAN DEFAULT FALSE,
            first_language TEXT,
            target_band_score REAL,
            current_level TEXT DEFAULT 'beginner',
            learning_goals TEXT,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0,
            preferred_ai_role TEXT,
            notification_preferences TEXT
        )
    """)
    
    # Create mentorship_connections table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentorship_connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mentor_id INTEGER NOT NULL,
            mentee_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            connection_message TEXT,
            goals TEXT,
            target_band_score REAL,
            focus_areas TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (mentor_id) REFERENCES users (id),
            FOREIGN KEY (mentee_id) REFERENCES users (id)
        )
    """)
    
    # Create mentorship_messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mentorship_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connection_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message_type TEXT DEFAULT 'text',
            content TEXT NOT NULL,
            file_url TEXT,
            file_name TEXT,
            file_size INTEGER,
            is_read BOOLEAN DEFAULT FALSE,
            read_at TIMESTAMP,
            is_edited BOOLEAN DEFAULT FALSE,
            edited_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (connection_id) REFERENCES mentorship_connections (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    """)
    
    # Create user_profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            bio TEXT,
            teaching_experience TEXT,
            specializations TEXT,
            certifications TEXT,
            timezone TEXT DEFAULT 'UTC',
            available_days TEXT,
            available_hours TEXT,
            is_available_for_mentorship BOOLEAN DEFAULT FALSE,
            max_mentees INTEGER DEFAULT 5,
            mentorship_status TEXT DEFAULT 'available',
            profile_image_url TEXT,
            social_links TEXT,
            total_mentees_helped INTEGER DEFAULT 0,
            average_rating REAL DEFAULT 0.0,
            total_sessions_conducted INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Initialize database on startup
init_database()

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IELTS Master Platform",
        "version": "2.1.2",
        "multi_agent_engine_loaded": True,
        "ai_feedback_available": True
    }

# Auth endpoints
@app.post("/api/v1/auth/login", response_model=LoginResponse)
async def login(user_data: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ? OR username = ?", (user_data.username, user_data.username))
    user = cursor.fetchone()
    
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email/username or password")
    
    # Update last login
    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
    db.commit()
    
    # Create token
    access_token = create_access_token(data={"sub": str(user["id"])})
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"]
        )
    )

# Mentorship endpoints
@app.get("/api/v1/mentorship/mentors")
async def get_mentors(current_user: int = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT u.*, up.* FROM users u
        LEFT JOIN user_profiles up ON u.id = up.user_id
        WHERE u.role IN ('mentor', 'tutor') AND up.is_available_for_mentorship = 1
    """)
    mentors = cursor.fetchall()
    
    mentor_list = []
    for mentor in mentors:
        mentor_data = {
            "id": mentor["id"],
            "username": mentor["username"],
            "full_name": mentor["full_name"],
            "email": mentor["email"],
            "role": mentor["role"],
            "target_band_score": mentor["target_band_score"],
            "current_level": mentor["current_level"],
            "profile": {
                "id": mentor["user_id"],
                "user_id": mentor["user_id"],
                "is_available_for_mentorship": mentor["is_available_for_mentorship"],
                "mentorship_status": mentor["mentorship_status"],
                "max_mentees": mentor["max_mentees"],
                "bio": mentor["bio"],
                "teaching_experience": mentor["teaching_experience"],
                "specializations": json.loads(mentor["specializations"]) if mentor["specializations"] else [],
                "certifications": json.loads(mentor["certifications"]) if mentor["certifications"] else [],
                "timezone": mentor["timezone"],
                "available_days": json.loads(mentor["available_days"]) if mentor["available_days"] else [],
                "available_hours": json.loads(mentor["available_hours"]) if mentor["available_hours"] else [],
                "profile_image_url": mentor["profile_image_url"],
                "social_links": mentor["social_links"],
                "total_mentees_helped": mentor["total_mentees_helped"],
                "average_rating": mentor["average_rating"],
                "total_sessions_conducted": mentor["total_sessions_conducted"],
                "created_at": mentor["created_at"],
                "updated_at": mentor["updated_at"]
            },
            "is_available": True
        }
        mentor_list.append(mentor_data)
    
    return {"success": True, "mentors": mentor_list, "count": len(mentor_list)}

@app.get("/api/v1/mentorship/connections/{connection_id}", response_model=ConnectionResponse)
async def get_connection(connection_id: int, current_user: int = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT mc.*, 
               mentor.id as mentor_id, mentor.email as mentor_email, mentor.username as mentor_username, mentor.full_name as mentor_full_name, mentor.role as mentor_role,
               mentee.id as mentee_id, mentee.email as mentee_email, mentee.username as mentee_username, mentee.full_name as mentee_full_name, mentee.role as mentee_role
        FROM mentorship_connections mc
        JOIN users mentor ON mc.mentor_id = mentor.id
        JOIN users mentee ON mc.mentee_id = mentee.id
        WHERE mc.id = ? AND (mc.mentor_id = ? OR mc.mentee_id = ?)
    """, (connection_id, current_user, current_user))
    
    connection = cursor.fetchone()
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return ConnectionResponse(
        id=connection["id"],
        mentor_id=connection["mentor_id"],
        mentee_id=connection["mentee_id"],
        status=connection["status"],
        connection_message=connection["connection_message"],
        goals=json.loads(connection["goals"]) if connection["goals"] else [],
        target_band_score=connection["target_band_score"],
        focus_areas=json.loads(connection["focus_areas"]) if connection["focus_areas"] else [],
        mentor=UserResponse(
            id=connection["mentor_id"],
            email=connection["mentor_email"],
            username=connection["mentor_username"],
            full_name=connection["mentor_full_name"],
            role=connection["mentor_role"]
        ),
        mentee=UserResponse(
            id=connection["mentee_id"],
            email=connection["mentee_email"],
            username=connection["mentee_username"],
            full_name=connection["mentee_full_name"],
            role=connection["mentee_role"]
        ),
        created_at=connection["created_at"]
    )

@app.get("/api/v1/mentorship/connections/{connection_id}/messages")
async def get_messages(connection_id: int, current_user: int = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT mm.*, u.email, u.username, u.full_name, u.role
        FROM mentorship_messages mm
        JOIN users u ON mm.sender_id = u.id
        WHERE mm.connection_id = ? AND (mm.connection_id IN (
            SELECT id FROM mentorship_connections WHERE mentor_id = ? OR mentee_id = ?
        ))
        ORDER BY mm.created_at ASC
    """, (connection_id, current_user, current_user))
    
    messages = cursor.fetchall()
    message_list = []
    for msg in messages:
        message_data = {
            "id": msg["id"],
            "connection_id": msg["connection_id"],
            "sender_id": msg["sender_id"],
            "message_type": msg["message_type"],
            "content": msg["content"],
            "file_url": msg["file_url"],
            "file_name": msg["file_name"],
            "file_size": msg["file_size"],
            "is_read": msg["is_read"],
            "read_at": msg["read_at"],
            "is_edited": msg["is_edited"],
            "edited_at": msg["edited_at"],
            "created_at": msg["created_at"],
            "sender": {
                "id": msg["sender_id"],
                "email": msg["email"],
                "username": msg["username"],
                "full_name": msg["full_name"],
                "role": msg["role"]
            }
        }
        message_list.append(message_data)
    
    return {"messages": message_list}

@app.post("/api/v1/mentorship/connections/{connection_id}/messages")
async def send_message(connection_id: int, content: str, message_type: str = "text", current_user: int = Depends(get_current_user), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Verify connection exists and user has access
    cursor.execute("""
        SELECT id FROM mentorship_connections 
        WHERE id = ? AND (mentor_id = ? OR mentee_id = ?)
    """, (connection_id, current_user, current_user))
    
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Connection not found")
    
    # Insert message
    cursor.execute("""
        INSERT INTO mentorship_messages (connection_id, sender_id, message_type, content)
        VALUES (?, ?, ?, ?)
    """, (connection_id, current_user, message_type, content))
    
    message_id = cursor.lastrowid
    db.commit()
    
    # Get the created message
    cursor.execute("""
        SELECT mm.*, u.email, u.username, u.full_name, u.role
        FROM mentorship_messages mm
        JOIN users u ON mm.sender_id = u.id
        WHERE mm.id = ?
    """, (message_id,))
    
    msg = cursor.fetchone()
    message_data = {
        "id": msg["id"],
        "connection_id": msg["connection_id"],
        "sender_id": msg["sender_id"],
        "message_type": msg["message_type"],
        "content": msg["content"],
        "file_url": msg["file_url"],
        "file_name": msg["file_name"],
        "file_size": msg["file_size"],
        "is_read": msg["is_read"],
        "read_at": msg["read_at"],
        "is_edited": msg["is_edited"],
        "edited_at": msg["edited_at"],
        "created_at": msg["created_at"],
        "sender": {
            "id": msg["sender_id"],
            "email": msg["email"],
            "username": msg["username"],
            "full_name": msg["full_name"],
            "role": msg["role"]
        }
    }
    
    return {"data": message_data}

# Admin endpoint for creating test users
@app.post("/api/v1/admin/create-test-user")
async def create_test_user(email: str, username: str, password: str, full_name: str, role: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (email, username))
    if cursor.fetchone():
        return {"message": f"User {email} already exists", "status": "exists"}
    
    # Create user
    password_hash = hash_password(password)
    cursor.execute("""
        INSERT INTO users (email, username, password_hash, full_name, role)
        VALUES (?, ?, ?, ?, ?)
    """, (email, username, password_hash, full_name, role))
    
    user_id = cursor.lastrowid
    db.commit()
    
    return {"message": f"Test user {email} created successfully", "user_id": user_id, "role": role, "password": password}

# Export for Vercel
handler = app
