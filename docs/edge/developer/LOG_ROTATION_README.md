# AI Camera Internal Log Rotation Configuration

## Overview

This document describes the internal log rotation setup for AI Camera application logs. The system uses Python's built-in logging rotation mechanisms to automatically rotate log files daily at 00:01 and maintains a 3-day retention policy to prevent disk space issues.

## Log Files Managed

The following log files are automatically rotated using internal Python logging:

1. **aicamera.log** - Main application logs (via `logging_config.py`)
2. **gunicorn_access.log** - Gunicorn web server access logs (via `setup_gunicorn_log_rotation.py`)
3. **gunicorn_error.log** - Gunicorn web server error logs (via `setup_gunicorn_log_rotation.py`)
4. **hailort.log** - HailoRT runtime logs (via `hailort_logging.py`)

## Configuration Details

### Rotation Schedule
- **Frequency**: Daily at 00:01 (midnight + 1 minute)
- **Retention**: 3 days of backups
- **Method**: Python TimedRotatingFileHandler
- **Archive Location**: Same directory with `.1`, `.2`, `.3` suffixes

### Internal Configuration
- **Main Logs**: `edge/src/core/utils/logging_config.py`
- **Gunicorn Logs**: `edge/scripts/setup_gunicorn_log_rotation.py`
- **HailoRT Logs**: `edge/config/hailort_logging.py`

## Manual Commands

### Test Logging System
```bash
cd /home/camuser/aicamera
python3 -c "
import sys
sys.path.insert(0, '/home/camuser/aicamera')
from edge.src.core.utils.logging_config import setup_logging
logger = setup_logging('INFO')
logger.info('Testing internal log rotation system')
"
```

### Test HailoRT Logging
```bash
cd /home/camuser/aicamera
python3 -c "
import sys
sys.path.insert(0, '/home/camuser/aicamera')
from edge.config.hailort_logging import configure_hailort_logging
configure_hailort_logging()
"
```

### Test Gunicorn Log Rotation
```bash
cd /home/camuser/aicamera/edge
python3 scripts/setup_gunicorn_log_rotation.py
```

## File Structure

```
/home/camuser/aicamera/edge/logs/
├── aicamera.log                    # Current main log
├── aicamera.log.1                 # Yesterday's log
├── aicamera.log.2                 # Day before yesterday
├── aicamera.log.3                 # 3 days ago
├── gunicorn_access.log            # Current access log
├── gunicorn_access.log.1          # Yesterday's access log
├── gunicorn_error.log             # Current error log
├── gunicorn_error.log.1           # Yesterday's error log
├── hailort.log                    # Current HailoRT log
├── hailort.log.1                  # Yesterday's HailoRT log
└── archive/                       # Archive directory (legacy)
```

## Monitoring

### Check Log Sizes
```bash
ls -lh /home/camuser/aicamera/edge/logs/*.log
```

### View Recent Log Entries
```bash
tail -f /home/camuser/aicamera/edge/logs/aicamera.log
tail -f /home/camuser/aicamera/edge/logs/gunicorn_error.log
```

### Check Rotation Status
```bash
# Check if rotation threads are running
ps aux | grep -i rotation
```

## Troubleshooting

### Log Rotation Not Working
1. Check if logging is initialized: Test with the manual commands above
2. Check permissions: `ls -la /home/camuser/aicamera/edge/logs/`
3. Check Python logging configuration: Verify `logging_config.py` is being imported

### Large Log Files
If log files are growing too large:
1. Restart the application to trigger log rotation
2. Manually clean up old files: `rm /home/camuser/aicamera/edge/logs/*.log.*`

### Permission Issues
```bash
sudo chown -R camuser:camuser /home/camuser/aicamera/edge/logs/
sudo chmod 644 /home/camuser/aicamera/edge/logs/*.log
```

## Configuration Files

### Main Logging Config (`edge/src/core/utils/logging_config.py`)
```python
file_handler = TimedRotatingFileHandler(
    filename=str(log_file),
    when='midnight',        # Rotate at midnight
    interval=1,             # Daily
    backupCount=3,          # Keep 3 backups
    encoding='utf-8',
    atTime=datetime.strptime('00:01', '%H:%M').time()  # Rotate at 00:01
)
```

### HailoRT Logging Config (`edge/config/hailort_logging.py`)
```python
# Sets environment variables for HailoRT logging
os.environ["HAILORT_LOGGER_PATH"] = str(logs_dir)
os.environ["HAILORT_LOG_FILE"] = str(log_file)
```

### Gunicorn Logging Config (`edge/scripts/setup_gunicorn_log_rotation.py`)
```python
# Sets up TimedRotatingFileHandler for gunicorn logs
access_handler = TimedRotatingFileHandler(
    filename=str(access_log_file),
    when='midnight',
    interval=1,
    backupCount=3,
    atTime=datetime.strptime('00:01', '%H:%M').time()
)
```

## Integration with Application

The log rotation is integrated with the application through:

1. **Python Logging**: Uses `TimedRotatingFileHandler` with daily rotation at 00:01
2. **Background Threads**: Daemon threads manage log rotation and cleanup
3. **HailoRT Logging**: Configured to write to the logs directory with rotation support
4. **Gunicorn Logging**: Separate rotation handler for web server logs

## Maintenance

### Regular Maintenance
- Monitor disk space usage
- Check log file sizes weekly
- Verify rotation is working monthly

### Emergency Cleanup
If disk space is critically low:
```bash
# Emergency cleanup - removes all rotated logs
rm /home/camuser/aicamera/edge/logs/*.log.*
rm -rf /home/camuser/aicamera/edge/logs/archive/
```

## Version History

- **v2.0** (2025-09-12): Internal log rotation system
  - Daily rotation at 00:01 using Python TimedRotatingFileHandler
  - 3-day retention with automatic cleanup
  - Background thread management
  - Integration with all log types (aicamera, gunicorn, hailort)

- **v1.0** (2025-09-12): External logrotate system (reverted)
  - Daily rotation at 2:00 AM using system logrotate
  - Compression enabled
  - Integration with Gunicorn and HailoRT logging
