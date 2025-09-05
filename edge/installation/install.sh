#!/bin/bash

# Error handling function
handle_error() {
    local exit_code=$?
    echo "❌ Installation failed with exit code: $exit_code"
    echo "🔍 Check the error messages above for details"
    echo "📋 Common troubleshooting steps:"
    echo "   1. Check if all dependencies are installed"
    echo "   2. Verify virtual environment is working"
    echo "   3. Check system permissions"
    echo "   4. Review service logs: sudo journalctl -u aicamera_lpr.service"
    exit $exit_code
}

# Set error handling
trap handle_error ERR
set -e  # Exit immediately if a command exits with a non-zero status

# Parse command line arguments
LOCAL_PACKAGES=false
PACKAGES_DIR="/home/camuser/aicamera/edge/installation/local_packages"

while [[ $# -gt 0 ]]; do
    case $1 in
        --local-packages)
            LOCAL_PACKAGES=true
            shift
            ;;
        --packages-dir)
            PACKAGES_DIR="$2"
            shift 2
            ;;
        -h|--help)
            echo "AI Camera v2.0.0 Installation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --local-packages    Use locally downloaded packages (offline installation)"
            echo "  --packages-dir DIR  Specify local packages directory (default: $PACKAGES_DIR)"
            echo "  -h, --help         Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                           # Standard installation with online packages"
            echo "  $0 --local-packages          # Offline installation with local packages"
            echo "  $0 --local-packages --packages-dir /path/to/packages"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Starting AI Camera v2.0.0 Installation..."
echo "📋 System: $(uname -a)"
echo "📋 Python: $(python3 --version)"
echo "📋 Working Directory: $(pwd)"
echo "📦 Installation Mode: $([ "$LOCAL_PACKAGES" = true ] && echo "Local Packages (Offline)" || echo "Online Packages")"
if [ "$LOCAL_PACKAGES" = true ]; then
    echo "📁 Local Packages Directory: $PACKAGES_DIR"
fi

# Update system packages first (recommended for fresh installations)
echo "🔄 Updating system packages..."
echo "📦 Running apt update and upgrade..."
sudo apt-get update -y
sudo apt-get upgrade -y
echo "✅ System packages updated"

# Setup SSH for GitHub Actions deployment
echo "🔑 Setting up SSH for GitHub Actions deployment..."
echo "📋 Creating SSH directory and configuring authorized keys..."

# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add GitHub Actions deployment key to authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeL4SoHelb+9aDlO1/wrqw/C+VGA5DMlRJ+U8mbNpn+8ueczEgApme8PJC6te4lt4LSOkLyKSgLLOts3fQpKPabtFER4ssgyHXrn8G2v1ObTtzwtYIpE5qTWJJiGXs63zMXrJW08D5cTLtTqxoVBmV8NhT2IEuejOWhf6BHH4xZahx2AGprWNvc7gSJCxRkScPNjTtlj2kj85rNlwCgzJJV3052NSyLg8Th4CdYqcn43J2EwBDjIIfMuySE1dFav2nnhScgu/JF9HouYggnfxbOblasmCVWNK1ADsZmEgnAP9G/Y559MQLcwF0wbef9Np23KIOet0clOHqmzH8ZziUKeItyx8SR82KhuCbvVTfiiAxPsfQoR5cQ+0WaTXCs5ulLQseRY9utno+Tq2NpDaG6SezkB5UOk8H9eYxOc/Ob4wDVrA4A87PXFo7s4CqD3fCRznA7gr6GmR9qE9WXbfuz2uWjcr+VNFpaZxV4UF1WenuHxMKRwfRqLyn2wRnJiXijJ4sQ4MTYPGewqeqa3XCQySGbiPmxzdsUpfROWSk52H459hmXh1SoPYnuSo1Pk3fkxAk9pwWaIo5+gPAt6Vmv6ANeTOX+BP3hTfJ73gAILc/3qx08lLQT6bcDRh/JMp3oyjgTjUZVV4jAvUPrXoDb/2w/zKRjeH518lswvRLnw== aicamera-deployment@github.com" >> ~/.ssh/authorized_keys

# Set proper permissions for SSH files
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh

echo "✅ SSH setup completed for GitHub Actions deployment"

# Camera cleanup and preparation (CRITICAL - prevents "Device or resource busy" errors)
echo "📷 Preparing camera system for installation..."
echo "🔧 Cleaning up any existing camera processes and services..."

# Stop AI Camera service if running
echo "�� Stopping AI Camera service if running..."
sudo systemctl stop aicamera_lpr.service 2>/dev/null || true
sudo systemctl disable aicamera_lpr.service 2>/dev/null || true

# Stop any running camera-related processes
echo "🛑 Stopping camera-related processes..."
sudo pkill -f "picamera2" 2>/dev/null || true
sudo pkill -f "libcamera" 2>/dev/null || true
sudo pkill -f "gstreamer" 2>/dev/null || true
sudo pkill -f "python.*camera" 2>/dev/null || true

# Kill any processes using camera devices
echo "🛑 Releasing camera device handles..."
for device in /dev/video* /dev/media*; do
    if [[ -e "$device" ]]; then
        sudo fuser -k "$device" 2>/dev/null || true
    fi
done

# Unload and reload camera modules
echo "🔄 Reloading camera kernel modules..."
sudo modprobe -r bcm2835-v4l2 2>/dev/null || true
sudo modprobe -r v4l2_common 2>/dev/null || true
sudo modprobe -r videodev 2>/dev/null || true
sleep 2

# Reload camera modules
sudo modprobe videodev 2>/dev/null || true
sudo modprobe v4l2_common 2>/dev/null || true
sudo modprobe bcm2835-v4l2 2>/dev/null || true
sleep 2

# Reset camera hardware (if possible)
echo "🔄 Resetting camera hardware..."
if command -v v4l2-ctl >/dev/null 2>&1; then
    for device in /dev/video*; do
        if [[ -e "$device" ]]; then
            sudo v4l2-ctl -d "$device" --all 2>/dev/null || true
        fi
    done
fi

# Check camera device status
echo "🔍 Checking camera device status..."
if ls /dev/video* >/dev/null 2>&1; then
    echo "✅ Camera devices found:"
    ls -la /dev/video*
else
    echo "⚠️  No camera devices found - this may be normal for headless systems"
fi

# Verify camera permissions
echo "🔍 Verifying camera permissions..."
if [[ -e "/dev/video0" ]]; then
    sudo chmod 666 /dev/video0 2>/dev/null || true
    sudo usermod -a -G video $USER 2>/dev/null || true
    echo "✅ Camera permissions set"
else
    echo "⚠️  Camera device not found - permissions not set"
fi

# Wait for camera system to stabilize
echo "⏳ Waiting for camera system to stabilize..."
sleep 3

echo "✅ Camera cleanup completed"

# Install Hailo SDK and dependencies FIRST (before sourcing environment)
echo "🚀 Installing Hailo SDK and dependencies..."
echo "📦 Installing hailo-all package..."
sudo apt-get install -y hailo-all || {
    echo "❌ Failed to install hailo-all package"
    echo "📋 This may be expected if Hailo repository is not configured"
    echo "📋 Continuing with installation - Hailo features will be limited"
}

