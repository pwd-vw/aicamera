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
    echo "   4. Review service logs: sudo journalctl -u aicamera_v1.3.service"
    exit $exit_code
}

# Set error handling
trap handle_error ERR
set -e  # Exit immediately if a command exits with a non-zero status

echo "🚀 Starting AI Camera v1.3 Installation..."
echo "📋 System: $(uname -a)"
echo "📋 Python: $(python3 --version)"
echo "📋 Working Directory: $(pwd)"

# Source environment variables (Hailo SDK) – initial try
echo "Sourcing environment variables and preparing virtual environment..."
if [[ -f "setup_env.sh" ]]; then
    source setup_env.sh || true
fi

# Verify virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]] || [[ ! -d "$VIRTUAL_ENV" ]]; then
    echo "❌ Virtual environment not activated or not found. Creating new one..."
    if [[ -d "venv_hailo" ]]; then
        echo "   Removing corrupted virtual environment..."
        rm -rf venv_hailo
    fi
    echo "   Creating new virtual environment (with system site-packages for libcamera access)..."
    python3 -m venv --system-site-packages venv_hailo
    source venv_hailo/bin/activate
    echo "✅ New virtual environment created and activated: $VIRTUAL_ENV"
else
    echo "✅ Virtual environment is active: $VIRTUAL_ENV"
fi

# Re-source Hailo environment after activating venv to ensure bindings are in this shell
if [[ -f "setup_env.sh" ]]; then
    source setup_env.sh || true
fi

# Install additional system dependencies (if needed)
echo "Installing additional system dependencies..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get install -y libcap-dev rapidjson-dev

# Camera stack required by picamera2 (Python module libcamera comes from system packages)
echo "Installing libcamera stack for Picamera2..."
sudo apt-get install -y python3-libcamera libcamera-tools libcamera-apps python3-libcamera-dev || true

# Ensure libcamera is accessible in virtual environment
echo "Ensuring libcamera is accessible in virtual environment..."
if python3 -c "import libcamera; print('libcamera available in system Python')" 2>/dev/null; then
    echo "✅ libcamera available in system Python"
    
    # Check if virtual environment can access libcamera
    if ! python -c "import libcamera; print('libcamera available in venv')" 2>/dev/null; then
        echo "⚠️  libcamera not accessible in virtual environment - recreating venv with system site-packages"
        deactivate 2>/dev/null || true
        rm -rf venv_hailo
        python3 -m venv --system-site-packages venv_hailo
        source venv_hailo/bin/activate
        PIP_CMD="$VIRTUAL_ENV/bin/pip"
        echo "✅ Recreated venv with system site-packages access"
    else
        echo "✅ libcamera accessible in virtual environment"
    fi
else
    echo "❌ libcamera not available in system Python - attempting to install"
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera python3-libcamera-dev libcamera-tools libcamera-apps || true
    
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
        --pyhailort) PYHAILORT_WHL="$2"; shift ;;
        --pytappas) PYTAPPAS_WHL="$2"; shift ;;
        --all) DOWNLOAD_RESOURCES_FLAG="--all" ;;
        --tag) TAG="$2"; shift ;;   # New parameter to specify tag
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

# Ensure we're using the virtual environment pip
if [[ -n "$VIRTUAL_ENV" ]]; then
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    echo "✅ Using virtual environment pip: $PIP_CMD"
else
    PIP_CMD="pip"
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
            rm -rf venv_hailo
            python3 -m venv --system-site-packages venv_hailo
            source venv_hailo/bin/activate
            PIP_CMD="$VIRTUAL_ENV/bin/pip"
            echo "✅ Recreated venv with access to system site-packages: $VIRTUAL_ENV"
        else
            echo "⚠️  libcamera not found in system Python. Proceeding; Picamera2 may fail to import."
        fi
    fi
fi

# Install wheel package first to enable wheel building for packages without pyproject.toml
echo "Installing wheel package for better wheel support..."
$PIP_CMD install wheel
echo "✅ Wheel package installed"

# Install specified Python wheels
if [[ -n "$PYHAILORT_WHL" ]]; then
    echo "Installing pyhailort wheel: $PYHAILORT_WHL"
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir "$PYHAILORT_WHL"
fi

if [[ -n "$PYTAPPAS_WHL" ]]; then
    echo "Installing pytappas wheel: $PYTAPPAS_WHL"
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir "$PYTAPPAS_WHL"
fi

