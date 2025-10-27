#!/bin/bash

# Railway Deployment Hook - Permanent Stability Fix
# This script runs automatically after every Railway deployment

echo "🚀 Railway Deployment Hook - Starting Permanent Stability Fix"
echo "=============================================================="

# Navigate to backend directory
cd /app/backend

# Wait for application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Run the permanent stability fix
echo "🔧 Running permanent stability fix..."
python permanent_stability_fix.py

# Check if fix was successful
if [ $? -eq 0 ]; then
    echo "✅ Permanent stability fix completed successfully!"
    echo "📱 Your application is now stable and ready to use."
else
    echo "❌ Permanent stability fix failed!"
    echo "🔄 Retrying in 30 seconds..."
    sleep 30
    python permanent_stability_fix.py
fi

echo "=============================================================="
echo "🏁 Railway Deployment Hook completed"

