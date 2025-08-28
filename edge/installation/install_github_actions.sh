#!/bin/bash

# GitHub Actions Edge Installation Script
# Optimized for automated deployment via GitHub Actions
# This script handles edge device installation without interactive prompts

set -e  # Exit immediately if a command exits with a non-zero status

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

echo "🚀 Starting AI Camera Edge Installation (GitHub Actions Mode)..."
echo "📋 System: $(uname -a)"
echo "📋 Python: $(python3 --version)"
echo "📋 Working Directory: $(pwd)"
echo "📋 GitHub Actions: Enabled"

# Configuration for GitHub Actions deployment
AICAMERA_ID="${AICAMERA_ID:-1}"
CHECKPOINT_ID="${CHECKPOINT_ID:-1}"
CAMERA_LOCATION="${CAMERA_LOCATION:-GitHub Actions Deployment}"

print_info "GitHub Actions Configuration:"
echo "  AICAMERA_ID: $AICAMERA_ID"
echo "  CHECKPOINT_ID: $CHECKPOINT_ID"
echo "  CAMERA_LOCATION: $CAMERA_LOCATION"

# Update system packages (non-interactive)
print_info "Updating system packages..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y
sudo apt-get upgrade -y --allow-downgrades --allow-remove-essential --allow-change-held-packages
print_status "System packages updated"

# Setup SSH for GitHub Actions deployment (non-interactive)
print_info "Setting up SSH for GitHub Actions deployment..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add GitHub Actions deployment key to authorized_keys
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCeL4SoHelb+9aDlO1/wrqw/C+VGA5DMlRJ+U8mbNpn+8ueczEgApme8PJC6te4lt4LSOkLyKSgLLOts3fQpKPabtFER4ssgyHXrn8G2v1ObTtzwtYIpE5qTWJJiGXs63zMXrJW08D5cTLtTqxoVBmV8NhT2IEuejOWhf6BHH4xZahx2AGprWNvc7gSJCxRkScPNjTtlj2kj85rNlwCgzJJV3052NSyLg8Th4CdYqcn43J2EwBDjIIfMuySE1dFav2nnhScgu/JF9HouYggnfxbOblasmCVWNK1ADsZmEgnAP9G/Y559MQLcwF0wbef9Np23KIOet0clOHqmzH8ZziUKeItyx8SR82KhuCbvVTfiiAxPsfQoR5cQ+0WaTXCs5ulLQseRY9utno+Tq2NpDaG6SezkB5UOk8H9eYxOc/Ob4wDVrA4A87PXFo7s4CqD3fCRznA7gr6GmR9qE9WXbfuz2uWjcr+VNFpaZxV4UF1WenuHxMKRwfRqLyn2wRnJiXijJ4sQ4MTYPGewqeqa3XCQySGbiPmxzdsUpfROWSk52H459hmXh1SoPYnuSo1Pk3fkxAk9pwWaIo5+gPAt6Vmv6ANeTOX+BP3hTfJ73gAILc/3qx08lLQT6bcDRh/JMp3oyjgTjUZVV4jAvUPrXoDb/2w/zKRjeH518lswvRLnw== aicamera-deployment@github.com" >> ~/.ssh/authorized_keys

# Set proper permissions for SSH files
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
print_status "SSH setup completed for GitHub Actions deployment"

# Camera cleanup and preparation
print_info "Preparing camera system for installation..."
sudo systemctl stop aicamera_lpr.service 2>/dev/null || true
sudo systemctl disable aicamera_lpr.service 2>/dev/null || true

# Stop any running camera-related processes
sudo pkill -f "picamera2" 2>/dev/null || true
sudo pkill -f "libcamera" 2>/dev/null || true
sudo pkill -f "gstreamer" 2>/dev/null || true
sudo pkill -f "python.*camera" 2>/dev/null || true

# Kill any processes using camera devices
for device in /dev/video* /dev/media*; do
    if [[ -e "$device" ]]; then
        sudo fuser -k "$device" 2>/dev/null || true
    fi
done

# Reload camera modules
sudo modprobe -r bcm2835-v4l2 2>/dev/null || true
sudo modprobe -r v4l2_common 2>/dev/null || true
sudo modprobe -r videodev 2>/dev/null || true
sleep 2

sudo modprobe videodev 2>/dev/null || true
sudo modprobe v4l2_common 2>/dev/null || true
sudo modprobe bcm2835-v4l2 2>/dev/null || true
sleep 2

