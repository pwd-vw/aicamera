#!/bin/bash

# AI Camera v2.0.0 - Complete Offline Installation Script
# This script performs a complete offline installation including system packages

set -e

PACKAGES_DIR="/home/camuser/aicamera/edge/installation/local_packages"
DOWNLOAD_SCRIPT="/home/camuser/aicamera/edge/installation/download_packages.sh"
INSTALL_SCRIPT="/home/camuser/aicamera/edge/installation/install.sh"
SYSTEM_PACKAGES_SCRIPT="/home/camuser/aicamera/edge/installation/install_system_packages.sh"

echo "🚀 AI Camera v2.0.0 - Complete Offline Installation"
echo "=================================================="
echo "📦 This script will prepare everything for offline installation"
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

# Step 1: Download system packages list for offline installation
echo "📦 Step 1: Preparing system packages for offline installation..."

# Create system packages list
echo "📋 Creating system packages list for offline installation..."
cat > "$PACKAGES_DIR/system_packages.txt" << 'EOF'
# AI Camera v2.0.0 System Packages for Offline Installation
# Install these packages on the target system before running offline installation

# Core system packages
python3-dev
python3-pip
python3-venv
build-essential
cmake
pkg-config

# OpenCV system package (replaces pip opencv-python-headless)
python3-opencv

# Camera and libcamera packages
libcamera-dev
libcamera-tools
python3-libcamera
libcamera-apps

# Image processing libraries
libjpeg-dev
libtiff5-dev
libpng-dev
libavcodec-dev
libavformat-dev
libswscale-dev
libv4l-dev
libxvidcore-dev
libx264-dev
libgtk-3-dev
libatlas-base-dev
gfortran

# Build dependencies
libssl-dev
libffi-dev
libxml2-dev
libxslt1-dev
zlib1g-dev
libbz2-dev
libreadline-dev
libsqlite3-dev
libncurses5-dev
libncursesw5-dev
xz-utils
tk-dev
liblzma-dev
ninja-build

# Web server
nginx

# Optional packages
chromium-browser
hailo-all
EOF

echo "✅ System packages list created: $PACKAGES_DIR/system_packages.txt"

# Step 2: Download Python packages
echo ""
echo "📦 Step 2: Downloading Python packages..."

if [ ! -f "$DOWNLOAD_SCRIPT" ]; then
    echo "❌ Download script not found: $DOWNLOAD_SCRIPT"
    exit 1
fi

# Check internet connectivity
if ! check_internet; then
    echo "❌ No internet connection detected"
    echo "📋 For offline installation, you need to download packages first"
    echo "📋 Please run this script when internet is available"
    exit 1
fi

echo "🌐 Internet connection detected, downloading packages..."
chmod +x "$DOWNLOAD_SCRIPT"
"$DOWNLOAD_SCRIPT"

if [ $? -eq 0 ]; then
    echo "✅ Python packages downloaded successfully"
else
    echo "❌ Package download failed"
    exit 1
fi

# Step 3: Create offline installation instructions
echo ""
echo "📦 Step 3: Creating offline installation instructions..."

cat > "$PACKAGES_DIR/OFFLINE_INSTALLATION_INSTRUCTIONS.md" << 'EOF'
# AI Camera v2.0.0 - Offline Installation Instructions

## Prerequisites
- Target system must be running Ubuntu/Debian-based Linux
- Python 3.11+ must be installed
- Root/sudo access required

## Step 1: Install System Packages
On the target system (with internet), run:
```bash
# Update package lists
sudo apt-get update

# Install all system packages
sudo apt-get install -y $(cat system_packages.txt | grep -v '^#' | grep -v '^$' | tr '\n' ' ')
```

## Step 2: Copy Packages to Target System
Copy the entire `local_packages` directory to the target system:
```bash
# Copy to target system (replace with actual target path)
scp -r local_packages/ user@target-system:/path/to/aicamera/edge/installation/
```

## Step 3: Run Offline Installation
On the target system (without internet), run:
```bash
# Navigate to AI Camera directory
cd /path/to/aicamera

# Run offline installation
./edge/installation/install_offline.sh
```

## Troubleshooting

### OpenCV Issues
If OpenCV import fails:
```bash
# Verify system OpenCV is installed
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"

# If not working, reinstall system OpenCV
sudo apt-get install --reinstall python3-opencv
```

### Missing Dependencies
If Python packages fail to install:
```bash
# Check if all wheel files are present
ls -la local_packages/*.whl

# Verify requirements file
cat local_packages/requirements_local.txt
```

### System Package Issues
If system packages are missing:
```bash
# Install missing packages from the list
sudo apt-get install -y <missing-package-name>
```

## Package Contents
- **Python wheels**: All Python packages as wheel files
- **System packages list**: List of required system packages
- **Requirements file**: Local requirements for pip installation
- **Installation script**: Offline installation script

## Support
For issues, check:
1. System package installation
2. Python virtual environment setup
3. File permissions
4. Available disk space (minimum 2GB)
EOF

echo "✅ Offline installation instructions created: $PACKAGES_DIR/OFFLINE_INSTALLATION_INSTRUCTIONS.md"

# Step 4: Create system package installation script
echo ""
echo "📦 Step 4: Creating system package installation script..."

cat > "$PACKAGES_DIR/install_system_packages_offline.sh" << 'EOF'
#!/bin/bash

# AI Camera v2.0.0 - System Packages Installation for Offline Setup
# This script installs system packages required for offline installation

set -e

echo "🚀 Installing AI Camera v2.0.0 System Packages for Offline Setup..."
echo "📦 Installing system packages required for offline installation..."

