#!/bin/bash

# Complete GitHub Actions Runner Setup
# This script completes the runner setup that was partially done

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

echo -e "${BLUE}🚀 Completing GitHub Actions Runner Setup${NC}"
echo "=============================================="

# Check if runner directory exists
if [ ! -d "/opt/github-runner" ]; then
    print_error "GitHub runner directory not found. Please run setup-github-runner.sh first."
    exit 1
fi

# Check if runner is already configured
if [ -d "/opt/github-runner/.runner" ]; then
    print_warning "Runner appears to be already configured. Checking status..."
    cd /opt/github-runner
    if sudo -u github-runner ./run.sh --once --version >/dev/null 2>&1; then
        print_status "Runner is already configured and working"
        exit 0
    else
        print_warning "Runner configuration may be incomplete, continuing setup..."
    fi
fi

# Get configuration details
print_info "Repository Configuration"
echo "=========================="

read -p "Enter GitHub repository (format: owner/repo) [popwandee/aicamera]: " REPO_URL
REPO_URL=${REPO_URL:-popwandee/aicamera}

read -p "Enter GitHub Personal Access Token: " GITHUB_TOKEN
if [[ -z "$GITHUB_TOKEN" ]]; then
    print_error "GitHub token is required"
    exit 1
fi

read -p "Enter runner name [lprserver-runner]: " RUNNER_NAME
RUNNER_NAME=${RUNNER_NAME:-lprserver-runner}

read -p "Enter runner labels [self-hosted,linux,lpr-server]: " RUNNER_LABELS
RUNNER_LABELS=${RUNNER_LABELS:-self-hosted,linux,lpr-server}

# Configure runner
print_info "Configuring runner..."

cd /opt/github-runner
sudo -u github-runner ./config.sh \
    --url "https://github.com/$REPO_URL" \
    --token "$GITHUB_TOKEN" \
    --name "$RUNNER_NAME" \
    --labels "$RUNNER_LABELS" \
    --unattended \
    --replace

print_status "Runner configured successfully"

# Install and start service
print_info "Installing runner service..."

sudo ./svc.sh install github-runner
sudo ./svc.sh start

print_status "Runner service installed and started"

# Create systemd service file for better management
print_info "Creating systemd service file..."

sudo tee /etc/systemd/system/github-runner.service > /dev/null <<EOF
[Unit]
Description=GitHub Actions Runner
After=network.target

[Service]
Type=simple
User=github-runner
Group=github-runner
WorkingDirectory=/opt/github-runner
ExecStart=/opt/github-runner/run.sh
Restart=always
RestartSec=10
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable github-runner
sudo systemctl restart github-runner

print_status "Systemd service created and enabled"

# Create management scripts
print_info "Creating management scripts..."

sudo tee /usr/local/bin/github-runner-status > /dev/null <<EOF
#!/bin/bash
sudo systemctl status github-runner
EOF

sudo tee /usr/local/bin/github-runner-restart > /dev/null <<EOF
#!/bin/bash
sudo systemctl restart github-runner
echo "GitHub Runner restarted"
EOF

sudo tee /usr/local/bin/github-runner-logs > /dev/null <<EOF
#!/bin/bash
sudo journalctl -u github-runner -f
EOF

sudo tee /usr/local/bin/github-runner-update > /dev/null <<EOF
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: github-runner-update <token>"
    exit 1
fi
cd /opt/github-runner
sudo -u github-runner ./run.sh --once
sudo -u github-runner ./config.sh --remove --unattended
sudo -u github-runner ./config.sh --url "https://github.com/$REPO_URL" --token "\$1" --name "$RUNNER_NAME" --labels "$RUNNER_LABELS" --unattended --replace
sudo systemctl restart github-runner
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
RUNNER_HOME=/opt/github-runner
SERVICE_NAME=github-runner
RUNNER_USER=github-runner
RUNNER_GROUP=github-runner
EOF

print_status "Configuration file created: /etc/github-runner.conf"

# Display status
print_info "Checking runner status..."
sleep 5

if sudo systemctl is-active --quiet github-runner; then
    print_status "Runner service is running"
else
    print_error "Runner service is not running"
    sudo systemctl status github-runner
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
echo "  Service: github-runner"
echo "  User: github-runner"
echo "  Home: /opt/github-runner"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Status:   github-runner-status"
echo "  Restart:  github-runner-restart"
echo "  Logs:     github-runner-logs"
echo "  Update:   github-runner-update <token>"
echo ""
echo -e "${BLUE}📁 Files:${NC}"
echo "  Config:   /etc/github-runner.conf"
echo "  Service:  /etc/systemd/system/github-runner.service"
echo "  Home:     /opt/github-runner"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "  1. Check runner status: github-runner-status"
echo "  2. View logs: github-runner-logs"
echo "  3. Test deployment: git push origin main"
echo "  4. Monitor at: https://github.com/$REPO_URL/actions"
echo ""
print_status "Setup completed successfully!"