# Verify camera permissions
if [[ -e "/dev/video0" ]]; then
    sudo chmod 666 /dev/video0 2>/dev/null || true
    sudo usermod -a -G video $USER 2>/dev/null || true
    print_status "Camera permissions set"
else
    print_warning "Camera device not found - permissions not set"
fi

sleep 3
print_status "Camera cleanup completed"

# Install Hailo SDK and dependencies
print_info "Installing Hailo SDK and dependencies..."
sudo apt-get install -y hailo-all || {
    print_warning "Failed to install hailo-all package"
    print_info "This may be expected if Hailo repository is not configured"
    print_info "Continuing with installation - Hailo features will be limited"
}

# Source environment variables (Hailo SDK)
print_info "Sourcing environment variables and preparing virtual environment..."
if [[ -f "edge/installation/setup_env.sh" ]]; then
    source edge/installation/setup_env.sh || true
fi

# Verify virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]] || [[ ! -d "$VIRTUAL_ENV" ]]; then
    print_info "Virtual environment not activated or not found. Creating new one..."
    if [[ -d "edge/venv_hailo" ]]; then
        print_info "Removing corrupted virtual environment..."
        rm -rf edge/venv_hailo
    fi
    print_info "Creating new virtual environment (with system site-packages for libcamera access)..."
    python3 -m venv --system-site-packages edge/venv_hailo
    source edge/venv_hailo/bin/activate
    print_status "New virtual environment created and activated: $VIRTUAL_ENV"
else
    print_status "Virtual environment is active: $VIRTUAL_ENV"
fi

# Re-source Hailo environment after activating venv
if [[ -f "edge/installation/setup_env.sh" ]]; then
    source edge/installation/setup_env.sh || true
fi

# Install additional system dependencies
print_info "Installing additional system dependencies..."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get install -y libcap-dev rapidjson-dev python3-libcamera libcamera-tools

# Ensure libcamera is accessible in virtual environment
print_info "Ensuring libcamera is accessible in virtual environment..."
if python3 -c "import libcamera; print('libcamera available in system Python')" 2>/dev/null; then
    print_status "libcamera available in system Python"
    
    if ! python -c "import libcamera; print('libcamera available in venv')" 2>/dev/null; then
        print_warning "libcamera not accessible in virtual environment - recreating venv with system site-packages"
        deactivate 2>/dev/null || true
        rm -rf edge/venv_hailo
        python3 -m venv --system-site-packages edge/venv_hailo
        source edge/venv_hailo/bin/activate
        PIP_CMD="$VIRTUAL_ENV/bin/pip"
        print_status "Recreated venv with system site-packages access"
    else
        print_status "libcamera accessible in virtual environment"
    fi
else
    print_error "libcamera not available in system Python - attempting to install"
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera libcamera-tools || true
    
    if python3 -c "import libcamera; print('libcamera now available')" 2>/dev/null; then
        print_status "libcamera installed successfully"
    else
        print_error "libcamera installation failed - camera functionality will be limited"
    fi
fi

# Verify pip is available in virtual environment
print_info "Verifying pip installation..."
if ! command -v pip &> /dev/null; then
    print_info "pip not found. Installing pip in virtual environment..."
    python -m ensurepip --upgrade
fi

# Ensure we're using the virtual environment pip
if [[ -n "$VIRTUAL_ENV" ]]; then
    PIP_CMD="$VIRTUAL_ENV/bin/pip"
    print_status "Using virtual environment pip: $PIP_CMD"
else
    PIP_CMD="pip"
    print_warning "Using system pip: $(which pip)"
fi

# Install wheel package first
print_info "Installing wheel package for better wheel support..."
$PIP_CMD install wheel
print_status "Wheel package installed"

# Install required Python dependencies
print_info "Installing required Python dependencies..."
IONICE="ionice -c2 -n7"  # best-effort, lowest priority
RENICE="renice 19 $$ >/dev/null || true"
eval "$RENICE"

# Install core dependencies first
print_info "Installing core dependencies..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir \
    "typing-extensions>=4.0.0" \
    "setuptools>=65.0.0" \
    "wheel>=0.40.0"

# Install edge specific requirements
print_info "Installing edge requirements..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt

# Install root requirements (for compatibility)
print_info "Installing root requirements..."
$IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt

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
    print_info "Installing Hailo Apps Infrastructure from version: 25.3.1..."
    $IONICE $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir "git+https://github.com/hailo-ai/hailo-apps-infra.git@25.3.1"
