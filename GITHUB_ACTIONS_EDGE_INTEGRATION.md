# GitHub Actions Edge Integration

This document explains how the edge installation has been integrated with GitHub Actions for automated deployments.

## Overview

The edge installation process has been enhanced to support automated deployment via GitHub Actions. This includes:

1. **GitHub Actions Installation Script**: `edge/installation/install_github_actions.sh`
2. **Updated Deployment Workflow**: `.github/workflows/deploy.yml`
3. **Non-interactive Installation**: Automated setup without user prompts
4. **Fallback Mechanisms**: Graceful degradation if the installation script fails

## Key Features

### 1. GitHub Actions Installation Script

**File**: `edge/installation/install_github_actions.sh`

**Purpose**: Automated edge device installation optimized for GitHub Actions

**Key Differences from Manual Installation**:
- **Non-interactive**: No user prompts, uses environment variables
- **Automated Configuration**: Sets up environment variables automatically
- **Error Handling**: Comprehensive error handling and fallback mechanisms
- **Service Management**: Automatically installs and starts systemd services
- **Validation**: Runs comprehensive validation tests

**Environment Variables Used**:
```bash
AICAMERA_ID="${AICAMERA_ID:-1}"
CHECKPOINT_ID="${CHECKPOINT_ID:-1}"
CAMERA_LOCATION="${CAMERA_LOCATION:-GitHub Actions Deployment}"
```

### 2. Updated Deployment Workflow

**File**: `.github/workflows/deploy.yml`

**Changes Made**:
- **Step 3**: Now runs the GitHub Actions installation script instead of manual dependency installation
- **Fallback**: Includes fallback to manual installation if the script fails
- **Service Management**: Handles both old and new service names (`aicamera_lpr.service` and `aicamera_v1.3.service`)
- **Rollback**: Updated rollback procedures to handle new service names

**Deployment Process**:
1. Pull latest code from repository
2. Run GitHub Actions installation script
3. Restart systemd service (with fallback to old service name)
4. Restart nginx
5. Validate deployment
6. Rollback if validation fails

### 3. Installation Script Features

#### Automated Setup
- **SSH Configuration**: Sets up SSH for GitHub Actions deployment
- **Camera System**: Prepares camera system and handles device conflicts
- **Hailo SDK**: Installs and configures Hailo SDK if available
- **Virtual Environment**: Creates and configures Python virtual environment
- **Dependencies**: Installs all required Python packages
- **Database**: Initializes and migrates database schema
- **Nginx**: Configures nginx with proper proxy settings
- **Systemd Service**: Installs and starts the AI Camera service

#### Validation
- **EasyOCR**: Validates EasyOCR installation and fixes issues
- **libcamera**: Validates camera system and handles hardware issues
- **degirum**: Validates AI detection libraries
- **Database**: Validates database setup and schema
- **Service**: Validates service startup and web interface accessibility

#### Error Handling
- **Graceful Degradation**: Continues installation even if some components fail
- **Fallback Mechanisms**: Multiple fallback options for critical components
- **Comprehensive Logging**: Detailed logging for troubleshooting
- **Rollback Support**: Integration with deployment rollback procedures

## Usage

### Manual Testing

To test the installation script manually:

```bash
# Set environment variables
export AICAMERA_ID="1"
export CHECKPOINT_ID="1"
export CAMERA_LOCATION="Test Installation"

# Run the installation script
./edge/installation/install_github_actions.sh
```

### GitHub Actions Deployment

The script is automatically used during GitHub Actions deployment:

1. **Automatic Trigger**: Pushes to `main` branch trigger deployment
2. **Manual Trigger**: Can be triggered manually with custom parameters
3. **Environment Variables**: Can be configured via GitHub repository variables
4. **Matrix Deployment**: Supports deployment to multiple edge devices

### Configuration

#### GitHub Repository Variables

Set these variables in your GitHub repository settings:

