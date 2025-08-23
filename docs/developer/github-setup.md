# GitHub Setup Guide for AI Camera Development

**Version:** 2.0.0  
**Last Updated:** 2025-08-23  
**Project:** AI Camera Monorepo

## Overview

This guide provides step-by-step instructions for setting up GitHub and GitHub CLI for development on the AI Camera project, following best practices for security and collaboration.

## Prerequisites

- GitHub account with access to the `popwandee/aicamera` repository
- Raspberry Pi 5 or compatible development environment
- Sudo access for system configuration
- Internet connection for dependency downloads

## Step 1: Install GitHub CLI

### Automated Installation (Recommended)

```bash
# Add GitHub CLI repository
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg

# Add repository to sources
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null

# Install GitHub CLI
sudo apt update && sudo apt install gh -y

# Verify installation
gh --version
```

### Manual Installation

If the automated installation fails, you can install from the official GitHub releases:

```bash
# Download latest release for ARM64
wget https://github.com/cli/cli/releases/latest/download/gh_*_linux_arm64.tar.gz

# Extract and install
tar -xzf gh_*_linux_arm64.tar.gz
sudo mv gh_*_linux_arm64/bin/gh /usr/local/bin/
```

## Step 2: Create GitHub Personal Access Token

### Token Creation Process

1. **Go to GitHub.com** and sign in to your account
2. **Navigate to Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. **Click "Generate new token"** → **"Generate new token (classic)"**

### Token Configuration

**Token Name:** `aicamera-dev-token`

**Expiration:** 
- **Recommended:** 90 days (for security)
- **Alternative:** 1 year (if you prefer longer sessions)

**Required Scopes:**

#### Core Repository Access
- ✅ **repo** (Full control of private repositories)
  - `repo:status` - Access commit status
  - `repo_deployment` - Access deployment status
  - `public_repo` - Access public repositories
  - `repo:invite` - Invite collaborators
  - `security_events` - Access security events

#### GitHub Actions & Workflows
- ✅ **workflow** (Update GitHub Action workflows)
- ✅ **write:packages** (Upload packages to GitHub Package Registry)
- ✅ **delete:packages** (Delete packages from GitHub Package Registry)

#### Organization Management
- ✅ **admin:org** (Full control of organizations and teams)
- ✅ **admin:org_hook** (Full control of organization hooks)

#### Repository Management
- ✅ **admin:repo_hook** (Full control of repository hooks)
- ✅ **delete_repo** (Delete repositories)

#### User Management
- ✅ **admin:public_key** (Full control of user SSH keys)
- ✅ **admin:gpg_key** (Full control of GPG keys)
- ✅ **user** (Update user profile)

#### Additional Features
- ✅ **gist** (Create gists)
- ✅ **notifications** (Access notifications)
- ✅ **write:discussion** (Create and edit discussions)

### Security Best Practices

- **Never commit the token** to your repository
- **Use environment variables** to store the token
- **Rotate tokens regularly** (every 90 days)
- **Use the minimum required scopes**
- **Monitor token usage** in GitHub settings
- **Store token securely** in environment variables

## Step 3: Configure GitHub CLI

### Authentication Setup

```bash
# Authenticate with GitHub CLI
gh auth login

# Select options:
# - GitHub.com
# - HTTPS
# - Yes (authenticate Git)
# - Paste an authentication token
# - Paste your token
```

### Verify Authentication

```bash
# Check authentication status
gh auth status

# Expected output:
# github.com
#   ✓ Logged in to github.com account popwandee
#   - Active account: true
#   - Git operations protocol: https
#   - Token: ghp_************************************
#   - Token scopes: 'admin:gpg_key', 'admin:org', ...
```

## Step 4: Configure Git for AI Camera Project

### Global Git Configuration

```bash
# Set your GitHub username
git config --global user.name "popwandee"

# Set your GitHub email
git config --global user.email "popwandee@gmail.com"

# Set default branch to main
git config --global init.defaultBranch main

# Verify configuration
git config --global --list
```

### Repository-Specific Configuration

```bash
# Navigate to project directory
cd /home/camuser/aicamera

# Verify remote repository
git remote -v

# Expected output:
# origin  https://github.com/popwandee/aicamera.git (fetch)
# origin  https://github.com/popwandee/aicamera.git (push)
```

## Step 5: Environment Variables Setup

### Add Token to Environment

```bash
# Add token to .bashrc (replace with your actual token)
echo 'export GITHUB_TOKEN="ghp_your_actual_token_here"' >> ~/.bashrc

# Reload environment
source ~/.bashrc

# Verify environment variable
echo $GITHUB_TOKEN
```

### Alternative: Use .env File

```bash
# Create .env file in project root
cat > .env << EOF
GITHUB_TOKEN=ghp_your_actual_token_here
GITHUB_USERNAME=popwandee
GITHUB_REPO=popwandee/aicamera
EOF

# Add .env to .gitignore (if not already present)
echo ".env" >> .gitignore
```

## Step 6: Test GitHub CLI Setup

### Repository Information

```bash
# View repository information
gh repo view

# List repository issues
gh issue list

# List repository pull requests
gh pr list

# View repository workflows
gh workflow list
```

### Create Test Issue

```bash
# Create a test issue
gh issue create --title "Test GitHub CLI Setup" --body "Testing GitHub CLI configuration for AI Camera development."

# List recent issues
gh issue list --limit 5
```

## Step 7: Development Workflow Setup

