#!/bin/bash
# AI Camera v2.0.0 - Boot Logo Setup Script
# This script sets up the AI Camera logo for boot splash screen

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Check if AI Camera logo exists
check_logo() {
    local logo_path="assets/aicamera_logo.png"
    if [[ ! -f "$logo_path" ]]; then
        log_error "AI Camera logo not found at $logo_path"
        exit 1
    fi
    log_info "Found AI Camera logo: $logo_path"
}

# Backup original splash image
backup_original() {
    local backup_path="/usr/share/plymouth/themes/pix/splash.png.backup"
    if [[ ! -f "$backup_path" ]]; then
        log_info "Backing up original splash image..."
        sudo cp /usr/share/plymouth/themes/pix/splash.png "$backup_path"
        log_success "Original splash image backed up to $backup_path"
    else
        log_info "Backup already exists: $backup_path"
    fi
}

# Install AI Camera logo
install_logo() {
    log_info "Installing AI Camera logo as boot splash..."
    sudo cp assets/aicamera_logo.png /usr/share/plymouth/themes/pix/splash.png
    log_success "AI Camera logo installed"
}

# Set Plymouth theme
set_theme() {
    log_info "Setting Plymouth theme to pix..."
    sudo plymouth-set-default-theme pix
    log_success "Plymouth theme set to pix"
}

# Update initramfs
update_initramfs() {
    log_info "Updating initramfs..."
    sudo update-initramfs -u -k all
    log_success "Initramfs updated"
}

# Test splash screen
test_splash() {
    log_info "Testing splash screen (will show for 3 seconds)..."
    sudo plymouth --show-splash --pid-file=/var/run/plymouth.pid &
    local pid=$!
    sleep 3
    sudo plymouth --quit
    wait $pid 2>/dev/null || true
    log_success "Splash screen test completed"
}

# Main function
main() {
    log_info "AI Camera Boot Logo Setup"
    log_info "=========================="
    
    check_root
    check_logo
    backup_original
    install_logo
    set_theme
    update_initramfs
    
    log_success "Boot logo setup completed successfully!"
    log_info "The AI Camera logo will be displayed on next boot"
    
    # Ask if user wants to test
    read -p "Do you want to test the splash screen now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_splash
    fi
    
    log_info "To see the new logo, reboot the system: sudo reboot"
}

# Run main function
main "$@"
