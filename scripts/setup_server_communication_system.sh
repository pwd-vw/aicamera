#!/bin/bash

# Setup Script for AI Camera Unified Communication System
# This script sets up MQTT broker, configures SFTP, and prepares the communication infrastructure

echo "🚀 Setting up AI Camera Unified Communication System..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root for system installations
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_warning "Running as root - be careful with system modifications"
    fi
}

# Check if service is already running
check_service_running() {
    local service_name=$1
    if systemctl is-active --quiet "$service_name"; then
        return 0
    else
        return 1
    fi
}

# Check if package is already installed
check_package_installed() {
    local package_name=$1
    if dpkg -l | grep -q "^ii  $package_name "; then
        return 0
    else
        return 1
    fi
}

# Install system dependencies
install_dependencies() {
    print_info "Installing system dependencies..."
    
    # Update package list
    if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update
        
        # Install MQTT broker (Mosquitto) - check if already installed
        if ! check_package_installed "mosquitto"; then
            print_info "Installing Mosquitto MQTT broker..."
            sudo apt-get install -y mosquitto mosquitto-clients
        else
            print_info "Mosquitto MQTT broker already installed"
        fi
        
        # Install rsync - check if already installed
        if ! check_package_installed "rsync"; then
            print_info "Installing rsync..."
            sudo apt-get install -y rsync
        else
            print_info "rsync already installed"
        fi
        
        # Install OpenSSH server (for SFTP) - check if already installed
        if ! check_package_installed "openssh-server"; then
            print_info "Installing OpenSSH server..."
            sudo apt-get install -y openssh-server
        else
            print_info "OpenSSH server already installed"
        fi
        
        # Install Python dependencies for edge communication
        print_info "Installing Python dependencies for edge communication..."
        sudo apt-get install -y python3-paho-mqtt python3-paramiko python3-pil python3-requests python3-websocket
        
        print_status "System dependencies installed"
        
    elif command -v yum >/dev/null 2>&1; then
        sudo yum update -y
        sudo yum install -y mosquitto rsync openssh-server
        print_status "System dependencies installed (YUM)"
        
    elif command -v brew >/dev/null 2>&1; then
        brew install mosquitto rsync
        print_status "System dependencies installed (Homebrew)"
        
    else
        print_error "Unsupported package manager. Please install mosquitto, rsync, and openssh-server manually."
        exit 1
    fi
}

# Setup MQTT broker
setup_mqtt() {
    print_info "Setting up MQTT broker..."
    
    # Check if Mosquitto is already running
    if check_service_running "mosquitto"; then
        print_info "Mosquitto service is already running"
        return 0
    fi
    
    # Check if snap version is running and stop it
    if pgrep -f "snap.*mosquitto" > /dev/null; then
        print_warning "Snap version of Mosquitto detected, stopping it..."
        sudo snap stop mosquitto
        sudo snap disable mosquitto
    fi
    
    # Create MQTT configuration
    sudo mkdir -p /etc/mosquitto/conf.d
    
    # Create clean mosquitto configuration (avoiding duplicates)
    cat << 'EOF' | sudo tee /etc/mosquitto/conf.d/aicamera.conf
# AI Camera MQTT Configuration
listener 1883
allow_anonymous true
max_connections 100
max_queued_messages 1000
EOF

    # Create log directory
    sudo mkdir -p /var/log/mosquitto
    sudo chown mosquitto:mosquitto /var/log/mosquitto
    
    # Create persistence directory
    sudo mkdir -p /var/lib/mosquitto
    sudo chown mosquitto:mosquitto /var/lib/mosquitto
    
    # Create runtime directory
    sudo mkdir -p /run/mosquitto
    sudo chown mosquitto:mosquitto /run/mosquitto
    
    # Enable and start mosquitto
    sudo systemctl enable mosquitto
    sudo systemctl start mosquitto
    
    # Check if MQTT broker is running
    if systemctl is-active --quiet mosquitto; then
        print_status "MQTT broker (Mosquitto) is running on port 1883"
    else
        print_error "Failed to start MQTT broker"
        exit 1
    fi
}