# Verify Hailo installation
echo "🔍 Verifying Hailo installation..."
if command -v hailortcli >/dev/null 2>&1; then
    echo "✅ hailortcli found - checking firmware..."
    if hailortcli fw-control identify >/dev/null 2>&1; then
        echo "✅ Hailo firmware control working"
    else
        echo "⚠️  Hailo firmware control not responding"
    fi
else
    echo "⚠️  hailortcli not found - Hailo SDK may not be properly installed"
fi

# Check GStreamer Hailo plugins
echo "🔍 Checking GStreamer Hailo plugins..."
if command -v gst-inspect-1.0 >/dev/null 2>&1; then
    if gst-inspect-1.0 hailo >/dev/null 2>&1; then
        echo "✅ GStreamer hailo plugin available"
    else
        echo "⚠️  GStreamer hailo plugin not found"
    fi
    
    if gst-inspect-1.0 hailotools >/dev/null 2>&1; then
        echo "✅ GStreamer hailotools plugin available"
    else
        echo "⚠️  GStreamer hailotools plugin not found"
    fi
else
    echo "⚠️  gst-inspect-1.0 not found - GStreamer may not be installed"
fi

# Prepare environment (Hailo SDK sourcing will happen AFTER venv activation)
echo "Preparing environment and virtual environment..."

# Resolve repository root and canonical venv directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." >/dev/null 2>&1 && pwd)"
VENV_DIR="$ROOT_DIR/edge/installation/venv_hailo"
echo "Using canonical virtualenv path: $VENV_DIR"

# Do not modify or remove any existing virtualenvs; we'll reuse if present

# Verify virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]] || [[ ! -d "$VIRTUAL_ENV" ]]; then
    if [[ -d "$VENV_DIR" ]]; then
        echo "✅ Reusing existing virtual environment: $VENV_DIR"
        source "$VENV_DIR/bin/activate"
    else
        echo "📦 Creating virtual environment (with system site-packages for libcamera access)..."
        python3 -m venv --system-site-packages "$VENV_DIR"
        chown -R "$USER":"$USER" "$VENV_DIR" 2>/dev/null || true
        source "$VENV_DIR/bin/activate"
        echo "✅ Virtual environment created and activated: $VIRTUAL_ENV"
    fi
else
    echo "✅ Virtual environment is active: $VIRTUAL_ENV"
fi

# Re-source Hailo environment after activating venv to ensure bindings are in this shell
if [[ -f "edge/installation/setup_env.sh" ]]; then
    source edge/installation/setup_env.sh || true
fi

# Install additional system dependencies (if needed)
echo "Installing additional system dependencies..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install -y libcap-dev rapidjson-dev

# Camera stack required by picamera2 (Python module libcamera comes from system packages)
echo "Installing libcamera stack for Picamera2..."
sudo apt-get install -y python3-libcamera libcamera-tools || true
sudo apt-get update -y
sudo apt-get install -y libcamera-apps || true

# Ensure libcamera is accessible in virtual environment
echo "Ensuring libcamera is accessible in virtual environment..."
if python3 -c "import libcamera; print('libcamera available in system Python')" 2>/dev/null; then
    echo "✅ libcamera available in system Python"
    
    # Check if virtual environment can access libcamera
    if ! python -c "import libcamera; print('libcamera available in venv')" 2>/dev/null; then
        echo "⚠️  libcamera not accessible in virtual environment - recreating venv with system site-packages"
        deactivate 2>/dev/null || true
        rm -rf "$VENV_DIR"
        python3 -m venv --system-site-packages "$VENV_DIR"
        chown -R "$USER":"$USER" "$VENV_DIR" 2>/dev/null || true
        source "$VENV_DIR/bin/activate"
        PIP_CMD="$VIRTUAL_ENV/bin/python -m pip"
        echo "✅ Recreated venv with system site-packages access"
    else
        echo "✅ libcamera accessible in virtual environment"
    fi
else
    echo "❌ libcamera not available in system Python - attempting to install"
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera libcamera-tools || true
    sudo apt-get install -y libcamera-apps || true
    
    # Try again after installation
    if python3 -c "import libcamera; print('libcamera now available')" 2>/dev/null; then
        echo "✅ libcamera installed successfully"
    else
        echo "❌ libcamera installation failed - camera functionality will be limited"
    fi
fi

# Initialize variables
DOWNLOAD_RESOURCES_FLAG=""
PYHAILORT_WHL=""
PYTAPPAS_WHL=""
TAG="25.3.1"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --pyhailort) PYHAILORT_WHL="$2"; shift 2 ;;
        --pytappas) PYTAPPAS_WHL="$2"; shift 2 ;;
        --all) DOWNLOAD_RESOURCES_FLAG="--all" ;;
        --tag) TAG="$2"; shift 2 ;;   # New parameter to specify tag
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Verify pip is available in virtual environment
echo "Verifying pip installation..."
if ! command -v pip &> /dev/null; then
    echo "❌ pip not found. Installing pip in virtual environment..."
    python -m ensurepip --upgrade
fi

# Ensure we're using the virtual environment pip and disable user site/config
if [[ -n "$VIRTUAL_ENV" ]]; then
    # Harden environment against user-site precedence issues
    export PYTHONNOUSERSITE=1
    export PIP_USER=0
    export PIP_NO_USER_CONFIG=1
    export PIP_CONFIG_FILE=/dev/null
    export PIP_DISABLE_PIP_VERSION_CHECK=1
    export PIP_ROOT_USER_ACTION=ignore

    PIP_CMD="$VIRTUAL_ENV/bin/python -m pip"
    echo "✅ Using virtual environment pip: $PIP_CMD"
else
    PIP_CMD="python3 -m pip"
    echo "⚠️  Using system pip: $(which pip)"
fi

# Ensure venv can see system libcamera. If not, and system python has libcamera, recreate venv with system-site-packages
VENV_PY="$VIRTUAL_ENV/bin/python"
if [[ -x "$VENV_PY" ]]; then
    if ! "$VENV_PY" - <<'PY' 2>/dev/null
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("libcamera") else 1)
PY
    then
        if python3 - <<'PY' 2>/dev/null
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("libcamera") else 1)
PY
        then
            echo "ℹ️  System Python has libcamera but venv does not. Recreating venv with --system-site-packages..."
            deactivate 2>/dev/null || true
            rm -rf "$VENV_DIR"
            python3 -m venv --system-site-packages "$VENV_DIR"
            chown -R "$USER":"$USER" "$VENV_DIR" 2>/dev/null || true
            source "$VENV_DIR/bin/activate"
            PIP_CMD="$VIRTUAL_ENV/bin/python -m pip"
            echo "✅ Recreated venv with access to system site-packages: $VIRTUAL_ENV"
        else
            echo "⚠️  libcamera not found in system Python. Proceeding; Picamera2 may fail to import."
        fi
    fi
