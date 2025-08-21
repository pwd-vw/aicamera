#!/usr/bin/env python3
"""
Installation Validation Script for AI Camera v1.3

This script validates that all components are properly installed and working
after a fresh installation.

Author: AI Camera Team
Version: 1.3.9
Date: August 2025
"""

import sys
import os
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_python_environment():
    """Check Python environment and virtual environment."""
    print("🔍 Checking Python environment...")
    
    import sys
    print(f"📋 Python executable: {sys.executable}")
    print(f"📋 Python version: {sys.version}")
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        return False


def check_systemd_service():
    """Check if systemd service is properly configured and running."""
    print("🔍 Checking systemd service...")
    
    try:
        # Check if service exists
        result = subprocess.run(['systemctl', 'is-enabled', 'aicamera_v1.3.service'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Service is enabled")
        else:
            print("❌ Service is not enabled")
            return False
        
        # Check if service is active
        result = subprocess.run(['systemctl', 'is-active', 'aicamera_v1.3.service'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Service is active")
            return True
        else:
            print(f"❌ Service is not active: {result.stdout.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking systemd service: {e}")
        return False


def check_nginx_service():
    """Check if nginx is properly configured and running."""
    print("🔍 Checking nginx service...")
    
    try:
        # Check if nginx is active
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ nginx is active")
        else:
            print(f"❌ nginx is not active: {result.stdout.strip()}")
            return False
        
        # Check nginx configuration
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ nginx configuration is valid")
            return True
        else:
            print(f"❌ nginx configuration error: {result.stderr.strip()}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking nginx: {e}")
        return False


def check_web_interface():
    """Check if web interface is accessible."""
    print("🔍 Checking web interface...")
    
    try:
        import requests
        
        # Try to access health endpoint
        response = requests.get('http://localhost/health', timeout=10)
        if response.status_code == 200:
            print("✅ Web interface is accessible")
            return True
        else:
            print(f"❌ Web interface returned status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing web interface: {e}")
        return False


def check_directories():
    """Check if required directories exist and have proper permissions."""
    print("🔍 Checking required directories...")
    
    required_dirs = [
        'logs',
        'db', 
        'captured_images',
        'resources/models',
        'v1_3/src'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            if os.access(path, os.R_OK | os.W_OK):
                print(f"✅ {dir_path} exists and is accessible")
            else:
                print(f"❌ {dir_path} exists but not accessible")
                all_ok = False
        else:
            print(f"❌ {dir_path} does not exist")
            all_ok = False
    
    return all_ok


def check_configuration_files():
    """Check if configuration files exist."""
    print("🔍 Checking configuration files...")
    
    required_files = [
        '.env.production',
        'nginx.conf',
        'systemd_service/aicamera_v1.3.service',
        'gunicorn_config.py'
    ]
    
    all_ok = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} does not exist")
            all_ok = False
    
    return all_ok


def run_component_validations():
    """Run component-specific validations."""
    print("🔍 Running component validations...")
    
    all_ok = True
    
    # Run EasyOCR validation
    try:
        result = subprocess.run([sys.executable, 'v1_3/scripts/validate_easyocr.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ EasyOCR validation passed")
        else:
            print("❌ EasyOCR validation failed")
            all_ok = False
    except Exception as e:
        print(f"❌ Error running EasyOCR validation: {e}")
        all_ok = False
    
    # Run database validation
    try:
        result = subprocess.run([sys.executable, 'v1_3/scripts/validate_database.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Database validation passed")
        else:
            print("❌ Database validation failed")
            all_ok = False
    except Exception as e:
        print(f"❌ Error running database validation: {e}")
        all_ok = False
    
    return all_ok


def check_logs():
    """Check if log files are being created."""
    print("🔍 Checking log files...")
    
    log_files = [
        'logs/aicamera.log',
        'v1_3/logs/aicamera.log'
    ]
    
    all_ok = True
    for log_file in log_files:
        path = Path(log_file)
        if path.exists():
            size = path.stat().st_size
            if size > 0:
                print(f"✅ {log_file} exists and has content ({size} bytes)")
            else:
                print(f"⚠️  {log_file} exists but is empty")
        else:
            print(f"❌ {log_file} does not exist")
            all_ok = False
    
    return all_ok


def main():
    """Main validation function."""
    print("🚀 Starting Installation Validation for AI Camera v1.3...")
    print("="*60)
    
    all_passed = True
    
    # Run all checks
    if not check_python_environment():
        all_passed = False
    
    if not check_directories():
        all_passed = False
    
    if not check_configuration_files():
        all_passed = False
    
    if not check_systemd_service():
        all_passed = False
    
    if not check_nginx_service():
        all_passed = False
    
    if not check_web_interface():
        all_passed = False
    
    if not run_component_validations():
        all_passed = False
    
    if not check_logs():
        all_passed = False
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ All installation validations passed!")
        print("🎉 AI Camera v1.3 is properly installed and ready for production use")
        print("\n📋 Quick access:")
        print("   🌐 Web Interface: http://localhost")
        print("   📊 Service Status: sudo systemctl status aicamera_v1.3.service")
        print("   📋 Service Logs: sudo journalctl -u aicamera_v1.3.service -f")
        return 0
    else:
        print("❌ Some installation validations failed")
        print("🔧 Please review the validation output above and fix any issues")
        print("\n📋 Common fixes:")
        print("   - Run: ./install.sh (to reinstall)")
        print("   - Check: sudo systemctl status aicamera_v1.3.service")
        print("   - Check: sudo nginx -t")
        print("   - Check: python v1_3/scripts/validate_easyocr.py")
        print("   - Check: python v1_3/scripts/validate_database.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
