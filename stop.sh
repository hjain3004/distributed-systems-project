#!/bin/bash

# Distributed Systems Performance Modeling - Stop Script
# This script stops both the backend and frontend servers

echo "🛑 Stopping Distributed Systems Performance Modeling..."
echo ""

# Stop backend
echo "Stopping backend..."
pkill -f "python.*simple_main" && echo "✅ Simple backend stopped" || true
pkill -f "uvicorn" && echo "✅ Uvicorn backend stopped" || true
# Force kill anything on port 3100 just in case
lsof -ti:3100 | xargs kill -9 2>/dev/null || true

# Stop frontend
echo "Stopping frontend..."
pkill -f "vite" && echo "✅ Frontend stopped" || echo "⚠️  Frontend was not running"

echo ""
echo "✅ All servers stopped"
echo ""
