#!/bin/bash

# Edge Communication System Setup Script for AI Camera
# This script sets up, configures, and verifies all edge-side communication components

echo "🚀 Setting up AI Camera Edge Communication System..."

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

# Check if package is already installed
check_package_installed() {
    local package_name=$1
    if dpkg -l | grep -q "^ii  $package_name "; then
        return 0
    else
        return 1
    fi
}

# Check if Python module is available
check_python_module() {
    local module_name=$1
    if python3 -c "import $module_name" 2>/dev/null; then
        return 0
    else
        return 1
    fi
}

# Install system dependencies for edge communication
install_system_dependencies() {
    print_info "Installing system dependencies for edge communication..."
    
    # Update package list
    sudo apt-get update
    
    # Install Python packages for edge communication
    local packages=(
        "python3-paho-mqtt"
        "python3-paramiko" 
        "python3-pil"
        "python3-requests"
        "python3-websocket"
        "python3-venv"
        "python3-pip"
    )
    
    for package in "${packages[@]}"; do
        if ! check_package_installed "$package"; then
            print_info "Installing $package..."
            sudo apt-get install -y "$package"
        else
            print_info "$package already installed"
        fi
    done
    
    print_status "System dependencies installed"
}

# Setup Python virtual environment
setup_python_environment() {
    print_info "Setting up Python virtual environment..."
    
    cd edge
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv_hailo" ]; then
        print_info "Creating Python virtual environment..."
        python3 -m venv venv_hailo
        print_status "Python virtual environment created"
    else
        print_info "Python virtual environment already exists"
    fi
    
    # Activate virtual environment and install dependencies
    source venv_hailo/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install core requirements if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        print_info "Installing core requirements..."
        pip install -r requirements.txt
    else
        print_warning "requirements.txt not found - creating basic requirements"
        cat > requirements.txt << 'REQEOF'
# AI Camera Edge Core Requirements
flask>=3.1.1
flask-socketio==5.3.6
python-socketio==5.9.0
werkzeug>=0.6
picamera2==0.3.12
sqlalchemy==2.0.23
alembic==1.12.1
pillow>=10.3.0
opencv-python==4.8.1.78
numpy==1.24.3
paramiko
paho-mqtt
requests
websocket-client
REQEOF
        pip install -r requirements.txt
    fi
    
    # Install communication-specific packages
    print_info "Installing communication dependencies..."
    local comm_packages=(
        "paho-mqtt"
        "paramiko"
        "pillow"
        "requests"
        "websocket-client"
    )
    
    for package in "${comm_packages[@]}"; do
        if ! check_python_module "${package//-/_}"; then
            pip install "$package"
        else
            print_info "$package already available"
        fi
    done
    
    deactivate
    cd ..
    
    print_status "Python environment setup complete"
}

