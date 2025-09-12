# AI Camera System Update Guide

This guide explains how to update your AI Camera system to the latest version without losing your configuration or data.

## Overview

The AI Camera system provides two main update mechanisms:

1. **In-Place Update**: Updates the system while preserving your configuration and data
2. **Factory Reset + Fresh Install**: Complete system reset with fresh installation

## Update Methods

### Method 1: In-Place Update (Recommended)

This method updates your system while preserving all your settings, data, and configuration.

#### Check for Updates

First, check if updates are available:

```bash
python edge/scripts/check_updates.py
```

This will show you:
- Current version information
- Available git updates
- System package updates
- Python package updates
- Service status

#### Perform Update

If updates are available, run the update script:

```bash
# Standard update (with backup)
./edge/scripts/update_system.sh

# Fast update (no backup)
./edge/scripts/update_system.sh --no-backup

# Maintenance mode (skip service restart)
./edge/scripts/update_system.sh --skip-services
```

#### Update Options

- `--no-backup`: Skip creating backup (faster, but not recommended)
- `--skip-services`: Skip stopping/starting services (for maintenance mode)
- `--force`: Force update even if no changes detected

### Method 2: Factory Reset + Fresh Install

If you encounter issues or want a completely clean installation:

```bash
# 1. Factory reset (removes everything)
./edge/scripts/factory_reset.sh

# 2. Fresh installation
./edge/installation/install.sh
```

## What Gets Updated

### In-Place Update Includes:

1. **System Packages**: Updates all system packages via apt
2. **Python Packages**: Updates all Python dependencies
3. **Application Code**: Pulls latest changes from git repository
4. **Database Schema**: Updates database schema if needed
5. **Service Configuration**: Updates systemd and nginx configurations
6. **Service Restart**: Restarts services with new configuration

### What's Preserved:

- Your `.env.production` configuration
- Database with all detection data
- Captured images
- Log files
- Custom settings

## Update Process Details

### Step-by-Step Process:

1. **System Status Check**: Verifies current system state
2. **Backup Creation**: Creates backup of important data (optional)
3. **Service Management**: Stops services for update
4. **Package Updates**: Updates system and Python packages
5. **Code Updates**: Pulls latest application code
6. **Schema Updates**: Updates database schema
7. **Configuration Updates**: Updates service configurations
8. **Service Restart**: Restarts services with new configuration
9. **Validation**: Validates the update was successful

### Backup Information:

When using the standard update (without `--no-backup`), the system creates a backup in:
```
backups/update_YYYYMMDD_HHMMSS/
├── lpr_data.db              # Database backup
├── .env.production          # Configuration backup
└── captured_images/         # Recent images backup
```

## Troubleshooting

### Update Fails

If the update fails:

1. **Check Logs**: Review the update output for error messages
2. **Restore Backup**: If backup was created, restore from backup directory
3. **Manual Fix**: Address specific issues mentioned in logs
4. **Factory Reset**: As last resort, use factory reset + fresh install

### Service Issues After Update

If services don't start after update:

```bash
# Check service status
sudo systemctl status aicamera_lpr.service

# Check service logs
sudo journalctl -u aicamera_lpr.service -f

# Restart services manually
sudo systemctl restart aicamera_lpr.service
sudo systemctl restart nginx
```

### Database Issues

If database issues occur:

```bash
# Validate database
python edge/scripts/validate_database.py

# Reinitialize database (preserves data)
python edge/scripts/init_database.py
```

## Best Practices

### Before Updating:

1. **Check Available Space**: Ensure at least 2GB free disk space
2. **Backup Important Data**: Always use backup option unless space is limited
3. **Check Service Status**: Ensure services are running before update
4. **Review Changes**: Check git log for recent changes

### During Update:

1. **Don't Interrupt**: Let the update process complete
2. **Monitor Output**: Watch for any error messages
3. **Check Services**: Verify services restart successfully

### After Update:

1. **Validate System**: Check that all services are running
2. **Test Functionality**: Verify camera and detection work
3. **Check Logs**: Review logs for any issues
4. **Clean Up**: Remove old backup files if update was successful

## Version Information

### Current Version: 2.0.0

The system tracks version information in multiple places:
- Git tags: `v2.0.0`
- Package.json: `2.0.0`
- Environment file: `DEVICE_VERSION=2.0.0`

### Version History:

- **v2.0.0**: Current stable version
- **v1.3.0**: Previous version (legacy)

## Automation

### Scheduled Updates

You can set up automated update checks using cron:

```bash
# Add to crontab (check for updates daily at 2 AM)
0 2 * * * cd /home/camuser/aicamera && python edge/scripts/check_updates.py >> /var/log/aicamera_update_check.log 2>&1
```

### Update Notifications

The update checker can be integrated with monitoring systems to send notifications when updates are available.

## Support

If you encounter issues with the update process:

1. **Check Documentation**: Review this guide and other documentation
2. **Review Logs**: Check system and application logs
3. **Factory Reset**: Use factory reset as last resort
4. **Contact Support**: Reach out to the AI Camera team

## Related Scripts

- `edge/scripts/update_system.sh`: Main update script
- `edge/scripts/check_updates.py`: Update checker
- `edge/scripts/factory_reset.sh`: Factory reset script
- `edge/scripts/validate_database.py`: Database validation
- `edge/installation/install.sh`: Fresh installation script
