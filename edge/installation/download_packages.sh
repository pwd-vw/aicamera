#!/bin/bash

# AI Camera v2.0.0 - Local Package Downloader
# This script downloads all stable packages locally for offline installation

set -e

PACKAGES_DIR="/home/camuser/aicamera/edge/installation/local_packages"
PYTHON_VERSION="3.11"
ARCH="aarch64"  # For Raspberry Pi 5

echo "🚀 Starting AI Camera v2.0.0 Package Download..."
echo "📦 Download directory: $PACKAGES_DIR"
echo "🐍 Python version: $PYTHON_VERSION"
echo "🏗️  Architecture: $ARCH"

# Create packages directory
mkdir -p "$PACKAGES_DIR"
cd "$PACKAGES_DIR"

# Function to download wheel files
download_wheel() {
    local package_name="$1"
    local version="$2"
    local extra_args="$3"
    
    echo "📦 Downloading $package_name==$version..."
    
    # Try to download wheel file
    if pip download --python-version "$PYTHON_VERSION" --platform linux_${ARCH} --only-binary=:all: --no-deps "$package_name==$version" $extra_args; then
        echo "✅ Downloaded $package_name==$version"
    else
        echo "⚠️  Failed to download wheel for $package_name==$version, trying source distribution..."
        pip download --python-version "$PYTHON_VERSION" --no-binary=:all: --no-deps "$package_name==$version" $extra_args
    fi
}

# Function to download from GitHub and create wheel
download_github_package() {
    local repo_url="$1"
    local package_name="$2"
    local version="$3"
    
    echo "📦 Downloading $package_name from GitHub..."
    
    # Clone the repository
    git clone --depth 1 --branch "$version" "$repo_url" "$package_name"
    
    # Create wheel
    cd "$package_name"
    python setup.py bdist_wheel
    cp dist/*.whl ../
    cd ..
    rm -rf "$package_name"
    
    echo "✅ Created wheel for $package_name"
}

echo "🔍 Downloading Python packages..."

# Core Framework packages
download_wheel "Flask" "3.1.2"
download_wheel "Flask-SocketIO" "5.3.6"
download_wheel "python-socketio" "5.9.0"
download_wheel "Werkzeug" "3.1.3"

# Database packages
download_wheel "SQLAlchemy" "2.0.23"
download_wheel "alembic" "1.12.1"

# Image Processing packages
download_wheel "Pillow" "10.4.0"
download_wheel "opencv-python" "4.8.1.78"
download_wheel "numpy" "1.24.3"

# Core Dependencies
download_wheel "typing-extensions" "4.15.0"
download_wheel "setuptools" "66.1.1"
download_wheel "wheel" "0.45.1"

# AI and OCR packages
download_wheel "easyocr" "1.7.1"
download_wheel "degirum" "0.18.2"
download_wheel "degirum-tools" "0.19.1"
download_wheel "degirum-cli" "0.2.0"

# WebSocket packages
download_wheel "websockets" "11.0.3"

# Database and Data Processing
download_wheel "pandas" "2.0.3"

# HTTP Requests
download_wheel "requests" "2.32.5"

# System Monitoring and Utilities
download_wheel "psutil" "7.0.0"
download_wheel "python-dotenv" "1.0.0"
download_wheel "matplotlib" "3.7.2"
download_wheel "setproctitle" "1.3.2"

# Development and Testing
download_wheel "notebook" "7.4.5"
download_wheel "ipykernel" "6.25.2"
download_wheel "pytest" "7.4.3"
download_wheel "pytest-cov" "4.1.0"

# WSGI Server
download_wheel "gunicorn" "23.0.0"

# Additional Dependencies
download_wheel "eventlet" "0.40.3"

# Experiment Dependencies
download_wheel "scikit-image" "0.21.0"

# Simulation Dependencies
download_wheel "faker" "37.6.0"

# Communication Dependencies
download_wheel "paho-mqtt" "1.6.1"
download_wheel "paramiko" "2.12.0"
download_wheel "websocket-client" "1.8.0"

echo "🔍 Downloading GitHub packages..."

# Download hailo-apps-infra from GitHub
download_github_package "https://github.com/hailo-ai/hailo-apps-infra.git" "hailo-apps-infra" "25.3.1"

echo "📋 Creating local requirements file..."

# Create a local requirements file with wheel paths
cat > requirements_local.txt << EOF
# AI Camera v2.0.0 Local Dependencies
# All packages downloaded locally for offline installation

# Core Framework
Flask==3.1.2
Flask-SocketIO==5.3.6
python-socketio==5.9.0
Werkzeug==3.1.3

# Database
SQLAlchemy==2.0.23
alembic==1.12.1

# Image Processing
Pillow==10.4.0
opencv-python==4.8.1.78
numpy==1.24.3

# Core Dependencies
typing-extensions==4.15.0
setuptools==66.1.1
wheel==0.45.1

# AI and OCR
easyocr==1.7.1
degirum>=0.18.2
degirum-tools==0.19.1
degirum-cli==0.2.0

# WebSocket
websockets==11.0.3

# Database and Data Processing
pandas==2.0.3

# HTTP Requests
requests==2.32.5

# System Monitoring and Utilities
psutil==7.0.0
python-dotenv==1.0.0
matplotlib==3.7.2
setproctitle==1.3.2

# Development and Testing
notebook==7.4.5
ipykernel==6.25.2
pytest==7.4.3
pytest-cov==4.1.0

# WSGI Server
gunicorn==23.0.0

# Additional Dependencies
eventlet==0.40.3

# Experiment Dependencies
scikit-image==0.21.0

# Simulation Dependencies
faker==37.6.0

# Communication Dependencies
paho-mqtt==1.6.1
paramiko==2.12.0
websocket-client==1.8.0

# Local GitHub packages
hailo-apps-infra==0.2.0
EOF

echo "📊 Package download summary:"
echo "📦 Total packages downloaded: $(ls -1 *.whl 2>/dev/null | wc -l)"
echo "📁 Download directory: $PACKAGES_DIR"
echo "📋 Local requirements file: requirements_local.txt"

echo ""
echo "✅ All packages downloaded successfully!"
echo "🚀 You can now run the installation with local packages:"
echo "   ./install.sh --local-packages"
echo ""
echo "📋 To update packages, run this script again:"
echo "   ./download_packages.sh"
