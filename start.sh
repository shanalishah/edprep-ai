#!/bin/bash

# Railway startup script
echo "🚀 Starting IELTS Master Platform..."

# Navigate to backend directory
cd backend

# Start the application
echo "📱 Starting FastAPI server..."
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT