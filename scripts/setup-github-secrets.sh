#!/bin/bash

# GitHub Repository Setup Script for CI/CD
# สำหรับตั้งค่า GitHub repository variables และ secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 GitHub Repository Setup Script for CI/CD${NC}"
echo "================================================"

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

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    print_error "GitHub CLI (gh) is not installed"
    echo ""
    echo "Please install GitHub CLI first:"
    echo "  Ubuntu/Debian: sudo apt install gh"
    echo "  macOS: brew install gh"
    echo "  Windows: winget install GitHub.cli"
    echo ""
    echo "Then authenticate with: gh auth login"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    print_error "Not authenticated with GitHub CLI"
    echo ""
    echo "Please authenticate with: gh auth login"
    exit 1
fi

# Get repository information
print_info "Repository Configuration"
echo "=========================="

# Get current repository
CURRENT_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || echo "")

if [[ -n "$CURRENT_REPO" ]]; then
    print_status "Current repository: $CURRENT_REPO"
    read -p "Use this repository? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        CURRENT_REPO=""
    fi
fi

if [[ -z "$CURRENT_REPO" ]]; then
    read -p "Enter GitHub repository (format: owner/repo): " REPO_URL
    if [[ ! $REPO_URL =~ ^[^/]+/[^/]+$ ]]; then
        print_error "Invalid repository format. Use: owner/repo"
        exit 1
    fi
    CURRENT_REPO=$REPO_URL
fi

print_info "Setting up repository: $CURRENT_REPO"

# Check SSH key
SSH_KEY_PATH="$HOME/.ssh/github_actions"
if [[ ! -f "$SSH_KEY_PATH" ]]; then
    print_warning "SSH key not found: $SSH_KEY_PATH"
    echo ""
    echo "Please run the SSH key setup script first:"
    echo "  ./scripts/setup-ssh-keys.sh"
    echo ""
    read -p "Continue without SSH key? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_status "SSH key found: $SSH_KEY_PATH"
fi

# Function to set repository variable
set_repo_variable() {
    local name=$1
    local value=$2
    local description=$3
    
    print_info "Setting variable: $name"
    
    if gh api repos/$CURRENT_REPO/actions/variables --method POST \
        --field name="$name" \
        --field value="$value" \
        --field visibility="private" &> /dev/null; then
        print_status "Variable $name set successfully"
    else
        print_warning "Failed to set variable $name (may already exist)"
    fi
}

# Function to set repository secret
set_repo_secret() {
    local name=$1
    local value=$2
    local description=$3
    
    print_info "Setting secret: $name"
    
    if echo "$value" | gh secret set "$name" --repo "$CURRENT_REPO" &> /dev/null; then
        print_status "Secret $name set successfully"
    else
        print_warning "Failed to set secret $name (may already exist)"
    fi
}

# Set repository variables
print_info "Setting repository variables..."
echo ""

set_repo_variable "ENABLE_SERVER_DEPLOYMENT" "true" "Enable deployment to LPR server"
set_repo_variable "ENABLE_EDGE_DEPLOYMENT" "true" "Enable deployment to edge devices"

# Set repository secrets
print_info "Setting repository secrets..."
echo ""

# SSH Private Key
if [[ -f "$SSH_KEY_PATH" ]]; then
    SSH_PRIVATE_KEY=$(cat "$SSH_KEY_PATH")
    set_repo_secret "SSH_PRIVATE_KEY" "$SSH_PRIVATE_KEY" "SSH private key for CI/CD"
else
    print_warning "SSH private key not found - skipping SSH_PRIVATE_KEY secret"
fi

# Server and Edge users
set_repo_secret "SERVER_USER" "lpruser" "Username for LPR server"
set_repo_secret "EDGE_USER" "camuser" "Username for edge devices"

# Optional: Database secrets
read -p "Do you want to set database secrets? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter database URL: " DB_URL
    if [[ -n "$DB_URL" ]]; then
        set_repo_secret "DATABASE_URL" "$DB_URL" "Database connection URL"
    fi
    
    read -p "Enter database password: " DB_PASSWORD
    if [[ -n "$DB_PASSWORD" ]]; then
        set_repo_secret "DB_PASSWORD" "$DB_PASSWORD" "Database password"
    fi
fi

# Optional: API keys
read -p "Do you want to set API keys? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter any API key name (or press Enter to skip): " API_KEY_NAME
    if [[ -n "$API_KEY_NAME" ]]; then
        read -p "Enter API key value: " API_KEY_VALUE
        if [[ -n "$API_KEY_VALUE" ]]; then
            set_repo_secret "$API_KEY_NAME" "$API_KEY_VALUE" "API key for $API_KEY_NAME"
        fi
    fi
fi

# Create workflow dispatch script
print_info "Creating workflow dispatch script..."

cat > ~/bin/deploy-manual << 'EOF'
#!/bin/bash
# Manual deployment script

REPO="your-repo-here"  # Replace with your repository