else
    print_warning "Hailo python package not found in the active venv. Skipping hailo-apps-infra install."
fi

# Validate EasyOCR installation
print_info "Validating EasyOCR installation..."
if python -c "import easyocr; print('✅ EasyOCR imported successfully')" 2>/dev/null; then
    print_status "EasyOCR validation passed"
else
    print_error "EasyOCR validation failed - attempting to fix..."
    $PIP_CMD install --upgrade --force-reinstall "typing-extensions>=4.0.0"
    $PIP_CMD install --upgrade --force-reinstall "easyocr>=1.7.0"
    
    if python -c "import easyocr; print('✅ EasyOCR fixed successfully')" 2>/dev/null; then
        print_status "EasyOCR fixed successfully"
    else
        print_error "EasyOCR installation failed - please check dependencies"
        exit 1
    fi
fi

# Validate EasyOCR and typing_extensions comprehensively
print_info "Running comprehensive EasyOCR validation..."
if python edge/scripts/validate_easyocr.py; then
    print_status "EasyOCR validation passed"
else
    print_error "EasyOCR validation failed - attempting to fix..."
    $PIP_CMD install --upgrade --force-reinstall "typing-extensions>=4.0.0"
    $PIP_CMD install --upgrade --force-reinstall "easyocr>=1.7.0"
    
    if python edge/scripts/validate_easyocr.py; then
        print_status "EasyOCR fixed successfully"
    else
        print_error "EasyOCR installation failed - please check dependencies"
        exit 1
    fi
fi

# Validate libcamera installation
print_info "Running comprehensive libcamera validation..."
if python edge/scripts/validate_libcamera.py; then
    print_status "libcamera validation passed"
else
    print_error "libcamera validation failed - attempting to fix..."
    sudo apt-get update -y
    sudo apt-get install -y python3-libcamera libcamera-tools || true
    
    if ! python -c "import libcamera; print('libcamera available')" 2>/dev/null; then
        print_warning "Recreating virtual environment with system site-packages access..."
        deactivate 2>/dev/null || true
        rm -rf edge/venv_hailo
        python3 -m venv --system-site-packages edge/venv_hailo
        source edge/venv_hailo/bin/activate
        PIP_CMD="$VIRTUAL_ENV/bin/pip"
        
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir \
            "typing-extensions>=4.0.0" \
            "setuptools>=65.0.0" \
            "wheel>=0.40.0"
        
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt
        $PIP_CMD install --prefer-binary --no-build-isolation --no-cache-dir -r edge/installation/requirements.txt
    fi
    
    if python edge/scripts/validate_libcamera.py; then
        print_status "libcamera fixed successfully"
    else
        print_error "libcamera installation failed - camera functionality will be limited"
        print_warning "You can still use the system without camera features"
    fi
fi

# Validate degirum installation
print_info "Validating degirum installation..."
if python -c "import degirum; print('✅ degirum imported successfully')" 2>/dev/null; then
    print_status "degirum validation passed"
else
    print_error "degirum validation failed - attempting to fix..."
    
    if [[ -f "setup_env.sh" ]]; then
        print_info "Sourcing Hailo environment..."
        source setup_env.sh || true
    fi
    
    print_info "Reinstalling degirum..."
    $PIP_CMD install --upgrade --force-reinstall "degirum>=0.18.2" || true
    $PIP_CMD install --upgrade --force-reinstall "degirum-tools==0.19.1" || true
    $PIP_CMD install --upgrade --force-reinstall "degirum-cli==0.2.0" || true
    
    if python -c "import degirum; print('✅ degirum fixed successfully')" 2>/dev/null; then
        print_status "degirum fixed successfully"
    else
        print_warning "degirum installation failed - detection functionality will be limited"
        print_info "This may be expected if Hailo SDK is not properly installed"
        print_info "You can still use the system without AI detection features"
    fi
fi

# Production setup - Create necessary directories and files
print_info "Setting up production environment..."
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
print_info "Setting up project ownership and permissions for development..."
sudo chown -R camuser:camuser /home/camuser/aicamera/ 2>/dev/null || true
sudo usermod -a -G camuser www-data 2>/dev/null || true

# Set proper directory permissions for nginx access
chmod 755 /home/camuser/aicamera/edge/src/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/css/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/src/web/static/js/ 2>/dev/null || true

