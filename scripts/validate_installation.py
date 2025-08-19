#!/usr/bin/env python3
"""
Installation Validation Script for AI Camera v1.3

This script validates that the installation is complete and working correctly.
It checks:
- Environment configuration
- Database schema
- Required directories and files
- Service configuration
- System requirements

Author: AI Camera Team
Version: 1.3.4
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def check_environment():
    """Check environment configuration."""
    print("🔍 Checking environment configuration...")
    
    env_file = Path('.env.production')
    if env_file.exists():
        print("✅ .env.production file exists")
        
        # Load and check key variables
        from dotenv import load_dotenv
        load_dotenv('.env.production')
        
        required_vars = ['AICAMERA_ID', 'CHECKPOINT_ID', 'LOCATION_LAT', 'LOCATION_LON']
        for var in required_vars:
            value = os.getenv(var)
            if value:
                print(f"   ✅ {var}: {value}")
            else:
                print(f"   ❌ {var}: Not set")
    else:
        print("❌ .env.production file not found")
        print("   Run: cp env.template .env.production")

def check_database():
    """Check database schema."""
    print("\n🔍 Checking database schema...")
    
    try:
        # Try to import config
        sys.path.insert(0, str(Path.cwd()))
        from v1_3.src.core.config import DATABASE_PATH
    except ImportError:
        DATABASE_PATH = "db/lpr_data.db"
        print(f"⚠️  Using default database path: {DATABASE_PATH}")
    
    db_path = Path(DATABASE_PATH)
    if db_path.exists():
        print(f"✅ Database exists: {db_path}")
        
        # Check schema
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check required tables
            tables = ['detection_results', 'health_checks', 'websocket_sender_logs']
            for table in tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if cursor.fetchone():
                    print(f"   ✅ Table exists: {table}")
                else:
                    print(f"   ❌ Table missing: {table}")
            
            # Check required columns in websocket_sender_logs
            cursor.execute("PRAGMA table_info(websocket_sender_logs)")
            columns = [col[1] for col in cursor.fetchall()]
            required_columns = ['aicamera_id', 'checkpoint_id']
            
            for col in required_columns:
                if col in columns:
                    print(f"   ✅ Column exists: websocket_sender_logs.{col}")
                else:
                    print(f"   ❌ Column missing: websocket_sender_logs.{col}")
            
            conn.close()
            
        except Exception as e:
            print(f"❌ Database error: {e}")
    else:
        print(f"❌ Database not found: {db_path}")
        print("   Run: python v1_3/scripts/update_database_schema.py")

def check_directories():
    """Check required directories."""
    print("\n🔍 Checking required directories...")
    
    required_dirs = ['logs', 'db', 'captured_images', 'resources/models']
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")

def check_files():
    """Check required files."""
    print("\n🔍 Checking required files...")
    
    required_files = [
        'v1_3/src/wsgi.py',
        'v1_3/src/__init__.py',
        'v1_3/__init__.py',
        'gunicorn_config.py',
        'setup_env.sh'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")

def check_service():
    """Check systemd service."""
    print("\n🔍 Checking systemd service...")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'aicamera_v1.3.service'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            status = result.stdout.strip()
            if status == 'active':
                print("✅ Service is running")
            else:
                print(f"⚠️  Service status: {status}")
        else:
            print("❌ Service not found or not running")
    except Exception as e:
        print(f"❌ Could not check service: {e}")

def check_system_requirements():
    """Check system requirements."""
    print("\n🔍 Checking system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} - requires 3.10+")
    
    # Check if running on ARM64
    import platform
    if platform.machine() == 'aarch64':
        print("✅ Architecture: ARM64 (Raspberry Pi compatible)")
    else:
        print(f"⚠️  Architecture: {platform.machine()} (not ARM64)")

def main():
    """Main validation function."""
    print("🚀 AI Camera v1.3 Installation Validation")
    print("=" * 50)
    
    check_environment()
    check_database()
    check_directories()
    check_files()
    check_service()
    check_system_requirements()
    
    print("\n" + "=" * 50)
    print("✅ Installation validation completed!")
    print("\n📝 Next steps:")
    print("   1. Fix any issues identified above")
    print("   2. Run: python v1_3/scripts/update_database_schema.py (if database issues)")
    print("   3. Restart service: sudo systemctl restart aicamera_v1.3.service")
    print("   4. Check logs: sudo journalctl -u aicamera_v1.3.service -f")

if __name__ == "__main__":
    main()