echo "Installing required Python dependencies (low priority, wheels preferred)..."
# Prefer wheels, avoid building from source, reduce concurrency to lower RAM usage
IONICE="ionice -c2 -n7"  # best-effort, lowest priority
RENICE="renice 19 $$ >/dev/null || true"
eval "$RENICE"

# Install core dependencies first to avoid conflicts
echo "Installing core dependencies..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir \
    "typing-extensions>=4.0.0" \
    "setuptools>=65.0.0" \
    "wheel>=0.40.0"

# Install v1_3 specific requirements with proper dependency resolution
echo "Installing v1_3 requirements..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r v1_3/requirements.txt

# Install root requirements (for compatibility)
echo "Installing root requirements..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r requirements.txt

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
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir "git+https://github.com/hailo-ai/hailo-apps-infra.git@$TAG"
else
    echo "⚠️  Hailo python package not found in the active venv. Skipping hailo-apps-infra install."
    echo "   Action required:"
    echo "   - Run: source setup_env.sh  (to load Hailo SDK into this venv), or"
    echo "   - Provide wheel paths: ./install.sh --pyhailort /path/pyhailort.whl [--pytappas /path/pytappas.whl]"
fi

# Validate EasyOCR installation
echo "🔍 Validating EasyOCR installation..."
if python -c "import easyocr; print('✅ EasyOCR imported successfully')" 2>/dev/null; then
    echo "✅ EasyOCR validation passed"
else
    echo "❌ EasyOCR validation failed - attempting to fix..."
    # Try to fix typing_extensions issue
    $PIP_CMD install --upgrade --force-reinstall "typing-extensions>=4.0.0"
    $PIP_CMD install --upgrade --force-reinstall "easyocr>=1.7.0"
    
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
if python v1_3/scripts/validate_easyocr.py; then
    echo "✅ EasyOCR validation passed"
else
    echo "❌ EasyOCR validation failed - attempting to fix..."
    # Try to fix typing_extensions issue
    $PIP_CMD install --upgrade --force-reinstall "typing-extensions>=4.0.0"
    $PIP_CMD install --upgrade --force-reinstall "easyocr>=1.7.0"
    
    # Test again
    if python v1_3/scripts/validate_easyocr.py; then
        echo "✅ EasyOCR fixed successfully"
    else
        echo "❌ EasyOCR installation failed - please check dependencies"
        exit 1
    fi
fi

# Validate libcamera installation
echo "🔍 Running comprehensive libcamera validation..."
if python v1_3/scripts/validate_libcamera.py; then
    echo "✅ libcamera validation passed"
else
    echo "❌ libcamera validation failed - attempting to fix..."
    # Try to fix libcamera installation
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera python3-libcamera-dev libcamera-tools libcamera-apps || true
    
    # Recreate virtual environment with system site-packages if needed
    if ! python -c "import libcamera; print('libcamera available')" 2>/dev/null; then
        echo "⚠️  Recreating virtual environment with system site-packages access..."
        deactivate 2>/dev/null || true
        rm -rf venv_hailo
        python3 -m venv --system-site-packages venv_hailo
        source venv_hailo/bin/activate
        PIP_CMD="$VIRTUAL_ENV/bin/pip"
        
        # Reinstall core dependencies
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir \
            "typing-extensions>=4.0.0" \
            "setuptools>=65.0.0" \
            "wheel>=0.40.0"
        
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r v1_3/requirements.txt
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r requirements.txt
    fi
    
    # Test again
    if python v1_3/scripts/validate_libcamera.py; then
        echo "✅ libcamera fixed successfully"
    else
        echo "❌ libcamera installation failed - camera functionality will be limited"
        echo "⚠️  You can still use the system without camera features"
    fi
fi

# Production setup - Create necessary directories and files
echo "Setting up production environment..."
mkdir -p logs
mkdir -p resources/models
mkdir -p v1_3/src
mkdir -p db
mkdir -p captured_images

# Set proper permissions for production
chmod 755 logs
chmod 755 resources
chmod 755 v1_3
chmod 755 db
chmod 755 captured_images

# Set proper project ownership and permissions for development
echo "Setting up project ownership and permissions for development..."
# Set entire project ownership to camuser for development access
sudo chown -R camuser:camuser /home/camuser/aicamera/ 2>/dev/null || true

# Add www-data to camuser group for nginx access to static files
sudo usermod -a -G camuser www-data 2>/dev/null || true

# Set proper directory permissions for nginx access
chmod 755 /home/camuser/aicamera/v1_3/src/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/v1_3/src/web/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/v1_3/src/web/static/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/v1_3/src/web/static/css/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/v1_3/src/web/static/js/ 2>/dev/null || true

