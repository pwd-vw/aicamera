#!/usr/bin/env python3
"""
HailoRT Logging Configuration

This module configures HailoRT logging to write to the edge/logs directory
instead of the current working directory. Includes log rotation support.
"""

import os
import sys
import logging
import logging.handlers
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta

def configure_hailort_logging():
    """
    Configure HailoRT logging to write to edge/logs directory with rotation.
    
    This function must be called BEFORE importing any HailoRT-related modules
    (degirum, hailo, etc.) to ensure logs are written to the correct location.
    """
    try:
        # Get the edge logs directory
        edge_dir = Path(__file__).parent.parent
        logs_dir = edge_dir / "logs"
        
        # Ensure logs directory exists
        logs_dir.mkdir(exist_ok=True)
        
        # Set HailoRT logging environment variables
        os.environ["HAILORT_LOGGER_PATH"] = str(logs_dir)
        os.environ["HAILO_MONITOR"] = "1"  # Enable monitoring
        os.environ["HAILO_TRACE"] = "0"    # Disable trace by default
        
        # Set the log file path
        log_file = logs_dir / "hailort.log"
        os.environ["HAILORT_LOG_FILE"] = str(log_file)
        
        # Force working directory to logs_dir to prevent root directory logging
        original_cwd = os.getcwd()
        try:
            os.chdir(str(logs_dir))
            # Set additional environment variables to ensure correct path
            os.environ["PWD"] = str(logs_dir)
        except Exception as e:
            print(f"Warning: Could not change working directory: {e}")
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
        
        # Setup HailoRT log rotation
        _setup_hailort_log_rotation(logs_dir)
        
        print(f"✅ HailoRT logging configured to: {log_file} (with rotation)")
        
    except Exception as e:
        print(f"⚠️  Failed to configure HailoRT logging: {e}")
        # Fallback to default location
        pass

def get_hailort_log_path():
    """
    Get the configured HailoRT log file path.
    
    Returns:
        str: Path to the HailoRT log file
    """
    edge_dir = Path(__file__).parent.parent
    logs_dir = edge_dir / "logs"
    return str(logs_dir / "hailort.log")

def _setup_hailort_log_rotation(logs_dir: Path):
    """Setup HailoRT log rotation."""
    def rotation_manager():
        while True:
            try:
                # Wait until next 00:01
                now = datetime.now()
                next_rotation = now.replace(hour=0, minute=1, second=0, microsecond=0)
                if next_rotation <= now:
                    next_rotation += timedelta(days=1)
                
                sleep_seconds = (next_rotation - now).total_seconds()
                time.sleep(sleep_seconds)
                
                # Perform HailoRT log rotation cleanup
                _cleanup_old_hailort_logs(logs_dir)
                
            except Exception as e:
                print(f"Error in HailoRT log rotation manager: {e}")
                time.sleep(3600)  # Wait 1 hour before retrying
    
    # Start the rotation manager in a daemon thread
    rotation_thread = threading.Thread(target=rotation_manager, daemon=True)
    rotation_thread.start()

def _cleanup_old_hailort_logs(logs_dir: Path, backup_count: int = 3):
    """Clean up old HailoRT log files."""
    try:
        # Get all rotated HailoRT log files
        rotated_files = list(logs_dir.glob("hailort.log.*"))
        
        if len(rotated_files) > backup_count:
            # Sort by modification time (oldest first)
            rotated_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files beyond backup_count
            files_to_remove = rotated_files[:-backup_count]
            for log_file in files_to_remove:
                try:
                    log_file.unlink()
                    print(f"Deleted old HailoRT log file: {log_file}")
                except Exception as e:
                    print(f"Failed to delete old HailoRT log file {log_file}: {e}")
                    
    except Exception as e:
        print(f"Error during HailoRT log cleanup: {e}")

def cleanup_old_logs():
    """
    Clean up old HailoRT logs from the root directory.
    """
    try:
        root_log = Path.cwd() / "hailort.log"
        if root_log.exists():
            # Move the log to the proper location
            edge_dir = Path(__file__).parent.parent
            logs_dir = edge_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            target_log = logs_dir / "hailort.log"
            if target_log.exists():
                # Append content to existing log
                with open(root_log, 'r') as src, open(target_log, 'a') as dst:
                    dst.write(f"\n--- Moved from root directory ---\n")
                    dst.write(src.read())
            else:
                # Move the file
                root_log.rename(target_log)
            
            print(f"✅ Moved hailort.log from root to {target_log}")
            
    except Exception as e:
        print(f"⚠️  Failed to cleanup old logs: {e}")

if __name__ == "__main__":
    # Test the configuration
    configure_hailort_logging()
    print(f"HailoRT log path: {get_hailort_log_path()}")
    cleanup_old_logs()
