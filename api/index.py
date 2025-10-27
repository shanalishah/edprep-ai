"""
Vercel Python API for IELTS Master Platform
Replicates the FastAPI backend functionality for deployment
"""

import os
import json
import sqlite3
import hashlib
import jwt
import bcrypt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs
import re

# Database setup
DB_PATH = "/tmp/ielts_master.db"

def init_database():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            is_active BOOLEAN DEFAULT 1,
            is_verified BOOLEAN DEFAULT 1,
            is_premium BOOLEAN DEFAULT 0,
            target_band_score REAL DEFAULT 7.0,
            current_level TEXT DEFAULT 'intermediate',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            total_points INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            streak_days INTEGER DEFAULT 0
        )
    ''')
    
    # Create mentorship connections table
    cursor.execute('''
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
            FOREIGN KEY (mentor_id) REFERENCES users (id),
            FOREIGN KEY (mentee_id) REFERENCES users (id)
        )
    ''')
    
    # Create mentorship messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mentorship_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            connection_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message_type TEXT DEFAULT 'text',
            content TEXT,
            file_url TEXT,
            file_name TEXT,
            file_size INTEGER,
            is_read BOOLEAN DEFAULT 0,
            read_at TIMESTAMP,
            is_edited BOOLEAN DEFAULT 0,
            edited_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (connection_id) REFERENCES mentorship_connections (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_default_users():
    """Create the 3 admin users"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if users already exist
    cursor.execute("SELECT COUNT(*) FROM users WHERE email LIKE 'admin%@edprep.ai'")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Create 3 admin users
        admin_users = [
            ('admin1@edprep.ai', 'admin1', 'Admin User 1'),
            ('admin2@edprep.ai', 'admin2', 'Admin User 2'),
            ('admin3@edprep.ai', 'admin3', 'Admin User 3')
        ]
        
        for email, username, full_name in admin_users:
            hashed_password = bcrypt.hashpw(b'test', bcrypt.gensalt()).decode('utf-8')
            cursor.execute('''
                INSERT INTO users (email, username, full_name, hashed_password, role, is_active, is_verified, is_premium, target_band_score, current_level)
                VALUES (?, ?, ?, ?, 'admin', 1, 1, 1, 8.5, 'advanced')
            ''', (email, username, full_name, hashed_password))
        
        # Create some sample connections
        cursor.execute('''
            INSERT INTO mentorship_connections (mentor_id, mentee_id, status, connection_message, goals, target_band_score, focus_areas)
            VALUES (1, 2, 'active', 'Let''s work together on IELTS preparation!', '["Improve IELTS score", "Get personalized feedback"]', 7.5, '["Writing", "Speaking"]')
        ''')
        
        # Create some sample messages
        cursor.execute('''
            INSERT INTO mentorship_messages (connection_id, sender_id, message_type, content)
            VALUES (1, 1, 'text', 'Welcome! I''m excited to help you with your IELTS preparation.'),
                   (1, 2, 'text', 'Thank you! I''m looking forward to improving my writing skills.')
        ''')
    
    conn.commit()
    conn.close()

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'email': row[1],
            'username': row[2],
            'full_name': row[3],
            'hashed_password': row[4],
            'role': row[5],
            'is_active': bool(row[6]),
            'is_verified': bool(row[7]),
            'is_premium': bool(row[8]),
            'target_band_score': row[9],
            'current_level': row[10],
            'created_at': row[11],
            'updated_at': row[12],
            'last_login': row[13],
            'total_points': row[14],
            'level': row[15],
            'streak_days': row[16]
        }
    return None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except:
        return False

def create_access_token(user_id: int) -> str:
    """Create JWT access token"""
    payload = {
        'sub': str(user_id),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, 'secret-key', algorithm='HS256')

def get_current_user(auth_header: str) -> Optional[Dict]:
    """Get current user from JWT token"""
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, 'secret-key', algorithms=['HS256'])
        user_id = int(payload['sub'])
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'user_id': row[0],
                'email': row[1],
                'username': row[2],
                'full_name': row[3],
                'role': row[5]
            }
    except:
        pass
    return None

def get_mentors() -> List[Dict]:
    """Get available mentors"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role IN ('admin', 'mentor', 'tutor') AND is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    
    mentors = []
    for row in rows:
        mentors.append({
            'id': row[0],
            'email': row[1],
            'username': row[2],
            'full_name': row[3],
            'role': row[5],
            'target_band_score': row[9],
            'current_level': row[10],
            'profile': {
                'bio': f"Experienced {row[5]} with expertise in IELTS preparation",
                'teaching_experience': "5+ years",
                'specializations': ['Writing', 'Speaking', 'Reading', 'Listening'],
                'average_rating': 4.8,
                'total_mentees_helped': 50,
                'is_available_for_mentorship': True
            }
        })
    return mentors

def get_connections(user_id: int) -> List[Dict]:
    """Get user connections"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, 
               m.email as mentor_email, m.username as mentor_username, m.full_name as mentor_name, m.role as mentor_role,
               e.email as mentee_email, e.username as mentee_username, e.full_name as mentee_name, e.role as mentee_role
        FROM mentorship_connections c
        LEFT JOIN users m ON c.mentor_id = m.id
        LEFT JOIN users e ON c.mentee_id = e.id
        WHERE c.mentor_id = ? OR c.mentee_id = ?
        ORDER BY c.created_at DESC
    ''', (user_id, user_id))
    rows = cursor.fetchall()
    conn.close()
    
    connections = []
    for row in rows:
        connections.append({
            'id': row[0],
            'mentor_id': row[1],
            'mentee_id': row[2],
            'status': row[3],
            'connection_message': row[4],
            'goals': json.loads(row[5]) if row[5] else [],
            'target_band_score': row[6],
            'focus_areas': json.loads(row[7]) if row[7] else [],
            'created_at': row[8],
            'mentor': {
                'id': row[1],
                'email': row[9],
                'username': row[10],
                'full_name': row[11],
                'role': row[12]
            },
            'mentee': {
                'id': row[2],
                'email': row[13],
                'username': row[14],
                'full_name': row[15],
                'role': row[16]
            }
        })
    return connections

