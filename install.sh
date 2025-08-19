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

# Source environment variables and activate virtual environment
echo "Sourcing environment variables and activating virtual environment..."
source setup_env.sh

# Install additional system dependencies (if needed)
echo "Installing additional system dependencies..."
sudo apt update
sudo apt install libcap-dev
sudo apt install -y rapidjson-dev

# Initialize variables
DOWNLOAD_RESOURCES_FLAG=""
PYHAILORT_WHL=""
PYTAPPAS_WHL=""
INSTALL_TEST_REQUIREMENTS=false
TAG="25.3.1"

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --pyhailort) PYHAILORT_WHL="$2"; shift ;;
        --pytappas) PYTAPPAS_WHL="$2"; shift ;;
        --test) INSTALL_TEST_REQUIREMENTS=true ;;
        --all) DOWNLOAD_RESOURCES_FLAG="--all" ;;
        --tag) TAG="$2"; shift ;;   # New parameter to specify tag
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Install specified Python wheels
if [[ -n "$PYHAILORT_WHL" ]]; then
    echo "Installing pyhailort wheel: $PYHAILORT_WHL"
    pip install "$PYHAILORT_WHL"
fi

if [[ -n "$PYTAPPAS_WHL" ]]; then
    echo "Installing pytappas wheel: $PYTAPPAS_WHL"
    pip install "$PYTAPPAS_WHL"
fi

# Install the required Python dependencies
echo "Installing required Python dependencies..."
pip install -r requirements.txt

# Install Hailo Apps Infrastructure from specified tag/branch
echo "Installing Hailo Apps Infrastructure from version: $TAG..."
pip install "git+https://github.com/hailo-ai/hailo-apps-infra.git@$TAG"

# Install test requirements if needed
if [[ "$INSTALL_TEST_REQUIREMENTS" == true ]]; then
    echo "Installing test requirements..."
    pip install -r tests/test_resources/requirements.txt
fi

# Production setup - Create necessary directories and files
echo "Setting up production environment..."
mkdir -p logs
mkdir -p resources/models
mkdir -p v1_3/src

# Set proper permissions for production
chmod 755 logs
chmod 755 resources
chmod 755 v1_3

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
                xdg-open http://localhost:5000/health 2>/dev/null || echo "Browser opened manually: http://localhost:5000/health"
            else
                echo "🌐 Service is running at: http://localhost:5000/health"
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
echo "📋 Service Status: sudo systemctl status aicamera_v1.3.service"
echo "📋 Service Logs: sudo journalctl -u aicamera_v1.3.service -f"
echo "🌐 Web Interface: http://localhost:5000"