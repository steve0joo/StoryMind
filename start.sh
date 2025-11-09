#!/bin/bash

##############################################################################
# StoryMind Development Server Startup Script
#
# This script starts both backend and frontend servers with a single command
# Ensures complete cleanup on exit (no lingering processes)
# Usage: ./start.sh
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# PID tracking
BACKEND_PID=""
FRONTEND_PID=""

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}         StoryMind Development Environment Startup          ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Function to cleanup on exit - GUARANTEED TERMINATION
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"

    # Kill process tree (parent + all children)
    if [ ! -z "$BACKEND_PID" ]; then
        # Kill entire process group
        pkill -TERM -P $BACKEND_PID 2>/dev/null || true
        kill -TERM $BACKEND_PID 2>/dev/null || true
        sleep 0.5
        kill -KILL $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Backend stopped (PID $BACKEND_PID)"
    fi

    if [ ! -z "$FRONTEND_PID" ]; then
        # Kill entire process group
        pkill -TERM -P $FRONTEND_PID 2>/dev/null || true
        kill -TERM $FRONTEND_PID 2>/dev/null || true
        sleep 0.5
        kill -KILL $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✓${NC} Frontend stopped (PID $FRONTEND_PID)"
    fi

    # Nuclear option: Kill ANY remaining Flask or Vite processes
    echo -e "${YELLOW}Cleaning up any remaining processes...${NC}"
    pkill -9 -f "python.*app.py" 2>/dev/null || true
    pkill -9 -f "vite" 2>/dev/null || true
    pkill -9 -f "node.*vite" 2>/dev/null || true

    # Force-kill anything on our ports
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
    lsof -ti:5173 | xargs kill -9 2>/dev/null || true

    # Wait a moment for cleanup
    sleep 1

    # Verify ports are clear
    if lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Warning: Port 5001 still in use"
    fi
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}✗${NC} Warning: Port 5173 still in use"
    fi

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}All servers terminated. Ports 5001 and 5173 are free.${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Set up trap to cleanup on ANY exit (Ctrl+C, error, normal exit)
trap cleanup EXIT INT TERM QUIT

# Pre-cleanup: Kill any existing processes
echo -e "${YELLOW}⚙  Pre-cleanup: Stopping any existing servers...${NC}"
pkill -9 -f "python.*app.py" 2>/dev/null || true
pkill -9 -f "vite" 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
sleep 1
echo -e "${GREEN}✓${NC} Ports cleared"
echo ""

# Start Backend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Starting Backend (Flask)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$BACKEND_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}✗${NC} Virtual environment not found!"
    echo -e "${YELLOW}Run: cd backend && python3.11 -m venv venv && pip install -r requirements.txt${NC}"
    exit 1
fi

# Start backend in background with proper process group
source venv/bin/activate
setsid python app.py > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
disown  # Detach from shell so trap handles cleanup

# Wait for backend to start
echo -n "Waiting for backend to start"
for i in {1..15}; do
    if curl -s http://localhost:5001/api/health >/dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} Backend running on ${GREEN}http://localhost:5001${NC}"
        echo -e "  PID: $BACKEND_PID"
        echo -e "  Logs: tail -f $PROJECT_ROOT/backend.log"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:5001/api/health >/dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗${NC} Backend failed to start. Check backend.log for errors."
    tail -20 "$PROJECT_ROOT/backend.log"
    exit 1
fi

echo ""

# Start Frontend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}Starting Frontend (React + Vite)...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚙  Installing frontend dependencies (first time)...${NC}"
    npm install
fi

# Start frontend in background with proper process group
setsid npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
disown  # Detach from shell so trap handles cleanup

# Wait for frontend to start
echo -n "Waiting for frontend to start"
for i in {1..20}; do
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo ""
        echo -e "${GREEN}✓${NC} Frontend running on ${GREEN}http://localhost:5173${NC}"
        echo -e "  PID: $FRONTEND_PID"
        echo -e "  Logs: tail -f $PROJECT_ROOT/frontend.log"
        break
    fi
    echo -n "."
    sleep 1
done

if ! curl -s http://localhost:5173 >/dev/null 2>&1; then
    echo ""
    echo -e "${RED}✗${NC} Frontend failed to start. Check frontend.log for errors."
    tail -20 "$PROJECT_ROOT/frontend.log"
    exit 1
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ StoryMind is running!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}➜${NC}  Frontend:  ${BLUE}http://localhost:5173${NC}"
echo -e "  ${GREEN}➜${NC}  Backend:   ${BLUE}http://localhost:5001${NC}"
echo -e "  ${GREEN}➜${NC}  API Docs:  ${BLUE}http://localhost:5001/api/health${NC}"
echo ""
echo -e "${YELLOW}Logs (in separate terminals):${NC}"
echo -e "  Backend:  tail -f $PROJECT_ROOT/backend.log"
echo -e "  Frontend: tail -f $PROJECT_ROOT/frontend.log"
echo ""
echo -e "${RED}Press Ctrl+C to stop all servers${NC}"
echo -e "${YELLOW}(All processes will be terminated completely - no lingering servers)${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Keep script running and monitor both processes
while true; do
    # Check if processes are still alive
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${RED}✗${NC} Backend process died unexpectedly"
        tail -20 "$PROJECT_ROOT/backend.log"
        exit 1
    fi

    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${RED}✗${NC} Frontend process died unexpectedly"
        tail -20 "$PROJECT_ROOT/frontend.log"
        exit 1
    fi

    sleep 2
done