def get_connection_by_id(connection_id: int, user_id: int) -> Optional[Dict]:
    """Get connection by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT c.*, 
               m.email as mentor_email, m.username as mentor_username, m.full_name as mentor_name, m.role as mentor_role,
               e.email as mentee_email, e.username as mentee_username, e.full_name as mentee_name, e.role as mentee_role
        FROM mentorship_connections c
        LEFT JOIN users m ON c.mentor_id = m.id
        LEFT JOIN users e ON c.mentee_id = e.id
        WHERE c.id = ? AND (c.mentor_id = ? OR c.mentee_id = ?)
    ''', (connection_id, user_id, user_id))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'mentor_id': row[1],
            'mentee_id': row[2],
            'status': row[3],
            'connection_message': row[4],
            'goals': json.loads(row[5]) if row[5] else [],
            'target_band_score': row[6],
            'focus_areas': json.loads(row[7]) if row[7] else [],
            'created_at': row[8],
            'mentor': {
                'id': row[1],
                'email': row[9],
                'username': row[10],
                'full_name': row[11],
                'role': row[12]
            },
            'mentee': {
                'id': row[2],
                'email': row[13],
                'username': row[14],
                'full_name': row[15],
                'role': row[16]
            }
        }
    return None

def get_messages(connection_id: int, user_id: int) -> List[Dict]:
    """Get messages for a connection"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verify user has access to this connection
    cursor.execute('''
        SELECT id FROM mentorship_connections 
        WHERE id = ? AND (mentor_id = ? OR mentee_id = ?)
    ''', (connection_id, user_id, user_id))
    
    if not cursor.fetchone():
        conn.close()
        return []
    
    cursor.execute('''
        SELECT m.*, u.email, u.username, u.full_name, u.role
        FROM mentorship_messages m
        LEFT JOIN users u ON m.sender_id = u.id
        WHERE m.connection_id = ?
        ORDER BY m.created_at ASC
    ''', (connection_id,))
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        messages.append({
            'id': row[0],
            'connection_id': row[1],
            'sender_id': row[2],
            'message_type': row[3],
            'content': row[4],
            'file_url': row[5],
            'file_name': row[6],
            'file_size': row[7],
            'is_read': bool(row[8]),
            'read_at': row[9],
            'is_edited': bool(row[10]),
            'edited_at': row[11],
            'created_at': row[12],
            'sender': {
                'id': row[2],
                'email': row[13],
                'username': row[14],
                'full_name': row[15],
                'role': row[16]
            }
        })
    return messages