- `ENABLE_EDGE_DEPLOYMENT`: Set to `true` to enable edge deployments
- `AICAMERA_ID`: Unique identifier for the edge device
- `CHECKPOINT_ID`: Checkpoint identifier
- `CAMERA_LOCATION`: Human-readable location description

#### SSH Configuration

The script automatically configures SSH for GitHub Actions:

- Adds deployment key to `~/.ssh/authorized_keys`
- Sets proper permissions for SSH files
- Enables secure communication between GitHub Actions and edge devices

## Troubleshooting

### Common Issues

1. **Installation Script Not Found**
   - Ensure `edge/installation/install_github_actions.sh` exists
   - Check file permissions (should be executable)
   - Verify the file is included in the repository

2. **Service Start Failure**
   - Check systemd service status: `sudo systemctl status aicamera_v1.3.service`
   - Review service logs: `sudo journalctl -u aicamera_v1.3.service -f`
   - Verify service file exists: `edge/systemd_service/aicamera_v1.3.service`

3. **Camera Issues**
   - Check camera permissions: `ls -la /dev/video*`
   - Verify camera modules: `lsmod | grep -E "(bcm2835|v4l2)"`
   - Test camera access: `python edge/scripts/validate_libcamera.py`

4. **Database Issues**
   - Check database file: `ls -la edge/db/`
   - Verify database schema: `python edge/scripts/validate_database.py`
   - Run database migrations: `python edge/src/database/schema_migration_v*.py`

### Logs and Debugging

#### Installation Logs
```bash
# View installation script output
./edge/installation/install_github_actions.sh 2>&1 | tee install.log

# Check for specific errors
grep -i "error\|failed\|warning" install.log
```

#### Service Logs
```bash
# View service logs
sudo journalctl -u aicamera_v1.3.service -f

# View nginx logs
sudo journalctl -u nginx -f

# View system logs
sudo journalctl -f
```

#### Validation Scripts
```bash
# Run validation scripts
python edge/scripts/validate_installation.py
python edge/scripts/validate_easyocr.py
python edge/scripts/validate_libcamera.py
python edge/scripts/validate_database.py
```

## Benefits

### For Development
- **Consistent Deployments**: Same installation process across all devices
- **Automated Testing**: Comprehensive validation during deployment
- **Quick Rollbacks**: Automatic rollback on deployment failure
- **Environment Parity**: Ensures development and production environments match

### For Operations
- **Zero-Downtime Deployments**: Rolling updates with health checks
- **Automatic Recovery**: Self-healing deployments with rollback
- **Monitoring Integration**: Health checks and status monitoring
- **Scalable Deployment**: Support for multiple edge devices

### For Maintenance
- **Automated Updates**: Push-based deployment from main branch
- **Backup Management**: Automatic backup creation and cleanup
- **Log Management**: Centralized logging and error reporting
- **Configuration Management**: Environment-specific configuration

## Future Enhancements

### Planned Improvements
1. **Blue-Green Deployment**: Zero-downtime deployment strategy
2. **Canary Deployments**: Gradual rollout to edge devices
3. **Configuration Management**: Centralized configuration via GitHub
4. **Monitoring Integration**: Prometheus/Grafana integration
5. **Health Checks**: Advanced health check endpoints
6. **Auto-scaling**: Dynamic edge device provisioning

### Integration Opportunities
1. **CI/CD Pipeline**: Integration with existing CI/CD tools
2. **Monitoring**: Integration with monitoring and alerting systems
3. **Backup**: Integration with backup and disaster recovery systems
4. **Security**: Integration with security scanning and compliance tools

## Conclusion

The GitHub Actions edge integration provides a robust, automated deployment solution that ensures consistent, reliable deployments across all edge devices. The comprehensive error handling and validation make it suitable for production use, while the fallback mechanisms ensure deployments can continue even when some components fail.

The integration maintains backward compatibility with existing manual installation processes while providing the benefits of automated deployment, making it easy to adopt and maintain.
