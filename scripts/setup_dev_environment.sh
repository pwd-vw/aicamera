#!/bin/bash

# AI Camera Development Environment Setup Script
# This script automates the setup of the development environment for the AI Camera monorepo

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command_exists apt; then
            echo "ubuntu"
        elif command_exists yum; then
            echo "centos"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
print_status "Detected OS: $OS"

# Function to install system dependencies based on OS
install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    case $OS in
        "ubuntu")
            sudo apt update
            sudo apt install -y \
                build-essential \
                python3 \
                python3-pip \
                python3-venv \
                python3-dev \
                git \
                curl \
                wget \
                unzip \
                postgresql \
                postgresql-contrib \
                sqlite3 \
                libsqlite3-dev \
                mosquitto \
                mosquitto-clients \
                openssh-server \
                rsync \
                docker.io \
                docker-compose \
                libffi-dev \
                libssl-dev \
                libjpeg-dev \
                libpng-dev \
                libfreetype6-dev \
                liblcms2-dev \
                libopenjp2-7-dev \
                libtiff5-dev \
                libwebp-dev \
                libharfbuzz-dev \
                libfribidi-dev \
                libxcb1-dev \
                pkg-config \
                libpq-dev
            ;;
        "macos")
            if ! command_exists brew; then
                print_status "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew install \
                python@3.9 \
                git \
                curl \
                wget \
                postgresql@14 \
                sqlite3 \
                mosquitto \
                openssh \
                rsync \
                docker \
                docker-compose \
                openssl \
                libffi \
                pkg-config
            ;;
        "windows")
            print_warning "Windows detected. Please install dependencies manually:"
            print_warning "1. Install Git for Windows"
            print_warning "2. Install Python 3.9+"
            print_warning "3. Install Node.js LTS"
            print_warning "4. Install PostgreSQL"
            print_warning "5. Install Docker Desktop"
            print_warning "6. Install Visual Studio Build Tools"
            return 1
            ;;
        *)
            print_error "Unsupported OS: $OS"
            return 1
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Function to install Node.js
install_nodejs() {
    print_status "Installing Node.js..."
    
    if command_exists node; then
        NODE_VERSION=$(node --version)
        print_status "Node.js already installed: $NODE_VERSION"
        return 0
    fi
    
    case $OS in
        "ubuntu"|"linux")
            # Install Node.js using NodeSource repository
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt install -y nodejs
            ;;
        "macos")
            brew install node
            ;;
        "windows")
            print_warning "Please install Node.js manually from https://nodejs.org/"
            return 1
            ;;
    esac
    
    print_success "Node.js installed: $(node --version)"
}

# Function to setup Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    cd edge
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    # Install Python dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
    
    # Install additional communication dependencies
    pip install \
        paho-mqtt \
        paramiko \
        python-socketio \
        requests \
        pillow \
        opencv-python \
        numpy \
        pytest \
        pytest-cov \
        black \
        flake8 \
        mypy \
        pre-commit
    
    print_success "Python environment setup complete"
    cd ..
}

# Function to setup Node.js environment
setup_nodejs_env() {
    print_status "Setting up Node.js environment..."
    
    cd server
    
    # Install dependencies
    if [ -f "package.json" ]; then
        npm install
        
        # Install additional communication dependencies
        npm install \
            mqtt \
            ssh2 \
            ssh2-sftp-client \
            socket.io \
            @nestjs/websockets \
            @nestjs/platform-socket.io
        
        # Install development dependencies
        npm install -D \
            @types/node \
            @types/jest \
            jest \
            ts-jest \
            @nestjs/testing \
            supertest \
            @types/supertest
    fi
    
    print_success "Node.js environment setup complete"
    cd ..
}

# Function to setup frontend environment
setup_frontend_env() {
    print_status "Setting up frontend environment..."
    
    if [ -d "frontend" ]; then
        cd frontend
        
        if [ -f "package.json" ]; then
            npm install
        fi
        
        print_success "Frontend environment setup complete"
        cd ..
    else
        print_warning "Frontend directory not found, skipping"
    fi
}

