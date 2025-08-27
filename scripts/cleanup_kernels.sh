#!/bin/bash
# AI Camera v2.0.0 - Kernel Cleanup Script
# This script removes old and incompatible kernels, keeping only the current rpi-2712 kernel

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

# Get current kernel version
get_current_kernel() {
    CURRENT_KERNEL=$(uname -r)
    log_info "Current running kernel: $CURRENT_KERNEL"
}

# Check hardware compatibility
check_hardware() {
    local model=$(cat /proc/cpuinfo | grep "Model" | head -1 | cut -d: -f2 | xargs)
    log_info "Hardware detected: $model"
    
    if [[ "$model" == *"Raspberry Pi 5"* ]]; then
        log_success "Raspberry Pi 5 detected - using rpi-2712 kernels"
        KERNEL_TYPE="rpi-2712"
    elif [[ "$model" == *"Raspberry Pi 4"* ]] || [[ "$model" == *"Raspberry Pi 400"* ]] || [[ "$model" == *"Raspberry Pi CM4"* ]]; then
        log_success "Raspberry Pi 4/400/CM4 detected - using rpi-2712 kernels"
        KERNEL_TYPE="rpi-2712"
    elif [[ "$model" == *"Raspberry Pi 3"* ]] || [[ "$model" == *"Raspberry Pi Zero 2"* ]]; then
        log_success "Raspberry Pi 3/Zero 2 detected - using rpi-v8 kernels"
        KERNEL_TYPE="rpi-v8"
    else
        log_warning "Unknown hardware - keeping both kernel types"
        KERNEL_TYPE="both"
    fi
}

# List installed kernels
list_installed_kernels() {
    log_info "Installed kernels:"
    dpkg -l | grep linux-image | grep -v "^rc" | while read line; do
        echo "  $line"
    done
}

# Remove old kernels
remove_old_kernels() {
    log_info "Removing old and incompatible kernels..."
    
    # Remove old 6.12.25 kernels
    if [[ "$KERNEL_TYPE" == "rpi-2712" ]]; then
        log_info "Removing old rpi-v8 kernels (incompatible with this hardware)..."
        apt remove -y linux-image-6.12.25+rpt-rpi-v8 linux-image-rpi-v8 2>/dev/null || true
        
        # Also remove any 6.6.x kernels if they exist
        apt remove -y linux-image-6.6.51+rpt-rpi-v8 2>/dev/null || true
        apt remove -y linux-image-6.6.51+rpt-rpi-2712 2>/dev/null || true
        
    elif [[ "$KERNEL_TYPE" == "rpi-v8" ]]; then
        log_info "Removing old rpi-2712 kernels (incompatible with this hardware)..."
        apt remove -y linux-image-6.12.25+rpt-rpi-2712 linux-image-rpi-2712 2>/dev/null || true
        
        # Also remove any 6.6.x kernels if they exist
        apt remove -y linux-image-6.6.51+rpt-rpi-2712 2>/dev/null || true
        apt remove -y linux-image-6.6.51+rpt-rpi-v8 2>/dev/null || true
    fi
    
    # Remove old 6.12.25 kernels of the same type
    if [[ "$KERNEL_TYPE" != "both" ]]; then
        log_info "Removing old 6.12.25 kernel of the same type..."
        apt remove -y linux-image-6.12.25+rpt-$KERNEL_TYPE 2>/dev/null || true
    fi
}

# Clean up package cache
cleanup_cache() {
    log_info "Cleaning up package cache..."
    apt autoremove -y
    apt autoclean
}

# Update kernel configuration
update_kernel_config() {
    log_info "Updating kernel configuration..."
    
    # Ensure kernel updates are enabled
    if [[ -f /etc/apt/apt.conf.d/01autoremove ]]; then
        log_info "Checking autoremove configuration..."
        if grep -q "linux-image" /etc/apt/apt.conf.d/01autoremove; then
            log_success "Kernel autoremove is already configured"
        else
            log_warning "Kernel autoremove not configured - kernels may accumulate"
        fi
    fi
    
    # Update package lists
    log_info "Updating package lists..."
    apt update
}

# Show final status
show_final_status() {
    log_info "Final kernel status:"
    echo ""
    log_info "Installed kernels after cleanup:"
    dpkg -l | grep linux-image | grep -v "^rc" | while read line; do
        echo "  $line"
    done
    
    echo ""
    log_info "Available kernel updates:"
    apt list --upgradable | grep linux-image || log_info "No kernel updates available"
    
    echo ""
    log_success "Kernel cleanup completed successfully!"
    log_info "Current kernel: $CURRENT_KERNEL"
    log_info "Hardware type: $KERNEL_TYPE"
}

# Main function
main() {
    log_info "AI Camera Kernel Cleanup Script"
    log_info "==============================="
    
    echo ""
    
    # Check root privileges
    check_root
    
    # Get current kernel
    get_current_kernel
    
    echo ""
    
    # Check hardware
    check_hardware
    
    echo ""
    
    # List current kernels
    list_installed_kernels
    
    echo ""
    
    # Remove old kernels
    remove_old_kernels
    
    echo ""
    
    # Clean up cache
    cleanup_cache
    
    echo ""
    
    # Update configuration
    update_kernel_config
    
    echo ""
    
    # Show final status
    show_final_status
}

# Run main function
main "$@"
