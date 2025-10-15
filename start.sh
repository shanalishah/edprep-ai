#!/bin/bash

# IELTS Master Platform Startup Script
# This script starts both the backend and frontend servers

set -e

echo "🚀 Starting IELTS Master Platform..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    print_error "Please run this script from the IELTS Master Platform root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
if check_port 8000; then
    print_warning "Port 8000 is already in use. Backend may already be running."
fi

if check_port 3000; then
    print_warning "Port 3000 is already in use. Frontend may already be running."
fi

# Start Backend
print_status "Starting FastAPI backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install --upgrade setuptools wheel

# Try minimal requirements first, fallback to full requirements
if [ -f "requirements-minimal.txt" ]; then
    print_status "Installing minimal requirements first..."
    pip install -r requirements-minimal.txt
else
    print_status "Installing full requirements..."
    pip install -r requirements.txt
fi

# Start backend server
print_status "Starting backend server on http://localhost:8000"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Go back to root directory
cd ..

# Start Frontend
print_status "Starting Next.js frontend server..."
cd frontend

# Install dependencies
print_status "Installing Node.js dependencies..."
npm install

# Start frontend server
print_status "Starting frontend server on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 3

# Go back to root directory
cd ..

# Display status
echo ""
print_success "🎉 IELTS Master Platform is now running!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    print_success "Servers stopped successfully"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop the servers
wait
