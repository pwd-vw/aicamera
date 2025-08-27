#!/bin/bash

# GitHub Actions Runner Setup Script
# สำหรับตั้งค่า self-hosted runner บนเครื่อง local

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RUNNER_VERSION="2.311.0"
RUNNER_USER="github-runner"
RUNNER_GROUP="github-runner"
RUNNER_HOME="/opt/github-runner"
SERVICE_NAME="github-runner"

echo -e "${BLUE}🚀 GitHub Actions Runner Setup Script${NC}"
echo "=================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}❌ This script should not be run as root${NC}"
   echo "Please run as a regular user with sudo privileges"
   exit 1
fi

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

# Check system requirements
print_info "Checking system requirements..."

# Check OS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "Linux OS detected"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "macOS detected"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    print_status "Windows OS detected (via WSL/Git Bash)"
    print_warning "For native Windows, use the PowerShell script: setup-github-runner.ps1"
else
    print_error "Unsupported OS: $OSTYPE"
    print_info "For Windows, use: scripts/setup-github-runner.ps1"
    exit 1
fi

# Check if Docker is available
if command -v docker &> /dev/null; then
    print_status "Docker is available"
else
    print_warning "Docker not found - some workflows may not work"
fi

# Check if Node.js is available
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js is available: $NODE_VERSION"
else
    print_warning "Node.js not found - will be installed"
fi

# Check if Python is available
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_status "Python3 is available: $PYTHON_VERSION"
else
    print_error "Python3 is required but not found"
    exit 1
fi

# Get repository information
print_info "Repository Configuration"
echo "=========================="

read -p "Enter GitHub repository (format: owner/repo): " REPO_URL
if [[ ! $REPO_URL =~ ^[^/]+/[^/]+$ ]]; then
    print_error "Invalid repository format. Use: owner/repo"
    exit 1
fi

read -p "Enter GitHub Personal Access Token: " GITHUB_TOKEN
if [[ -z "$GITHUB_TOKEN" ]]; then
    print_error "GitHub token is required"
    exit 1
fi

read -p "Enter runner name (default: $(hostname)-runner): " RUNNER_NAME
RUNNER_NAME=${RUNNER_NAME:-$(hostname)-runner}

read -p "Enter runner labels (comma-separated, default: self-hosted,linux): " RUNNER_LABELS
RUNNER_LABELS=${RUNNER_LABELS:-self-hosted,linux}

# Create runner user and group
print_info "Creating runner user and group..."

if ! getent group $RUNNER_GROUP > /dev/null 2>&1; then
    sudo groupadd $RUNNER_GROUP
    print_status "Created group: $RUNNER_GROUP"
else
    print_status "Group already exists: $RUNNER_GROUP"
fi

if ! getent passwd $RUNNER_USER > /dev/null 2>&1; then
    sudo useradd -r -g $RUNNER_GROUP -d $RUNNER_HOME -s /bin/bash $RUNNER_USER
    print_status "Created user: $RUNNER_USER"
else
    print_status "User already exists: $RUNNER_USER"
fi

# Create runner directory
print_info "Setting up runner directory..."

sudo mkdir -p $RUNNER_HOME
sudo chown $RUNNER_USER:$RUNNER_GROUP $RUNNER_HOME
sudo chmod 755 $RUNNER_HOME

# Download and install runner
print_info "Downloading GitHub Actions Runner..."

cd /tmp
RUNNER_ARCH="linux-x64"
RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"

if [[ "$OSTYPE" == "darwin"* ]]; then
    RUNNER_ARCH="osx-x64"
    RUNNER_URL="https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
fi

wget -O actions-runner.tar.gz $RUNNER_URL
print_status "Downloaded runner version $RUNNER_VERSION"

# Extract runner
sudo tar -xzf actions-runner.tar.gz -C $RUNNER_HOME --strip-components=1
sudo chown -R $RUNNER_USER:$RUNNER_GROUP $RUNNER_HOME
print_status "Extracted runner to $RUNNER_HOME"

# Install dependencies
print_info "Installing runner dependencies..."

cd $RUNNER_HOME
sudo -u $RUNNER_USER ./bin/installdependencies.sh
print_status "Installed runner dependencies"