# Setup SFTP server
setup_sftp() {
    print_info "Setting up SFTP server..."
    
    # Create AI Camera user for SFTP
    if ! id "aicamera" >/dev/null 2>&1; then
        sudo useradd -m -d /home/aicamera -s /bin/bash aicamera
        echo "aicamera:aicamera123" | sudo chpasswd
        print_status "Created aicamera user for SFTP access"
    else
        print_info "aicamera user already exists"
    fi
    
    # Create image storage directory
    sudo mkdir -p /home/aicamera/image_storage
    sudo chown aicamera:aicamera /home/aicamera/image_storage
    sudo chmod 755 /home/aicamera/image_storage
    
    # Create SFTP configuration
    if ! grep -q "# AI Camera SFTP Configuration" /etc/ssh/sshd_config; then
        cat << 'EOF' | sudo tee -a /etc/ssh/sshd_config

# AI Camera SFTP Configuration
Match User aicamera
    ChrootDirectory /home/aicamera
    ForceCommand internal-sftp
    AllowTcpForwarding no
    X11Forwarding no
    PasswordAuthentication yes
EOF
        
        # Restart SSH service
        sudo systemctl restart sshd
        print_status "SFTP configuration added to SSH"
    else
        print_info "SFTP configuration already exists"
    fi
    
    # Test SFTP connection
    print_info "Testing SFTP connection..."
    if echo "pwd" | sftp -o BatchMode=no -o StrictHostKeyChecking=no -P 22 aicamera@localhost 2>/dev/null; then
        print_status "SFTP server is accessible"
    else
        print_warning "SFTP test connection failed - manual verification needed"
    fi
}

# Setup image storage directories
setup_storage() {
    print_info "Setting up image storage directories..."
    
    # Create server image storage directory
    mkdir -p ./server/image_storage
    mkdir -p ./server/image_storage/_thumbnails
    mkdir -p ./server/image_storage/_temp
    
    # Create edge captured images directory
    mkdir -p ./edge/captured_images
    mkdir -p ./edge/temp
    
    # Set permissions
    chmod 755 ./server/image_storage
    chmod 755 ./edge/captured_images
    
    print_status "Image storage directories created"
}

# Setup Node.js dependencies for server
setup_server_deps() {
    print_info "Installing server dependencies..."
    
    if [ -f "./server/package.json" ]; then
        cd server
        npm install
        cd ..
        print_status "Server Node.js dependencies installed"
    else
        print_warning "server/package.json not found - skipping Node.js dependencies"
    fi
}

# Setup Python dependencies for edge
setup_edge_deps() {
    print_info "Setting up edge Python dependencies..."
    
    if [ -f "./edge/requirements.txt" ]; then
        cd edge
        
        # Create virtual environment if it doesn't exist
        if [ ! -d "venv_hailo" ]; then
            python3 -m venv venv_hailo
            print_status "Created Python virtual environment"
        fi
        
        # Activate virtual environment and install dependencies
        source venv_hailo/bin/activate
        pip install --upgrade pip
        
        # Install core requirements
        pip install -r requirements.txt
        
        # Install communication dependencies (only if not already installed system-wide)
        if ! python3 -c "import paho.mqtt.client" 2>/dev/null; then
            pip install paho-mqtt
        else
            print_info "paho-mqtt already available"
        fi
        
        if ! python3 -c "import paramiko" 2>/dev/null; then
            pip install paramiko
        else
            print_info "paramiko already available"
        fi
        
        if ! python3 -c "import PIL" 2>/dev/null; then
            pip install pillow
        else
            print_info "PIL/Pillow already available"
        fi
        
        deactivate
        cd ..
        print_status "Edge Python dependencies installed"
    else
        print_warning "edge/requirements.txt not found - skipping Python dependencies"
    fi
}

# Create configuration files
create_configs() {
    print_info "Creating configuration files..."
    
    # Create edge environment file
    if [ ! -f "./edge/.env" ]; then
        cat << 'EOF' > ./edge/.env
# AI Camera Edge Configuration
DEVICE_ID=aicamera-edge-001
DEVICE_MODEL=AI-CAM-EDGE-V2
DEVICE_LOCATION=Test Location

# Server Configuration
SERVER_URL=http://localhost:3000
SERVER_HOST=localhost

# MQTT Configuration
MQTT_ENABLED=true
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# SFTP Configuration
SERVER_SFTP_ENABLED=true
SERVER_SFTP_HOST=localhost
SERVER_SFTP_PORT=22
SERVER_SFTP_USERNAME=aicamera
SERVER_SFTP_PASSWORD=aicamera123

# Storage Configuration
STORAGE_MANAGER_ENABLED=true
TRANSFER_RETRY_INTERVAL=60
MAX_TRANSFER_RETRIES=3
IMAGE_COMPRESSION_ENABLED=true
IMAGE_COMPRESSION_QUALITY=85

# Paths
CAPTURED_IMAGES_PATH=captured_images
DATABASE_PATH=db/lpr_data.db
EOF
        print_status "Created edge .env configuration file"
    else
        print_info "Edge .env file already exists"
    fi
    
    # Create server environment additions
    if [ ! -f "./server/.env.local" ]; then
        cat << 'EOF' > ./server/.env.local
# AI Camera Server Communication Configuration

# MQTT Configuration
MQTT_ENABLED=true
MQTT_URL=mqtt://localhost:1883
MQTT_CLIENT_ID=aicamera-server

# SFTP Configuration
SFTP_ENABLED=false
SFTP_PORT=2222
SFTP_PASSWORD=aicamera123

# Image Storage
IMAGE_STORAGE_PATH=./image_storage
EOF
        print_status "Created server .env.local configuration file"
    else
        print_info "Server .env.local file already exists"
    fi
}

