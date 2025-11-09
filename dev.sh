#!/bin/bash

##############################################################################
# StoryMind Development Helper Script
#
# Convenient commands for development tasks
# Usage: ./dev.sh [command]
##############################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# Function to show help
show_help() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}         StoryMind Development Helper Commands             ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${GREEN}Server Management:${NC}"
    echo -e "  ./dev.sh start          ${YELLOW}Start both backend and frontend${NC}"
    echo -e "  ./dev.sh stop           ${YELLOW}Stop all servers${NC}"
    echo -e "  ./dev.sh restart        ${YELLOW}Restart all servers${NC}"
    echo -e "  ./dev.sh status         ${YELLOW}Check server status${NC}"
    echo ""
    echo -e "${GREEN}Database:${NC}"
    echo -e "  ./dev.sh db-clean       ${YELLOW}Clean database completely${NC}"
    echo -e "  ./dev.sh db-status      ${YELLOW}Show database stats${NC}"
    echo ""
    echo -e "${GREEN}Logs:${NC}"
    echo -e "  ./dev.sh logs           ${YELLOW}Show live logs (both servers)${NC}"
    echo -e "  ./dev.sh logs-backend   ${YELLOW}Show backend logs only${NC}"
    echo -e "  ./dev.sh logs-frontend  ${YELLOW}Show frontend logs only${NC}"
    echo ""
    echo -e "${GREEN}Testing:${NC}"
    echo -e "  ./dev.sh test-rag       ${YELLOW}Test RAG system quality${NC}"
    echo -e "  ./dev.sh test-api       ${YELLOW}Test API endpoints${NC}"
    echo ""
    echo -e "${GREEN}Utilities:${NC}"
    echo -e "  ./dev.sh quota          ${YELLOW}Show API quota usage${NC}"
    echo -e "  ./dev.sh open           ${YELLOW}Open app in browser${NC}"
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Start servers
cmd_start() {
    echo -e "${GREEN}Starting StoryMind...${NC}"
    "$PROJECT_ROOT/start.sh"
}

# Stop servers
cmd_stop() {
    echo -e "${YELLOW}Stopping StoryMind...${NC}"
    "$PROJECT_ROOT/stop.sh"
}

# Restart servers
cmd_restart() {
    cmd_stop
    sleep 2
    cmd_start
}

# Check status
cmd_status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                    Server Status                          ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    # Check backend
    if curl -s http://localhost:5001/api/health >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Backend:  ${GREEN}Running${NC} (http://localhost:5001)"
    else
        echo -e "${RED}✗${NC} Backend:  ${RED}Stopped${NC}"
    fi

    # Check frontend
    if curl -s http://localhost:5173 >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Frontend: ${GREEN}Running${NC} (http://localhost:5173)"
    else
        echo -e "${RED}✗${NC} Frontend: ${RED}Stopped${NC}"
    fi

    echo ""
}

# Clean database
cmd_db_clean() {
    echo -e "${YELLOW}⚠  This will delete ALL data (books, characters, images)${NC}"
    read -p "Are you sure? (yes/no): " -r
    if [[ $REPLY == "yes" ]]; then
        cd "$BACKEND_DIR"
        source venv/bin/activate
        python clean_everything.py
    else
        echo -e "${GREEN}Cancelled${NC}"
    fi
}

# Database status
cmd_db_status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}                   Database Status                         ${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""

    sqlite3 "$BACKEND_DIR/data/storymind.db" << EOF
.mode column
.headers on
SELECT 'Books' as EntityType, COUNT(*) as Count FROM books
UNION ALL
SELECT 'Characters', COUNT(*) FROM characters
UNION ALL
SELECT 'Images', COUNT(*) FROM images;
EOF

    echo ""
}

# Show logs
cmd_logs() {
    tail -f "$PROJECT_ROOT/backend.log" "$PROJECT_ROOT/frontend.log" 2>/dev/null
}

cmd_logs_backend() {
    tail -f "$PROJECT_ROOT/backend.log" 2>/dev/null || tail -f "$BACKEND_DIR/logs/storymind.log"
}

cmd_logs_frontend() {
    tail -f "$PROJECT_ROOT/frontend.log" 2>/dev/null
}

# Test RAG
cmd_test_rag() {
    cd "$BACKEND_DIR"
    source venv/bin/activate
    python test_rag_quality.py
}

# Test API
cmd_test_api() {
    echo ""
    echo -e "${BLUE}Testing API Endpoints...${NC}"
    echo ""

    # Health check
    echo -e "${YELLOW}Health Check:${NC}"
    curl -s http://localhost:5001/api/health | jq . || echo -e "${RED}Failed${NC}"
    echo ""

    # Books
    echo -e "${YELLOW}Books:${NC}"
    curl -s http://localhost:5001/api/books | jq '.total' || echo -e "${RED}Failed${NC}"
    echo ""

    # Characters health
    echo -e "${YELLOW}Characters Health:${NC}"
    curl -s http://localhost:5001/api/characters/health | jq . || echo -e "${RED}Failed${NC}"
    echo ""
}

# Show quota
cmd_quota() {
    echo ""
    echo -e "${BLUE}API Quota Information:${NC}"
    echo ""
    echo "Gemini API Quota: https://ai.google.dev/gemini-api/docs/quota"
    echo "Your Usage: https://console.cloud.google.com/billing"
    echo ""
    echo -e "${GREEN}Current Optimization: 9 API calls per book${NC}"
    echo ""
}

# Open in browser
cmd_open() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open http://localhost:5173
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open http://localhost:5173
    else
        echo "Please open http://localhost:5173 in your browser"
    fi
}

# Main command handler
case "$1" in
    start)
        cmd_start
        ;;
    stop)
        cmd_stop
        ;;
    restart)
        cmd_restart
        ;;
    status)
        cmd_status
        ;;
    db-clean)
        cmd_db_clean
        ;;
    db-status)
        cmd_db_status
        ;;
    logs)
        cmd_logs
        ;;
    logs-backend)
        cmd_logs_backend
        ;;
    logs-frontend)
        cmd_logs_frontend
        ;;
    test-rag)
        cmd_test_rag
        ;;
    test-api)
        cmd_test_api
        ;;
    quota)
        cmd_quota
        ;;
    open)
        cmd_open
        ;;
    *)
        show_help
        ;;
esac