# Function to setup databases
setup_databases() {
    print_status "Setting up databases..."
    
    case $OS in
        "ubuntu"|"linux")
            # Start PostgreSQL
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            
            # Create database user and database
            sudo -u postgres psql -c "CREATE USER aicamera WITH PASSWORD 'aicamera123';" 2>/dev/null || true
            sudo -u postgres psql -c "CREATE DATABASE aicamera_db OWNER aicamera;" 2>/dev/null || true
            sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE aicamera_db TO aicamera;" 2>/dev/null || true
            ;;
        "macos")
            # Start PostgreSQL
            brew services start postgresql@14
            
            # Create database user and database
            createdb aicamera_db 2>/dev/null || true
            ;;
    esac
    
    # Setup server database
    cd server
    if command_exists npx; then
        npx prisma generate
        npx prisma db push --preview-feature
    fi
    cd ..
    
    # Setup edge database
    cd edge
    if [ -f "scripts/init_database.py" ]; then
        source venv/bin/activate
        python scripts/init_database.py
    fi
    cd ..
    
    print_success "Databases setup complete"
}

# Function to setup communication services
setup_communication_services() {
    print_status "Setting up communication services..."
    
    case $OS in
        "ubuntu"|"linux")
            # Start MQTT broker
            sudo systemctl start mosquitto
            sudo systemctl enable mosquitto
            
            # Start SSH server
            sudo systemctl start ssh
            sudo systemctl enable ssh
            
            # Create SFTP user
            sudo useradd -m -s /bin/bash aicamera 2>/dev/null || true
            echo "aicamera:aicamera123" | sudo chpasswd
            ;;
        "macos")
            # Start MQTT broker
            brew services start mosquitto
            
            # Start SSH server
            sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist
            
            # Create SFTP user
            sudo dscl . -create /Users/aicamera
            sudo dscl . -create /Users/aicamera UserShell /bin/bash
            sudo dscl . -create /Users/aicamera RealName "AI Camera"
            sudo dscl . -create /Users/aicamera UniqueID 1001
            sudo dscl . -create /Users/aicamera PrimaryGroupID 1000
            sudo dscl . -create /Users/aicamera NFSHomeDirectory /Users/aicamera
            sudo dscl . -passwd /Users/aicamera aicamera123
            sudo createhomedir -c -u aicamera
            ;;
    esac
    
    # Create image storage directories
    mkdir -p server/image_storage
    mkdir -p edge/captured_images
    
    print_success "Communication services setup complete"
}

# Function to create environment files
create_environment_files() {
    print_status "Creating environment files..."
    
    # Edge environment
    if [ ! -f "edge/.env" ]; then
        cat > edge/.env << EOF
# Device Configuration
DEVICE_ID=aicamera-edge-001
DEVICE_MODEL=AI-CAM-EDGE-V2
SERVER_URL=http://localhost:3000

# Communication Settings
MQTT_ENABLED=true
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# SFTP Settings
SERVER_SFTP_HOST=localhost
SERVER_SFTP_PORT=22
SERVER_SFTP_USERNAME=aicamera
SERVER_SFTP_PASSWORD=aicamera123

# Storage Settings
STORAGE_MANAGER_ENABLED=true
IMAGE_COMPRESSION_ENABLED=true
IMAGE_COMPRESSION_QUALITY=85
EOF
        print_success "Edge environment file created"
    fi
    
    # Server environment
    if [ ! -f "server/.env" ]; then
        cat > server/.env << EOF
# Database Configuration
DATABASE_URL="postgresql://aicamera:aicamera123@localhost:5432/aicamera_db"

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
API_KEY_SECRET=your-api-key-secret-change-this-in-production

# Server Configuration
PORT=3000
NODE_ENV=development
EOF
        print_success "Server environment file created"
    fi
    
    # Communication environment
    if [ ! -f "server/.env.communication" ]; then
        cat > server/.env.communication << EOF
# MQTT Broker Settings
MQTT_ENABLED=true
MQTT_URL=mqtt://localhost:1883

# SFTP Server Settings
SFTP_ENABLED=true
SFTP_PORT=2222
SFTP_PASSWORD=aicamera123

# Image Storage Settings
IMAGE_STORAGE_PATH=./image_storage
IMAGE_THUMBNAIL_SIZE=200
EOF
        print_success "Communication environment file created"
    fi
}