# Create edge communication services
create_communication_services() {
    print_info "Creating edge communication services..."
    
    cd edge
    
    # Create services directory
    mkdir -p src/services
    
    # Create MQTT Client Service
    cat > src/services/mqtt_client.py << 'MQTTEOF'
import paho.mqtt.client as mqtt
import json
import logging
import time
from typing import Optional, Callable

class MQTTClient:
    def __init__(self, host='localhost', port=1883, topic_prefix='aicamera/edge', client_id=None):
        self.host = host
        self.port = port
        self.topic_prefix = topic_prefix
        self.client_id = client_id or f"edge-{int(time.time())}"
        self.client = mqtt.Client(client_id=self.client_id)
        self.connected = False
        self.setup_callbacks()
        
    def setup_callbacks(self):
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            logging.info(f"Connected to MQTT broker at {self.host}:{self.port}")
            # Subscribe to relevant topics
            self.client.subscribe(f"{self.topic_prefix}/+/command")
        else:
            logging.error(f"Failed to connect to MQTT broker, return code: {rc}")
            
    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        logging.info("Disconnected from MQTT broker")
        
    def on_publish(self, client, userdata, mid):
        logging.debug(f"Message published with ID: {mid}")
        
    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            logging.info(f"Received message on {msg.topic}: {payload}")
        except json.JSONDecodeError:
            logging.warning(f"Received non-JSON message on {msg.topic}")
            
    def connect(self):
        try:
            self.client.connect(self.host, self.port, 60)
            self.client.loop_start()
            return True
        except Exception as e:
            logging.error(f"Failed to connect to MQTT broker: {e}")
            return False
            
    def disconnect(self):
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            
    def publish_detection(self, device_id: str, detection_data: dict) -> bool:
        if not self.connected:
            logging.error("Not connected to MQTT broker")
            return False
            
        topic = f"{self.topic_prefix}/{device_id}/detection"
        message = json.dumps(detection_data)
        result = self.client.publish(topic, message, qos=1)
        return result.is_published()
        
    def publish_heartbeat(self, device_id: str, status: str = "online") -> bool:
        if not self.connected:
            return False
            
        topic = f"{self.topic_prefix}/{device_id}/heartbeat"
        message = json.dumps({
            "status": status,
            "timestamp": time.time(),
            "device_id": device_id
        })
        result = self.client.publish(topic, message, qos=0)
        return result.is_published()
MQTTEOF

    # Create SFTP Transfer Service
    cat > src/services/sftp_transfer.py << 'SFTPEOF'
import paramiko
import os
import logging
import time
from pathlib import Path
from typing import Optional

class SFTPTransfer:
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.transport = None
        self.sftp = None
        
    def connect(self) -> bool:
        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logging.info(f"Connected to SFTP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to SFTP server: {e}")
            return False
            
    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
            
    def transfer_image(self, local_path: str, remote_path: str) -> bool:
        if not self.sftp:
            if not self.connect():
                return False
                
        try:
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                self.sftp.stat(remote_dir)
            except FileNotFoundError:
                self.sftp.mkdir(remote_dir)
                
            # Transfer file
            self.sftp.put(local_path, remote_path)
            logging.info(f"Image transferred successfully: {remote_path}")
            return True
        except Exception as e:
            logging.error(f"SFTP transfer failed: {e}")
            return False
SFTPEOF

    # Create WebSocket Client Service
    cat > src/services/websocket_client.py << 'WSEOF'
import websocket
import json
import logging
import threading
import time
from typing import Optional, Callable

class WebSocketClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        
    def connect(self) -> bool:
        try:
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
                
            return self.connected
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            return False
            
    def on_open(self, ws):
        self.connected = True
        self.reconnect_attempts = 0
        logging.info(f"WebSocket connected to {self.server_url}")
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            logging.info(f"Received WebSocket message: {data}")
        except json.JSONDecodeError:
            logging.warning(f"Received non-JSON WebSocket message: {message}")
            
    def on_error(self, ws, error):
        logging.error(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        logging.info("WebSocket connection closed")
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logging.info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(self.reconnect_delay)
            self.connect()
            
    def send_metadata(self, metadata: dict) -> bool:
        if self.connected and self.ws:
            try:
                self.ws.send(json.dumps(metadata))
                return True
            except Exception as e:
                logging.error(f"Failed to send metadata: {e}")
                return False
        return False
        
    def disconnect(self):
        if self.ws:
            self.ws.close()
WSEOF

    cd ..
    
    print_status "Edge communication services created"
}

# Create edge configuration files
create_edge_configuration() {
    print_info "Creating edge configuration files..."
    
    cd edge
    
    # Create edge environment file from template
    if [ ! -f ".env.production" ]; then
        print_info "Creating .env.production from template..."
        cp installation/env.production.template .env.production
        
        # Update with local development values
        sed -i 's/your-server-url:3000/localhost:3000/g' .env.production
        sed -i 's/your-server-url/localhost/g' .env.production
        sed -i 's/your-mqtt-broker-url/localhost/g' .env.production
        sed -i 's/your-sftp-server-url/localhost/g' .env.production
        sed -i 's/your-sftp-password/aicamera123/g' .env.production
        sed -i 's/Production Location/Local Development/g' .env.production
        
        print_status "Created edge .env.production configuration file"
    else
        print_info "Edge .env.production file already exists"
    fi
    
    cd ..
    
    print_status "Edge configuration files created"
}

# Test edge communication system
test_edge_communication() {
    print_info "Testing edge communication system..."
    
    cd edge
    
    # Test Python environment
    if [ -d "venv_hailo" ]; then
        print_info "Testing Python virtual environment..."
        source venv_hailo/bin/activate
        
        # Test imports
        local test_modules=("paho.mqtt.client" "paramiko" "PIL" "requests" "websocket")
        local all_imports_ok=true
        
        for module in "${test_modules[@]}"; do
            if python3 -c "import $module" 2>/dev/null; then
                print_info "✅ $module imported successfully"
            else
                print_error "❌ Failed to import $module"
                all_imports_ok=false
            fi
        done
        
        if [ "$all_imports_ok" = true ]; then
            print_status "All Python modules imported successfully"
        else
            print_error "Some Python modules failed to import"
            return 1
        fi
        
        deactivate
    else
        print_error "Python virtual environment not found"
        return 1
    fi
    
    # Test configuration
    if [ -f ".env.production" ]; then
        print_info "Edge configuration file exists"
        print_status "Edge configuration loaded successfully"
    else
        print_error "Edge .env.production file not found"
        return 1
    fi
    
    # Test service creation
    if [ -f "src/services/mqtt_client.py" ] && \
       [ -f "src/services/sftp_transfer.py" ] && \
       [ -f "src/services/websocket_client.py" ]; then
        print_status "Edge communication services created successfully"
    else
        print_error "Some edge communication services are missing"
        return 1
    fi
    
    cd ..
    
    print_status "Edge communication system tests completed successfully"
}

# Create edge startup script
create_edge_startup_script() {
    print_info "Creating edge startup script..."
    
    cd edge
    
    cat > start_edge.sh << 'STARTEOF'
#!/bin/bash

# AI Camera Edge Startup Script

echo "🚀 Starting AI Camera Edge Application..."

# Check if virtual environment exists
if [ ! -d "venv_hailo" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if configuration exists
if [ ! -f ".env.production" ]; then
    echo "❌ Configuration file not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating Python virtual environment..."
source venv_hailo/bin/activate

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import paho.mqtt.client, paramiko, PIL, requests, websocket" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing Python dependencies. Installing..."
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Starting edge application..."
python3 src/main.py

# Deactivate virtual environment on exit
deactivate
STARTEOF

    chmod +x start_edge.sh
    
    cd ..
    
    print_status "Edge startup script created"
}

# Main execution
main() {
    echo "🔧 AI Camera Edge Communication System Setup"
    echo "============================================="
    
    check_root
    
    # Parse command line arguments
    INSTALL_DEPS=true
    SETUP_PYTHON=true
    CREATE_SERVICES=true
    CREATE_CONFIG=true
    TEST_SYSTEM=true
    CREATE_STARTUP=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-deps)
                INSTALL_DEPS=false
                shift
                ;;
            --no-python)
                SETUP_PYTHON=false
                shift
                ;;
            --no-services)
                CREATE_SERVICES=false
                shift
                ;;
            --no-config)
                CREATE_CONFIG=false
                shift
                ;;
            --no-test)
                TEST_SYSTEM=false
                shift
                ;;
            --no-startup)
                CREATE_STARTUP=false
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [options]"
                echo "Options:"
                echo "  --no-deps      Skip installing system dependencies"
                echo "  --no-python    Skip Python environment setup"
                echo "  --no-services  Skip creating communication services"
                echo "  --no-config    Skip creating configuration files"
                echo "  --no-test      Skip testing the system"
                echo "  --no-startup   Skip creating startup script"
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
        install_system_dependencies
    fi
    
    if [ "$SETUP_PYTHON" = true ]; then
        setup_python_environment
    fi
    
    if [ "$CREATE_SERVICES" = true ]; then
        create_communication_services
    fi
    
    if [ "$CREATE_CONFIG" = true ]; then
        create_edge_configuration
    fi
    
    if [ "$TEST_SYSTEM" = true ]; then
        test_edge_communication
    fi
    
    if [ "$CREATE_STARTUP" = true ]; then
        create_edge_startup_script
    fi
    
    echo ""
    echo "🎉 Edge Communication System Setup Complete!"
    echo "============================================"
    print_status "Python Environment: ./edge/venv_hailo"
    print_status "Communication Services: ./edge/src/services/"
    print_status "Configuration: ./edge/.env.production"
    print_status "Startup Script: ./edge/start_edge.sh"
    echo ""
    print_info "Next steps:"
    echo "1. Start the edge application: cd edge && ./start_edge.sh"
    echo "2. Check logs for any errors or warnings"
    echo "3. Verify communication with server components"
    echo "4. Monitor MQTT topics: mosquitto_sub -h localhost -t 'aicamera/edge/#'"
    echo ""
    print_warning "Make sure the server is running before starting edge devices"
}

# Run main function
main "$@"
