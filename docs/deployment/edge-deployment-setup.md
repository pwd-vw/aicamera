# Edge Deployment Setup

This document explains how to set up automated Edge deployment using GitHub Actions.

## Overview

The Edge deployment workflow automatically deploys changes to the Edge component when:
- Changes are pushed to the `main` branch
- Changes affect files in the `edge/` directory
- The workflow file itself is updated

## Deployment Flow

1. **Trigger**: Push to main branch with edge directory changes
2. **Backup**: Create backup of current deployment
3. **Update**: Pull latest code from main branch
4. **Dependencies**: Update Python dependencies
5. **Restart**: Restart systemd service and nginx
6. **Test**: Verify service health and web interface
7. **Rollback**: Automatically rollback if deployment fails

## Required GitHub Secrets

You need to configure the following secrets in your GitHub repository:

### 1. SSH_PRIVATE_KEY
- **Description**: SSH private key for connecting to the Edge device
- **Type**: SSH private key
- **Format**: The entire private key content (including `-----BEGIN OPENSSH PRIVATE KEY-----`)

### 2. EDGE_HOST
- **Description**: IP address or hostname of the Edge device
- **Type**: String
- **Example**: `192.168.1.100` or `edge-device.local`

### 3. EDGE_USER
- **Description**: Username for SSH connection to Edge device
- **Type**: String
- **Example**: `camuser`

## Setup Instructions

### Step 1: Generate SSH Key Pair

On your local machine or CI server:

```bash
# Generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions@aicamera" -f ~/.ssh/github_actions_key

# Display public key to add to Edge device
cat ~/.ssh/github_actions_key.pub

# Display private key to add to GitHub secrets
cat ~/.ssh/github_actions_key
```

### Step 2: Add Public Key to Edge Device

On the Edge device:

```bash
# Add the public key to authorized_keys
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys

# Set proper permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 3: Configure GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret:

   **SSH_PRIVATE_KEY**:
   ```
   -----BEGIN OPENSSH PRIVATE KEY-----
   YOUR_PRIVATE_KEY_CONTENT
   -----END OPENSSH PRIVATE KEY-----
   ```

   **EDGE_HOST**:
   ```
   192.168.1.100
   ```

   **EDGE_USER**:
   ```
   camuser
   ```

### Step 4: Test SSH Connection

Test the SSH connection from GitHub Actions:

```bash
# Test connection (replace with your values)
ssh -i ~/.ssh/github_actions_key camuser@192.168.1.100 "echo 'SSH connection successful'"
```

## Deployment Workflow

### Edge Deployment (`edge-deploy.yml`)
- **Recommended approach** for production deployments
- Updates code and Python dependencies
- Restarts systemd service and nginx
- Includes automatic rollback on failure
- Skips system-level installation (handled separately)
- Fast and reliable for incremental updates

## Manual Deployment

If you prefer manual deployment, you can run the deployment script directly:

```bash
# On the Edge device
cd /home/camuser/aicamera

# Pull latest changes
git fetch origin
git reset --hard origin/main

# Update dependencies
source venv_hailo/bin/activate
pip install -r edge/requirements.txt

# Restart services
sudo systemctl restart aicamera_lpr.service
sudo systemctl restart nginx

# Test deployment
curl http://localhost/health
```

## Troubleshooting

### Common Issues

1. **SSH Connection Failed**
   - Verify SSH_PRIVATE_KEY secret is correct
   - Check EDGE_HOST and EDGE_USER values
   - Ensure public key is in authorized_keys

2. **Service Failed to Start**
   - Check systemd logs: `sudo journalctl -u aicamera_lpr.service`
   - Verify dependencies are installed
   - Check configuration files

3. **Health Check Failed**
   - Verify service is running: `sudo systemctl status aicamera_lpr.service`
   - Check nginx configuration: `sudo nginx -t`
   - Test manually: `curl http://localhost/health`

### Rollback

If deployment fails, the workflow automatically rolls back to the previous backup:

```bash
# Manual rollback (if needed)
cd /home/camuser/aicamera_backups
LATEST_BACKUP=$(ls -t edge_backup_*.tar.gz | head -1)
cd /home/camuser/aicamera
tar -xzf "/home/camuser/aicamera_backups/$LATEST_BACKUP" .
sudo systemctl restart aicamera_lpr.service
sudo systemctl restart nginx
```

## Dependency Management

### Critical Package Updates

The deployment workflow is configured to **ignore major version updates** for critical packages:

```yaml
# These packages are protected from automatic major updates:
- flask           # Web framework - breaking changes can break entire app
- opencv-python   # Computer vision - API changes can break detection
- picamera2       # Camera interface - hardware-specific, very sensitive
- degirum         # Hailo AI - vendor-specific, critical for inference
```

### Why Protect These Packages?

1. **Production Stability**: Your Edge device runs 24/7 with real-time AI inference
2. **Hardware Integration**: Camera and AI accelerator integration is sensitive to API changes
3. **Breaking Changes**: Major updates can introduce incompatible changes
4. **Manual Review**: Allows time to test and validate before deployment

### Update Strategy

- **Minor/Patch Updates**: Automatically applied via Dependabot
- **Major Updates**: Manual review required via pull requests
- **Testing**: Major updates should be tested in development first
- **Rollback**: Always have a rollback plan for major updates

## Security Considerations

1. **SSH Key Security**
   - Use dedicated SSH key for GitHub Actions
   - Never commit private keys to repository
   - Rotate keys regularly

2. **Network Security**
   - Use firewall rules to restrict access
   - Consider VPN for remote deployments
   - Monitor SSH access logs

3. **Service Security**
   - Keep system packages updated
   - Monitor service logs for issues
   - Use HTTPS in production

## Monitoring

Monitor deployment status:

```bash
# Check service status
sudo systemctl status aicamera_lpr.service

# View service logs
sudo journalctl -u aicamera_lpr.service -f

# Check nginx status
sudo systemctl status nginx

# Test health endpoint
curl http://localhost/health
```

## Backup Management

Backups are automatically managed:

- **Location**: `/home/camuser/aicamera_backups/`
- **Format**: `edge_backup_YYYYMMDD_HHMMSS.tar.gz`
- **Retention**: Last 5 backups kept automatically
- **Manual cleanup**: `rm /home/camuser/aicamera_backups/edge_backup_*.tar.gz`
