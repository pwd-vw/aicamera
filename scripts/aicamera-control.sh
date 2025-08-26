#!/bin/bash

# AI Camera Control Script
# This script manages the AI Camera backend and frontend services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service names
BACKEND_SERVICE="aicamera-backend"
FRONTEND_SERVICE="aicamera-frontend"
SERVICES=("$BACKEND_SERVICE" "$FRONTEND_SERVICE")

# Configuration
SERVICE_DIR="/home/devuser/aicamera/server/systemd_service"
BACKEND_PORT=3000
FRONTEND_PORT=5173

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# Function to check if service exists
service_exists() {
    local service=$1
    systemctl --user list-unit-files | grep -q "^${service}.service"
}

# Function to install services
install_services() {
    print_status $BLUE "Installing AI Camera services..."
    
    if [ ! -d "$SERVICE_DIR" ]; then
        print_status $RED "Service directory not found: $SERVICE_DIR"
        exit 1
    fi
    
    # Create systemd user directory if it doesn't exist
    mkdir -p ~/.config/systemd/user
    
    for service in "${SERVICES[@]}"; do
        local service_file="$SERVICE_DIR/${service}.service"
        if [ -f "$service_file" ]; then
            print_status $YELLOW "Installing $service..."
            cp "$service_file" ~/.config/systemd/user/
            systemctl --user daemon-reload
            systemctl --user enable "$service"
            print_status $GREEN "$service installed and enabled"
        else
            print_status $RED "Service file not found: $service_file"
        fi
    done
    
    print_status $GREEN "All services installed successfully"
}

# Function to uninstall services
uninstall_services() {
    print_status $BLUE "Uninstalling AI Camera services..."
    
    for service in "${SERVICES[@]}"; do
        if service_exists "$service"; then
            print_status $YELLOW "Stopping and disabling $service..."
            systemctl --user stop "$service" 2>/dev/null || true
            systemctl --user disable "$service" 2>/dev/null || true
            rm -f ~/.config/systemd/user/"$service".service
            print_status $GREEN "$service uninstalled"
        else
            print_status $YELLOW "$service not found, skipping..."
        fi
    done
    
    systemctl --user daemon-reload
    print_status $GREEN "All services uninstalled successfully"
}

# Function to start services
start_services() {
    print_status $BLUE "Starting AI Camera services..."
    
    for service in "${SERVICES[@]}"; do
        if service_exists "$service"; then
            print_status $YELLOW "Starting $service..."
            systemctl --user start "$service"
            sleep 2
            if systemctl --user is-active --quiet "$service"; then
                print_status $GREEN "$service started successfully"
            else
                print_status $RED "$service failed to start"
                systemctl --user status "$service" --no-pager -l
            fi
        else
            print_status $RED "$service not found. Run 'install' first."
        fi
    done
}

# Function to stop services
stop_services() {
    print_status $BLUE "Stopping AI Camera services..."
    
    for service in "${SERVICES[@]}"; do
        if service_exists "$service"; then
            print_status $YELLOW "Stopping $service..."
            systemctl --user stop "$service"
            print_status $GREEN "$service stopped"
        else
            print_status $YELLOW "$service not found, skipping..."
        fi
    done
}

# Function to restart services
restart_services() {
    print_status $BLUE "Restarting AI Camera services..."
    
    for service in "${SERVICES[@]}"; do
        if service_exists "$service"; then
            print_status $YELLOW "Restarting $service..."
            systemctl --user restart "$service"
            sleep 2
            if systemctl --user is-active --quiet "$service"; then
                print_status $GREEN "$service restarted successfully"
            else
                print_status $RED "$service failed to restart"
            fi
        else
            print_status $RED "$service not found. Run 'install' first."
        fi
    done
}

