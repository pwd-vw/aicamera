#!/bin/bash
# AI Camera v2.0.0 - Check Boot Logo Status Script
# This script checks the current boot logo status

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

# Check Plymouth availability
check_plymouth() {
    if command -v plymouth >/dev/null 2>&1; then
        log_success "Plymouth is available"
        return 0
    else
        log_warning "Plymouth is not available"
        return 1
    fi
}

# Check current splash image
check_splash_image() {
    local splash_path="/usr/share/plymouth/themes/pix/splash.png"
    local backup_path="/usr/share/plymouth/themes/pix/splash.png.backup"
    
    if [[ ! -f "$splash_path" ]]; then
        log_error "Splash image not found: $splash_path"
        return 1
    fi
    
    log_info "Current splash image: $splash_path"
    log_info "File size: $(ls -lh "$splash_path" | awk '{print $5}')"
    log_info "Last modified: $(ls -lh "$splash_path" | awk '{print $6, $7, $8}')"
    
    # Check if backup exists
    if [[ -f "$backup_path" ]]; then
        log_info "Backup exists: $backup_path"
        log_info "Backup size: $(ls -lh "$backup_path" | awk '{print $5}')"
        log_info "Backup modified: $(ls -lh "$backup_path" | awk '{print $6, $7, $8}')"
        
        # Compare files
        if cmp -s "$splash_path" "$backup_path"; then
            log_success "Current splash image is the original Raspberry Pi logo"
            return 0
        else
            log_success "Current splash image is the AI Camera logo"
            return 1
        fi
    else
        log_warning "No backup found - cannot determine if logo is original or custom"
        return 2
    fi
}

# Check Plymouth theme
check_theme() {
    local theme_path="/etc/alternatives/default.plymouth"
    if [[ -L "$theme_path" ]]; then
        local target=$(readlink "$theme_path")
        log_info "Current Plymouth theme: $target"
        
        if [[ "$target" == *"pix"* ]]; then
            log_success "Plymouth theme is set to pix"
        else
            log_warning "Plymouth theme is not pix: $target"
        fi
    else
        log_warning "Plymouth theme link not found"
    fi
}

# Check initramfs
check_initramfs() {
    log_info "Checking initramfs..."
    if command -v update-initramfs >/dev/null 2>&1; then
        log_success "update-initramfs is available"
        
        # Check if initramfs files exist
        local initramfs_files=(
            "/boot/initrd.img-$(uname -r)"
            "/boot/firmware/initramfs8"
            "/boot/firmware/initramfs_2712"
        )
        
        for file in "${initramfs_files[@]}"; do
            if [[ -f "$file" ]]; then
                log_info "Initramfs file exists: $file"
                log_info "File size: $(ls -lh "$file" | awk '{print $5}')"
                log_info "Last modified: $(ls -lh "$file" | awk '{print $6, $7, $8}')"
            else
                log_warning "Initramfs file not found: $file"
            fi
        done
    else
        log_warning "update-initramfs not available"
    fi
}

# Main function
main() {
    log_info "AI Camera Boot Logo Status Check"
    log_info "================================"
    
    echo ""
    
    # Check Plymouth
    log_info "Checking Plymouth availability..."
    check_plymouth
    
    echo ""
    
    # Check splash image
    log_info "Checking splash image..."
    check_splash_image
    local splash_status=$?
    
    echo ""
    
    # Check theme
    log_info "Checking Plymouth theme..."
    check_theme
    
    echo ""
    
    # Check initramfs
    check_initramfs
    
    echo ""
    
    # Summary
    log_info "Boot Logo Status Summary:"
    log_info "========================="
    
    if [[ $splash_status -eq 0 ]]; then
        log_success "Status: Original Raspberry Pi logo is active"
        log_info "To set AI Camera logo: sudo ./scripts/setup_boot_logo.sh"
    elif [[ $splash_status -eq 1 ]]; then
        log_success "Status: AI Camera logo is active"
        log_info "To restore original logo: sudo ./scripts/restore_boot_logo.sh"
    else
        log_warning "Status: Cannot determine current logo status"
        log_info "To set AI Camera logo: sudo ./scripts/setup_boot_logo.sh"
        log_info "To restore original logo: sudo ./scripts/restore_boot_logo.sh"
    fi
    
    echo ""
    log_info "To test splash screen: sudo plymouth --show-splash --pid-file=/var/run/plymouth.pid"
    log_info "To quit splash screen: sudo plymouth --quit"
}

# Run main function
main "$@"
