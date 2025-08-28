#!/bin/bash

# SSH Key Setup Script for CI/CD
# สำหรับตั้งค่า SSH keys และทดสอบการเชื่อมต่อ

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SSH_KEY_NAME="github_actions"
SSH_KEY_PATH="$HOME/.ssh/$SSH_KEY_NAME"
SERVERS=(
    "lprserver.tail605477.ts.net:lpruser"
    "aicamera1.tail605477.ts.net:camuser"
    "aicamera2.tail605477.ts.net:camuser"
    "aicamera3.tail605477.ts.net:camuser"
)

echo -e "${BLUE}🔑 SSH Key Setup Script for CI/CD${NC}"
echo "====================================="

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   echo "Please run as a regular user"
   exit 1
fi

# Create SSH directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Check if SSH key already exists
if [[ -f "$SSH_KEY_PATH" ]]; then
    print_warning "SSH key already exists: $SSH_KEY_PATH"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Using existing SSH key"
    else
        print_info "Generating new SSH key..."
        ssh-keygen -t ed25519 -C "github-actions@aicamera" -f "$SSH_KEY_PATH" -N ""
        print_status "New SSH key generated"
    fi
else
    print_info "Generating new SSH key..."
    ssh-keygen -t ed25519 -C "github-actions@aicamera" -f "$SSH_KEY_PATH" -N ""
    print_status "SSH key generated"
fi

# Set correct permissions
chmod 600 "$SSH_KEY_PATH"
chmod 644 "$SSH_KEY_PATH.pub"

# Display public key
echo ""
print_info "Public Key (add this to GitHub Secrets as SSH_PRIVATE_KEY):"
echo "=================================================================="
echo ""
cat "$SSH_KEY_PATH.pub"
echo ""

# Function to test SSH connection
test_ssh_connection() {
    local server=$1
    local user=$2
    local hostname=$(echo $server | cut -d: -f1)
    
    print_info "Testing SSH connection to $user@$hostname..."
    
    if ssh -o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=no -i "$SSH_KEY_PATH" "$user@$hostname" "echo 'SSH connection successful'" 2>/dev/null; then
        print_status "SSH connection to $user@$hostname successful"
        return 0
    else
        print_error "SSH connection to $user@$hostname failed"
        return 1
    fi
}

# Function to setup SSH key on remote server
setup_ssh_key_on_server() {
    local server=$1
    local user=$2
    local hostname=$(echo $server | cut -d: -f1)
    
    print_info "Setting up SSH key on $user@$hostname..."
    
    # Create .ssh directory and authorized_keys file
    ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$user@$hostname" << 'ENDSSH'
        mkdir -p ~/.ssh
        chmod 700 ~/.ssh
        touch ~/.ssh/authorized_keys
        chmod 600 ~/.ssh/authorized_keys
ENDSSH
    
    # Copy public key to server
    ssh-copy-id -i "$SSH_KEY_PATH.pub" -o StrictHostKeyChecking=no "$user@$hostname"
    
    print_status "SSH key setup completed for $user@$hostname"
}

# Test existing connections first
print_info "Testing existing SSH connections..."
echo ""

connection_tests=()
for server_info in "${SERVERS[@]}"; do
    server=$(echo $server_info | cut -d: -f1)
    user=$(echo $server_info | cut -d: -f2)
    
    if test_ssh_connection "$server" "$user"; then
        connection_tests+=("$server_info:success")
    else
        connection_tests+=("$server_info:failed")
    fi
done

echo ""
print_info "Connection Test Results:"
echo "============================"

failed_connections=()
for test_result in "${connection_tests[@]}"; do
    server_info=$(echo $test_result | cut -d: -f1,2)
    status=$(echo $test_result | cut -d: -f3)
    server=$(echo $server_info | cut -d: -f1)
    user=$(echo $server_info | cut -d: -f2)
    
    if [[ "$status" == "success" ]]; then
        print_status "$user@$server: Connected"
    else
        print_error "$user@$server: Failed"
        failed_connections+=("$server_info")
    fi
done