echo "🚀 Manual Deployment Script"
echo "=========================="

# Get deployment options
echo "Deployment Options:"
echo "1. Deploy to LPR Server only"
echo "2. Deploy to Edge Devices only"
echo "3. Deploy to all environments"
echo "4. Deploy to specific edge device"
read -p "Choose option (1-4): " choice

case $choice in
    1)
        gh workflow run deploy.yml --repo $REPO --field deploy_server=true --field deploy_edge=false
        ;;
    2)
        gh workflow run deploy.yml --repo $REPO --field deploy_server=false --field deploy_edge=true
        ;;
    3)
        gh workflow run deploy.yml --repo $REPO --field deploy_server=true --field deploy_edge=true
        ;;
    4)
        echo "Edge Devices:"
        echo "1. aicamera1"
        echo "2. aicamera2"
        echo "3. aicamera3"
        read -p "Choose device (1-3): " device_choice
        
        case $device_choice in
            1) device="aicamera1" ;;
            2) device="aicamera2" ;;
            3) device="aicamera3" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac
        
        gh workflow run deploy.yml --repo $REPO --field deploy_server=false --field deploy_edge=true --field target_edge=$device
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo "✅ Deployment triggered successfully!"
echo "📋 Check status at: https://github.com/$REPO/actions"
EOF

# Update the script with the actual repository
sed -i "s/your-repo-here/$CURRENT_REPO/g" ~/bin/deploy-manual

chmod +x ~/bin/deploy-manual
print_status "Manual deployment script created: ~/bin/deploy-manual"

# Create status check script
cat > ~/bin/check-deployment << 'EOF'
#!/bin/bash
# Check deployment status

REPO="your-repo-here"  # Replace with your repository

echo "🔍 Checking deployment status..."
echo "================================"

# Get latest workflow run
LATEST_RUN=$(gh run list --repo $REPO --limit 1 --json databaseId,status,conclusion,workflowName,createdAt --jq '.[0]')

if [[ "$LATEST_RUN" == "null" ]]; then
    echo "❌ No workflow runs found"
    exit 1
fi

RUN_ID=$(echo "$LATEST_RUN" | jq -r '.databaseId')
STATUS=$(echo "$LATEST_RUN" | jq -r '.status')
CONCLUSION=$(echo "$LATEST_RUN" | jq -r '.conclusion')
WORKFLOW=$(echo "$LATEST_RUN" | jq -r '.workflowName')
CREATED=$(echo "$LATEST_RUN" | jq -r '.createdAt')

echo "📋 Latest Run: $WORKFLOW"
echo "🆔 Run ID: $RUN_ID"
echo "📅 Created: $CREATED"
echo "📊 Status: $STATUS"
echo "✅ Conclusion: $CONCLUSION"

if [[ "$STATUS" == "completed" ]]; then
    if [[ "$CONCLUSION" == "success" ]]; then
        echo "🎉 Deployment completed successfully!"
    else
        echo "❌ Deployment failed!"
        echo ""
        echo "📋 View logs:"
        echo "gh run view $RUN_ID --repo $REPO"
    fi
else
    echo "⏳ Deployment in progress..."
    echo ""
    echo "📋 View logs:"
    echo "gh run view $RUN_ID --repo $REPO --log"
fi
EOF

# Update the script with the actual repository
sed -i "s/your-repo-here/$CURRENT_REPO/g" ~/bin/check-deployment

chmod +x ~/bin/check-deployment
print_status "Status check script created: ~/bin/check-deployment"

# Display current variables and secrets
print_info "Current repository configuration:"
echo ""

echo "📋 Variables:"
gh api repos/$CURRENT_REPO/actions/variables --jq '.variables[] | "  \(.name): \(.value)"' 2>/dev/null || echo "  No variables found"

echo ""
echo "🔐 Secrets:"
gh secret list --repo $CURRENT_REPO 2>/dev/null || echo "  No secrets found"

# Display final summary
echo ""
echo -e "${GREEN}🎉 GitHub Repository Setup Complete!${NC}"
echo "=========================================="
echo ""
echo -e "${BLUE}📋 Repository:${NC}"
echo "  $CURRENT_REPO"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  Manual deploy: deploy-manual"
echo "  Check status: check-deployment"
echo "  View workflows: gh workflow list --repo $CURRENT_REPO"
echo "  View runs: gh run list --repo $CURRENT_REPO"
echo ""
echo -e "${BLUE}🌐 URLs:${NC}"
echo "  Repository: https://github.com/$CURRENT_REPO"
echo "  Actions: https://github.com/$CURRENT_REPO/actions"
echo "  Settings: https://github.com/$CURRENT_REPO/settings/secrets/actions"
echo ""
echo -e "${YELLOW}⚠️  Next Steps:${NC}"
echo "  1. Test the CI/CD workflow"
echo "  2. Monitor deployment logs"
echo "  3. Configure branch protection rules if needed"
echo ""

print_status "GitHub repository setup completed successfully!"
