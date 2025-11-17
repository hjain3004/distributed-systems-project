#!/bin/bash

# Distributed Systems Performance Modeling - Stop Script
# This script stops both the backend and frontend servers

echo "🛑 Stopping Distributed Systems Performance Modeling..."
echo ""

# Stop backend
echo "Stopping backend..."
pkill -f "python.*simple_main" && echo "✅ Backend stopped" || echo "⚠️  Backend was not running"

# Stop frontend
echo "Stopping frontend..."
pkill -f "vite" && echo "✅ Frontend stopped" || echo "⚠️  Frontend was not running"

echo ""
echo "✅ All servers stopped"
echo ""
