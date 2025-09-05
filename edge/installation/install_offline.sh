#!/bin/bash

# AI Camera v2.0.0 - Offline Installation Script
# This script performs a complete offline installation using locally downloaded packages

set -e

PACKAGES_DIR="/home/camuser/aicamera/edge/installation/local_packages"
DOWNLOAD_SCRIPT="/home/camuser/aicamera/edge/installation/download_packages.sh"
INSTALL_SCRIPT="/home/camuser/aicamera/edge/installation/install.sh"

echo "🚀 AI Camera v2.0.0 - Offline Installation"
echo "=========================================="
echo "📦 This script will perform a complete offline installation"
echo "📁 Local packages directory: $PACKAGES_DIR"
echo ""

# Check if we're in the right directory
if [ ! -f "$INSTALL_SCRIPT" ]; then
    echo "❌ Installation script not found: $INSTALL_SCRIPT"
    echo "📋 Please run this script from the AI Camera project root directory"
    exit 1
fi

# Function to check internet connectivity
check_internet() {
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Step 1: Check if packages are already downloaded
if [ -d "$PACKAGES_DIR" ] && [ -f "$PACKAGES_DIR/requirements_local.txt" ]; then
    echo "✅ Local packages already exist"
    echo "📦 Found $(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l) wheel files"
    echo ""
    read -p "🔄 Do you want to re-download packages? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        REDOWNLOAD=true
    else
        REDOWNLOAD=false
    fi
else
    REDOWNLOAD=true
fi

# Step 2: Download packages if needed
if [ "$REDOWNLOAD" = true ]; then
    echo "📦 Step 1: Downloading packages locally..."
    
    if [ ! -f "$DOWNLOAD_SCRIPT" ]; then
        echo "❌ Download script not found: $DOWNLOAD_SCRIPT"
        exit 1
    fi
    
    # Check internet connectivity
    if ! check_internet; then
        echo "❌ No internet connection detected"
        echo "📋 For offline installation, you need to download packages first"
        echo "📋 Please run this script when internet is available, or"
        echo "📋 Copy the local_packages directory from another machine"
        exit 1
    fi
    
    echo "🌐 Internet connection detected, downloading packages..."
    chmod +x "$DOWNLOAD_SCRIPT"
    "$DOWNLOAD_SCRIPT"
    
    if [ $? -eq 0 ]; then
        echo "✅ Packages downloaded successfully"
    else
        echo "❌ Package download failed"
        exit 1
    fi
else
    echo "✅ Using existing local packages"
fi

echo ""

# Step 3: Verify local packages
echo "📦 Step 2: Verifying local packages..."
if [ ! -d "$PACKAGES_DIR" ]; then
    echo "❌ Local packages directory not found: $PACKAGES_DIR"
    exit 1
fi

if [ ! -f "$PACKAGES_DIR/requirements_local.txt" ]; then
    echo "❌ Local requirements file not found"
    exit 1
fi

WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
if [ "$WHEEL_COUNT" -eq 0 ]; then
    echo "❌ No wheel files found in packages directory"
    exit 1
fi

echo "✅ Found $WHEEL_COUNT wheel files"
echo "✅ Local packages verification completed"

echo ""

# Step 4: Install system packages first (if script exists)
echo "📦 Step 3: Installing system packages..."
if [ -f "$PACKAGES_DIR/install_system_packages_offline.sh" ]; then
    echo "🔧 Installing system packages for offline setup..."
    chmod +x "$PACKAGES_DIR/install_system_packages_offline.sh"
    "$PACKAGES_DIR/install_system_packages_offline.sh"
    
    if [ $? -eq 0 ]; then
        echo "✅ System packages installed successfully"
    else
        echo "⚠️  System package installation had issues - continuing with Python installation"
    fi
else
    echo "⚠️  System package installation script not found"
    echo "📋 Please ensure system packages are installed manually:"
    echo "   sudo apt-get install python3-opencv python3-dev build-essential nginx"
fi

# Step 5: Update local requirements file to match downloaded packages
echo ""
echo "📦 Step 4: Updating local requirements file..."
echo "🔧 Ensuring local requirements match downloaded ARM64 wheels..."

# Create updated requirements file with correct versions
cat > "$PACKAGES_DIR/requirements_local.txt" << 'EOF'
# AI Camera v2.0.0 Local Dependencies
# All packages downloaded locally for offline installation

# Core Framework
Flask==3.1.2
Flask-SocketIO==5.3.6
python-socketio==5.9.0
Werkzeug==3.1.3

# Database
SQLAlchemy==2.0.43
alembic==1.12.1

# Image Processing
Pillow==11.3.0
opencv-python-headless==4.12.0.88
numpy==2.3.2

# Core Dependencies
typing-extensions==4.12.2
setuptools==75.6.0
wheel==0.45.1

# AI and OCR
easyocr==1.7.1
degirum==0.18.2
degirum-tools==0.19.1
degirum-cli==0.2.0

# WebSocket
websockets==12.0

# Database and Data Processing
pandas==2.3.2

# HTTP Requests
requests==2.32.3

# System Monitoring and Utilities
psutil==7.0.0
python-dotenv==1.0.1
matplotlib==3.9.4
setproctitle==1.3.6

# Development and Testing
notebook==7.4.5
ipykernel==6.29.5
pytest==8.3.4
pytest-cov==6.0.0

# WSGI Server
gunicorn==23.0.0

# Additional Dependencies
eventlet==0.40.3

# Experiment Dependencies
scikit-image==0.25.2

# Simulation Dependencies
faker==33.2.0

# Communication Dependencies
paho-mqtt==1.6.1
paramiko==3.4.0
websocket-client==1.8.0

# Local GitHub packages
hailo-apps-infra==0.2.0
EOF

echo "✅ Local requirements file updated with ARM64 wheel versions"

# Step 6: Perform offline installation
echo ""
echo "📦 Step 5: Performing offline installation..."
echo "🔧 Running installation with local packages..."

chmod +x "$INSTALL_SCRIPT"
"$INSTALL_SCRIPT" --local-packages --packages-dir "$PACKAGES_DIR"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Offline installation completed successfully!"
    echo "✅ AI Camera v2.0.0 is ready to use"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Check service status: sudo systemctl status aicamera_lpr.service"
    echo "   2. View service logs: sudo journalctl -u aicamera_lpr.service -f"
    echo "   3. Access web interface: http://localhost"
    echo "   4. Check health endpoint: http://localhost/health"
    echo ""
    echo "🔧 Troubleshooting:"
    echo "   - If camera issues: Check camera permissions and hardware"
    echo "   - If web interface issues: Check nginx status and logs"
    echo "   - If service issues: Check systemd service logs"
else
    echo ""
    echo "❌ Offline installation failed"
    echo "📋 Check the error messages above for details"
    echo "📋 Common troubleshooting steps:"
    echo "   1. Verify all local packages are present"
    echo "   2. Check virtual environment setup"
    echo "   3. Verify system permissions"
    echo "   4. Review installation logs"
    exit 1
fi