# Setup SSH keys for failed connections
if [[ ${#failed_connections[@]} -gt 0 ]]; then
    echo ""
    print_warning "Some connections failed. Attempting to setup SSH keys..."
    echo ""
    
    for server_info in "${failed_connections[@]}"; do
        server=$(echo $server_info | cut -d: -f1)
        user=$(echo $server_info | cut -d: -f2)
        
        print_info "Setting up SSH key for $user@$server..."
        
        # Check if we can connect with password
        read -p "Can you connect to $user@$server with password? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            setup_ssh_key_on_server "$server" "$user"
            
            # Test connection again
            if test_ssh_connection "$server" "$user"; then
                print_status "SSH key setup successful for $user@$server"
            else
                print_error "SSH key setup failed for $user@$server"
            fi
        else
            print_warning "Skipping $user@$server - manual setup required"
        fi
    done
fi

# Create SSH config file for easier management
print_info "Creating SSH config file..."

cat > ~/.ssh/config << EOF
# GitHub Actions CI/CD SSH Configuration

# LPR Server
Host lprserver
    HostName lprserver.tail605477.ts.net
    User lpruser
    IdentityFile ~/.ssh/$SSH_KEY_NAME
    StrictHostKeyChecking no
    ConnectTimeout 10

# Edge Devices
Host aicamera1
    HostName aicamera1.tail605477.ts.net
    User camuser
    IdentityFile ~/.ssh/$SSH_KEY_NAME
    StrictHostKeyChecking no
    ConnectTimeout 10

Host aicamera2
    HostName aicamera2.tail605477.ts.net
    User camuser
    IdentityFile ~/.ssh/$SSH_KEY_NAME
    StrictHostKeyChecking no
    ConnectTimeout 10

Host aicamera3
    HostName aicamera3.tail605477.ts.net
    User camuser
    IdentityFile ~/.ssh/$SSH_KEY_NAME
    StrictHostKeyChecking no
    ConnectTimeout 10
EOF

chmod 600 ~/.ssh/config
print_status "SSH config file created: ~/.ssh/config"

# Test all connections using SSH config
echo ""
print_info "Testing all connections using SSH config..."
echo ""

all_success=true
for server_info in "${SERVERS[@]}"; do
    server=$(echo $server_info | cut -d: -f1)
    user=$(echo $server_info | cut -d: -f2)
    host_alias=$(echo $server | cut -d. -f1)
    
    print_info "Testing connection to $host_alias..."
    
    if ssh -o ConnectTimeout=10 -o BatchMode=yes "$host_alias" "echo 'SSH connection successful'" 2>/dev/null; then
        print_status "✅ $host_alias: Connected"
    else
        print_error "❌ $host_alias: Failed"
        all_success=false
    fi
done

# Create management scripts
print_info "Creating management scripts..."

cat > ~/bin/test-ssh-connections << 'EOF'
#!/bin/bash
# Test all SSH connections

echo "🔍 Testing SSH connections..."
echo "============================"

servers=("lprserver" "aicamera1" "aicamera2" "aicamera3")

for server in "${servers[@]}"; do
    echo -n "Testing $server... "
    if ssh -o ConnectTimeout=5 -o BatchMode=yes "$server" "echo 'OK'" 2>/dev/null; then
        echo "✅ Connected"
    else
        echo "❌ Failed"
    fi
done
EOF

cat > ~/bin/deploy-test << 'EOF'
#!/bin/bash
# Test deployment to all servers

echo "🚀 Testing deployment to all servers..."
echo "======================================"

servers=("lprserver" "aicamera1" "aicamera2" "aicamera3")

for server in "${servers[@]}"; do
    echo "Testing $server..."
    
    # Test basic connectivity
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$server" "echo 'Connection OK'" 2>/dev/null; then
        echo "❌ Connection failed"
        continue
    fi
    
    # Test service status
    if ssh "$server" "sudo systemctl is-active --quiet aicamera_*.service 2>/dev/null || echo 'No service found'"; then
        echo "✅ Service check passed"
    else
        echo "⚠️  Service check failed"
    fi
    
    # Test health endpoint
    if [[ "$server" == "lprserver" ]]; then
        if ssh "$server" "curl -s -f http://localhost:3000/health >/dev/null 2>&1"; then
            echo "✅ Health check passed"
        else
            echo "❌ Health check failed"
        fi
    else
        if ssh "$server" "curl -s -f http://localhost/health >/dev/null 2>&1"; then
            echo "✅ Health check passed"
        else
            echo "❌ Health check failed"
        fi
    fi
    
    echo ""
done
EOF

mkdir -p ~/bin
chmod +x ~/bin/test-ssh-connections
chmod +x ~/bin/deploy-test

print_status "Management scripts created in ~/bin/"

# Display final summary
echo ""
echo -e "${GREEN}🎉 SSH Key Setup Complete!${NC}"
echo "================================"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo "  SSH Key: $SSH_KEY_PATH"
echo "  Public Key: $SSH_KEY_PATH.pub"
echo "  Config: ~/.ssh/config"
echo "  Scripts: ~/bin/"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Test connections: test-ssh-connections"
echo "  Test deployment: deploy-test"
echo "  Quick connect: ssh lprserver"
echo "  Quick connect: ssh aicamera1"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "  1. Add the private key to GitHub Secrets as SSH_PRIVATE_KEY"
echo "  2. Test the CI/CD workflow"
echo "  3. Monitor deployment logs"
echo ""

if [[ "$all_success" == true ]]; then
    print_status "All SSH connections are working correctly!"
else
    print_warning "Some connections failed. Please check manually."
fi

echo ""
print_info "SSH key setup completed successfully!"
