"""
Simplified Vercel Python API for IELTS Master Platform
Optimized for Vercel's serverless environment
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

# In-memory database for Vercel (since SQLite doesn't persist in serverless)
USERS_DB = {}
CONNECTIONS_DB = {}
MESSAGES_DB = {}
MESSAGE_ID_COUNTER = 1

def init_database():
    """Initialize in-memory database with default users"""
    global USERS_DB, CONNECTIONS_DB, MESSAGES_DB, MESSAGE_ID_COUNTER
    
    # Create 3 admin users
    admin_users = [
        {
            'id': 1,
            'email': 'admin1@edprep.ai',
            'username': 'admin1',
            'full_name': 'Admin User 1',
            'hashed_password': bcrypt.hashpw(b'test', bcrypt.gensalt()).decode('utf-8'),
            'role': 'admin',
            'is_active': True,
            'is_verified': True,
            'is_premium': True,
            'target_band_score': 8.5,
            'current_level': 'advanced',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_login': None,
            'total_points': 0,
            'level': 1,
            'streak_days': 0
        },
        {
            'id': 2,
            'email': 'admin2@edprep.ai',
            'username': 'admin2',
            'full_name': 'Admin User 2',
            'hashed_password': bcrypt.hashpw(b'test', bcrypt.gensalt()).decode('utf-8'),
            'role': 'admin',
            'is_active': True,
            'is_verified': True,
            'is_premium': True,
            'target_band_score': 8.5,
            'current_level': 'advanced',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_login': None,
            'total_points': 0,
            'level': 1,
            'streak_days': 0
        },
        {
            'id': 3,
            'email': 'admin3@edprep.ai',
            'username': 'admin3',
            'full_name': 'Admin User 3',
            'hashed_password': bcrypt.hashpw(b'test', bcrypt.gensalt()).decode('utf-8'),
            'role': 'admin',
            'is_active': True,
            'is_verified': True,
            'is_premium': True,
            'target_band_score': 8.5,
            'current_level': 'advanced',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'last_login': None,
            'total_points': 0,
            'level': 1,
            'streak_days': 0
        }
    ]
    
    # Initialize users
    for user in admin_users:
        USERS_DB[user['id']] = user
        USERS_DB[user['email']] = user
    
    # Create sample connection
    CONNECTIONS_DB[1] = {
        'id': 1,
        'mentor_id': 1,
        'mentee_id': 2,
        'status': 'active',
        'connection_message': "Let's work together on IELTS preparation!",
        'goals': ['Improve IELTS score', 'Get personalized feedback'],
        'target_band_score': 7.5,
        'focus_areas': ['Writing', 'Speaking'],
        'created_at': datetime.now().isoformat(),
        'mentor': USERS_DB[1],
        'mentee': USERS_DB[2]
    }
    
    # Create sample messages
    MESSAGES_DB[1] = {
        'id': 1,
        'connection_id': 1,
        'sender_id': 1,
        'message_type': 'text',
        'content': 'Welcome! I\'m excited to help you with your IELTS preparation.',
        'file_url': None,
        'file_name': None,
        'file_size': None,
        'is_read': False,
        'read_at': None,
        'is_edited': False,
        'edited_at': None,
        'created_at': datetime.now().isoformat(),
        'sender': USERS_DB[1]
    }
    
    MESSAGES_DB[2] = {
        'id': 2,
        'connection_id': 1,
        'sender_id': 2,
        'message_type': 'text',
        'content': 'Thank you! I\'m looking forward to improving my writing skills.',
        'file_url': None,
        'file_name': None,
        'file_size': None,
        'is_read': False,
        'read_at': None,
        'is_edited': False,
        'edited_at': None,
        'created_at': datetime.now().isoformat(),
        'sender': USERS_DB[2]
    }
    
    MESSAGE_ID_COUNTER = 3

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    return USERS_DB.get(email)

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
        return USERS_DB.get(user_id)
    except:
        return None

def get_mentors() -> List[Dict]:
    """Get available mentors"""
    mentors = []
    for user_id, user in USERS_DB.items():
        if isinstance(user_id, int) and user.get('role') in ['admin', 'mentor', 'tutor']:
            mentors.append({
                'id': user['id'],
                'email': user['email'],
                'username': user['username'],
                'full_name': user['full_name'],
                'role': user['role'],
                'target_band_score': user['target_band_score'],
                'current_level': user['current_level'],
                'profile': {
                    'bio': f"Experienced {user['role']} with expertise in IELTS preparation",
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
    connections = []
    for conn_id, conn in CONNECTIONS_DB.items():
        if conn['mentor_id'] == user_id or conn['mentee_id'] == user_id:
            connections.append(conn)
    return connections

def get_connection_by_id(connection_id: int, user_id: int) -> Optional[Dict]:
    """Get connection by ID"""
    conn = CONNECTIONS_DB.get(connection_id)
    if conn and (conn['mentor_id'] == user_id or conn['mentee_id'] == user_id):
        return conn
    return None

def get_messages(connection_id: int, user_id: int) -> List[Dict]:
    """Get messages for a connection"""
    # Verify user has access to this connection
    conn = CONNECTIONS_DB.get(connection_id)
    if not conn or (conn['mentor_id'] != user_id and conn['mentee_id'] != user_id):
        return []
    
    messages = []
    for msg_id, msg in MESSAGES_DB.items():
        if msg['connection_id'] == connection_id:
            messages.append(msg)
    
    # Sort by created_at
    messages.sort(key=lambda x: x['created_at'])
    return messages

def send_message(connection_id: int, sender_id: int, content: str, message_type: str = 'text') -> Dict:
    """Send a message"""
    global MESSAGE_ID_COUNTER
    
    # Verify user has access to this connection
    conn = CONNECTIONS_DB.get(connection_id)
    if not conn or (conn['mentor_id'] != sender_id and conn['mentee_id'] != sender_id):
        raise ValueError("Connection not found or user not authorized")
    
    message_id = MESSAGE_ID_COUNTER
    MESSAGE_ID_COUNTER += 1
    
    message = {
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
        'sender': USERS_DB[sender_id]
    }
    
    MESSAGES_DB[message_id] = message
    return message

def handler(request):
    """Main request handler"""
    # Initialize database
    init_database()
    
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
    
    connections = get_connections(current_user['id'])
    
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
    
    connection = get_connection_by_id(connection_id, current_user['id'])
    
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
    
    messages = get_messages(connection_id, current_user['id'])
    
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
        
        message = send_message(connection_id, current_user['id'], content, message_type)
        
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