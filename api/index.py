from http.server import BaseHTTPRequestHandler
import json
import time

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Add CORS headers
        self.send_cors_headers()
        
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy", 
                "service": "IELTS Master Platform", 
                "version": "2.1.2",
                "note": "Vercel + Supabase deployment - Railway removed"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/api/v1/mentorship/mentors':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
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
                "count": 1,
                "note": "Use Supabase for real mentor data"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path.startswith('/api/v1/mentorship/connections/') and '/messages' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "messages": [
                    {
                        "id": 1,
                        "connection_id": 1,
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
                    }
                ],
                "note": "Use Supabase for real messages"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path.startswith('/api/v1/mentorship/connections/'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "connection": {
                    "id": 1,
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
                },
                "note": "Use Supabase for real connections"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "note": "Use Supabase for real data"}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        # Add CORS headers
        self.send_cors_headers()
        
        if self.path == '/api/v1/auth/login':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "access_token": "fallback-token-123",
                "token_type": "bearer",
                "user": {
                    "id": 1,
                    "email": "fallback@edprep.ai",
                    "username": "fallback_user",
                    "full_name": "Fallback User",
                    "role": "student"
                },
                "note": "Use Supabase for real authentication"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path.startswith('/api/v1/mentorship/connections/') and '/messages' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "data": {
                    "id": 3,
                    "connection_id": 1,
                    "sender_id": 2,
                    "message_type": "text",
                    "content": "Test message",
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
                },
                "note": "Use Supabase for real messages"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "note": "Use Supabase for real data"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_cors_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')