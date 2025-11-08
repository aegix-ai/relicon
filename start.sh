#!/bin/bash

# Enhanced startup script for Relicon with improved backend
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if processes are running
check_process() {
    local port=$1
    local name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        warning "$name is already running on port $port"
        return 0
    else
        return 1
    fi
}

# Kill existing processes
cleanup() {
    log "Cleaning up existing processes..."
    
    # Kill processes on specific ports
    for port in 5000 8000; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            log "Killing process on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    # Kill by process name
    pkill -f "next dev" 2>/dev/null || true
    pkill -f "server_improved.py" 2>/dev/null || true
    pkill -f "server.py" 2>/dev/null || true
    
    sleep 2
}

# Start backend with improved server
start_backend() {
    log "Starting improved backend server..."
    
    cd engine
    
    # Check Python dependencies
    if ! python3 -c "import fastapi, uvicorn" 2>/dev/null; then
        error "Missing Python dependencies. Installing..."
        pip3 install -r requirements.txt
    fi
    
    # Start the improved server
    python3 server_improved.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait for backend to start
    log "Waiting for backend to start..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            success "Backend started successfully on port 8000"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    error "Backend failed to start"
    return 1
}

# Start frontend
start_frontend() {
    log "Starting frontend server..."
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        log "Installing frontend dependencies..."
        pnpm install
    fi
    
    # Start frontend
    pnpm dev &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    log "Waiting for frontend to start..."
    for i in {1..60}; do
        if curl -s http://localhost:5000 >/dev/null 2>&1; then
            success "Frontend started successfully on port 5000"
            return 0
        fi
        sleep 1
        echo -n "."
    done
    
    error "Frontend failed to start"
    return 1
}

# Health check
health_check() {
    log "Performing health checks..."
    
    # Check backend health
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        success "Backend health check passed"
    else
        error "Backend health check failed"
        return 1
    fi
    
    # Check frontend health
    if curl -s http://localhost:5000/api/health >/dev/null 2>&1; then
        success "Frontend health check passed"
    else
        warning "Frontend health check failed (may be normal during startup)"
    fi
    
    # Test API connectivity
    if curl -s http://localhost:5000/api/engine/health >/dev/null 2>&1; then
        success "Frontend-Backend connectivity verified"
    else
        warning "Frontend-Backend connectivity test failed"
    fi
}

# Show status
show_status() {
    echo ""
    echo "🚀 Relicon Enhanced Development Server"
    echo "======================================"
    echo ""
    echo "📱 Frontend:     http://localhost:5000"
    echo "🔧 Backend API:  http://localhost:8000"
    echo "❤️  Health:      http://localhost:8000/health"
    echo "📊 Metrics:      http://localhost:8000/metrics"
    echo ""
    echo "🎬 Creative Studio: http://localhost:5000/dashboard/studio"
    echo "💬 Chat System:     http://localhost:5000/dashboard/chat"
    echo "📈 Analytics:       http://localhost:5000/dashboard/analytics"
    echo ""
    echo "Press Ctrl+C to stop all services"
}

# Graceful shutdown
shutdown() {
    echo ""
    log "Shutting down services..."
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    cleanup
    success "All services stopped"
    exit 0
}

# Set up signal handlers
trap shutdown SIGINT SIGTERM

# Main execution
main() {
    log "Starting Relicon Enhanced Development Environment..."
    
    # Cleanup any existing processes
    cleanup
    
    # Start services
    if start_backend && start_frontend; then
        # Perform health checks
        sleep 3
        health_check
        
        # Show status
        show_status
        
        # Keep script running
        while true; do
            sleep 1
        done
    else
        error "Failed to start services"
        cleanup
        exit 1
    fi
}

# Handle command line arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        cleanup
        success "Services stopped"
        ;;
    "restart")
        cleanup
        sleep 2
        main
        ;;
    "status")
        if check_process 8000 "Backend" && check_process 5000 "Frontend"; then
            success "All services are running"
            show_status
        else
            error "Some services are not running"
        fi
        ;;
    "health")
        health_check
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|health}"
        exit 1
        ;;
esac
