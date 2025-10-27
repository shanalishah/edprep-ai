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
                "note": "Fallback API - Railway backend may be down"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "note": "This is a fallback API"}
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
                "note": "Fallback login - use Supabase for real authentication"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"error": "Not found", "note": "This is a fallback API"}
            self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_cors_headers()

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '86400')