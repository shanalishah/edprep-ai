from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            self.send_cors_headers()
            
            if self.path == '/api/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {
                    "status": "healthy", 
                    "service": "IELTS Master Platform", 
                    "version": "2.1.2",
                    "note": "Vercel + Supabase deployment"
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
                    "count": 1
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Not found"}
                self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def do_POST(self):
        try:
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
                    }
                }
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = {"error": "Not found"}
                self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_cors_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')