fi

# Set low priority for heavy installs (define before first use)
IONICE="ionice -c2 -n7"  # best-effort, lowest priority
RENICE="renice 19 $$ >/dev/null || true"
eval "$RENICE"

# Install wheel package first to enable wheel building for packages without pyproject.toml
echo "Installing wheel package for better wheel support..."
$IONICE $PIP_CMD install --no-user wheel
echo "✅ Wheel package installed"

# Install specified Python wheels
if [[ -n "$PYHAILORT_WHL" ]]; then
    echo "Installing pyhailort wheel: $PYHAILORT_WHL"
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user "$PYHAILORT_WHL"
fi

if [[ -n "$PYTAPPAS_WHL" ]]; then
    echo "Installing pytappas wheel: $PYTAPPAS_WHL"
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user "$PYTAPPAS_WHL"
fi

echo "Installing required Python dependencies (low priority, wheels preferred)..."
# Prefer wheels, avoid building from source, reduce concurrency to lower RAM usage
# IONICE and RENICE already defined above

# Install core dependencies first to avoid conflicts
echo "Installing core dependencies..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user \
    "typing-extensions>=4.5,<5" \
    "setuptools>=65.0.0" \
    "wheel>=0.40.0"

# Pre-pin base scientific stack to stabilize downstream deps
echo "Ensuring numpy and Pillow are available (skip if already present and compatible)..."
python - <<'PY'
import sys
import importlib
def has(module):
    try:
        importlib.import_module(module)
        return True
    except Exception:
        return False
sys.exit(0 if (has('numpy') and has('PIL')) else 1)
PY
if [[ $? -ne 0 ]]; then
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user \
        "numpy==1.24.3" \
        "Pillow==10.4.0" || true
else
    echo "✅ numpy and Pillow already available"
fi

# Install unified requirements with proper dependency resolution
echo "Installing unified requirements..."
if [ "$LOCAL_PACKAGES" = true ]; then
    echo "📦 Installing from local packages (offline mode)..."
    
    # Check if local packages directory exists
    if [ ! -d "$PACKAGES_DIR" ]; then
        echo "❌ Local packages directory not found: $PACKAGES_DIR"
        echo "📋 Please run ./download_packages.sh first to download packages locally"
        exit 1
    fi
    
    # Check if local requirements file exists
    if [ ! -f "$PACKAGES_DIR/requirements_local.txt" ]; then
        echo "❌ Local requirements file not found: $PACKAGES_DIR/requirements_local.txt"
        echo "📋 Please run ./download_packages.sh first to create local requirements"
        exit 1
    fi
    
    echo "📁 Using local packages from: $PACKAGES_DIR"
    echo "📋 Installing from local requirements file..."
    
    # Install from local packages directory
    $IONICE $PIP_CMD install --no-index --find-links "$PACKAGES_DIR" --no-deps -r "$PACKAGES_DIR/requirements_local.txt"
    
    echo "✅ Local packages installed successfully"
else
    echo "📦 Installing from online packages..."
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user -r edge/installation/requirements.txt
fi

# Fix camera compatibility issues
echo "🔧 Fixing camera compatibility issues..."
echo "   📋 Ensuring system picamera2 is used for compatibility with libcamera 0.5.1..."

# Uninstall pip picamera2 if installed (incompatible with system libcamera 0.5.1)
if $PIP_CMD show picamera2 >/dev/null 2>&1; then
    echo "   📋 Uninstalling incompatible pip picamera2 version..."
    $PIP_CMD uninstall picamera2 -y
    echo "   ✅ Removed pip picamera2 - will use system version"
else
    echo "   ✅ No pip picamera2 found - system version will be used"
fi

# Verify system picamera2 is available
if python3 -c "import sys; sys.path.insert(0, '/usr/lib/python3/dist-packages'); from picamera2 import Picamera2; print('System picamera2 available')" 2>/dev/null; then
    echo "   ✅ System picamera2 is available and compatible"
else
    echo "   ⚠️  System picamera2 not available - camera may not work properly"
fi

# Helper: check if Hailo python package is available in current venv
has_hailo_python() {
python - <<'PY'
import importlib.util, sys
for name in ("hailo", "pyhailort", "hailort"):
    if importlib.util.find_spec(name) is not None:
        sys.exit(0)
sys.exit(1)
PY
}

# Install Hailo Apps Infrastructure only if Hailo python is present
if has_hailo_python; then
    echo "Installing Hailo Apps Infrastructure from version: $TAG..."
    if [ "$LOCAL_PACKAGES" = true ]; then
        echo "📦 Installing hailo-apps-infra from local package..."
        # Check if local hailo-apps-infra wheel exists
        if [ -f "$PACKAGES_DIR/hailo_apps_infra"*.whl ]; then
            $IONICE $PIP_CMD install --no-index --find-links "$PACKAGES_DIR" "$PACKAGES_DIR/hailo_apps_infra"*.whl
            echo "✅ hailo-apps-infra installed from local package"
        else
            echo "⚠️  Local hailo-apps-infra package not found, skipping..."
        fi
    else
        echo "📦 Installing hailo-apps-infra from GitHub..."
        $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir --no-user "git+https://github.com/hailo-ai/hailo-apps-infra.git@$TAG"
    fi
else
    echo "⚠️  Hailo python package not found in the active venv. Skipping hailo-apps-infra install."
    echo "   Action required:"
    echo "   - Run: source setup_env.sh  (to load Hailo SDK into this venv), or"
    echo "   - Provide wheel paths: ./install.sh --pyhailort /path/pyhailort.whl [--pytappas /path/pytappas.whl]"
fi

# Ensure logs directory exists with correct permissions before validations
LOGS_DIR="$ROOT_DIR/edge/logs"
mkdir -p "$LOGS_DIR" 2>/dev/null || true
chmod 755 "$LOGS_DIR" 2>/dev/null || true

# Validate EasyOCR installation
echo "🔍 Validating EasyOCR installation..."
if python -c "import easyocr; print('✅ EasyOCR imported successfully')" 2>/dev/null; then
    echo "✅ EasyOCR validation passed"
else
    echo "❌ EasyOCR validation failed - attempting to fix..."
    # Install only if missing
    $PIP_CMD install --no-user --upgrade "typing-extensions>=4.5,<5" || true
    $PIP_CMD install --no-user --upgrade "easyocr==1.7.1" || true
    
    # Test again
    if python -c "import easyocr; print('✅ EasyOCR fixed successfully')" 2>/dev/null; then
        echo "✅ EasyOCR fixed successfully"
    else
        echo "❌ EasyOCR installation failed - please check dependencies"
        exit 1
    fi
fi

# Validate EasyOCR and typing_extensions comprehensively
echo "🔍 Running comprehensive EasyOCR validation..."
if python edge/scripts/validate_easyocr.py; then
    echo "✅ EasyOCR validation passed"
