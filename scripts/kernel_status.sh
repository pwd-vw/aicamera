#!/bin/bash
# AI Camera v2.0.0 - Kernel Status Script
# This script shows the current kernel status and configuration

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

# Get system information
get_system_info() {
    log_info "System Information:"
    echo "  Hardware: $(cat /proc/cpuinfo | grep "Model" | head -1 | cut -d: -f2 | xargs)"
    echo "  Architecture: $(uname -m)"
    echo "  Current Kernel: $(uname -r)"
    echo "  Kernel Version: $(uname -v)"
}

# Show installed kernels
show_installed_kernels() {
    log_info "Installed Kernels:"
    local kernels=$(dpkg -l | grep linux-image | grep -v "^rc")
    if [[ -n "$kernels" ]]; then
        echo "$kernels" | while read line; do
            echo "  $line"
        done
    else
        log_warning "No kernels found"
    fi
}

# Show boot configuration
show_boot_config() {
    log_info "Boot Configuration:"
    echo "  Boot firmware kernel: $(ls -la /boot/firmware/kernel* 2>/dev/null | head -1 | awk '{print $9}' || echo "Not found")"
    echo "  Config.txt arm_64bit: $(grep -E "^arm_64bit" /boot/firmware/config.txt 2>/dev/null | head -1 || echo "Not set")"
    echo "  Auto initramfs: $(grep -E "^auto_initramfs" /boot/firmware/config.txt 2>/dev/null | head -1 || echo "Not set")"
}

# Show kernel update configuration
show_update_config() {
    log_info "Kernel Update Configuration:"
    
    # Check apt preferences
    if [[ -f /etc/apt/preferences.d/99-kernel-updates ]]; then
        log_success "Apt preferences configured"
        echo "  rpi-2712 kernels: Prioritized"
        echo "  rpi-v8 kernels: Blocked"
    else
        log_warning "Apt preferences not configured"
    fi
    
    # Check unattended upgrades
    if [[ -f /etc/apt/apt.conf.d/50unattended-upgrades ]]; then
        log_success "Unattended upgrades configured"
    else
        log_warning "Unattended upgrades not configured"
    fi
    
    # Check automatic cleanup
    if [[ -f /usr/local/bin/cleanup-old-kernels ]]; then
        log_success "Automatic kernel cleanup configured"
        echo "  Schedule: Weekly (Sunday 2:00 AM)"
    else
        log_warning "Automatic kernel cleanup not configured"
    fi
}

# Check for available updates
check_updates() {
    log_info "Available Updates:"
    
    # Update package lists
    apt update >/dev/null 2>&1
    
    # Check for kernel updates
    local kernel_updates=$(apt list --upgradable 2>/dev/null | grep linux-image-rpi-2712 || true)
    
    if [[ -n "$kernel_updates" ]]; then
        log_warning "Kernel updates available:"
        echo "$kernel_updates" | while read line; do
            echo "  $line"
        done
    else
        log_success "No kernel updates available"
    fi
    
    # Check for other updates
    local total_updates=$(apt list --upgradable 2>/dev/null | wc -l)
    if [[ $total_updates -gt 0 ]]; then
        log_info "Total packages with updates: $total_updates"
    fi
}

# Show disk usage
show_disk_usage() {
    log_info "Disk Usage:"
    echo "  Boot partition: $(df -h /boot | tail -1 | awk '{print $5 " used (" $3 "/" $2 ")"}')"
    echo "  Root partition: $(df -h / | tail -1 | awk '{print $5 " used (" $3 "/" $2 ")"}')"
}

# Show kernel modules
show_kernel_modules() {
    log_info "Kernel Modules (loaded):"
    local modules=$(lsmod | head -10 | awk '{print "  " $1 ": " $2 " instances"}')
    if [[ -n "$modules" ]]; then
        echo "$modules"
    else
        log_warning "No kernel modules found"
    fi
}

# Show initramfs status
show_initramfs_status() {
    log_info "Initramfs Status:"
    local initramfs_files=$(ls -la /boot/initrd.img* 2>/dev/null || true)
    if [[ -n "$initramfs_files" ]]; then
        echo "$initramfs_files" | while read line; do
            echo "  $line"
        done
    else
        log_warning "No initramfs files found"
    fi
}

# Main function
main() {
    log_info "AI Camera Kernel Status Report"
    log_info "=============================="
    
    echo ""
    
    # Get system information
    get_system_info
    
    echo ""
    
    # Show installed kernels
    show_installed_kernels
    
    echo ""
    
    # Show boot configuration
    show_boot_config
    
    echo ""
    
    # Show update configuration
    show_update_config
    
    echo ""
    
    # Check for updates
    check_updates
    
    echo ""
    
    # Show disk usage
    show_disk_usage
    
    echo ""
    
    # Show kernel modules
    show_kernel_modules
    
    echo ""
    
    # Show initramfs status
    show_initramfs_status
    
    echo ""
    log_success "Kernel status report completed!"
    log_info "Useful commands:"
    log_info "  - Check for updates: /usr/local/bin/check-kernel-updates"
    log_info "  - Clean old kernels: /usr/local/bin/cleanup-old-kernels"
    log_info "  - Update system: sudo apt update && sudo apt upgrade"
}

# Run main function
main "$@"