# Function to setup development tools
setup_development_tools() {
    print_status "Setting up development tools..."
    
    # Make scripts executable
    chmod +x scripts/*.sh 2>/dev/null || true
    chmod +x edge/scripts/*.sh 2>/dev/null || true
    chmod +x server/scripts/*.sh 2>/dev/null || true
    
    # Setup git hooks
    if command_exists pre-commit; then
        pre-commit install
    fi
    
    print_success "Development tools setup complete"
}

# Function to verify installation
verify_installation() {
    print_status "Verifying installation..."
    
    # Check Python
    if command_exists python3; then
        print_success "Python: $(python3 --version)"
    else
        print_error "Python not found"
    fi
    
    # Check Node.js
    if command_exists node; then
        print_success "Node.js: $(node --version)"
    else
        print_error "Node.js not found"
    fi
    
    # Check npm
    if command_exists npm; then
        print_success "npm: $(npm --version)"
    else
        print_error "npm not found"
    fi
    
    # Check Git
    if command_exists git; then
        print_success "Git: $(git --version)"
    else
        print_error "Git not found"
    fi
    
    # Check PostgreSQL
    if command_exists psql; then
        print_success "PostgreSQL: $(psql --version)"
    else
        print_error "PostgreSQL not found"
    fi
    
    # Check MQTT
    if command_exists mosquitto_pub; then
        print_success "MQTT (Mosquitto) installed"
    else
        print_error "MQTT not found"
    fi
    
    # Check Docker
    if command_exists docker; then
        print_success "Docker: $(docker --version)"
    else
        print_warning "Docker not found (optional)"
    fi
    
    print_success "Installation verification complete"
}

# Function to run tests
run_tests() {
    print_status "Running basic tests..."
    
    # Test MQTT
    if command_exists mosquitto_pub; then
        timeout 5 mosquitto_pub -h localhost -t test -m "hello" 2>/dev/null && print_success "MQTT test passed" || print_warning "MQTT test failed"
    fi
    
    # Test PostgreSQL
    if command_exists psql; then
        psql -h localhost -U aicamera -d aicamera_db -c "SELECT 1;" 2>/dev/null && print_success "PostgreSQL test passed" || print_warning "PostgreSQL test failed"
    fi
    
    print_success "Basic tests complete"
}

# Main setup function
main() {
    print_status "Starting AI Camera development environment setup..."
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root"
        exit 1
    fi
    
    # Install system dependencies
    install_system_dependencies
    
    # Install Node.js
    install_nodejs
    
    # Setup Python environment
    setup_python_env
    
    # Setup Node.js environment
    setup_nodejs_env
    
    # Setup frontend environment
    setup_frontend_env
    
    # Setup databases
    setup_databases
    
    # Setup communication services
    setup_communication_services
    
    # Create environment files
    create_environment_files
    
    # Setup development tools
    setup_development_tools
    
    # Verify installation
    verify_installation
    
    # Run tests
    run_tests
    
    print_success "🎉 Development environment setup complete!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Start the server: cd server && npm run start:dev"
    print_status "2. Start the frontend: cd frontend && npm run serve"
    print_status "3. Run edge simulator: cd edge/scripts && ./run_simulator.sh"
    print_status "4. Access admin dashboard: http://localhost:8080"
    print_status "5. Monitor MQTT: mosquitto_sub -h localhost -t 'aicamera/#'"
    print_status ""
    print_status "Happy coding! 🚀"
}

# Run main function
main "$@"
