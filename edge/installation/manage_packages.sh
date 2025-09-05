#!/bin/bash

# AI Camera v2.0.0 - Package Management Script
# This script helps manage local packages for offline installation

set -e

PACKAGES_DIR="/home/camuser/aicamera/edge/installation/local_packages"
DOWNLOAD_SCRIPT="/home/camuser/aicamera/edge/installation/download_packages.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Function to show help
show_help() {
    echo "AI Camera v2.0.0 - Package Management Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  download     Download all packages locally"
    echo "  update       Update existing local packages"
    echo "  list         List all local packages"
    echo "  clean        Clean local packages directory"
    echo "  verify       Verify local packages integrity"
    echo "  info         Show package information"
    echo "  help         Show this help message"
    echo ""
    echo "Options:"
    echo "  --force      Force operation (skip confirmations)"
    echo "  --packages-dir DIR  Specify packages directory (default: $PACKAGES_DIR)"
    echo ""
    echo "Examples:"
    echo "  $0 download                    # Download all packages"
    echo "  $0 update --force              # Update packages without confirmation"
    echo "  $0 list                        # List all local packages"
    echo "  $0 clean --force               # Clean packages directory"
    echo "  $0 verify                      # Verify package integrity"
}

# Function to download packages
download_packages() {
    print_info "Downloading packages to: $PACKAGES_DIR"
    
    if [ ! -f "$DOWNLOAD_SCRIPT" ]; then
        print_error "Download script not found: $DOWNLOAD_SCRIPT"
        exit 1
    fi
    
    chmod +x "$DOWNLOAD_SCRIPT"
    "$DOWNLOAD_SCRIPT"
    
    if [ $? -eq 0 ]; then
        print_status "Packages downloaded successfully"
    else
        print_error "Package download failed"
        exit 1
    fi
}

# Function to update packages
update_packages() {
    print_info "Updating local packages..."
    
    if [ ! -d "$PACKAGES_DIR" ]; then
        print_warning "Local packages directory not found, downloading packages..."
        download_packages
        return
    fi
    
    if [ "$FORCE" != true ]; then
        read -p "🔄 This will re-download all packages. Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Update cancelled"
            return
        fi
    fi
    
    print_info "Backing up existing packages..."
    BACKUP_DIR="${PACKAGES_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    cp -r "$PACKAGES_DIR" "$BACKUP_DIR"
    print_status "Backup created: $BACKUP_DIR"
    
    print_info "Downloading updated packages..."
    download_packages
    
    print_status "Packages updated successfully"
    print_info "Old packages backed up to: $BACKUP_DIR"
}

# Function to list packages
list_packages() {
    print_info "Local packages in: $PACKAGES_DIR"
    
    if [ ! -d "$PACKAGES_DIR" ]; then
        print_error "Local packages directory not found"
        exit 1
    fi
    
    echo ""
    echo "📦 Wheel files:"
    if ls "$PACKAGES_DIR"/*.whl >/dev/null 2>&1; then
        ls -la "$PACKAGES_DIR"/*.whl | awk '{print "  " $9 " (" $5 " bytes)"}'
    else
        print_warning "No wheel files found"
    fi
    
    echo ""
    echo "📋 Requirements file:"
    if [ -f "$PACKAGES_DIR/requirements_local.txt" ]; then
        print_status "requirements_local.txt exists"
        echo "  Package count: $(grep -c "^[A-Za-z]" "$PACKAGES_DIR/requirements_local.txt" || echo "0")"
    else
        print_warning "requirements_local.txt not found"
    fi
    
    echo ""
    echo "📊 Summary:"
    WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
    echo "  Total wheel files: $WHEEL_COUNT"
    echo "  Directory size: $(du -sh "$PACKAGES_DIR" | cut -f1)"
}

# Function to clean packages
clean_packages() {
    print_info "Cleaning local packages directory: $PACKAGES_DIR"
    
    if [ ! -d "$PACKAGES_DIR" ]; then
        print_warning "Local packages directory not found"
        return
    fi
    
    if [ "$FORCE" != true ]; then
        read -p "🗑️  This will delete all local packages. Continue? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Clean cancelled"
            return
        fi
    fi
    
    rm -rf "$PACKAGES_DIR"
    print_status "Local packages directory cleaned"
}

# Function to verify packages
verify_packages() {
    print_info "Verifying local packages..."
    
    if [ ! -d "$PACKAGES_DIR" ]; then
        print_error "Local packages directory not found"
        exit 1
    fi
    
    # Check requirements file
    if [ ! -f "$PACKAGES_DIR/requirements_local.txt" ]; then
        print_error "requirements_local.txt not found"
        exit 1
    fi
    
    # Check wheel files
    WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
    if [ "$WHEEL_COUNT" -eq 0 ]; then
        print_error "No wheel files found"
        exit 1
    fi
    
    # Check for corrupted wheels
    print_info "Checking wheel file integrity..."
    CORRUPTED=0
    for wheel in "$PACKAGES_DIR"/*.whl; do
        if [ -f "$wheel" ]; then
            if ! python3 -m zipfile -t "$wheel" >/dev/null 2>&1; then
                print_error "Corrupted wheel: $(basename "$wheel")"
                CORRUPTED=$((CORRUPTED + 1))
            fi
        fi
    done
    
    if [ "$CORRUPTED" -eq 0 ]; then
        print_status "All wheel files are valid"
    else
        print_error "$CORRUPTED corrupted wheel files found"
        exit 1
    fi
    
    print_status "Package verification completed successfully"
}

# Function to show package information
show_info() {
    print_info "AI Camera v2.0.0 Package Information"
    echo ""
    echo "📦 Package Management:"
    echo "  Local packages directory: $PACKAGES_DIR"
    echo "  Download script: $DOWNLOAD_SCRIPT"
    echo ""
    
    if [ -d "$PACKAGES_DIR" ]; then
        WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
        echo "📊 Current Status:"
        echo "  Wheel files: $WHEEL_COUNT"
        echo "  Directory size: $(du -sh "$PACKAGES_DIR" | cut -f1)"
        echo "  Last modified: $(stat -c %y "$PACKAGES_DIR" 2>/dev/null || echo "Unknown")"
    else
        echo "📊 Current Status:"
        echo "  Local packages: Not downloaded"
    fi
    
    echo ""
    echo "🔧 Available Commands:"
    echo "  $0 download    # Download all packages locally"
    echo "  $0 update      # Update existing packages"
    echo "  $0 list        # List all local packages"
    echo "  $0 verify      # Verify package integrity"
    echo "  $0 clean       # Clean packages directory"
}

# Parse command line arguments
COMMAND=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        download|update|list|clean|verify|info|help)
            COMMAND="$1"
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        --packages-dir)
            PACKAGES_DIR="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Execute command
case $COMMAND in
    download)
        download_packages
        ;;
    update)
        update_packages
        ;;
    list)
        list_packages
        ;;
    clean)
        clean_packages
        ;;
    verify)
        verify_packages
        ;;
    info)
        show_info
        ;;
    help|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac
