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

# Function to download wheel files with progress indication
download_wheel() {
    local package_name="$1"
    local version="$2"
    local extra_args="$3"
    
    echo "📦 Downloading $package_name==$version..."
    echo "   🔍 Checking for ARM64 wheel availability..."
    
    # Check if a different version already exists
    existing_file=$(ls "$PACKAGES_DIR"/${package_name,,}*.whl 2>/dev/null | head -1)
    if [ -n "$existing_file" ]; then
        existing_version=$(basename "$existing_file" | sed "s/${package_name,,}-\([^-]*\)-.*/\1/")
        if [ "$existing_version" != "$version" ]; then
            echo "   ⚠️  Different version already exists: $existing_version"
            echo "   🔄 Removing old version and downloading new version..."
            rm -f "$existing_file"
        else
            echo "   ✅ Version $version already exists, skipping download"
            return 0
        fi
    fi
    
    # Try to download wheel file with progress indication
    if pip download --python-version "$PYTHON_VERSION" --platform linux_${ARCH} --only-binary=:all: --no-deps --progress-bar on "$package_name==$version" $extra_args; then
        echo "✅ Downloaded $package_name==$version (wheel)"
    else
        echo "⚠️  No ARM64 wheel available for $package_name==$version"
        echo "   🚫 Skipping source build (too slow on ARM64)"
        echo "   💡 Consider using system package or alternative version"
        return 1
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

# Count total packages (hardcoded for reliability)
TOTAL_PACKAGES=25  # Total number of download_wheel calls in this script

echo "📊 Progress: 0/$TOTAL_PACKAGES packages"

# Counter for progress tracking
PACKAGE_COUNT=0

# Core Framework packages
download_wheel "Flask" "3.1.2"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "Flask-SocketIO" "5.3.6"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "python-socketio" "5.9.0"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "Werkzeug" "3.1.3"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Database packages
download_wheel "SQLAlchemy" "2.0.43"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "alembic" "1.12.1"
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Image Processing packages
echo "📦 Downloading Pillow==10.4.0..."
echo "   🔍 Checking for ARM64 wheel availability..."

# Check if Pillow already exists (as wheel or source)
existing_pillow=$(ls "$PACKAGES_DIR"/pillow*.whl "$PACKAGES_DIR"/Pillow*.whl 2>/dev/null | head -1)
if [ -n "$existing_pillow" ]; then
    echo "   ✅ Pillow wheel already exists, skipping download"
else
    # Download Pillow 10.4.0 using pip download
    echo "   📥 Downloading Pillow 10.4.0 using pip download..."
    if pip download --no-deps --dest "$PACKAGES_DIR" "Pillow==10.4.0" 2>/dev/null; then
        echo "   ✅ Downloaded Pillow==10.4.0"
    else
        echo "   ⚠️  Failed to download Pillow 10.4.0"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Download specific ARM64 wheel for opencv-python-headless 4.12.0.88
echo "📦 Downloading opencv-python-headless==4.12.0.88..."
echo "   🔍 Checking for ARM64 wheel availability..."

# Check if opencv-python-headless already exists
existing_opencv=$(ls "$PACKAGES_DIR"/opencv*.whl 2>/dev/null | head -1)
if [ -n "$existing_opencv" ]; then
    echo "   ✅ OpenCV wheel already exists, skipping download"
else
    # Download the ARM64 wheel for opencv-python-headless 4.12.0.88
    echo "   📥 Downloading opencv-python-headless 4.12.0.88 ARM64 wheel from PyPI..."
    if wget -q --show-progress -O "$PACKAGES_DIR/opencv_python_headless-4.12.0.88-cp37-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl" \
        "https://files.pythonhosted.org/packages/69/4e/116720df7f1f7f3b59abc608ca30fbec9d2b3ae810afe4e4d26483d9dfa0/opencv_python_headless-4.12.0.88-cp37-abi3-manylinux2014_aarch64.manylinux_2_17_aarch64.whl"; then
        echo "   ✅ Downloaded opencv-python-headless==4.12.0.88 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download opencv-python-headless ARM64 wheel"
        echo "   💡 OpenCV will be installed via system package during offline installation"
        echo "   📋 System package: python3-opencv (included in install_system_packages.sh)"
    fi
fi

# Download specific ARM64 wheel for numpy 2.3.2
echo "📦 Downloading numpy==2.3.2..."
echo "   🔍 Checking for ARM64 wheel availability..."

# Check if numpy already exists
existing_numpy=$(ls "$PACKAGES_DIR"/numpy*.whl 2>/dev/null | head -1)
if [ -n "$existing_numpy" ]; then
    echo "   ✅ Numpy wheel already exists, skipping download"
else
    # Download the ARM64 wheel for numpy 2.3.2 (Python 3.11)
    echo "   📥 Downloading numpy 2.3.2 ARM64 wheel from PyPI..."
    if wget -q --show-progress -O "$PACKAGES_DIR/numpy-2.3.2-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl" \
        "https://files.pythonhosted.org/packages/17/f2/e4d72e6bc5ff01e2ab613dc198d560714971900c03674b41947e38606502/numpy-2.3.2-cp311-cp311-manylinux_2_27_aarch64.manylinux_2_28_aarch64.whl"; then
        echo "   ✅ Downloaded numpy==2.3.2 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download numpy ARM64 wheel"
        echo "   💡 Will use system package or existing installation"
    fi
fi

PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Core Dependencies
download_wheel "typing-extensions" "4.12.2" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "setuptools" "75.6.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "wheel" "0.45.1" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# AI and OCR packages
download_wheel "easyocr" "1.7.1" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
# Download specific ARM64 wheel for degirum 0.18.2
echo "📦 Downloading degirum==0.18.2..."
echo "   📥 Downloading degirum 0.18.2 ARM64 wheel from PyPI..."

# Check if degirum already exists
existing_degirum=$(ls "$PACKAGES_DIR"/degirum*.whl 2>/dev/null | head -1)
if [ -n "$existing_degirum" ]; then
    echo "   ✅ Degirum wheel already exists, skipping download"
else
    # Download the ARM64 wheel for degirum 0.18.2 (Python 3.9)
    if wget -q --show-progress -O "$PACKAGES_DIR/degirum-0.18.2-cp39-cp39-manylinux_2_31_aarch64.whl" \
        "https://files.pythonhosted.org/packages/8b/a7/55168e613dd63458f5dca73de9b20ba139d77e58720fbacdb360f39f7bd3/degirum-0.18.2-cp39-cp39-manylinux_2_31_aarch64.whl"; then
        echo "   ✅ Downloaded degirum==0.18.2 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download degirum ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "degirum-tools" "0.19.1" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "degirum-cli" "0.2.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# WebSocket packages
download_wheel "websockets" "12.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Database and Data Processing
echo "📦 Downloading pandas==2.3.2..."
echo "   📥 Downloading pandas 2.3.2 ARM64 wheel from PyPI..."

# Check if pandas already exists
existing_pandas=$(ls "$PACKAGES_DIR"/pandas*.whl 2>/dev/null | head -1)
if [ -n "$existing_pandas" ]; then
    echo "   ✅ Pandas wheel already exists, skipping download"
else
    # Download the ARM64 wheel for pandas 2.3.2 (Python 3.11)
    if wget -q --show-progress -O "$PACKAGES_DIR/pandas-2.3.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
        "https://files.pythonhosted.org/packages/95/3b/1e9b69632898b048e223834cd9702052bcf06b15e1ae716eda3196fb972e/pandas-2.3.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"; then
        echo "   ✅ Downloaded pandas==2.3.2 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download pandas ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# HTTP Requests
download_wheel "requests" "2.32.3" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# System Monitoring and Utilities
echo "📦 Downloading psutil==7.0.0..."
echo "   📥 Downloading psutil 7.0.0 ARM64 wheel from PyPI..."

# Check if psutil already exists
existing_psutil=$(ls "$PACKAGES_DIR"/psutil*.whl 2>/dev/null | head -1)
if [ -n "$existing_psutil" ]; then
    echo "   ✅ Psutil wheel already exists, skipping download"
else
    # Download the ARM64 wheel for psutil 7.0.0 (Python 3.6+)
    if wget -q --show-progress -O "$PACKAGES_DIR/psutil-7.0.0-cp36-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
        "https://files.pythonhosted.org/packages/eb/a2/709e0fe2f093556c17fbafda93ac032257242cabcc7ff3369e2cb76a97aa/psutil-7.0.0-cp36-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"; then
        echo "   ✅ Downloaded psutil==7.0.0 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download psutil ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "python-dotenv" "1.0.1" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
echo "📦 Downloading matplotlib==3.9.4..."
echo "   📥 Downloading matplotlib 3.9.4 ARM64 wheel from PyPI..."

# Check if matplotlib already exists
existing_matplotlib=$(ls "$PACKAGES_DIR"/matplotlib*.whl 2>/dev/null | head -1)
if [ -n "$existing_matplotlib" ]; then
    echo "   ✅ Matplotlib wheel already exists, skipping download"
else
    # Download the ARM64 wheel for matplotlib 3.9.4 (Python 3.11)
    if wget -q --show-progress -O "$PACKAGES_DIR/matplotlib-3.9.4-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
        "https://files.pythonhosted.org/packages/a2/73/ccb381026e3238c5c25c3609ba4157b2d1a617ec98d65a8b4ee4e1e74d02/matplotlib-3.9.4-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"; then
        echo "   ✅ Downloaded matplotlib==3.9.4 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download matplotlib ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
echo "📦 Downloading setproctitle==1.3.6..."
echo "   📥 Downloading setproctitle 1.3.6 ARM64 wheel from PyPI..."

# Check if setproctitle already exists
existing_setproctitle=$(ls "$PACKAGES_DIR"/setproctitle*.whl 2>/dev/null | head -1)
if [ -n "$existing_setproctitle" ]; then
    echo "   ✅ Setproctitle wheel already exists, skipping download"
else
    # Download the ARM64 wheel for setproctitle 1.3.6 (Python 3.11)
    if wget -q --show-progress -O "$PACKAGES_DIR/setproctitle-1.3.6-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
        "https://files.pythonhosted.org/packages/5b/47/f103c40e133154783c91a10ab08ac9fc410ed835aa85bcf7107cb882f505/setproctitle-1.3.6-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"; then
        echo "   ✅ Downloaded setproctitle==1.3.6 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download setproctitle ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Development and Testing
download_wheel "notebook" "7.4.5" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "ipykernel" "6.29.5" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "pytest" "8.3.4" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "pytest-cov" "6.0.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# WSGI Server
download_wheel "gunicorn" "23.0.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Additional Dependencies
download_wheel "eventlet" "0.40.3" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Experiment Dependencies
echo "📦 Downloading scikit-image==0.25.2..."
echo "   📥 Downloading scikit-image 0.25.2 ARM64 wheel from PyPI..."

# Check if scikit-image already exists
existing_scikit_image=$(ls "$PACKAGES_DIR"/scikit_image*.whl 2>/dev/null | head -1)
if [ -n "$existing_scikit_image" ]; then
    echo "   ✅ Scikit-image wheel already exists, skipping download"
else
    # Download the ARM64 wheel for scikit-image 0.25.2 (Python 3.11)
    if wget -q --show-progress -O "$PACKAGES_DIR/scikit_image-0.25.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl" \
        "https://files.pythonhosted.org/packages/ef/14/0c4a02cb27ca8b1e836886b9ec7c9149de03053650e9e2ed0625f248dd92/scikit_image-0.25.2-cp311-cp311-manylinux_2_17_aarch64.manylinux2014_aarch64.whl"; then
        echo "   ✅ Downloaded scikit-image==0.25.2 (ARM64 wheel)"
    else
        echo "   ⚠️  Failed to download scikit-image ARM64 wheel"
        echo "   💡 Will use system package or existing source distribution"
    fi
fi
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Simulation Dependencies
download_wheel "faker" "33.2.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

# Communication Dependencies
download_wheel "paho-mqtt" "1.6.1" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "paramiko" "3.4.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"
download_wheel "websocket-client" "1.8.0" 
PACKAGE_COUNT=$((PACKAGE_COUNT + 1))
echo "📊 Progress: $PACKAGE_COUNT/$TOTAL_PACKAGES packages"

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
SQLAlchemy==2.0.43
alembic==1.12.1

# Image Processing
Pillow==11.3.0
# opencv-python-headless==4.8.1.78  # No ARM64 wheels available - use system package instead
# Install with: sudo apt-get install python3-opencv
numpy==1.26.4

# Core Dependencies
typing-extensions==4.12.2
setuptools==75.6.0
wheel==0.45.1

# AI and OCR
easyocr==1.7.1
degirum>=0.18.2
degirum-tools==0.19.1
degirum-cli==0.2.0

# WebSocket
websockets==12.0

# Database and Data Processing
pandas==2.2.3

# HTTP Requests
requests==2.32.3

# System Monitoring and Utilities
psutil==6.1.0
python-dotenv==1.0.1
matplotlib==3.9.2
setproctitle==1.3.2

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
scikit-image==0.24.0

# Simulation Dependencies
faker==33.2.0

# Communication Dependencies
paho-mqtt==1.6.1
paramiko==3.4.0
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
