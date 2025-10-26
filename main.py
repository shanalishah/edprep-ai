#!/usr/bin/env python3
"""
IELTS Master Platform - Railway Deployment Entry Point
This file helps Railway detect this as a Python project and redirects to the backend.
"""

import os
import sys
import subprocess

def main():
    """Main entry point for Railway deployment"""
    # Change to backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Start the FastAPI application
    cmd = [
        sys.executable, '-m', 'uvicorn', 
        'app.main:app', 
        '--host', '0.0.0.0', 
        '--port', os.environ.get('PORT', '8000')
    ]
    
    print(f"Starting IELTS Master Platform backend...")
    print(f"Command: {' '.join(cmd)}")
    
    subprocess.run(cmd)

if __name__ == "__main__":
    main()

