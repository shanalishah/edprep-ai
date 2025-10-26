# Railway Database Recovery Script

This script automatically recreates users and mentor profiles when Railway database resets.

## The Problem:
- Railway database resets during deployments
- Users and mentor profiles get deleted
- Frontend shows "no mentors found"

## The Solution:
Run this script after every Railway deployment to restore the database.

## Usage:
```bash
cd backend
python railway_recovery.py
```

## What it does:
1. Creates all user accounts (admin, students, mentors, tutors)
2. Sets up mentor/tutor profiles
3. Verifies everything is working

## Auto-run after deployments:
Add this to your Railway deployment hooks or run manually after each deployment.
