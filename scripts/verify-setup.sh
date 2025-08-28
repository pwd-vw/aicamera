#!/bin/bash

# Verify GitHub Actions Runner Setup
# This script checks the current status of the GitHub runner setup

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

echo -e "${BLUE}🔍 GitHub Actions Runner Setup Verification${NC}"
echo "=============================================="

# Check runner directory
print_info "Checking runner directory..."
if [ -d "/opt/github-runner" ]; then
    print_status "Runner directory exists: /opt/github-runner"
    ls -la /opt/github-runner/
else
    print_error "Runner directory not found: /opt/github-runner"
fi

# Check runner user
print_info "Checking runner user..."
if getent passwd github-runner > /dev/null 2>&1; then
    print_status "Runner user exists: github-runner"
else
    print_error "Runner user not found: github-runner"
fi

# Check runner group
print_info "Checking runner group..."
if getent group github-runner > /dev/null 2>&1; then
    print_status "Runner group exists: github-runner"
else
    print_error "Runner group not found: github-runner"
fi

# Check runner configuration
print_info "Checking runner configuration..."
if [ -f "/opt/github-runner/.runner" ]; then
    print_status "Runner configuration exists"
    print_status "Runner is configured"
    echo "Configuration details:"
    cat /opt/github-runner/.runner | jq . 2>/dev/null || cat /opt/github-runner/.runner
elif [ -d "/opt/github-runner/.runner" ]; then
    print_status "Runner configuration directory exists"
    print_status "Runner is configured"
else
    print_error "Runner not configured (no .runner file or directory)"
fi

# Check systemd service
print_info "Checking systemd service..."
if systemctl list-unit-files | grep -q github-runner; then
    print_status "GitHub runner service exists"
    
    if systemctl is-active --quiet github-runner; then
        print_status "GitHub runner service is running"
    else
        print_warning "GitHub runner service is not running"
        systemctl status github-runner --no-pager -l
    fi
    
    if systemctl is-enabled --quiet github-runner; then
        print_status "GitHub runner service is enabled"
    else
        print_warning "GitHub runner service is not enabled"
    fi
else
    print_error "GitHub runner service not found"
fi

# Check management scripts
print_info "Checking management scripts..."
SCRIPTS=("github-runner-status" "github-runner-restart" "github-runner-logs" "github-runner-update")
for script in "${SCRIPTS[@]}"; do
    if [ -f "/usr/local/bin/$script" ]; then
        print_status "Management script exists: $script"
    else
        print_warning "Management script missing: $script"
    fi
done

# Check configuration file
print_info "Checking configuration file..."
if [ -f "/etc/github-runner.conf" ]; then
    print_status "Configuration file exists: /etc/github-runner.conf"
    echo "Configuration contents:"
    cat /etc/github-runner.conf
else
    print_warning "Configuration file missing: /etc/github-runner.conf"
fi

# Check GitHub repository access
print_info "Checking GitHub repository access..."
if [ -d "/home/devuser/aicamera/.git" ]; then
    print_status "Git repository found"
    cd /home/devuser/aicamera
    REMOTE_URL=$(git remote get-url origin 2>/dev/null || echo "No remote found")
    print_info "Remote URL: $REMOTE_URL"
else
    print_warning "Git repository not found in current directory"
fi

# Check Tailscale network
print_info "Checking Tailscale network..."
if command -v tailscale >/dev/null 2>&1; then
    print_status "Tailscale is installed"
    TAILSCALE_STATUS=$(tailscale status 2>/dev/null || echo "Status unavailable")
    print_info "Tailscale status: $TAILSCALE_STATUS"
else
    print_warning "Tailscale not found"
fi

# Check SSH connectivity to edge devices
print_info "Checking SSH connectivity to edge devices..."
EDGE_DEVICES=("aicamera1" "aicamera2" "aicamera3" "aicamera4" "aicamera5")
for device in "${EDGE_DEVICES[@]}"; do
    HOST="$device.tail605477.ts.net"
    if ssh -o ConnectTimeout=5 -o BatchMode=yes camuser@$HOST "echo 'SSH connection successful'" 2>/dev/null; then
        print_status "SSH connection to $HOST: OK"
    else
        print_warning "SSH connection to $HOST: Failed"
    fi
done

# Summary
echo ""
echo -e "${BLUE}📊 Setup Summary${NC}"
echo "================"

if [ -f "/opt/github-runner/.runner" ] && systemctl is-active --quiet github-runner; then
    print_status "GitHub Actions Runner is CONFIGURED and RUNNING"
    echo ""
    print_info "Next steps:"
    echo "  1. Test deployment: git push origin main"
    echo "  2. Monitor at: https://github.com/popwandee/aicamera/actions"
    echo "  3. Check runner logs: github-runner-logs"
else
    print_error "GitHub Actions Runner is NOT FULLY CONFIGURED"
    echo ""
    print_info "To complete setup:"
    echo "  1. Generate GitHub Personal Access Token"
    echo "  2. Run: ./scripts/complete-runner-setup.sh"
    echo "  3. Follow the guide: GITHUB_RUNNER_SETUP_GUIDE.md"
fi

echo ""
print_info "For detailed setup instructions, see: GITHUB_RUNNER_SETUP_GUIDE.md"
