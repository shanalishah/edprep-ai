#!/bin/bash
cd /app/backend
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT