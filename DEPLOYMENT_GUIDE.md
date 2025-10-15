# Vercel Deployment Guide

## Overview
This guide will help you deploy your IELTS Master Platform to Vercel for cloud development and production use.

## Prerequisites
- GitHub repository (✅ Already set up: https://github.com/shanalishah/edprep-ai)
- Vercel account (free tier available)
- Backend API deployed separately (Railway, Render, or similar)

## Step 1: Deploy Backend First

Since Vercel is primarily for frontend deployment, you'll need to deploy your backend separately:

### Option A: Railway (Recommended)
1. Go to [Railway.app](https://railway.app)
2. Connect your GitHub account
3. Create new project from GitHub repo
4. Select your repository
5. Railway will auto-detect the Python backend
6. Add environment variables from `backend/env.example`
7. Deploy and get your backend URL

### Option B: Render
1. Go to [Render.com](https://render.com)
2. Connect GitHub and create new Web Service
3. Select your repository
4. Configure:
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
5. Add environment variables
6. Deploy

### Option C: Heroku
1. Create Heroku app
2. Connect GitHub repository
3. Add Python buildpack
4. Configure Procfile: `web: cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

## Step 2: Deploy Frontend to Vercel

### Method 1: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to your project
cd ielts-master-platform

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? (your account)
# - Link to existing project? N
# - Project name: ielts-master-platform
# - Directory: ./frontend
# - Override settings? N
```

### Method 2: Vercel Dashboard
1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import from GitHub
4. Select your repository: `shanalishah/edprep-ai`
5. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
6. Add Environment Variables (see below)
7. Deploy

## Step 3: Environment Variables

Add these environment variables in Vercel:

### Required Variables
```
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Optional Variables
```
NEXT_PUBLIC_APP_NAME=IELTS Master Platform
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=production
```

## Step 4: Configure Backend CORS

Update your backend CORS settings to allow your Vercel domain:

In `backend/app/main.py`, update:
```python
BACKEND_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "https://your-app-name.vercel.app",  # Add your Vercel URL
    "https://*.vercel.app",  # Allow all Vercel preview deployments
]
```

## Step 5: GitHub Integration

### Automatic Deployments
1. In Vercel dashboard, go to your project
2. Go to Settings → Git
3. Enable "Automatic deployments"
4. Now every push to main branch will auto-deploy

### Preview Deployments
- Every pull request gets a preview deployment
- Perfect for testing changes before merging

## Step 6: Custom Domain (Optional)

1. In Vercel dashboard, go to Settings → Domains
2. Add your custom domain
3. Configure DNS records as instructed
4. SSL certificate is automatically provisioned

## Step 7: Monitoring & Analytics

### Vercel Analytics
1. Go to Analytics tab in Vercel dashboard
2. Enable Web Analytics
3. Monitor performance and user behavior

### Error Monitoring
Consider adding Sentry or similar for error tracking:
```bash
npm install @sentry/nextjs
```

## Troubleshooting

### Build Failures
- Check build logs in Vercel dashboard
- Ensure all dependencies are in `package.json`
- Verify environment variables are set

### API Connection Issues
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check CORS settings in backend
- Ensure backend is accessible from internet

### Performance Issues
- Enable Vercel's Edge Functions
- Optimize images with Next.js Image component
- Use Vercel's CDN for static assets

## Production Checklist

- [ ] Backend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS settings updated
- [ ] Custom domain configured (optional)
- [ ] Analytics enabled
- [ ] Error monitoring set up
- [ ] SSL certificate active
- [ ] Performance optimized

## Cost Considerations

### Vercel Free Tier
- 100GB bandwidth/month
- Unlimited personal projects
- Automatic HTTPS
- Global CDN

### Backend Hosting
- **Railway**: $5/month after free tier
- **Render**: Free tier available, $7/month for paid
- **Heroku**: $7/month for basic dyno

## Next Steps

1. **Deploy backend** to Railway/Render/Heroku
2. **Deploy frontend** to Vercel
3. **Test the full application**
4. **Set up monitoring**
5. **Configure custom domain**
6. **Enable analytics**

## Support

- [Vercel Documentation](https://vercel.com/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