# Update package lists
echo "🔄 Updating package lists..."
sudo apt-get update

# Install all packages from the list
echo "📦 Installing system packages..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    pkg-config \
    python3-opencv \
    libcamera-dev \
    libcamera-tools \
    python3-libcamera \
    libcamera-apps \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    liblzma-dev \
    ninja-build \
    nginx

echo "✅ System packages installed successfully!"
echo ""
echo "📋 OpenCV installation summary:"
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" 2>/dev/null || echo "⚠️  OpenCV not accessible - may need virtual environment setup"
echo ""
echo "🚀 System is now ready for offline AI Camera installation!"
EOF

chmod +x "$PACKAGES_DIR/install_system_packages_offline.sh"
echo "✅ System package installation script created: $PACKAGES_DIR/install_system_packages_offline.sh"

# Step 5: Create package verification script
echo ""
echo "📦 Step 5: Creating package verification script..."

cat > "$PACKAGES_DIR/verify_packages.sh" << 'EOF'
#!/bin/bash

# AI Camera v2.0.0 - Package Verification Script
# This script verifies that all required packages are available for offline installation

set -e

echo "🔍 AI Camera v2.0.0 - Package Verification"
echo "=========================================="

PACKAGES_DIR="$(dirname "$0")"
ERRORS=0

# Check if packages directory exists
if [ ! -d "$PACKAGES_DIR" ]; then
    echo "❌ Packages directory not found: $PACKAGES_DIR"
    exit 1
fi

echo "📁 Packages directory: $PACKAGES_DIR"

# Check Python wheel files
echo ""
echo "🔍 Checking Python wheel files..."
WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
if [ "$WHEEL_COUNT" -gt 0 ]; then
    echo "✅ Found $WHEEL_COUNT Python wheel files"
else
    echo "❌ No Python wheel files found"
    ((ERRORS++))
fi

# Check requirements file
echo ""
echo "🔍 Checking requirements file..."
if [ -f "$PACKAGES_DIR/requirements_local.txt" ]; then
    echo "✅ Requirements file found: requirements_local.txt"
    echo "📋 Packages in requirements: $(grep -c '^[^#]' "$PACKAGES_DIR/requirements_local.txt")"
else
    echo "❌ Requirements file not found: requirements_local.txt"
    ((ERRORS++))
fi

# Check system packages list
echo ""
echo "🔍 Checking system packages list..."
if [ -f "$PACKAGES_DIR/system_packages.txt" ]; then
    echo "✅ System packages list found: system_packages.txt"
    echo "📋 System packages: $(grep -c '^[^#]' "$PACKAGES_DIR/system_packages.txt")"
else
    echo "❌ System packages list not found: system_packages.txt"
    ((ERRORS++))
fi

# Check installation instructions
echo ""
echo "🔍 Checking installation instructions..."
if [ -f "$PACKAGES_DIR/OFFLINE_INSTALLATION_INSTRUCTIONS.md" ]; then
    echo "✅ Installation instructions found: OFFLINE_INSTALLATION_INSTRUCTIONS.md"
else
    echo "❌ Installation instructions not found: OFFLINE_INSTALLATION_INSTRUCTIONS.md"
    ((ERRORS++))
fi

# Check system package installation script
echo ""
echo "🔍 Checking system package installation script..."
if [ -f "$PACKAGES_DIR/install_system_packages_offline.sh" ]; then
    echo "✅ System package installation script found: install_system_packages_offline.sh"
else
    echo "❌ System package installation script not found: install_system_packages_offline.sh"
    ((ERRORS++))
fi

# Summary
echo ""
echo "📊 Verification Summary:"
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All packages and files are ready for offline installation"
    echo "🚀 You can now copy this directory to the target system"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Copy local_packages/ to target system"
    echo "   2. Run install_system_packages_offline.sh on target system"
    echo "   3. Run install_offline.sh on target system"
else
    echo "❌ Found $ERRORS issues - please fix before offline installation"
    exit 1
fi
EOF

chmod +x "$PACKAGES_DIR/verify_packages.sh"
echo "✅ Package verification script created: $PACKAGES_DIR/verify_packages.sh"

# Step 6: Run verification
echo ""
echo "📦 Step 6: Verifying packages..."
"$PACKAGES_DIR/verify_packages.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Complete offline installation package prepared successfully!"
    echo "✅ All files are ready for offline installation"
    echo ""
    echo "📋 Package contents:"
    echo "   📁 $PACKAGES_DIR/"
    echo "      ├── *.whl files (Python packages)"
    echo "      ├── requirements_local.txt (Python requirements)"
    echo "      ├── system_packages.txt (System packages list)"
    echo "      ├── install_system_packages_offline.sh (System package installer)"
    echo "      ├── verify_packages.sh (Package verifier)"
    echo "      └── OFFLINE_INSTALLATION_INSTRUCTIONS.md (Instructions)"
    echo ""
    echo "🚀 Next steps for offline installation:"
    echo "   1. Copy the entire local_packages/ directory to target system"
    echo "   2. On target system: ./local_packages/install_system_packages_offline.sh"
    echo "   3. On target system: ./edge/installation/install_offline.sh"
    echo ""
    echo "📊 Package size: $(du -sh "$PACKAGES_DIR" | cut -f1)"
    echo "📊 Total files: $(find "$PACKAGES_DIR" -type f | wc -l)"
else
    echo ""
    echo "❌ Package verification failed"
    echo "📋 Please check the errors above and fix them"
    exit 1
fi