# Function to show status
show_status() {
    print_status $BLUE "AI Camera Services Status"
    echo "=================================="
    
    for service in "${SERVICES[@]}"; do
        echo -n "$service: "
        if service_exists "$service"; then
            if systemctl --user is-active --quiet "$service"; then
                echo -e "${GREEN}ACTIVE${NC}"
            else
                echo -e "${RED}INACTIVE${NC}"
            fi
        else
            echo -e "${YELLOW}NOT INSTALLED${NC}"
        fi
    done
    
    echo ""
    print_status $BLUE "Port Status:"
    echo "Backend (Port $BACKEND_PORT):"
    if netstat -tulpn 2>/dev/null | grep -q ":$BACKEND_PORT "; then
        echo -e "  ${GREEN}Port $BACKEND_PORT is in use${NC}"
        netstat -tulpn 2>/dev/null | grep ":$BACKEND_PORT " | head -1
    else
        echo -e "  ${RED}Port $BACKEND_PORT is not in use${NC}"
    fi
    
    echo "Frontend (Port $FRONTEND_PORT):"
    if netstat -tulpn 2>/dev/null | grep -q ":$FRONTEND_PORT "; then
        echo -e "  ${GREEN}Port $FRONTEND_PORT is in use${NC}"
        netstat -tulpn 2>/dev/null | grep ":$FRONTEND_PORT " | head -1
    else
        echo -e "  ${RED}Port $FRONTEND_PORT is not in use${NC}"
    fi
    
    echo ""
    print_status $BLUE "Service Logs (last 5 lines):"
    for service in "${SERVICES[@]}"; do
        if service_exists "$service"; then
            echo "$service logs:"
            journalctl --user -u "$service" -n 5 --no-pager || echo "  No logs available"
            echo ""
        fi
    done
}

# Function to show logs
show_logs() {
    local service=${1:-"all"}
    
    if [ "$service" = "all" ]; then
        print_status $BLUE "Showing logs for all services..."
        for s in "${SERVICES[@]}"; do
            if service_exists "$s"; then
                echo "=== $s logs ==="
                journalctl --user -u "$s" --no-pager -f &
            fi
        done
        wait
    else
        if service_exists "$service"; then
            print_status $BLUE "Showing logs for $service..."
            journalctl --user -u "$service" --no-pager -f
        else
            print_status $RED "Service $service not found"
        fi
    fi
}

# Function to build and deploy
build_and_deploy() {
    print_status $BLUE "Building and deploying AI Camera..."
    
    # Build backend
    print_status $YELLOW "Building backend..."
    cd /home/devuser/aicamera/server
    npm run build
    
    # Build frontend
    print_status $YELLOW "Building frontend..."
    cd /home/devuser/aicamera/server/frontend
    npm run build
    
    print_status $GREEN "Build completed successfully"
    
    # Restart services if they're running
    if systemctl --user is-active --quiet "$BACKEND_SERVICE" || systemctl --user is-active --quiet "$FRONTEND_SERVICE"; then
        print_status $YELLOW "Restarting services with new build..."
        restart_services
    fi
}

# Function to show help
show_help() {
    echo "AI Camera Control Script"
    echo "======================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install     - Install and enable systemd services"
    echo "  uninstall   - Uninstall and disable systemd services"
    echo "  start       - Start all services"
    echo "  stop        - Stop all services"
    echo "  restart     - Restart all services"
    echo "  status      - Show status of all services and ports"
    echo "  logs [service] - Show logs (default: all services)"
    echo "  build       - Build backend and frontend"
    echo "  deploy      - Build and restart services"
    echo "  help        - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 install"
    echo "  $0 start"
    echo "  $0 status"
    echo "  $0 logs aicamera-backend"
    echo "  $0 deploy"
    echo ""
    echo "Service URLs:"
    echo "  Backend API:  http://localhost:$BACKEND_PORT"
    echo "  Frontend:     http://localhost:$FRONTEND_PORT"
}

# Main script logic
case "${1:-help}" in
    install)
        install_services
        ;;
    uninstall)
        uninstall_services
        ;;
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    build)
        build_and_deploy
        ;;
    deploy)
        build_and_deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_status $RED "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