def send_message(connection_id: int, sender_id: int, content: str, message_type: str = 'text') -> Dict:
    """Send a message"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verify user has access to this connection
    cursor.execute('''
        SELECT id FROM mentorship_connections 
        WHERE id = ? AND (mentor_id = ? OR mentee_id = ?)
    ''', (connection_id, sender_id, sender_id))
    
    if not cursor.fetchone():
        conn.close()
        raise ValueError("Connection not found or user not authorized")
    
    cursor.execute('''
        INSERT INTO mentorship_messages (connection_id, sender_id, message_type, content)
        VALUES (?, ?, ?, ?)
    ''', (connection_id, sender_id, message_type, content))
    
    message_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {
        'id': message_id,
        'connection_id': connection_id,
        'sender_id': sender_id,
        'message_type': message_type,
        'content': content,
        'file_url': None,
        'file_name': None,
        'file_size': None,
        'is_read': False,
        'read_at': None,
        'is_edited': False,
        'edited_at': None,
        'created_at': datetime.now().isoformat(),
        'sender': get_user_by_email(get_user_by_id(sender_id)['email'])
    }

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            'id': row[0],
            'email': row[1],
            'username': row[2],
            'full_name': row[3],
            'hashed_password': row[4],
            'role': row[5],
            'is_active': bool(row[6]),
            'is_verified': bool(row[7]),
            'is_premium': bool(row[8]),
            'target_band_score': row[9],
            'current_level': row[10],
            'created_at': row[11],
            'updated_at': row[12],
            'last_login': row[13],
            'total_points': row[14],
            'level': row[15],
            'streak_days': row[16]
        }
    return None

def handler(request):
    """Main request handler"""
    # Initialize database
    init_database()
    create_default_users()
    
    # Parse request
    method = request.get('method', 'GET')
    path = request.get('path', '')
    headers = request.get('headers', {})
    body = request.get('body', '')
    
    # CORS headers
    cors_headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }
    
    # Handle preflight requests
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': ''
        }
    
    try:
        # Route requests
        if path == '/api/v1/auth/login' and method == 'POST':
            return handle_login(body, cors_headers)
        elif path == '/api/v1/mentorship/mentors' and method == 'GET':
            return handle_get_mentors(headers, cors_headers)
        elif path == '/api/v1/mentorship/connections' and method == 'GET':
            return handle_get_connections(headers, cors_headers)
        elif path.startswith('/api/v1/mentorship/connections/') and path.endswith('/messages') and method == 'GET':
            connection_id = int(path.split('/')[-2])
            return handle_get_messages(connection_id, headers, cors_headers)
        elif path.startswith('/api/v1/mentorship/connections/') and path.endswith('/messages') and method == 'POST':
            connection_id = int(path.split('/')[-2])
            return handle_send_message(connection_id, body, headers, cors_headers)
        elif path.startswith('/api/v1/mentorship/connections/') and not path.endswith('/messages') and method == 'GET':
            connection_id = int(path.split('/')[-1])
            return handle_get_connection(connection_id, headers, cors_headers)
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'detail': 'Not found'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'detail': str(e)})
        }

def handle_login(body: str, cors_headers: Dict) -> Dict:
    """Handle login request"""
    try:
        # Parse form data
        form_data = parse_qs(body)
        username = form_data.get('username', [''])[0]
        password = form_data.get('password', [''])[0]
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'detail': 'Username and password required'})
            }
        
        # Find user
        user = get_user_by_email(username)
        if not user:
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'detail': 'Invalid email/username or password'})
            }
        
        # Verify password
        if not verify_password(password, user['hashed_password']):
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'detail': 'Invalid email/username or password'})
            }
        
        # Create token
        access_token = create_access_token(user['id'])
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'access_token': access_token,
                'token_type': 'bearer',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'is_active': user['is_active'],
                    'is_verified': user['is_verified'],
                    'is_premium': user['is_premium'],
                    'target_band_score': user['target_band_score'],
                    'current_level': user['current_level'],
                    'created_at': user['created_at'],
                    'updated_at': user['updated_at'],
                    'last_login': user['last_login'],
                    'total_points': user['total_points'],
                    'level': user['level'],
                    'streak_days': user['streak_days']
                }
            })
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'detail': str(e)})
        }

def handle_get_mentors(headers: Dict, cors_headers: Dict) -> Dict:
    """Handle get mentors request"""
    auth_header = headers.get('authorization', '')
    current_user = get_current_user(auth_header)
    
    if not current_user:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Authentication required'})
        }
    
    mentors = get_mentors()
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'mentors': mentors,
            'count': len(mentors)
        })
    }

def handle_get_connections(headers: Dict, cors_headers: Dict) -> Dict:
    """Handle get connections request"""
    auth_header = headers.get('authorization', '')
    current_user = get_current_user(auth_header)
    
    if not current_user:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Authentication required'})
        }
    
    connections = get_connections(current_user['user_id'])
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'connections': connections,
            'count': len(connections)
        })
    }

def handle_get_connection(connection_id: int, headers: Dict, cors_headers: Dict) -> Dict:
    """Handle get connection request"""
    auth_header = headers.get('authorization', '')
    current_user = get_current_user(auth_header)
    
    if not current_user:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Authentication required'})
        }
    
    connection = get_connection_by_id(connection_id, current_user['user_id'])
    
    if not connection:
        return {
            'statusCode': 404,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Connection not found'})
        }
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'connection': connection
        })
    }

def handle_get_messages(connection_id: int, headers: Dict, cors_headers: Dict) -> Dict:
    """Handle get messages request"""
    auth_header = headers.get('authorization', '')
    current_user = get_current_user(auth_header)
    
    if not current_user:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Authentication required'})
        }
    
    messages = get_messages(connection_id, current_user['user_id'])
    
    return {
        'statusCode': 200,
        'headers': cors_headers,
        'body': json.dumps({
            'success': True,
            'messages': messages
        })
    }

def handle_send_message(connection_id: int, body: str, headers: Dict, cors_headers: Dict) -> Dict:
    """Handle send message request"""
    auth_header = headers.get('authorization', '')
    current_user = get_current_user(auth_header)
    
    if not current_user:
        return {
            'statusCode': 401,
            'headers': cors_headers,
            'body': json.dumps({'detail': 'Authentication required'})
        }
    
    try:
        # Parse form data
        form_data = parse_qs(body)
        content = form_data.get('content', [''])[0]
        message_type = form_data.get('message_type', ['text'])[0]
        
        if not content:
            return {
                'statusCode': 400,
                'headers': cors_headers,
                'body': json.dumps({'detail': 'Message content required'})
            }
        
        message = send_message(connection_id, current_user['user_id'], content, message_type)
        
        return {
            'statusCode': 200,
            'headers': cors_headers,
            'body': json.dumps({
                'success': True,
                'message': 'Message sent successfully',
                'data': message
            })
        }
    
    except ValueError as e:
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'detail': str(e)})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'detail': str(e)})
        }

# Vercel handler
def vercel_handler(request):
    return handler(request)