#!/bin/bash

# Troubleshooting script for AI Camera v1.3 installation issues
# This script diagnoses and fixes common problems encountered during installation

set -e

echo "🔧 AI Camera v1.3 Installation Troubleshooter"
echo "=============================================="

# Function to check if running as root
check_root() {
    if [[ "$(id -u)" == "0" ]]; then
        echo "❌ This script should not be run as root"
        echo "📋 Please run as camuser: ./scripts/troubleshoot_installation.sh"
        exit 1
    fi
}

# Function to check virtual environment
check_venv() {
    echo "🔍 Checking virtual environment..."
    if [[ -z "$VIRTUAL_ENV" ]]; then
        echo "❌ Virtual environment not activated"
        echo "📋 Activating virtual environment..."
        source venv_hailo/bin/activate
        echo "✅ Virtual environment activated: $VIRTUAL_ENV"
    else
        echo "✅ Virtual environment active: $VIRTUAL_ENV"
    fi
}

# Function to fix nginx issues
fix_nginx() {
    echo "🔧 Fixing nginx issues..."
    
    # Stop nginx first
    sudo systemctl stop nginx 2>/dev/null || true
    
    # Fix permission issues
    sudo mkdir -p /run/nginx
    sudo chown www-data:www-data /run/nginx 2>/dev/null || true
    sudo chmod 755 /run/nginx
    
    sudo mkdir -p /var/cache/nginx
    sudo chown www-data:www-data /var/cache/nginx 2>/dev/null || true
    
    # Fix main nginx.conf for non-root users
    if [[ "$(id -u)" != "0" ]]; then
        echo "   Adjusting nginx configuration for non-root user..."
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup.$(date +%Y%m%d_%H%M%S) || true
        sudo sed -i 's/^user www-data;/# user www-data; # Commented for non-root installation/' /etc/nginx/nginx.conf || true
    fi
    
    # Test and start nginx
    if sudo nginx -t 2>/dev/null; then
        echo "   ✅ nginx configuration is valid"
        sudo systemctl start nginx
        echo "   ✅ nginx started successfully"
    else
        echo "   ⚠️  nginx configuration test failed - attempting to start anyway..."
        if sudo systemctl start nginx 2>/dev/null; then
            echo "   ✅ nginx started successfully (configuration test ignored)"
        else
            echo "   ❌ nginx failed to start"
            return 1
        fi
    fi
}

# Function to fix camera issues
fix_camera() {
    echo "🔧 Fixing camera issues..."
    
    # Check camera hardware
    echo "   Checking camera hardware..."
    if [[ -e "/dev/video0" ]] || [[ -e "/dev/video1" ]] || [[ -e "/dev/video2" ]]; then
        echo "   ✅ Camera device found"
    else
        echo "   ⚠️  No camera device found - camera features will be disabled"
        echo "   📋 This is normal if no camera is connected"
    fi
    
    # Check libcamera installation
    echo "   Checking libcamera installation..."
    if python -c "import libcamera; print('libcamera available')" 2>/dev/null; then
        echo "   ✅ libcamera available in Python"
    else
        echo "   ❌ libcamera not available - attempting to fix..."
        sudo apt-get update -y
        sudo apt-get install -y python3-libcamera python3-libcamera-dev libcamera-tools libcamera-apps || true
        
        # Recreate venv if needed
        if ! python -c "import libcamera; print('libcamera available')" 2>/dev/null; then
            echo "   ⚠️  Recreating virtual environment with system site-packages..."
            deactivate 2>/dev/null || true
            rm -rf venv_hailo
            python3 -m venv --system-site-packages venv_hailo
            source venv_hailo/bin/activate
            
            # Reinstall dependencies
            pip install --prefer-binary --no-build-isolation --no-cache-dir \
                "typing-extensions>=4.0.0" \
                "setuptools>=65.0.0" \
                "wheel>=0.40.0"
            
            pip install --prefer-binary --no-build-isolation --no-cache-dir -r v1_3/requirements.txt
            pip install --prefer-binary --no-build-isolation --no-cache-dir -r requirements.txt
        fi
    fi
    
    # Check camera pipeline configuration
    if [[ -f "/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml" ]]; then
        echo "   ✅ Camera pipeline configuration exists"
    else
        echo "   ⚠️  Camera pipeline configuration missing"
        echo "   📋 This may cause camera initialization issues"
    fi
}