# Create systemd service files
create_services() {
    print_info "Creating systemd service files..."
    
    # Create MQTT service (if not using system mosquitto)
    cat << 'EOF' | sudo tee /etc/systemd/system/aicamera-mqtt.service
[Unit]
Description=AI Camera MQTT Broker
After=network.target
Wants=network.target

[Service]
Type=notify
ExecStart=/usr/sbin/mosquitto -c /etc/mosquitto/conf.d/aicamera.conf
ExecReload=/bin/kill -HUP $MAINPID
User=mosquitto
Group=mosquitto
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    # Enable the service
    sudo systemctl daemon-reload
    sudo systemctl enable aicamera-mqtt
    
    print_status "Created systemd services"
}

# Test communication system functionality
test_communication_system() {
    print_info "Testing communication system..."
    
    # Test MQTT broker
    print_info "Testing MQTT broker..."
    if mosquitto_pub -h localhost -t test/topic -m "Hello MQTT" -p 1883 >/dev/null 2>&1; then
        print_status "MQTT broker test successful"
    else
        print_error "MQTT broker test failed"
        return 1
    fi
    
    # Test SFTP server
    print_info "Testing SFTP server..."
    if echo "pwd" | sftp -o BatchMode=no -o StrictHostKeyChecking=no -P 22 aicamera@localhost >/dev/null 2>&1; then
        print_status "SFTP server test successful"
    else
        print_error "SFTP server test failed"
        return 1
    fi
    
    # Test storage directories
    print_info "Testing storage directories..."
    if [ -d "./server/image_storage" ] && [ -d "./edge/captured_images" ]; then
        print_status "Storage directories are ready"
    else
        print_error "Storage directories not found"
        return 1
    fi
    
    print_status "Communication system tests completed successfully"
}

# Create test data
create_test_data() {
    print_info "Creating test data..."
    
    # Create a test image for edge
    if command -v python3 >/dev/null 2>&1; then
        python3 << 'EOF'
from PIL import Image, ImageDraw
import os

# Create test image
img = Image.new('RGB', (640, 480), color='lightblue')
draw = ImageDraw.Draw(img)
draw.text((10, 10), "AI Camera Test Image", fill='black')
draw.rectangle([100, 100, 200, 150], outline='red', width=2)

# Save to edge captured_images
os.makedirs('./edge/captured_images', exist_ok=True)
img.save('./edge/captured_images/test_image.jpg', 'JPEG')
print("Test image created")
EOF
        print_status "Test image created in edge/captured_images/"
    else
        print_warning "Python3 not available for test image creation"
    fi
}

# Main execution
main() {
    echo "🔧 AI Camera Communication System Setup"
    echo "========================================"
    
    check_root
    
    # Parse command line arguments
    INSTALL_DEPS=true
    SETUP_MQTT=true
    SETUP_SFTP=true
    CREATE_TEST_DATA=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-deps)
                INSTALL_DEPS=false
                shift
                ;;
            --no-mqtt)
                SETUP_MQTT=false
                shift
                ;;
            --no-sftp)
                SETUP_SFTP=false
                shift
                ;;
            --no-test-data)
                CREATE_TEST_DATA=false
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --no-deps      Skip installing system dependencies"
                echo "  --no-mqtt      Skip MQTT broker setup"
                echo "  --no-sftp      Skip SFTP server setup"
                echo "  --no-test-data Skip creating test data"
                echo "  -h, --help     Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Setup steps
    if [ "$INSTALL_DEPS" = true ]; then
        install_dependencies
    fi
    
    if [ "$SETUP_MQTT" = true ]; then
        setup_mqtt
    fi
    
    if [ "$SETUP_SFTP" = true ]; then
        setup_sftp
    fi
    
    setup_storage
    setup_server_deps
    setup_edge_deps
    create_configs
    create_services
    test_communication_system
    
    if [ "$CREATE_TEST_DATA" = true ]; then
        create_test_data
    fi
    
    echo ""
    echo "🎉 Communication System Setup Complete!"
    echo "======================================="
    print_status "MQTT Broker: localhost:1883"
    print_status "SFTP Server: localhost:22 (user: aicamera, pass: aicamera123)"
    print_status "Image Storage: ./server/image_storage"
    print_status "Edge Images: ./edge/captured_images"
    echo ""
    print_info "Next steps:"
    echo "1. Start the server: cd server && npm run start:dev"
    echo "2. Start the edge simulator: cd edge/scripts && ./run_simulator.sh"
    echo "3. Check the admin dashboard for device approval"
    echo "4. Monitor image transfers via the API"
    echo ""
    print_warning "Remember to configure firewall rules for MQTT (1883) and SFTP (22) if needed"
}

# Run main function
main "$@"