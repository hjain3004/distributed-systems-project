#!/bin/bash

# Distributed Systems Performance Modeling - Startup Script
# This script starts both the backend and frontend servers

echo "🚀 Starting Distributed Systems Performance Modeling..."
echo ""

# Kill any existing processes on these ports
echo "Cleaning up old processes..."
pkill -f "python.*simple_main" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# Start backend
echo "Starting backend on port 3001..."
nohup python3 backend/simple_main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 2

# Check if backend started
if curl -s http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:3001"
else
    echo "❌ Backend failed to start. Check /tmp/backend.log"
    exit 1
fi

# Start frontend
echo "Starting frontend on port 4000..."
cd frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 4

# Check if frontend started
if curl -s http://localhost:4000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on http://localhost:4000"
else
    echo "❌ Frontend failed to start. Check /tmp/frontend.log"
    exit 1
fi

echo ""
echo "🎉 All servers are running!"
echo ""
echo "📝 Access the application:"
echo "   Frontend:  http://localhost:4000"
echo "   Backend:   http://localhost:3001"
echo "   API Docs:  http://localhost:3001/api/docs"
echo ""
echo "📋 To stop the servers:"
echo "   ./stop.sh"
echo ""
echo "📊 To view logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
