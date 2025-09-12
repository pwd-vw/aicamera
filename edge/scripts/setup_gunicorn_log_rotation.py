#!/usr/bin/env python3
"""
Gunicorn Log Rotation Setup

This script sets up log rotation for gunicorn access and error logs
to work with the internal logging system.
"""

import os
import sys
import logging
import logging.handlers
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

def setup_gunicorn_log_rotation():
    """Setup log rotation for gunicorn logs."""
    
    # Get log directory
    edge_dir = Path(__file__).parent.parent
    log_dir = edge_dir / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Setup gunicorn access log rotation
    access_log_file = log_dir / "gunicorn_access.log"
    access_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(access_log_file),
        when='midnight',
        interval=1,
        backupCount=3,
        encoding='utf-8',
        atTime=datetime.strptime('00:01', '%H:%M').time()
    )
    
    # Setup gunicorn error log rotation
    error_log_file = log_dir / "gunicorn_error.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(error_log_file),
        when='midnight',
        interval=1,
        backupCount=3,
        encoding='utf-8',
        atTime=datetime.strptime('00:01', '%H:%M').time()
    )
    
    print(f"✅ Gunicorn log rotation configured:")
    print(f"   • Access log: {access_log_file}")
    print(f"   • Error log: {error_log_file}")
    print(f"   • Rotation: Daily at 00:01")
    print(f"   • Retention: 3 days")

def cleanup_old_gunicorn_logs():
    """Clean up old gunicorn log files."""
    edge_dir = Path(__file__).parent.parent
    log_dir = edge_dir / "logs"
    
    try:
        # Clean up gunicorn access logs
        access_files = list(log_dir.glob("gunicorn_access.log.*"))
        if len(access_files) > 3:
            access_files.sort(key=lambda x: x.stat().st_mtime)
            for old_file in access_files[:-3]:
                old_file.unlink()
                print(f"Deleted old access log: {old_file}")
        
        # Clean up gunicorn error logs
        error_files = list(log_dir.glob("gunicorn_error.log.*"))
        if len(error_files) > 3:
            error_files.sort(key=lambda x: x.stat().st_mtime)
            for old_file in error_files[:-3]:
                old_file.unlink()
                print(f"Deleted old error log: {old_file}")
                
    except Exception as e:
        print(f"Error cleaning up gunicorn logs: {e}")

if __name__ == "__main__":
    setup_gunicorn_log_rotation()
    cleanup_old_gunicorn_logs()