# Set proper file permissions for static files (readable by group for nginx)
chmod 644 /home/camuser/aicamera/v1_3/src/web/static/css/*.css 2>/dev/null || true
chmod 644 /home/camuser/aicamera/v1_3/src/web/static/js/*.js 2>/dev/null || true

# Ensure directories have group write permissions for collaborative editing
chmod 775 /home/camuser/aicamera/v1_3/src/web/static/css/ 2>/dev/null || true
chmod 775 /home/camuser/aicamera/v1_3/src/web/static/js/ 2>/dev/null || true

# Set proper permissions for captured images directory
chmod 755 /home/camuser/aicamera/captured_images/ 2>/dev/null || true

# Create basic WSGI file if it doesn't exist
if [[ ! -f "v1_3/src/wsgi.py" ]]; then
    echo "Creating basic WSGI file..."
    cat > v1_3/src/wsgi.py << 'EOF'
from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health_check():
    return {'status': 'healthy', 'service': 'aicamera_v1.3'}

@app.route('/')
def index():
    return {'message': 'AI Camera v1.3 Service Running'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
EOF
fi

# Create __init__.py files for Python packages
touch v1_3/__init__.py
touch v1_3/src/__init__.py

# Setup environment configuration
echo "Setting up environment configuration..."
if [[ ! -f ".env.production" ]]; then
    if [[ -f "env.template" ]]; then
        cp env.template .env.production
        echo "✅ Created .env.production file from template"
        echo "📝 Please edit .env.production file to customize your installation:"
        echo "   - Set AICAMERA_ID and CHECKPOINT_ID for unique identification"
        echo "   - Configure GPS coordinates (LOCATION_LAT, LOCATION_LON)"
        echo "   - Choose appropriate Hailo models for your device"
        echo "   - Set camera and detection parameters"
    else
        echo "⚠️  env.template not found - please create .env.production file manually"
    fi
else
    echo "✅ .env.production file already exists"
fi

# Load .env.production and prompt for key identifiers if needed
if [[ -f ".env.production" ]]; then
    echo "🔎 Verifying required identifiers in .env.production (AICAMERA_ID, CHECKPOINT_ID, CAMERA_LOCATION)..."

    # Export variables from .env.production into current shell
    set -a
    source ./.env.production || true
    set +a

    # Helper to update or insert env var
    update_env_var() {
        local key="$1"; shift
        local value="$1"; shift || true
        local replace_value="$value"
        # Escape '&' for sed replacement safety
        replace_value="${replace_value//&/\\&}"
        if grep -q "^${key}=" .env.production; then
            sed -i "s|^${key}=.*|${key}=${replace_value}|" .env.production
        else
            echo "${key}=${replace_value}" >> .env.production
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
    source ./.env.production || true
    set +a
fi

# Initialize database schema (fresh install safe)
echo "🔧 Initializing database schema..."
if python v1_3/scripts/init_database.py; then
    echo "✅ Database initialized"
else
    echo "❌ Database initialization failed"
    exit 1
fi

# Validate database setup
echo "🔍 Validating database setup..."
if python v1_3/scripts/validate_database.py; then
    echo "✅ Database validation passed"
else
    echo "❌ Database validation failed"
    echo "🔧 Attempting to fix database issues..."
    # Try to reinitialize database
    python v1_3/scripts/init_database.py
    if python v1_3/scripts/validate_database.py; then
        echo "✅ Database fixed successfully"
    else
        echo "❌ Database validation still failed - manual intervention required"
        exit 1
    fi
fi

# Install and configure nginx (before starting service)
echo "🌐 Installing and configuring nginx..."
if ! command -v nginx >/dev/null 2>&1; then
    echo "   Installing nginx..."
    sudo apt-get update -y
    sudo apt-get install -y nginx
else
    echo "   nginx already installed"
fi

if [[ -f "nginx.conf" ]]; then
    echo "   Applying nginx site configuration..."
    # Backup default if exists
    if [[ -f "/etc/nginx/sites-available/default" ]]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup || true
    fi
    # Copy our config and enable it
    sudo cp nginx.conf /etc/nginx/sites-available/aicamera
    sudo ln -sf /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/aicamera
    # Remove default site if present
    sudo rm -f /etc/nginx/sites-enabled/default || true
    # Test config
    if sudo nginx -t; then
        echo "   ✅ nginx configuration is valid"
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        echo "   ✅ nginx started"
    else
        echo "   ❌ nginx configuration test failed"
        exit 1
    fi
else
    echo "   ❌ nginx.conf not found in project root"
    echo "   Ensure a valid nginx.conf exists that proxies to unix:/tmp/aicamera.sock"
    exit 1
fi

# Setup and start systemd service
echo "Setting up systemd service..."
if [[ -f "systemd_service/aicamera_v1.3.service" ]]; then
    sudo cp systemd_service/aicamera_v1.3.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable aicamera_v1.3.service
    
    echo "Starting aicamera_v1.3 service..."
    if sudo systemctl start aicamera_v1.3.service; then
        echo "✅ Service started successfully"
        
        # Wait for service to be fully ready
        echo "Waiting for service to be ready..."
        sleep 5
        
        # Check service status
        if sudo systemctl is-active --quiet aicamera_v1.3.service; then
            echo "✅ Service is running"
            
            # Try to open browser automatically (if GUI is available)
            if command -v xdg-open &> /dev/null && [[ -n "$DISPLAY" ]]; then
                echo "Opening browser to check service..."
                sleep 2
                xdg-open http://localhost/health 2>/dev/null || echo "Browser opened manually: http://localhost/health"
            else
                echo "🌐 Service is running at: http://localhost/health"
                echo "📊 Check service status with: sudo systemctl status aicamera_v1.3.service"
            fi
        else
            echo "❌ Service failed to start properly"
            sudo systemctl status aicamera_v1.3.service
            exit 1
        fi
    else
        echo "❌ Failed to start service"
        sudo systemctl status aicamera_v1.3.service
        exit 1
    fi
else
    echo "❌ Service file not found: systemd_service/aicamera_v1.3.service"
    exit 1
fi

echo "🎉 Installation completed successfully!"
echo "🚀 Production environment is ready!"

# Run validation
echo ""
echo "🔍 Running installation validation..."
if python scripts/validate_installation.py; then
    echo "✅ Installation validation completed"
else
    echo "⚠️  Installation validation found issues"
    echo "📋 Please review the validation output above"
fi

echo ""
echo "📋 Service Status: sudo systemctl status aicamera_v1.3.service"
echo "📋 Service Logs: sudo journalctl -u aicamera_v1.3.service -f"
echo "🌐 Web Interface: http://localhost"
echo "🔍 Validation: python scripts/validate_installation.py"

# Setup kiosk browser service
echo ""
echo "🖥️  Setting up kiosk browser service..."
if [[ -f "systemd_service/kiosk-browser.service" ]]; then
    # Install chromium-browser if not present
    if ! command -v chromium-browser >/dev/null 2>&1; then
        echo "   Installing chromium-browser..."
        sudo apt-get update -y
        sudo apt-get install -y chromium-browser
    else
        echo "   chromium-browser already installed"
    fi
    
    # Copy service file and enable it
    sudo cp systemd_service/kiosk-browser.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable kiosk-browser.service
    
    echo "   ✅ Kiosk browser service enabled"
    echo "   📋 To start kiosk browser: sudo systemctl start kiosk-browser.service"
    echo "   📋 To stop kiosk browser: sudo systemctl stop kiosk-browser.service"
    echo "   📋 Kiosk browser logs: sudo journalctl -u kiosk-browser.service -f"
    
    # Install desktop launcher if desktop environment is available
    if [[ -n "$DISPLAY" ]] && [[ -d "/home/camuser/Desktop" ]]; then
        echo "   🖥️  Installing desktop launcher..."
        cp aicamera-browser.desktop /home/camuser/Desktop/
        chmod +x /home/camuser/Desktop/aicamera-browser.desktop
        chown camuser:camuser /home/camuser/Desktop/aicamera-browser.desktop
        echo "   ✅ Desktop launcher installed at /home/camuser/Desktop/aicamera-browser.desktop"
    else
        echo "   ℹ️  Desktop environment not detected, skipping desktop launcher"
    fi
    
    # Start kiosk browser service if GUI is available
    if [[ -n "$DISPLAY" ]]; then
        echo "   🚀 Starting kiosk browser service..."
        if sudo systemctl start kiosk-browser.service; then
            echo "   ✅ Kiosk browser service started successfully"
            echo "   🌐 Web interface should open automatically in full screen mode"
        else
            echo "   ⚠️  Failed to start kiosk browser service automatically"
            echo "   📋 You can start it manually with: sudo systemctl start kiosk-browser.service"
        fi
    else
        echo "   ℹ️  No GUI detected, kiosk browser service not started automatically"
        echo "   📋 Start it manually when GUI is available: sudo systemctl start kiosk-browser.service"
    fi
else
    echo "   ❌ Kiosk browser service file not found: systemd_service/kiosk-browser.service"
fi