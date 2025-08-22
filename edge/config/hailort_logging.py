#!/usr/bin/env python3
"""
HailoRT Logging Configuration

This module configures HailoRT logging to write to the edge/logs directory
instead of the current working directory.
"""

import os
import sys
from pathlib import Path

def configure_hailort_logging():
    """
    Configure HailoRT logging to write to edge/logs directory.
    
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
        
        print(f"✅ HailoRT logging configured to: {log_file}")
        
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
