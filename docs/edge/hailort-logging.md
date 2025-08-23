# HailoRT Logging Configuration

## Overview

HailoRT (Hailo Runtime) creates log files when the `degirum` Python library is imported. By default, these logs are written to the current working directory as `hailort.log`. This document explains how the AI Camera project configures HailoRT logging to write to the proper location.

## Problem

- **Default Behavior**: HailoRT logs are written to the current working directory
- **Issue**: This creates `hailort.log` in the project root directory
- **Impact**: Clutters the project root and makes log management difficult

## Solution

The AI Camera project configures HailoRT logging to write to `edge/logs/hailort.log` instead of the root directory.

### Configuration Files

#### `edge/config/hailort_logging.py`
Main configuration module that sets up HailoRT logging environment variables.

**Key Functions:**
- `configure_hailort_logging()`: Sets environment variables before importing degirum
- `get_hailort_log_path()`: Returns the configured log file path
- `cleanup_old_logs()`: Moves existing logs from root to proper location

#### `edge/scripts/fix_hailort_logging.py`
Utility script to fix existing logging configuration and move old logs.

### Environment Variables

The following environment variables are set to control HailoRT logging:

```bash
HAILORT_LOGGER_PATH=/home/camuser/aicamera/edge/logs
HAILO_MONITOR=1
HAILO_TRACE=0
HAILORT_LOG_FILE=/home/camuser/aicamera/edge/logs/hailort.log
```

## Implementation

### 1. Import Configuration

All components that import `degirum` must configure logging first:

```python
# Configure HailoRT logging before importing degirum
from edge.config.hailort_logging import configure_hailort_logging
configure_hailort_logging()

import degirum as dg
```

### 2. Components Updated

The following components have been updated to use proper HailoRT logging:

- `edge/src/components/health_monitor.py`
- `edge/src/components/detection_processor.py`
- `edge/src/services/experiment_service.py`

### 3. Log Directory Structure

```
edge/
├── logs/
│   ├── hailort.log          # HailoRT runtime logs
│   ├── aicamera.log         # Application logs
│   ├── gunicorn_access.log  # Gunicorn access logs
│   └── gunicorn_error.log   # Gunicorn error logs
```

## Usage

### Fix Existing Logging

To fix existing HailoRT logging configuration:

```bash
cd edge
python scripts/fix_hailort_logging.py
```

This script will:
1. Create the `edge/logs/` directory if it doesn't exist
2. Move existing `hailort.log` from root to `edge/logs/`
3. Set environment variables for future runs
4. Test the configuration

### Manual Configuration

To manually configure HailoRT logging:

```python
from edge.config.hailort_logging import configure_hailort_logging

# Configure before importing degirum
configure_hailort_logging()

# Now safe to import degirum
import degirum as dg
```

### Check Log Location

To check where HailoRT logs are being written:

```python
from edge.config.hailort_logging import get_hailort_log_path
print(f"HailoRT log path: {get_hailort_log_path()}")
```

## Troubleshooting

### Log Still Appearing in Root Directory

If `hailort.log` still appears in the root directory:

1. **Check Import Order**: Ensure `configure_hailort_logging()` is called before importing `degirum`
2. **Environment Variables**: Verify environment variables are set correctly
3. **Permissions**: Ensure the `edge/logs/` directory is writable
4. **Multiple Processes**: Check if multiple processes are importing degirum

### Debug Configuration

To debug the configuration:

```python
import os
print(f"HAILORT_LOGGER_PATH: {os.environ.get('HAILORT_LOGGER_PATH')}")
print(f"HAILO_MONITOR: {os.environ.get('HAILO_MONITOR')}")
print(f"HAILO_TRACE: {os.environ.get('HAILO_TRACE')}")
```

### Manual Cleanup

To manually move logs:

```bash
# Move existing log
mv hailort.log edge/logs/

# Or append to existing log
cat hailort.log >> edge/logs/hailort.log
rm hailort.log
```

## System-wide Configuration

The system also has a global HailoRT configuration at `/etc/default/hailort_service`:

```bash
[Service]
HAILORT_LOGGER_PATH="/var/log/hailo"
HAILO_MONITOR=0
HAILO_TRACE=0
```

This configuration affects the HailoRT system service, while the project-specific configuration affects Python applications using the `degirum` library.

## Best Practices

1. **Always Configure First**: Call `configure_hailort_logging()` before importing `degirum`
2. **Check Log Location**: Verify logs are being written to the correct location
3. **Monitor Log Size**: HailoRT logs can grow large; implement log rotation if needed
4. **Environment Consistency**: Ensure all components use the same logging configuration
5. **Documentation**: Update this document when adding new components that use degirum

## Related Files

- `edge/config/hailort_logging.py` - Main configuration module
- `edge/scripts/fix_hailort_logging.py` - Fix script
- `edge/logs/` - Log directory
- `/etc/default/hailort_service` - System-wide HailoRT configuration
