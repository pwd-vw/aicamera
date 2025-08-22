#!/usr/bin/env python3
"""
Fix HailoRT Logging Script

This script moves existing hailort.log from the root directory to edge/logs/
and configures HailoRT to log to the proper location.
"""

import os
import shutil
from pathlib import Path

def fix_hailort_logging():
    """
    Fix HailoRT logging by moving logs to edge/logs/ directory.
    """
    print("🔧 Fixing HailoRT logging configuration...")
    
    # Get paths
    current_dir = Path.cwd()
    if current_dir.name == "edge":
        # Running from edge directory
        edge_dir = current_dir
        project_root = current_dir.parent
    else:
        # Running from project root
        project_root = current_dir
        edge_dir = project_root / "edge"
    
    logs_dir = edge_dir / "logs"
    root_log = project_root / "hailort.log"
    
    # Create logs directory if it doesn't exist
    logs_dir.mkdir(exist_ok=True)
    print(f"✅ Created logs directory: {logs_dir}")
    
    # Move existing log from root to edge/logs/
    if root_log.exists():
        target_log = logs_dir / "hailort.log"
        
        if target_log.exists():
            # Append content to existing log
            print(f"📝 Appending root log to existing {target_log}")
            with open(root_log, 'r') as src, open(target_log, 'a') as dst:
                dst.write(f"\n--- Moved from root directory on {os.popen('date').read().strip()} ---\n")
                dst.write(src.read())
            
            # Remove the root log
            root_log.unlink()
            print(f"🗑️  Removed {root_log}")
        else:
            # Move the file
            shutil.move(str(root_log), str(target_log))
            print(f"📁 Moved {root_log} to {target_log}")
    else:
        print("ℹ️  No hailort.log found in root directory")
    
    # Set up environment variables for future runs
    os.environ["HAILORT_LOGGER_PATH"] = str(logs_dir)
    os.environ["HAILO_MONITOR"] = "1"
    os.environ["HAILO_TRACE"] = "0"
    
    print(f"✅ HailoRT logging configured to: {logs_dir}")
    print(f"📋 Environment variables set:")
    print(f"   HAILORT_LOGGER_PATH={logs_dir}")
    print(f"   HAILO_MONITOR=1")
    print(f"   HAILO_TRACE=0")
    
    # Test the configuration
    try:
        from edge.config.hailort_logging import configure_hailort_logging, get_hailort_log_path
        configure_hailort_logging()
        print(f"✅ Configuration test successful")
        print(f"📋 Log path: {get_hailort_log_path()}")
    except Exception as e:
        print(f"⚠️  Configuration test failed: {e}")
    
    print("\n🎉 HailoRT logging fix completed!")
    print("📋 Future HailoRT logs will be written to edge/logs/hailort.log")

if __name__ == "__main__":
    fix_hailort_logging()
