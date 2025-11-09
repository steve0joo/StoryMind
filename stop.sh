#!/bin/bash

##############################################################################
# StoryMind Server Shutdown Script
#
# This script stops all backend and frontend servers
# Usage: ./stop.sh
##############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}Stopping StoryMind Servers...${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Stop backend (Flask)
echo -e "${YELLOW}Stopping Backend...${NC}"
pkill -f "python.*app.py" 2>/dev/null && echo -e "${GREEN}✓${NC} Backend stopped" || echo -e "${YELLOW}⚠${NC}  No backend process found"

# Stop frontend (Vite)
echo -e "${YELLOW}Stopping Frontend...${NC}"
pkill -f "vite" 2>/dev/null && echo -e "${GREEN}✓${NC} Frontend stopped" || echo -e "${YELLOW}⚠${NC}  No frontend process found"

# Kill any processes on specific ports
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo ""
echo -e "${GREEN}All servers stopped!${NC}"
echo ""
