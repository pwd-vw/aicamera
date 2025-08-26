#!/bin/bash

# AI Camera Nginx Installation Script
# This script installs and configures nginx as a reverse proxy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

print_status $BLUE "Installing AI Camera Nginx Configuration..."

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_status $RED "Please don't run this script as root. Use your regular user account."
    exit 1
fi

# Install nginx if not already installed
if ! command -v nginx &> /dev/null; then
    print_status $YELLOW "Installing nginx..."
    sudo apt update
    sudo apt install -y nginx
    print_status $GREEN "Nginx installed successfully"
else
    print_status $GREEN "Nginx is already installed"
fi

# Stop nginx temporarily
print_status $YELLOW "Stopping nginx temporarily..."
sudo systemctl stop nginx

# Backup existing default site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    print_status $YELLOW "Backing up default nginx site..."
    sudo mv /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
    print_status $GREEN "Default site backed up"
fi

# Copy our nginx configuration
print_status $YELLOW "Installing AI Camera nginx configuration..."
sudo cp /home/devuser/aicamera/server/nginx.conf /etc/nginx/sites-available/aicamera

# Create symlink to enable the site
if [ -L /etc/nginx/sites-enabled/aicamera ]; then
    sudo rm /etc/nginx/sites-enabled/aicamera
fi
sudo ln -s /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/aicamera

# Test nginx configuration
print_status $YELLOW "Testing nginx configuration..."
if sudo nginx -t; then
    print_status $GREEN "Nginx configuration is valid"
else
    print_status $RED "Nginx configuration test failed!"
    exit 1
fi

# Create directory for frontend build if it doesn't exist
sudo mkdir -p /home/devuser/aicamera/server/frontend/dist
sudo chown devuser:devuser /home/devuser/aicamera/server/frontend/dist

# Start and enable nginx
print_status $YELLOW "Starting and enabling nginx..."
sudo systemctl start nginx
sudo systemctl enable nginx

# Check if nginx is running
if sudo systemctl is-active --quiet nginx; then
    print_status $GREEN "Nginx is running successfully"
else
    print_status $RED "Failed to start nginx"
    exit 1
fi

# Set up log rotation for nginx
print_status $YELLOW "Setting up log rotation..."
sudo mkdir -p /var/log/nginx
sudo chown www-data:adm /var/log/nginx

# Allow nginx to access the Unix socket
print_status $YELLOW "Setting up permissions for Unix socket..."
sudo usermod -a -G devuser www-data

print_status $GREEN "AI Camera Nginx installation completed successfully!"
print_status $BLUE "You can now access the application at: http://localhost/"
print_status $YELLOW "Note: Make sure to build the frontend and start the backend service"