# Set proper file permissions for static files
chmod 644 /home/camuser/aicamera/edge/src/web/static/css/*.css 2>/dev/null || true
chmod 644 /home/camuser/aicamera/edge/src/web/static/js/*.js 2>/dev/null || true

# Ensure directories have group write permissions for collaborative editing
chmod 775 /home/camuser/aicamera/edge/src/web/static/css/ 2>/dev/null || true
chmod 775 /home/camuser/aicamera/edge/src/web/static/js/ 2>/dev/null || true
chmod 755 /home/camuser/aicamera/edge/captured_images/ 2>/dev/null || true

# Create basic WSGI file if it doesn't exist
if [[ ! -f "edge/src/wsgi.py" ]]; then
    print_info "Creating basic WSGI file..."
    cat > edge/src/wsgi.py << 'EOF'
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
touch edge/__init__.py
touch edge/src/__init__.py

# Setup environment configuration for GitHub Actions
print_info "Setting up environment configuration for GitHub Actions..."
if [[ ! -f "edge/installation/.env.production" ]]; then
    if [[ -f "edge/installation/env.template" ]]; then
        cp edge/installation/env.template edge/installation/.env.production
        print_status "Created .env.production file from template"
    else
        print_warning "edge/installation/env.template not found - please create .env.production file manually"
    fi
else
    print_status ".env.production file already exists in edge/installation/"
fi

# Update .env.production with GitHub Actions configuration
if [[ -f "edge/installation/.env.production" ]]; then
    print_info "Updating .env.production with GitHub Actions configuration..."
    
    # Export variables from .env.production into current shell
    set -a
    source edge/installation/.env.production || true
    set +a

    # Helper to update or insert env var
    update_env_var() {
        local key="$1"
        local value="$2"
        local replace_value="$value"
        # Escape '&' for sed replacement safety
        replace_value="${replace_value//&/\\&}"
        if grep -q "^${key}=" edge/installation/.env.production; then
            sed -i "s|^${key}=.*|${key}=${replace_value}|" edge/installation/.env.production
        else
            echo "${key}=${replace_value}" >> edge/installation/.env.production
        fi
    }

    # Update with GitHub Actions values
    update_env_var "AICAMERA_ID" "$AICAMERA_ID"
    update_env_var "CHECKPOINT_ID" "$CHECKPOINT_ID"
    update_env_var "CAMERA_LOCATION" "\"$CAMERA_LOCATION\""

    print_status "Updated .env.production with GitHub Actions configuration"

    # Reload to ensure environment reflects latest values
    set -a
    source edge/installation/.env.production || true
    set +a
fi

# Initialize database schema
print_info "Initializing database schema..."
if python edge/scripts/init_database.py; then
    print_status "Database initialized"
else
    print_error "Database initialization failed"
    exit 1
fi

# Run database schema migrations
print_info "Running database schema migrations..."
print_info "Applying schema migration v2 (enhanced OCR support)..."
if python edge/src/database/schema_migration_v2.py; then
    print_status "Schema migration v2 completed"
else
    print_warning "Schema migration v2 failed or not needed"
fi

print_info "Applying schema migration v3 (complete image storage pipeline)..."
if python edge/src/database/schema_migration_v3.py; then
    print_status "Schema migration v3 completed"
else
    print_warning "Schema migration v3 failed or not needed"
fi

# Validate database setup
print_info "Validating database setup..."
if python edge/scripts/validate_database.py; then
    print_status "Database validation passed"
else
    print_error "Database validation failed"
    print_info "Attempting to fix database issues..."
    python edge/scripts/init_database.py
    if python edge/scripts/validate_database.py; then
        print_status "Database fixed successfully"
    else
        print_error "Database validation still failed - manual intervention required"
        exit 1
    fi
fi

# Install and configure nginx
print_info "Installing and configuring nginx..."
if ! command -v nginx >/dev/null 2>&1; then
    print_info "Installing nginx..."
    sudo apt-get update -y
    sudo apt-get install -y nginx
else
    print_status "nginx already installed"
fi

if [[ -f "edge/nginx.conf" ]]; then
    print_info "Applying nginx site configuration..."
    if [[ -f "/etc/nginx/sites-available/default" ]]; then
        sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup || true
    fi
    sudo cp edge/nginx.conf /etc/nginx/sites-available/aicamera
    sudo ln -sf /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/aicamera
    sudo rm -f /etc/nginx/sites-enabled/default || true
    
    # Fix nginx permission issues
    sudo mkdir -p /run/nginx
    sudo chown www-data:www-data /run/nginx 2>/dev/null || true
    sudo chmod 755 /run/nginx
    
    sudo mkdir -p /var/log/nginx
    sudo chown www-data:www-data /var/log/nginx 2>/dev/null || true
    
    if [[ "$(id -u)" != "0" ]]; then
        print_info "Adjusting nginx configuration for non-root user..."
        sudo cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup || true
        sudo sed -i 's/^user www-data;/# user www-data; # Commented for non-root installation/' /etc/nginx/nginx.conf || true
    fi
    
    if sudo nginx -t 2>/dev/null; then
        print_status "nginx configuration is valid"
        sudo systemctl enable nginx
        sudo systemctl restart nginx
        print_status "nginx started successfully"
        
        # Apply nginx configuration fixes for Unix socket proxy
        if sudo sed -i 's|proxy_pass http://unix:/tmp/aicamera.sock/[^;]*;|proxy_pass http://unix:/tmp/aicamera.sock;|g' /etc/nginx/sites-available/aicamera; then
            print_status "Fixed proxy_pass directives"
            
            if sudo nginx -t 2>/dev/null; then
                print_status "Nginx configuration still valid after fixes"
                sudo systemctl reload nginx
                print_status "Nginx reloaded with fixes"
            else
                print_warning "Nginx configuration invalid after fixes - manual check required"
            fi
        else
            print_warning "Failed to apply nginx configuration fixes"
        fi
    else
        print_warning "nginx configuration test failed - attempting to fix..."
        sudo mkdir -p /var/cache/nginx
        sudo chown www-data:www-data /var/cache/nginx 2>/dev/null || true
        
        if sudo systemctl start nginx 2>/dev/null; then
            print_status "nginx started successfully (configuration test ignored)"
            sudo systemctl enable nginx
        else
            print_error "nginx failed to start - manual intervention required"
            exit 1
        fi
    fi
else
    print_error "edge/nginx.conf not found in project root"
    exit 1
fi

# Setup and start systemd service
print_info "Setting up systemd service..."
if [[ -f "edge/systemd_service/aicamera_v1.3.service" ]]; then
    sudo cp edge/systemd_service/aicamera_v1.3.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable aicamera_v1.3.service
    
    print_info "Starting aicamera_v1.3 service..."
    if sudo systemctl start aicamera_v1.3.service; then
        print_status "Service started successfully"
        
        sleep 5
        
        if sudo systemctl is-active --quiet aicamera_v1.3.service; then
            print_status "Service is running"
            
            # Validate web interface is accessible
            print_info "Validating web interface accessibility..."
            max_retries=10
            retry_count=0
            web_accessible=false
            
            while [[ $retry_count -lt $max_retries ]]; do
                if curl -s -f http://localhost/health >/dev/null 2>&1; then
                    print_status "Web interface is accessible"
                    web_accessible=true
                    break
                else
                    print_info "Attempt $((retry_count + 1))/$max_retries: Web interface not ready yet..."
                    retry_count=$((retry_count + 1))
                    sleep 3
                fi
            done
            
            if [[ "$web_accessible" == "false" ]]; then
                print_warning "Web interface validation failed after $max_retries attempts"
                sudo journalctl -u aicamera_v1.3.service --no-pager -n 20
                print_info "Service is running but web interface may have issues"
            fi
            
            print_info "Service is running at: http://localhost/health"
        else
            print_error "Service failed to start properly"
            sudo systemctl status aicamera_v1.3.service
            exit 1
        fi
    else
        print_error "Failed to start service"
        sudo systemctl status aicamera_v1.3.service
        exit 1
    fi
else
    print_error "Service file not found: edge/systemd_service/aicamera_v1.3.service"
    exit 1
fi

# Run validation
print_info "Running installation validation..."
if python edge/scripts/validate_installation.py; then
    print_status "Installation validation completed"
else
    print_warning "Installation validation found issues"
    print_info "Please review the validation output above"
fi

print_status "GitHub Actions Edge Installation completed successfully!"
print_status "The edge device is now ready for automated deployments!"
print_info "Service Status: sudo systemctl status aicamera_v1.3.service"
print_info "Service Logs: sudo journalctl -u aicamera_v1.3.service -f"
print_info "Web Interface: http://localhost"
print_info "Validation: python edge/scripts/validate_installation.py"