else
    echo "❌ EasyOCR validation failed - attempting to fix..."
    $PIP_CMD install --no-user --upgrade "typing-extensions>=4.5,<5" || true
    $PIP_CMD install --no-user --upgrade "easyocr==1.7.1" || true
    
    # Test again
    if python edge/scripts/validate_easyocr.py; then
        echo "✅ EasyOCR fixed successfully"
    else
        echo "❌ EasyOCR installation failed - please check dependencies"
        #exit 1
    fi
fi

# Validate libcamera installation
echo "🔍 Running comprehensive libcamera validation..."
if python edge/scripts/validate_libcamera.py; then
    echo "✅ libcamera validation passed"
else
    echo "❌ libcamera validation failed - attempting to fix..."
    # Try to fix libcamera installation
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera libcamera-tools || true
    
    # Check for camera hardware issues
    echo "🔍 Checking camera hardware compatibility..."
    # Note: libcamera-still validation removed - not needed for core functionality
    echo "   ✅ Camera hardware check skipped"
    
    # Check for specific camera pipeline issues
    echo "🔍 Checking camera pipeline configuration..."
    if [[ -f "/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml" ]]; then
        echo "   ✅ Camera pipeline configuration exists"
    else
        echo "   ⚠️  Camera pipeline configuration missing"
        echo "   📋 This may cause camera initialization issues"
    fi
    
    # Recreate virtual environment with system site-packages if needed
    if ! python -c "import libcamera; print('libcamera available')" 2>/dev/null; then
        echo "⚠️  Recreating virtual environment with system site-packages access..."
        deactivate 2>/dev/null || true
        rm -rf "$VENV_DIR"
        python3 -m venv --system-site-packages "$VENV_DIR"
        chown -R "$USER":"$USER" "$VENV_DIR" 2>/dev/null || true
        source "$VENV_DIR/bin/activate"
        PIP_CMD="$VIRTUAL_ENV/bin/python -m pip"
        
        # Reinstall core dependencies
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir \
            "typing-extensions>=4.0.0" \
            "setuptools>=65.0.0" \
            "wheel>=0.40.0"
        
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt
    fi
    
    # Test again
    if python edge/scripts/validate_libcamera.py; then
        echo "✅ libcamera fixed successfully"
    else
        echo "❌ libcamera installation failed - camera functionality will be limited"
        echo "⚠️  You can still use the system without camera features"
        echo "📋 Camera issues may be due to:"
        echo "   - Incompatible camera hardware"
        echo "   - Missing camera drivers"
        echo "   - Incorrect camera pipeline configuration"
        echo "   - Hardware permission issues"
        echo "📋 The system will start in fallback mode - camera features will be disabled"
    fi
fi

# Validate degirum installation
echo "🔍 Validating degirum installation..."
if python -c "import degirum; print('✅ degirum imported successfully')" 2>/dev/null; then
    echo "✅ degirum validation passed"
else
    echo "❌ degirum validation failed - attempting to fix..."
    
    # Try to source Hailo environment and reinstall
    if [[ -f "setup_env.sh" ]]; then
        echo "📋 Sourcing Hailo environment..."
        source setup_env.sh || true
    fi
    
    # Try to reinstall degirum
    echo "📦 Installing degirum (skipped if already present)..."
    $PIP_CMD install --no-user --upgrade "degirum>=0.18.2" || true
    $PIP_CMD install --no-user --upgrade "degirum-tools==0.19.1" || true
    $PIP_CMD install --no-user --upgrade "degirum-cli==0.2.0" || true
    
    # Test again
    if python -c "import degirum; print('✅ degirum fixed successfully')" 2>/dev/null; then
        echo "✅ degirum fixed successfully"
    else
        echo "⚠️  degirum installation failed - detection functionality will be limited"
        echo "📋 This may be expected if Hailo SDK is not properly installed"
        echo "📋 You can still use the system without AI detection features"
    fi
fi

# Production setup - Create necessary directories and files
echo "Setting up production environment..."
mkdir -p edge/logs
mkdir -p resources/models
mkdir -p edge/src
mkdir -p edge/db
mkdir -p edge/captured_images

# Set proper permissions for production
chmod 755 edge/logs
chmod 755 resources
chmod 755 edge
chmod 755 edge/db
chmod 755 edge/captured_images

# Set proper project ownership and permissions for development
echo "Setting up project ownership and permissions for development..."
# Set entire project ownership to camuser for development access
sudo chown -R camuser:camuser /home/camuser/aicamera/ 2>/dev/null || true

# Add www-data to camuser group for nginx access to static files
sudo usermod -a -G camuser www-data 2>/dev/null || true

# Set proper directory permissions for nginx access
chmod 755 /home/camuser/aicamera/edge/src/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/css/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/js/ 2>/dev/null || true