# Configure runner
print_info "Configuring runner..."

sudo -u $RUNNER_USER ./config.sh \
    --url "https://github.com/$REPO_URL" \
    --token "$GITHUB_TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --unattended \
    --replace

print_status "Runner configured successfully"

# Install and start service
print_info "Installing runner service..."

sudo ./svc.sh install $RUNNER_USER
sudo ./svc.sh start

print_status "Runner service installed and started"

# Create systemd service file for better management
print_info "Creating systemd service file..."

sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=GitHub Actions Runner
After=network.target

[Service]
Type=simple
User=$RUNNER_USER
Group=$RUNNER_GROUP
WorkingDirectory=$RUNNER_HOME
ExecStart=$RUNNER_HOME/run.sh
Restart=always
RestartSec=10
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
sudo systemctl restart $SERVICE_NAME

print_status "Systemd service created and enabled"

# Create management scripts
print_info "Creating management scripts..."

sudo tee /usr/local/bin/github-runner-status > /dev/null <<EOF
#!/bin/bash
sudo systemctl status $SERVICE_NAME
EOF

sudo tee /usr/local/bin/github-runner-restart > /dev/null <<EOF
#!/bin/bash
sudo systemctl restart $SERVICE_NAME
echo "GitHub Runner restarted"
EOF

sudo tee /usr/local/bin/github-runner-logs > /dev/null <<EOF
#!/bin/bash
sudo journalctl -u $SERVICE_NAME -f
EOF

sudo tee /usr/local/bin/github-runner-update > /dev/null <<EOF
#!/bin/bash
cd $RUNNER_HOME
sudo -u $RUNNER_USER ./run.sh --once
sudo -u $RUNNER_USER ./config.sh --remove --unattended
sudo -u $RUNNER_USER ./config.sh --url "https://github.com/$REPO_URL" --token "\$1" --name "$RUNNER_NAME" --labels "$RUNNER_LABELS" --unattended --replace
sudo systemctl restart $SERVICE_NAME
echo "GitHub Runner updated"
EOF

sudo chmod +x /usr/local/bin/github-runner-*

print_status "Management scripts created"

# Create configuration file
print_info "Creating configuration file..."

sudo tee /etc/github-runner.conf > /dev/null <<EOF
# GitHub Actions Runner Configuration
REPO_URL=$REPO_URL
RUNNER_NAME=$RUNNER_NAME
RUNNER_LABELS=$RUNNER_LABELS
RUNNER_HOME=$RUNNER_HOME
SERVICE_NAME=$SERVICE_NAME
RUNNER_USER=$RUNNER_USER
RUNNER_GROUP=$RUNNER_GROUP
EOF

print_status "Configuration file created: /etc/github-runner.conf"

# Display status
print_info "Checking runner status..."
sleep 5

if sudo systemctl is-active --quiet $SERVICE_NAME; then
    print_status "Runner service is running"
else
    print_error "Runner service is not running"
    sudo systemctl status $SERVICE_NAME
fi

# Display useful information
echo ""
echo -e "${GREEN}🎉 GitHub Actions Runner Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 Configuration:${NC}"
echo "  Repository: $REPO_URL"
echo "  Runner Name: $RUNNER_NAME"
echo "  Labels: $RUNNER_LABELS"
echo "  Service: $SERVICE_NAME"
echo "  User: $RUNNER_USER"
echo "  Home: $RUNNER_HOME"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Status:   github-runner-status"
echo "  Restart:  github-runner-restart"
echo "  Logs:     github-runner-logs"
echo "  Update:   github-runner-update <token>"
echo ""
echo -e "${BLUE}📁 Files:${NC}"
echo "  Config:   /etc/github-runner.conf"
echo "  Service:  /etc/systemd/system/$SERVICE_NAME.service"
echo "  Home:     $RUNNER_HOME"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo "  - Keep your GitHub token secure"
echo "  - Monitor runner logs for issues"
echo "  - Update runner periodically"
echo "  - Backup configuration if needed"
echo ""

# Clean up
rm -f /tmp/actions-runner.tar.gz
print_status "Setup completed successfully!"
