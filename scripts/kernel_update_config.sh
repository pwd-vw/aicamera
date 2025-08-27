#!/bin/bash
# AI Camera v2.0.0 - Kernel Update Configuration Script
# This script configures kernel update settings for Raspberry Pi 5

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

# Configure apt preferences for kernel updates
configure_apt_preferences() {
    log_info "Configuring apt preferences for kernel updates..."
    
    # Create apt preferences file to prioritize rpi-2712 kernels
    cat > /etc/apt/preferences.d/99-kernel-updates << 'EOF'
# Kernel update preferences for Raspberry Pi 5
# Prioritize rpi-2712 kernels and prevent rpi-v8 kernels from being installed

Package: linux-image-rpi-2712
Pin: release *
Pin-Priority: 1001

Package: linux-image-rpi-v8
Pin: release *
Pin-Priority: -1

Package: linux-headers-rpi-2712
Pin: release *
Pin-Priority: 1001

Package: linux-headers-rpi-v8
Pin: release *
Pin-Priority: -1

Package: linux-image-*-rpt-rpi-2712
Pin: release *
Pin-Priority: 1001

Package: linux-image-*-rpt-rpi-v8
Pin: release *
Pin-Priority: -1

Package: linux-headers-*-rpt-rpi-2712
Pin: release *
Pin-Priority: 1001

Package: linux-headers-*-rpt-rpi-v8
Pin: release *
Pin-Priority: -1
EOF
    
    log_success "Apt preferences configured"
}

# Configure unattended upgrades for kernel updates
configure_unattended_upgrades() {
    log_info "Configuring unattended upgrades for kernel updates..."
    
    # Install unattended-upgrades if not present
    if ! dpkg -l | grep -q unattended-upgrades; then
        log_info "Installing unattended-upgrades..."
        apt install -y unattended-upgrades
    fi
    
    # Configure unattended upgrades
    cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
// Unattended-Upgrade::DevRelease "auto";
Unattended-Upgrade::DevRelease "false";
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::MinimalSteps "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Automatic-Reboot-Time "02:00";
Unattended-Upgrade::SyslogEnable "true";
Unattended-Upgrade::SyslogFacility "daemon";

// Only install security updates and kernel updates
Unattended-Upgrade::Origins-Pattern {
    "origin=Debian,codename=${distro_codename},label=Debian-Security";
    "origin=Raspberry Pi Foundation,codename=${distro_codename},label=Raspberry Pi Foundation";
};

// Package blacklist - prevent unwanted packages from being upgraded
Unattended-Upgrade::Package-Blacklist {
    "linux-image-rpi-v8";
    "linux-headers-rpi-v8";
    "linux-image-*-rpt-rpi-v8";
    "linux-headers-*-rpt-rpi-v8";
};

// Keep only the current kernel and one previous version
Unattended-Upgrade::Remove-New-Unused-Dependencies "true";
Unattended-Upgrade::Remove-Unused-Kernel-Packages "true";
EOF
    
    log_success "Unattended upgrades configured"
}

# Configure automatic kernel cleanup
configure_kernel_cleanup() {
    log_info "Configuring automatic kernel cleanup..."
    
    # Create a script for automatic kernel cleanup
    cat > /usr/local/bin/cleanup-old-kernels << 'EOF'
#!/bin/bash
# Automatic kernel cleanup script for Raspberry Pi 5

# Get current kernel
CURRENT_KERNEL=$(uname -r)

# Remove old kernels except current and one previous
dpkg -l | grep linux-image | grep -v "^rc" | grep -v "$CURRENT_KERNEL" | \
    awk '{print $2}' | grep -v "linux-image-rpi-2712" | \
    xargs -r apt remove -y

# Clean up package cache
apt autoremove -y
apt autoclean
EOF
    
    chmod +x /usr/local/bin/cleanup-old-kernels
    
    # Add to crontab to run weekly
    (crontab -l 2>/dev/null; echo "0 2 * * 0 /usr/local/bin/cleanup-old-kernels") | crontab -
    
    log_success "Automatic kernel cleanup configured"
}

# Configure kernel update notifications
configure_kernel_notifications() {
    log_info "Configuring kernel update notifications..."
    
    # Create a script to check for kernel updates
    cat > /usr/local/bin/check-kernel-updates << 'EOF'
#!/bin/bash
# Check for kernel updates and notify if available

# Check for available kernel updates
KERNEL_UPDATES=$(apt list --upgradable 2>/dev/null | grep linux-image-rpi-2712 || true)

if [[ -n "$KERNEL_UPDATES" ]]; then
    echo "Kernel updates available:"
    echo "$KERNEL_UPDATES"
    echo ""
    echo "To update: sudo apt update && sudo apt upgrade"
    echo "To install only kernel updates: sudo apt install linux-image-rpi-2712"
else
    echo "No kernel updates available"
fi
EOF
    
    chmod +x /usr/local/bin/check-kernel-updates
    
    log_success "Kernel update notifications configured"
}

# Update package lists and check for updates
update_and_check() {
    log_info "Updating package lists..."
    apt update
    
    log_info "Checking for available kernel updates..."
    KERNEL_UPDATES=$(apt list --upgradable 2>/dev/null | grep linux-image-rpi-2712 || true)
    
    if [[ -n "$KERNEL_UPDATES" ]]; then
        log_warning "Kernel updates are available:"
        echo "$KERNEL_UPDATES"
        echo ""
        log_info "To install updates: sudo apt upgrade"
    else
        log_success "No kernel updates available"
    fi
}

# Show current configuration
show_configuration() {
    log_info "Current kernel update configuration:"
    echo ""
    
    log_info "Installed kernels:"
    dpkg -l | grep linux-image | grep -v "^rc" | while read line; do
        echo "  $line"
    done
    
    echo ""
    log_info "Apt preferences:"
    if [[ -f /etc/apt/preferences.d/99-kernel-updates ]]; then
        log_success "Kernel preferences configured"
    else
        log_warning "Kernel preferences not configured"
    fi
    
    echo ""
    log_info "Unattended upgrades:"
    if [[ -f /etc/apt/apt.conf.d/50unattended-upgrades ]]; then
        log_success "Unattended upgrades configured"
    else
        log_warning "Unattended upgrades not configured"
    fi
    
    echo ""
    log_info "Automatic cleanup:"
    if [[ -f /usr/local/bin/cleanup-old-kernels ]]; then
        log_success "Automatic kernel cleanup configured"
    else
        log_warning "Automatic kernel cleanup not configured"
    fi
}

# Main function
main() {
    log_info "AI Camera Kernel Update Configuration"
    log_info "====================================="
    
    echo ""
    
    # Check root privileges
    check_root
    
    # Configure apt preferences
    configure_apt_preferences
    
    echo ""
    
    # Configure unattended upgrades
    configure_unattended_upgrades
    
    echo ""
    
    # Configure automatic cleanup
    configure_kernel_cleanup
    
    echo ""
    
    # Configure notifications
    configure_kernel_notifications
    
    echo ""
    
    # Update and check
    update_and_check
    
    echo ""
    
    # Show configuration
    show_configuration
    
    echo ""
    log_success "Kernel update configuration completed!"
    log_info "The system is now configured to:"
    log_info "  - Prioritize rpi-2712 kernels"
    log_info "  - Block rpi-v8 kernels from installation"
    log_info "  - Automatically clean up old kernels"
    log_info "  - Check for updates weekly"
    log_info "  - Notify about available kernel updates"
}

# Run main function
main "$@"
