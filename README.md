# IELTS Master Platform - WIP

### Frontend (Vercel)
```bash
cd frontend
npm install
npm run dev
```

### Backend (Railway)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Project Structure

```
ielts-master-platform/
├── frontend/          # Next.js frontend (Vercel)
│   ├── src/
│   │   ├── app/       # App router with API routes
│   │   ├── lib/       # Centralized imports
│   │   └── data/      # Shared data store
│   └── package.json
├── backend/           # FastAPI backend (Railway)
│   ├── app/
│   │   ├── main.py    # FastAPI application
│   │   ├── models/    # Database models
│   │   └── services/  # Business logic
│   └── requirements.txt
├── vercel.json        # Vercel configuration
├── railway.toml       # Railway configuration
└── .gitignore
```

## Deployment

- **Frontend**: Deploy to Vercel (automatic from GitHub)
- **Backend**: Deploy to Railway (automatic from GitHub)
