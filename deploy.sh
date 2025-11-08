#!/bin/bash

# Relicon Production Deployment Script
# Enhanced with reliability, monitoring, and rollback capabilities

set -e

# Configuration
PROJECT_NAME="relicon"
BACKUP_DIR="./backups"
LOG_FILE="./deploy.log"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f ".env.local" ]; then
        error ".env.local file not found"
        exit 1
    fi
    
    # Validate required environment variables
    required_vars=("OPENAI_API_KEY" "LUMA_API_KEY" "ELEVENLABS_API_KEY" "NEXT_PUBLIC_SUPABASE_URL")
    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" .env.local; then
            error "Required environment variable $var not found in .env.local"
            exit 1
        fi
    done
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    log "Creating backup..."
    
    mkdir -p "$BACKUP_DIR"
    backup_name="backup_$(date +'%Y%m%d_%H%M%S')"
    
    # Backup current deployment if exists
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "Backing up current deployment..."
        
        # Export current containers
        docker-compose -f docker-compose.prod.yml config > "$BACKUP_DIR/$backup_name.yml"
        
        # Backup volumes
        docker run --rm -v ${PROJECT_NAME}_video_outputs:/data -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/${backup_name}_videos.tar.gz -C /data .
        
        success "Backup created: $backup_name"
        echo "$backup_name" > "$BACKUP_DIR/latest_backup"
    else
        log "No existing deployment to backup"
    fi
}

# Build images
build_images() {
    log "Building Docker images..."
    
    # Build with build args for optimization
    docker-compose -f docker-compose.prod.yml build \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --parallel
    
    success "Images built successfully"
}

# Deploy services
deploy_services() {
    log "Deploying services..."
    
    # Stop existing services gracefully
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "Stopping existing services..."
        docker-compose -f docker-compose.prod.yml down --timeout 30
    fi
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    success "Services deployed"
}

# Health check
health_check() {
    log "Performing health checks..."
    
    local start_time=$(date +%s)
    local timeout=$HEALTH_CHECK_TIMEOUT
    
    # Check backend health
    log "Checking backend health..."
    while true; do
        if curl -f http://localhost:8000/health &>/dev/null; then
            success "Backend is healthy"
            break
        fi
        
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            error "Backend health check timeout"
            return 1
        fi
        
        log "Waiting for backend... (${elapsed}s/${timeout}s)"
        sleep 5
    done
    
    # Check frontend health
    log "Checking frontend health..."
    start_time=$(date +%s)
    while true; do
        if curl -f http://localhost:3000/api/health &>/dev/null; then
            success "Frontend is healthy"
            break
        fi
        
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            error "Frontend health check timeout"
            return 1
        fi
        
        log "Waiting for frontend... (${elapsed}s/${timeout}s)"
        sleep 5
    done
    
    # Test video generation endpoint
    log "Testing video generation endpoint..."
    if curl -f -X POST http://localhost:8000/health &>/dev/null; then
        success "Video generation endpoint is accessible"
    else
        warning "Video generation endpoint test failed"
    fi
    
    success "All health checks passed"
}

# Rollback function
rollback() {
    error "Deployment failed, initiating rollback..."
    
    if [ -f "$BACKUP_DIR/latest_backup" ]; then
        local backup_name=$(cat "$BACKUP_DIR/latest_backup")
        log "Rolling back to backup: $backup_name"
        
        # Stop current deployment
        docker-compose -f docker-compose.prod.yml down --timeout 30
        
        # Restore from backup
        if [ -f "$BACKUP_DIR/$backup_name.yml" ]; then
            docker-compose -f "$BACKUP_DIR/$backup_name.yml" up -d
            success "Rollback completed"
        else
            error "Backup file not found, manual intervention required"
        fi
    else
        error "No backup available for rollback"
    fi
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up old backups..."
    
    # Keep only last 5 backups
    if [ -d "$BACKUP_DIR" ]; then
        cd "$BACKUP_DIR"
        ls -t backup_*.yml 2>/dev/null | tail -n +6 | xargs -r rm
        ls -t backup_*_videos.tar.gz 2>/dev/null | tail -n +6 | xargs -r rm
        cd - > /dev/null
        success "Old backups cleaned up"
    fi
}

# Show deployment status
show_status() {
    log "Deployment Status:"
    echo "===================="
    
    # Show running containers
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    log "Service URLs:"
    echo "Frontend: http://localhost:3000"
    echo "Backend API: http://localhost:8000"
    echo "Backend Health: http://localhost:8000/health"
    echo "Prometheus: http://localhost:9090"
    
    echo ""
    log "Logs:"
    echo "View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "Backend logs: docker-compose -f docker-compose.prod.yml logs -f backend"
    echo "Frontend logs: docker-compose -f docker-compose.prod.yml logs -f frontend"
}

# Main deployment function
main() {
    log "Starting Relicon production deployment..."
    
    # Trap errors for rollback
    trap rollback ERR
    
    check_prerequisites
    create_backup
    build_images
    deploy_services
    
    # Health checks with rollback on failure
    if ! health_check; then
        rollback
        exit 1
    fi
    
    cleanup_backups
    show_status
    
    success "Deployment completed successfully!"
    log "Deployment took $(($(date +%s) - $(date +%s))) seconds"
}

# Handle command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "status")
        show_status
        ;;
    "logs")
        docker-compose -f docker-compose.prod.yml logs -f "${2:-}"
        ;;
    "stop")
        log "Stopping services..."
        docker-compose -f docker-compose.prod.yml down
        success "Services stopped"
        ;;
    "restart")
        log "Restarting services..."
        docker-compose -f docker-compose.prod.yml restart
        success "Services restarted"
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|status|logs|stop|restart}"
        echo ""
        echo "Commands:"
        echo "  deploy   - Deploy the application (default)"
        echo "  rollback - Rollback to previous version"
        echo "  status   - Show deployment status"
        echo "  logs     - Show logs (optionally specify service)"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        exit 1
        ;;
esac
