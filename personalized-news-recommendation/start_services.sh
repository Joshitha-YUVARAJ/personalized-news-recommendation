#!/bin/bash

# Kill any existing processes on these ports
echo "Stopping any existing services..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 2

# Start backend
echo "Starting backend..."
cd /Volumes/GauravExSSD/MacFiles/AA_LAST_SEM/CareerBot/Smart-News-Recommendation-System-main
source .venv/bin/activate
export PYTHONPATH=/Volumes/GauravExSSD/MacFiles/AA_LAST_SEM/CareerBot/Smart-News-Recommendation-System-main
nohup uvicorn server.app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &

# Start frontend
echo "Starting frontend..."
cd /Volumes/GauravExSSD/MacFiles/AA_LAST_SEM/CareerBot/Smart-News-Recommendation-System-main/web
nohup npm run dev > frontend.log 2>&1 &

# Wait for services to start
echo "Waiting for services to start..."
sleep 5

# Test both services
echo "Testing services..."
echo "Backend:" $(curl -s http://localhost:8000/health 2>/dev/null || echo "FAILED")
echo "Frontend:" $(curl -s -I http://localhost:5173 2>/dev/null | head -1 || echo "FAILED")

echo "Services started! Check:"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"