# Function to fix service issues
fix_service() {
    echo "🔧 Fixing service issues..."
    
    # Stop service first
    sudo systemctl stop aicamera_lpr.service 2>/dev/null || true
    
    # Check if service file exists
    if [[ ! -f "/etc/systemd/system/aicamera_lpr.service" ]]; then
        echo "   ❌ Service file not found, copying from installation..."
        
        if [[ -f "systemd_service/aicamera_lpr.service" ]]; then
            sudo cp systemd_service/aicamera_lpr.service /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable aicamera_lpr.service
            echo "   ✅ Service file copied and enabled"
        else
            echo "   ❌ Service file not found in installation directory"
            return 1
        fi
    fi
    
    # Start service
    if sudo systemctl start aicamera_lpr.service; then
        echo "   ✅ Service started successfully"
        
        if sudo systemctl is-active --quiet aicamera_lpr.service; then
            echo "   ✅ Service is running"
            sudo systemctl status aicamera_lpr.service
        else
            echo "   ❌ Service failed to start"
            sudo systemctl status aicamera_lpr.service
            return 1
        fi
    else
        echo "   ❌ Failed to start service"
        return 1
    fi
    
    # Show recent logs
    echo ""
    echo "📋 Recent service logs:"
    sudo journalctl -u aicamera_lpr.service --no-pager -n 20
    
    echo ""
    echo "📋 Troubleshooting commands:"
    echo "   - Check service status: sudo systemctl status aicamera_lpr.service"
    echo "   - Check service logs: sudo journalctl -u aicamera_lpr.service -f"
}

# Function to validate web interface
validate_web_interface() {
    echo "🔍 Validating web interface..."
    
    max_retries=15
    retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        if curl -s -f http://localhost/health >/dev/null 2>&1; then
            echo "✅ Web interface is accessible"
            return 0
        else
            echo "   Attempt $((retry_count + 1))/$max_retries: Web interface not ready yet..."
            retry_count=$((retry_count + 1))
            sleep 3
        fi
    done
    
    echo "❌ Web interface validation failed after $max_retries attempts"
    echo "📋 Checking service logs..."
    sudo journalctl -u aicamera_lpr.service --no-pager -n 20
    return 1
}

# Function to run component validations
run_validations() {
    echo "🔍 Running component validations..."
    
    # EasyOCR validation
    if python edge/scripts/validate_easyocr.py; then
        echo "✅ EasyOCR validation passed"
    else
        echo "❌ EasyOCR validation failed"
    fi
    
    # Database validation
    if python edge/scripts/validate_database.py; then
        echo "✅ Database validation passed"
    else
        echo "❌ Database validation failed"
    fi
    
    # libcamera validation
    if python edge/scripts/validate_libcamera.py; then
        echo "✅ libcamera validation passed"
    else
        echo "❌ libcamera validation failed"
    fi
}

# Main troubleshooting function
main() {
    check_root
    check_venv
    
    echo ""
    echo "🔧 Starting troubleshooting process..."
    
    # Fix nginx issues
    if ! fix_nginx; then
        echo "❌ Failed to fix nginx issues"
    fi
    
    # Fix camera issues
    if ! fix_camera; then
        echo "❌ Failed to fix camera issues"
    fi
    
    # Fix service issues
    if ! fix_service; then
        echo "❌ Failed to fix service issues"
    fi
    
    # Validate web interface
    if ! validate_web_interface; then
        echo "❌ Web interface validation failed"
    fi
    
    # Run component validations
    run_validations
    
    echo ""
    echo "🎉 Troubleshooting completed!"
    echo "📋 Next steps:"
    echo "   - Check web interface: http://localhost"
    echo "   - Check service status: sudo systemctl status aicamera_lpr.service"
    echo "   - Check service logs: sudo journalctl -u aicamera_lpr.service -f"
    echo "   - Run validation: python scripts/validate_installation.py"
}

# Run main function
main "$@"

