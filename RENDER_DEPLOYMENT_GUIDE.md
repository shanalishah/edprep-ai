# Render Deployment Guide (Free Alternative)

## Why Render?
- Free PostgreSQL database (persistent)
- Free web service tier
- Better reliability than Railway free tier
- No database resets
- Always-on service

## Steps to Deploy on Render:

### 1. Backend Deployment
1. Go to https://render.com
2. Connect your GitHub repository
3. Create new "Web Service"
4. Select your repository
5. Configure:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3

### 2. Database Setup
1. Create new "PostgreSQL" service
2. Copy connection string
3. Add environment variables:
   - DATABASE_URL: (from PostgreSQL service)
   - OPENAI_API_KEY: your key
   - ANTHROPIC_API_KEY: your key

### 3. Frontend Deployment
1. Create new "Static Site"
2. Select your repository
3. Configure:
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/out`
   - Environment Variables:
     - NEXT_PUBLIC_API_URL: (your backend URL)

## Benefits:
- Free PostgreSQL database
- No database resets
- Better uptime
- Persistent storage
