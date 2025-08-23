#!/bin/bash
# AI Camera v2.0.0 - Restore Original Boot Logo Script
# This script restores the original Raspberry Pi logo for boot splash screen

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

# Check if backup exists
check_backup() {
    local backup_path="/usr/share/plymouth/themes/pix/splash.png.backup"
    if [[ ! -f "$backup_path" ]]; then
        log_error "Backup file not found at $backup_path"
        log_error "Cannot restore original logo"
        exit 1
    fi
    log_info "Found backup file: $backup_path"
}

# Restore original splash image
restore_original() {
    log_info "Restoring original splash image..."
    sudo cp /usr/share/plymouth/themes/pix/splash.png.backup /usr/share/plymouth/themes/pix/splash.png
    log_success "Original splash image restored"
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
    log_info "AI Camera Boot Logo Restore"
    log_info "==========================="
    
    check_root
    check_backup
    restore_original
    update_initramfs
    
    log_success "Boot logo restore completed successfully!"
    log_info "The original Raspberry Pi logo will be displayed on next boot"
    
    # Ask if user wants to test
    read -p "Do you want to test the splash screen now? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        test_splash
    fi
    
    log_info "To see the original logo, reboot the system: sudo reboot"
}

# Run main function
main "$@"