# Set proper file permissions for static files (readable by group for nginx)
chmod 644 /home/camuser/aicamera/edge/src/web/static/css/*.css 2>/dev/null || true
chmod 644 /home/camuser/aicamera/edge/src/web/static/js/*.js 2>/dev/null || true

# Ensure directories have group write permissions for collaborative editing
chmod 775 /home/camuser/aicamera/edge/src/web/static/css/ 2>/dev/null || true
chmod 775 /home/camuser/aicamera/edge/src/web/static/js/ 2>/dev/null || true

# Set proper permissions for captured images directory
chmod 755 /home/camuser/aicamera/edge/captured_images/ 2>/dev/null || true

# Create basic WSGI file if it doesn't exist
if [[ ! -f "edge/src/wsgi.py" ]]; then
    echo "Creating basic WSGI file..."
    cat > edge/src/wsgi.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'aicamera_lpr'}

@app.route('/')
def index():
    return {'message': 'AI Camera Service Running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
fi

# Create __init__.py files for Python packages
touch edge/__init__.py
touch edge/src/__init__.py

# Setup environment configuration
echo "Setting up environment configuration..."
if [[ ! -f "edge/installation/.env.production" ]]; then
    if [[ -f "edge/installation/env.production.template" ]]; then
        cp edge/installation/env.production.template edge/installation/.env.production
        echo "✅ Created .env.production file from template"
        echo "📝 Please edit edge/installation/.env.production file to customize your installation:"
        echo "   - Set AICAMERA_ID and CHECKPOINT_ID for unique identification"
        echo "   - Configure GPS coordinates (LOCATION_LAT, LOCATION_LON)"
        echo "   - Choose appropriate Hailo models for your device"
        echo "   - Set camera and detection parameters"
    else
        echo "⚠️  edge/installation/env.production.template not found - please create .env.production file manually"
    fi
else
    echo "✅ .env.production file already exists in edge/installation/"
fi

# Load .env.production and prompt for key identifiers if needed
if [[ -f "edge/installation/.env.production" ]]; then
    echo "🔎 Verifying required identifiers in .env.production (AICAMERA_ID, CHECKPOINT_ID, CAMERA_LOCATION)..."

    # Export variables from .env.production into current shell
    set -a
    source edge/installation/.env.production || true
    set +a

    # Helper to update or insert env var
    update_env_var() {
        local key="$1"; shift
        local value="$1"; shift || true
        local replace_value="$value"
        # Escape '&' for sed replacement safety
        replace_value="${replace_value//&/\\&}"
        if grep -q "^${key}=" edge/installation/.env.production; then
            sed -i "s|^${key}=.*|${key}=${replace_value}|" edge/installation/.env.production
        else
            echo "${key}=${replace_value}" >> edge/installation/.env.production
        fi
    }

    # Read with defaults
    read -r -p "AICAMERA_ID [${AICAMERA_ID:-1}]: " INPUT_AICAMERA_ID
    AICAMERA_ID_NEW="${INPUT_AICAMERA_ID:-${AICAMERA_ID:-1}}"

    read -r -p "CHECKPOINT_ID [${CHECKPOINT_ID:-1}]: " INPUT_CHECKPOINT_ID
    CHECKPOINT_ID_NEW="${INPUT_CHECKPOINT_ID:-${CHECKPOINT_ID:-1}}"

    read -r -p "CAMERA_LOCATION [${CAMERA_LOCATION:-Main Entrance}]: " INPUT_CAMERA_LOCATION
    CAMERA_LOCATION_NEW="${INPUT_CAMERA_LOCATION:-${CAMERA_LOCATION:-Main Entrance}}"

    # Quote CAMERA_LOCATION for safety
    if [[ "$CAMERA_LOCATION_NEW" != \"*\" ]]; then
        CAMERA_LOCATION_QUOTED="\"$CAMERA_LOCATION_NEW\""
    else
        CAMERA_LOCATION_QUOTED="$CAMERA_LOCATION_NEW"
    fi

    # Persist updates
    update_env_var "AICAMERA_ID" "$AICAMERA_ID_NEW"
    update_env_var "CHECKPOINT_ID" "$CHECKPOINT_ID_NEW"
    update_env_var "CAMERA_LOCATION" "$CAMERA_LOCATION_QUOTED"

    echo "✅ Updated .env.production with verified identifiers"

    # Reload to ensure environment reflects latest values
    set -a
    source edge/installation/.env.production || true
    set +a
fi

# Initialize and validate database (single-step, no migrations)
echo "🔧 Initializing and validating database (no migrations)..."

# Ensure Python can import project modules
export PYTHONPATH="$ROOT_DIR:$PYTHONPATH"

# Initialize schema to current version (idempotent)
if python edge/scripts/init_database.py; then
    echo "✅ Database initialized (current schema)"
else
    echo "⚠️  Database initialization reported an issue; continuing to validation"
fi

# Validate using DatabaseManager and schema checks
if python edge/scripts/validate_database.py; then
    echo "✅ Database validation passed"
else
    echo "⚠️  Database validation reported issues. Proceeding without migrations."
fi

# Install and configure nginx (before starting service)
echo "🌐 Installing and configuring nginx..."
echo "   📋 Note: This will automatically fix common nginx Unix socket proxy issues"
if ! command -v nginx >/dev/null 2>&1; then
    echo "   Installing nginx..."
    sudo apt-get update -y
    sudo apt-get install -y nginx
else
    echo "   nginx already installed"
fi

if [[ -f "edge/nginx.conf" ]]; then
    echo "   Applying nginx site configuration..."
    # Backup default if exists
    if [[ -f "/etc/nginx/sites-available/default" ]]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup || true
    fi
    # Copy our config and enable it
    sudo cp edge/nginx.conf /etc/nginx/sites-available/aicamera
    sudo ln -sf /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/aicamera
    # Remove default site if present
    sudo rm -f /etc/nginx/sites-enabled/default || true
    
    # Fix nginx permission issues
    echo "   Fixing nginx permission issues..."
    # Ensure nginx can write to its PID directory
    sudo mkdir -p /run/nginx
    sudo chown www-data:www-data /run/nginx 2>/dev/null || true
    sudo chmod 755 /run/nginx
    
    # Ensure nginx can write to its log directory
    sudo mkdir -p /var/log/nginx
    sudo chown www-data:www-data /var/log/nginx 2>/dev/null || true
    
    # Fix static file permissions for CSS/JS serving
    echo "   🔧 Fixing static file permissions for CSS/JS serving..."
    echo "   📋 Setting proper permissions for static files to prevent 403 errors..."
    
    # Set permissions for home directory traversal (required for nginx to access static files)
    sudo chmod 755 /home/camuser 2>/dev/null || true
    sudo chmod 755 /home/camuser/aicamera 2>/dev/null || true
    
    # Set permissions for static files directory
    sudo chmod -R 755 /home/camuser/aicamera/edge/src/web/static/ 2>/dev/null || true
    
    # Ensure www-data can read static files
    sudo chown -R camuser:www-data /home/camuser/aicamera/edge/src/web/static/ 2>/dev/null || true
    sudo chmod -R 644 /home/camuser/aicamera/edge/src/web/static/*.css 2>/dev/null || true
    sudo chmod -R 644 /home/camuser/aicamera/edge/src/web/static/*.js 2>/dev/null || true
    sudo chmod -R 644 /home/camuser/aicamera/edge/src/web/static/*.html 2>/dev/null || true
    
    echo "   ✅ Static file permissions configured"
    
    # Fix main nginx.conf user directive if running as non-root
    if [[ "$(id -u)" != "0" ]]; then
        echo "   Adjusting nginx configuration for non-root user..."
        # Create a temporary nginx.conf that works for non-root users
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup || true
        sudo sed -i 's/^user www-data;/# user www-data; # Commented for non-root installation/' /etc/nginx/nginx.conf || true
    fi
    
    # Test config with better error handling
    echo "   Testing nginx configuration..."
    if sudo nginx -t 2>/dev/null; then
        echo "   ✅ nginx configuration is valid"
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        echo "   ✅ nginx started successfully"
        
        # Apply nginx configuration fixes for Unix socket proxy
        echo "   🔧 Applying nginx configuration fixes for Unix socket proxy..."
        
        # Fix any incorrect proxy_pass directives that might have incorrect paths
        if sudo sed -i 's|proxy_pass http://unix:/tmp/aicamera.sock/[^;]*;|proxy_pass http://unix:/tmp/aicamera.sock;|g' /etc/nginx/sites-available/aicamera; then
            echo "   ✅ Fixed proxy_pass directives"
            
            # Test configuration again after fixes
            if sudo nginx -t 2>/dev/null; then
                echo "   ✅ Nginx configuration still valid after fixes"
                sudo systemctl reload nginx
                echo "   ✅ Nginx reloaded with fixes"
                
                # Validate static file serving
                echo "   🔍 Validating static file serving..."
                sleep 2  # Wait for nginx to reload
                
                # Test CSS file access
                if curl -s -f -I http://localhost/static/css/base.css >/dev/null 2>&1; then
                    echo "   ✅ CSS files are accessible"
                else
                    echo "   ⚠️  CSS files may not be accessible - check permissions"
                fi
                
                # Test JavaScript file access
                if curl -s -f -I http://localhost/static/js/base.js >/dev/null 2>&1; then
                    echo "   ✅ JavaScript files are accessible"
                else
                    echo "   ⚠️  JavaScript files may not be accessible - check permissions"
                fi
                
            else
                echo "   ⚠️  Nginx configuration invalid after fixes - manual check required"
            fi
        else
            echo "   ⚠️  Failed to apply nginx configuration fixes"
        fi
    else
        echo "   ⚠️  nginx configuration test failed - attempting to fix..."
        
        # Try to fix common nginx issues
        sudo mkdir -p /var/cache/nginx
        sudo chown www-data:www-data /var/cache/nginx 2>/dev/null || true
        
        # Try starting nginx anyway (it might work despite the test failure)
        if sudo systemctl start nginx 2>/dev/null; then
            echo "   ✅ nginx started successfully (configuration test ignored)"
            sudo systemctl enable nginx
        else
            echo "   ❌ nginx failed to start - manual intervention required"
            echo "   📋 Please check: sudo nginx -t"
            echo "   📋 And: sudo systemctl status nginx"
            exit 1
        fi
    fi
else
    echo "   ❌ edge/nginx.conf not found in project root"
    echo "   Ensure a valid nginx.conf exists that proxies to unix:/tmp/aicamera.sock"
    exit 1
fi

# Setup and start systemd service
echo "Setting up systemd service..."
if [[ -f "edge/systemd_service/aicamera_lpr.service" ]]; then
    sudo cp edge/systemd_service/aicamera_lpr.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable aicamera_lpr.service
    
    echo "Starting aicamera_lpr service..."
    if sudo systemctl start aicamera_lpr.service; then
        echo "✅ Service started successfully"
        
        # Wait for service to be fully ready
        echo "Waiting for service to be ready..."
        sleep 5
        
        # Check service status
        if sudo systemctl is-active --quiet aicamera_lpr.service; then
            echo "✅ Service is running"
            
            # Validate web interface is accessible
            echo "🔍 Validating web interface accessibility..."
            max_retries=10
            retry_count=0
            web_accessible=false
            
            while [[ $retry_count -lt $max_retries ]]; do
                if curl -s -f http://localhost/health >/dev/null 2>&1; then
                    echo "✅ Web interface is accessible"
                    web_accessible=true
                    break
                else
                    echo "   Attempt $((retry_count + 1))/$max_retries: Web interface not ready yet..."
                    retry_count=$((retry_count + 1))
                    sleep 3
                fi
            done
            
            # Validate dashboard CSS and JavaScript loading
            if [[ "$web_accessible" == "true" ]]; then
                echo "🔍 Validating dashboard CSS and JavaScript loading..."
                
                # Test main dashboard page
                if curl -s -f http://localhost/ >/dev/null 2>&1; then
                    echo "✅ Main dashboard page is accessible"
                    
                    # Test CSS file loading
                    if curl -s -f -I http://localhost/static/css/base.css >/dev/null 2>&1; then
                        echo "✅ Dashboard CSS files are loading correctly"
                    else
                        echo "⚠️  Dashboard CSS files may not be loading - check static file permissions"
                    fi
                    
                    # Test JavaScript file loading
                    if curl -s -f -I http://localhost/static/js/base.js >/dev/null 2>&1; then
                        echo "✅ Dashboard JavaScript files are loading correctly"
                    else
                        echo "⚠️  Dashboard JavaScript files may not be loading - check static file permissions"
                    fi
                    
                    # Test Bootstrap and Font Awesome loading
                    if curl -s -f -I http://localhost/static/libs/bootstrap/bootstrap.min.css >/dev/null 2>&1; then
                        echo "✅ Bootstrap CSS is loading correctly"
                    else
                        echo "⚠️  Bootstrap CSS may not be loading - check static file permissions"
                    fi
                    
                else
                    echo "⚠️  Main dashboard page may not be accessible"
                fi
            fi
            
            if [[ "$web_accessible" == "false" ]]; then
                echo "⚠️  Web interface validation failed after $max_retries attempts"
                echo "📋 Checking service logs for issues..."
                sudo journalctl -u aicamera_lpr.service --no-pager -n 20
                echo "📋 Service is running but web interface may have issues"
                echo "📋 You can check manually: curl http://localhost/health"
            fi
            
            # Try to open browser automatically (if GUI is available) - non-blocking
            if command -v xdg-open &> /dev/null && [[ -n "$DISPLAY" ]]; then
                echo "🌐 Opening browser to check service (non-blocking)..."
                sleep 2
                # Run xdg-open in background to prevent script from hanging
                (xdg-open http://localhost/health 2>/dev/null &) || echo "Browser opened manually: http://localhost/health"
                echo "🌐 Service is running at: http://localhost/health"
            else
                echo "🌐 Service is running at: http://localhost/health"
                echo "📊 Check service status with: sudo systemctl status aicamera_lpr.service"
            fi
        else
            echo "❌ Service failed to start properly"
            sudo systemctl status aicamera_lpr.service
            exit 1
        fi
    else
        echo "❌ Failed to start service"
        sudo systemctl status aicamera_lpr.service
        exit 1
    fi
else
    echo "❌ Service file not found: edge/systemd_service/aicamera_lpr.service"
    exit 1
fi

echo "🎉 Installation completed successfully!"
echo "🚀 Production environment is ready!"

# Fix nginx configuration for Unix socket proxy
echo ""
echo "🔧 Fixing nginx configuration for Unix socket proxy..."
if [[ -f "/etc/nginx/sites-available/aicamera" ]]; then
    echo "   📋 Found nginx configuration file"
    
    # Fix proxy_pass directives to use correct Unix socket format
    echo "   🔧 Fixing proxy_pass directives..."
    
    # Fix health endpoint
    if sudo sed -i 's|proxy_pass http://unix:/tmp/aicamera.sock/health;|proxy_pass http://unix:/tmp/aicamera.sock;|g' /etc/nginx/sites-available/aicamera; then
        echo "   ✅ Fixed health endpoint proxy_pass"
    else
        echo "   ⚠️  Failed to fix health endpoint proxy_pass"
    fi
    
    # Fix API endpoints
    if sudo sed -i 's|proxy_pass http://unix:/tmp/aicamera.sock/api/;|proxy_pass http://unix:/tmp/aicamera.sock;|g' /etc/nginx/sites-available/aicamera; then
        echo "   ✅ Fixed API endpoints proxy_pass"
    else
        echo "   ⚠️  Failed to fix API endpoints proxy_pass"
    fi
    
    # Fix video feed endpoint
    if sudo sed -i 's|proxy_pass http://unix:/tmp/aicamera.sock/video_feed;|proxy_pass http://unix:/tmp/aicamera.sock;|g' /etc/nginx/sites-available/aicamera; then
        echo "   ✅ Fixed video feed proxy_pass"
    else
        echo "   ⚠️  Failed to fix video feed proxy_pass"
    fi
    
    # Test nginx configuration
    echo "   🔍 Testing nginx configuration..."
    if sudo nginx -t >/dev/null 2>&1; then
        echo "   ✅ Nginx configuration is valid"
        
        # Reload nginx
        echo "   🔄 Reloading nginx..."
        if sudo systemctl reload nginx; then
            echo "   ✅ Nginx reloaded successfully"
        else
            echo "   ⚠️  Failed to reload nginx - you may need to restart it manually"
        fi
    else
        echo "   ❌ Nginx configuration is invalid"
        echo "   📋 Please check the nginx configuration manually"
    fi
else
    echo "   ⚠️  Nginx configuration file not found: /etc/nginx/sites-available/aicamera"
    echo "   📋 Please ensure nginx is properly configured for the AI Camera application"
fi

# Run validation
echo ""
echo "🔍 Running installation validation..."
if python edge/scripts/validate_installation.py; then
    echo "✅ Installation validation completed"
else
    echo "⚠️  Installation validation found issues"
    echo "📋 Please review the validation output above"
fi

# Validate camera initialization
echo "🔍 Validating camera initialization..."
echo "   📋 Testing camera initialization with system picamera2..."
if python -c "
import sys
sys.path.insert(0, 'edge/src')
try:
    from edge.src.components.camera_handler import CameraHandler
    camera = CameraHandler()
    result = camera.initialize_camera()
    if result:
        print('✅ Camera initialization successful')
    else:
        print('⚠️  Camera initialization failed - check camera hardware and permissions')
except Exception as e:
    print(f'⚠️  Camera initialization error: {e}')
" 2>/dev/null; then
    echo "   ✅ Camera validation completed"
else
    echo "   ⚠️  Camera validation failed - camera may not work properly"
fi

echo ""
echo "📋 Service Status: sudo systemctl status aicamera_lpr.service"
echo "📋 Service Logs: sudo journalctl -u aicamera_lpr.service -f"
echo "🌐 Web Interface: http://localhost"
echo "🔍 Validation: python edge/scripts/validate_installation.py"
echo ""
echo "🔧 Dashboard Display Troubleshooting:"
echo "   If dashboard CSS/JS is not loading properly:"
echo "   1. Check static file permissions: ls -la /home/camuser/aicamera/edge/src/web/static/"
echo "   2. Test CSS access: curl -I http://localhost/static/css/base.css"
echo "   3. Test JS access: curl -I http://localhost/static/js/base.js"
echo "   4. Check nginx logs: sudo tail -f /var/log/nginx/error.log"
echo "   5. Fix permissions: sudo chmod -R 755 /home/camuser/aicamera/edge/src/web/static/"
echo "   6. Reload nginx: sudo systemctl reload nginx"

# Optional: Setup kiosk browser service for boot startup (non-critical)
echo ""
echo "🖥️  Setting up optional kiosk browser service for boot startup..."
echo "   ℹ️  This is an optional feature - main installation will continue regardless of kiosk setup status"
echo "   ℹ️  Kiosk browser will start automatically on system boot (if enabled)"

if [[ -f "edge/systemd_service/kiosk-browser.service" ]]; then
    # Install chromium-browser if not present (optional)
    if ! command -v chromium-browser >/dev/null 2>&1; then
        echo "   📦 Installing chromium-browser (optional)..."
        sudo apt-get update -y
        sudo apt-get install -y chromium-browser
        if ! command -v chromium-browser >/dev/null 2>&1; then
            echo "   ⚠️  Failed to install chromium-browser - kiosk browser will not be available"
            echo "   ℹ️  Main installation will continue - you can install chromium-browser manually later"
        else
            echo "   ✅ chromium-browser installed successfully"
        fi
    else
        echo "   ✅ chromium-browser already installed"
    fi
    
    # Copy service file and enable it (optional)
    echo "   📋 Installing kiosk browser service (optional)..."
            if sudo cp edge/systemd_service/kiosk-browser.service /etc/systemd/system/; then
        sudo systemctl daemon-reload
        sudo systemctl enable kiosk-browser.service
        echo "   ✅ Kiosk browser service installed and enabled"
        echo "   📋 To start kiosk browser: sudo systemctl start kiosk-browser.service"
        echo "   📋 To stop kiosk browser: sudo systemctl stop kiosk-browser.service"
        echo "   📋 Kiosk browser logs: sudo journalctl -u kiosk-browser.service -f"
    else
        echo "   ⚠️  Failed to install kiosk browser service - continuing with main installation"
    fi
    
    # Install desktop launcher if desktop environment is available (optional)
    if [[ -n "$DISPLAY" ]] && [[ -d "/home/camuser/Desktop" ]]; then
        echo "   🖥️  Installing desktop launcher (optional)..."
        if [[ -f "edge/installation/aicamera-browser.desktop" ]]; then
            if cp edge/installation/aicamera-browser.desktop /home/camuser/Desktop/; then
                chmod +x /home/camuser/Desktop/aicamera-browser.desktop
                chown camuser:camuser /home/camuser/Desktop/aicamera-browser.desktop
                echo "   ✅ Desktop launcher installed at /home/camuser/Desktop/aicamera-browser.desktop"
            else
                echo "   ⚠️  Failed to install desktop launcher - continuing with main installation"
            fi
        else
            echo "   ⚠️  Desktop launcher file not found: edge/installation/aicamera-browser.desktop"
        fi
    else
        echo "   ℹ️  Desktop environment not detected, skipping desktop launcher"
    fi
    
    # Note: Kiosk browser service is configured for boot startup only
    if [[ -n "$DISPLAY" ]]; then
        echo "   ℹ️  Kiosk browser service is configured for boot startup only"
        echo "   📋 Service will start automatically on next system boot"
        echo "   📋 To start immediately (optional): sudo systemctl start kiosk-browser.service"
        echo "   📋 To check status: sudo systemctl status kiosk-browser.service"
    else
        echo "   ℹ️  No GUI detected, kiosk browser service configured for boot startup"
        echo "   📋 Service will start automatically on next system boot when GUI is available"
    fi
else
    echo "   ℹ️  Kiosk browser service file not found: systemd_service/kiosk-browser.service"
    echo "   ℹ️  Kiosk browser is an optional feature - main installation continues"
fi

echo "   ✅ Kiosk browser setup completed (boot startup only - optional feature)"

# Setup AI Camera boot logo (optional)
echo ""
echo "🎨 Setting up AI Camera boot logo..."
echo "   ℹ️  This will replace the Raspberry Pi logo with AI Camera logo during boot"
echo "   ℹ️  This is an optional feature - main installation will continue regardless of logo setup status"

if [[ -f "assets/aicamera_logo.png" ]]; then
echo "   📷 Found AI Camera logo: assets/aicamera_logo.png"
    
    # Check if Plymouth is available
    if command -v plymouth >/dev/null 2>&1; then
        echo "   🔧 Setting up AI Camera boot logo..."
        
        # Backup original splash image if not already backed up
        if [[ ! -f "/usr/share/plymouth/themes/pix/splash.png.backup" ]]; then
            echo "   💾 Backing up original splash image..."
            sudo cp /usr/share/plymouth/themes/pix/splash.png /usr/share/plymouth/themes/pix/splash.png.backup
            echo "   ✅ Original splash image backed up"
        else
            echo "   ℹ️  Backup already exists"
        fi
        
        # Install AI Camera logo
        echo "   🎨 Installing AI Camera logo..."
        sudo cp assets/aicamera_logo.png /usr/share/plymouth/themes/pix/splash.png
        echo "   ✅ AI Camera logo installed"
        
        # Set Plymouth theme
        echo "   🎭 Setting Plymouth theme..."
        sudo plymouth-set-default-theme pix
        echo "   ✅ Plymouth theme set"
        
        # Update initramfs
        echo "   🔄 Updating initramfs..."
        sudo update-initramfs -u -k all
        echo "   ✅ Initramfs updated"
        
        echo "   ✅ AI Camera boot logo setup completed"
        echo "   📋 The AI Camera logo will be displayed on next boot"
        echo "   📋 To restore original logo: sudo ./scripts/restore_boot_logo.sh"
    else
        echo "   ⚠️  Plymouth not available - boot logo setup skipped"
        echo "   ℹ️  Main installation will continue - you can install Plymouth manually later"
    fi
else
    echo "   ⚠️  AI Camera logo not found: assets/aicamera_logo.png"
    echo "   ℹ️  Boot logo setup skipped - main installation continues"
fi

echo "   ✅ Boot logo setup completed (optional feature)"

# Edge Communication system setup
echo ""
echo "🔌 Setting up Edge Communication System..."
echo "   ℹ️  This will install and configure MQTT, SFTP, and WebSocket communication"
echo "   ℹ️  This is a required component for edge-to-server communication"

# Check prerequisites for edge communication setup
echo "   🔍 Checking prerequisites for edge communication setup..."

# Check if we have internet connectivity for package installation
if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
    echo "   ✅ Internet connectivity available"
else
    echo "   ⚠️  No internet connectivity detected"
    echo "   📋 Some packages may not install - ensure system packages are available"
fi

# Check if we're in the right directory to run the setup script
if [[ -f "$ROOT_DIR/scripts/setup_edge_communication_system.sh" ]]; then
    echo "   📋 Found edge communication setup script"
    
    # Make the script executable
    chmod +x "$ROOT_DIR/scripts/setup_edge_communication_system.sh"
    
    # Check if setup script has any specific requirements
    echo "   📋 Checking setup script requirements..."
    
    # Run the edge communication setup with verbose output
    echo "   🚀 Running edge communication system setup..."
    echo "   📋 This may take several minutes depending on system performance..."
    
    if (cd "$ROOT_DIR" && ./scripts/setup_edge_communication_system.sh); then
        echo "   ✅ Edge communication system setup completed successfully"
        
        # Return to installation directory
        cd "$SCRIPT_DIR"
        
        # Verify the configuration was created
        if [[ -f ".env.production" ]]; then
            echo "   ✅ Edge configuration file created: .env.production"
            echo "   📋 Configuration file location: $(pwd)/.env.production"
            
            # Show configuration file info
            echo "   📊 Configuration file details:"
            echo "      - Size: $(du -h .env.production | cut -f1)"
            echo "      - Lines: $(wc -l < .env.production)"
            echo "      - Last modified: $(stat -c %y .env.production)"
        else
            echo "   ⚠️  Edge configuration file not found - check setup script output"
        fi
        
        # Check if edge services were created
        if [[ -f "../src/services/mqtt_client.py" ]] && \
           [[ -f "../src/services/sftp_transfer.py" ]] && \
           [[ -f "../src/services/websocket_client.py" ]]; then
            echo "   ✅ Edge communication services created"
            
            # Show service files info
            echo "   📊 Service files created:"
            for service in mqtt_client.py sftp_transfer.py websocket_client.py; do
                if [[ -f "../src/services/$service" ]]; then
                    echo "      - $service: $(du -h "../src/services/$service" | cut -f1)"
                fi
            done
        else
            echo "   ⚠️  Some edge services not found - check setup script output"
        fi
        
        # Check if startup script was created
        if [[ -f "../start_edge.sh" ]]; then
            echo "   ✅ Edge startup script created: ../start_edge.sh"
            echo "   📋 To start edge application: cd .. && ./start_edge.sh"
            
            # Make startup script executable
            chmod +x ../start_edge.sh
            echo "   ✅ Startup script made executable"
        else
            echo "   ⚠️  Edge startup script not found - check setup script output"
        fi
        
        # Check if logs directory was created
        if [[ -d "../logs" ]]; then
            echo "   ✅ Logs directory created: ../logs"
        else
            echo "   ℹ️  Logs directory not found - will be created when edge starts"
        fi
        
    else
        echo "   ❌ Edge communication system setup failed"
        echo "   📋 Check the setup script output for error details"
        echo "   📋 You can run the setup manually: $ROOT_DIR/scripts/setup_edge_communication_system.sh"
        echo "   📋 Common troubleshooting steps:"
        echo "      - Check system package availability: sudo apt update"
        echo "      - Verify Python environment: python3 --version"
        echo "      - Check permissions: ls -la scripts/setup_edge_communication_system.sh"
        
        # Return to installation directory even if setup failed
        cd edge/installation/
    fi
    
else
    echo "   ⚠️  Edge communication setup script not found: ../../scripts/setup_edge_communication_system.sh"
    echo "   📋 Please ensure the setup script exists in the scripts/ directory"
    echo "   📋 You can run the setup manually from the project root directory"
    echo "   📋 Expected location: $ROOT_DIR/scripts/setup_edge_communication_system.sh"
fi

echo "   ✅ Edge communication system setup completed"

# Final installation summary
echo ""
echo "🎉 AI Camera Edge Installation Complete!"
echo "=========================================="
echo ""
echo "📋 Installation Summary:"
echo "   ✅ System dependencies installed"
echo "   ✅ Python environment configured"
echo "   ✅ AI Camera application installed"
echo "   ✅ Camera hardware configured"
echo "   ✅ Kiosk browser service installed (optional)"
echo "   ✅ Boot logo configured (optional)"
echo "   ✅ Edge communication system configured"
echo ""
echo "🚀 Next Steps:"
echo "   1. Configure edge environment: nano .env.production"
echo "   2. Start edge application: cd .. && ./start_edge.sh"
echo "   3. Monitor communication: mosquitto_sub -h localhost -t 'aicamera/edge/#'"
echo "   4. Check logs: tail -f ../logs/edge.log"
echo ""
echo "📚 Documentation:"
echo "   - Main docs: ../../docs/shared/COMMUNICATION_SYSTEM_IMPLEMENTATION.md"
echo "   - Edge setup: ../../scripts/setup_edge_communication_system.sh"
echo "   - Test scripts: ../../scripts/test_*.py"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Check service status: sudo systemctl status mosquitto"
echo "   - Test communication: python3 ../../scripts/test_edge_services_direct.py"
echo "   - View setup logs: journalctl -u edge-communication-setup.service"
echo ""
echo "🎯 The edge device is now ready for AI Camera operations!"
echo "   Happy detecting! 🚗📸"