### Branch Management

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Push branch to remote
git push -u origin feature/your-feature-name

# Create pull request
gh pr create --title "Feature: Your Feature Name" --body "Description of your feature"
```

### Issue Management

```bash
# Create issue
gh issue create --title "Bug: Issue Title" --body "Description of the issue" --label "bug"

# Assign issue to yourself
gh issue edit 123 --assignee popwandee

# Add labels to issue
gh issue edit 123 --add-label "priority-high,edge"
```

### Release Management

```bash
# View releases
gh release list

# Create release
gh release create v2.1.0 --title "Release v2.1.0" --notes "Release notes here"

# View workflow runs
gh run list
```

## Step 8: AI Camera Project-Specific Commands

### Automated Versioning

The AI Camera project uses automated semantic versioning via GitHub Actions:

```bash
# Check current version
cat server/package.json | grep '"version"'

# View versioning workflow
gh workflow view version.yml

# List workflow runs
gh run list --workflow version.yml
```

### Service Management

```bash
# Check service status
sudo systemctl status aicamera_lpr.service

# View service logs
sudo journalctl -u aicamera_lpr.service -f

# Restart service
sudo systemctl restart aicamera_lpr.service
```

### Development Testing

```bash
# Activate Python virtual environment
source edge/venv_hailo/bin/activate

# Run tests
cd edge && python -m pytest tests/

# Check application health
curl http://localhost/health
```

## Step 9: Troubleshooting

### Common Issues

#### Authentication Problems

```bash
# Re-authenticate
gh auth logout
gh auth login

# Check token validity
gh auth status
```

#### Permission Issues

```bash
# Check repository permissions
gh repo view --json permissions

# Verify token scopes
gh auth status
```

#### Git Configuration Issues

```bash
# Reset Git configuration
git config --global --unset user.name
git config --global --unset user.email

# Reconfigure
git config --global user.name "popwandee"
git config --global user.email "popwandee@gmail.com"
```

#### Environment Variable Issues

```bash
# Check environment variables
env | grep GITHUB

# Reload environment
source ~/.bashrc
```

### Token Rotation

When your token expires or for security reasons:

1. **Create new token** following Step 2
2. **Update environment variable:**
   ```bash
   # Remove old token from .bashrc
   sed -i '/GITHUB_TOKEN/d' ~/.bashrc
   
   # Add new token
   echo 'export GITHUB_TOKEN="ghp_new_token_here"' >> ~/.bashrc
   
   # Reload environment
   source ~/.bashrc
   ```
3. **Re-authenticate GitHub CLI:**
   ```bash
   gh auth logout
   gh auth login
   ```

## Step 10: Security Best Practices

### Token Security

- **Never share your token** with others
- **Use different tokens** for different environments
- **Monitor token usage** in GitHub settings
- **Rotate tokens regularly** (every 90 days)
- **Use fine-grained tokens** when possible

### Repository Security

- **Enable 2FA** on your GitHub account
- **Use SSH keys** for additional security
- **Review repository access** regularly
- **Monitor repository activity**

### Development Security

- **Never commit sensitive data** (tokens, passwords, keys)
- **Use environment variables** for configuration
- **Review code before committing**
- **Use branch protection rules**

## Step 11: Integration with AI Camera Workflow

### Automated Workflows

The AI Camera project uses several automated workflows:

```bash
# View all workflows
gh workflow list

# View specific workflow
gh workflow view version.yml

# Run workflow manually
gh workflow run version.yml
```

### Semantic Versioning

The project follows semantic versioning with automated releases:

```bash
# Check current version
cat server/package.json | grep '"version"'

# View release history
gh release list

# Create pre-release
git checkout feature/new-feature
# Make changes and commit with conventional commit message
git commit -m "feat: add new feature"
git push origin feature/new-feature
# GitHub Actions will create alpha release automatically
```

### Conventional Commits

Follow conventional commit format for automated versioning:

```bash
# Feature (minor version bump)
git commit -m "feat: add new camera feature"

# Bug fix (patch version bump)
git commit -m "fix: resolve video streaming issue"

# Breaking change (major version bump)
git commit -m "BREAKING CHANGE: update camera API"

# Documentation
git commit -m "docs: update installation guide"

# Style changes
git commit -m "style: format code according to standards"

# Refactoring
git commit -m "refactor: improve camera handler performance"

# Tests
git commit -m "test: add camera integration tests"

# Chores
git commit -m "chore: update dependencies"
```

## Conclusion

You now have a complete GitHub setup for AI Camera development with:

- ✅ **GitHub CLI** installed and configured
- ✅ **Personal Access Token** with appropriate scopes
- ✅ **Git configuration** for the project
- ✅ **Environment variables** for secure token storage
- ✅ **Development workflow** setup
- ✅ **Security best practices** implemented
- ✅ **Integration** with AI Camera automated workflows

### Next Steps

1. **Start developing** on feature branches
2. **Create issues** for bugs and features
3. **Submit pull requests** for code review
4. **Follow conventional commits** for automated versioning
5. **Monitor workflows** and releases

### Support

- **GitHub CLI Documentation:** https://cli.github.com/
- **GitHub API Documentation:** https://docs.github.com/en/rest
- **AI Camera Project Issues:** https://github.com/popwandee/aicamera/issues
- **AI Camera Project Discussions:** https://github.com/popwandee/aicamera/discussions

---

**Note:** This guide is specific to the AI Camera v2.0.0 monorepo. For other projects, adjust the repository name and configuration accordingly.
