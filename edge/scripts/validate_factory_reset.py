#!/usr/bin/env python3
"""
Factory Reset Validation Script for AI Camera v2.0

This script validates the system state after factory reset and before reinstallation
to ensure no dependency issues exist.

Author: AI Camera Team
Version: 2.0
Date: September 2025
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd, capture_output=True, text=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=text, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_system_services():
    """Check if any AI Camera services are still running."""
    print("🔍 Checking system services...")
    
    # Core services (required)
    core_services = [
        "aicamera_lpr.service",
        "nginx"
    ]
    
    # Optional services
    optional_services = [
        "kiosk-browser.service"
    ]
    
    issues = []
    
    # Check core services
    for service in core_services:
        success, stdout, stderr = run_command(["systemctl", "is-active", service])
        if success and stdout.strip() == "active":
            issues.append(f"⚠️  Core service {service} is still running")
        else:
            print(f"   ✅ Core service {service} is not running")
    
    # Check optional services
    for service in optional_services:
        success, stdout, stderr = run_command(["systemctl", "is-active", service])
        if success and stdout.strip() == "active":
            print(f"   ⚠️  Optional service {service} is still running (will be cleaned up)")
        else:
            print(f"   ✅ Optional service {service} is not running")
    
    return issues

def check_systemd_files():
    """Check if systemd service files are properly removed."""
    print("🔍 Checking systemd service files...")
    
    # Core service files (required)
    core_service_files = [
        "/etc/systemd/system/aicamera_lpr.service"
    ]
    
    # Optional service files
    optional_service_files = [
        "/etc/systemd/system/kiosk-browser.service"
    ]
    
    issues = []
    
    # Check core service files
    for service_file in core_service_files:
        if os.path.exists(service_file):
            issues.append(f"⚠️  Core service file still exists: {service_file}")
        else:
            print(f"   ✅ Core service file removed: {service_file}")
    
    # Check optional service files
    for service_file in optional_service_files:
        if os.path.exists(service_file):
            print(f"   ⚠️  Optional service file still exists: {service_file} (will be cleaned up)")
        else:
            print(f"   ✅ Optional service file removed: {service_file}")
    
    return issues

def check_nginx_config():
    """Check nginx configuration state."""
    print("🔍 Checking nginx configuration...")
    
    issues = []
    
    # Check if nginx site configs are removed
    nginx_sites = [
        "/etc/nginx/sites-enabled/aicamera",
        "/etc/nginx/sites-available/aicamera"
    ]
    
    for site in nginx_sites:
        if os.path.exists(site):
            issues.append(f"⚠️  Nginx site config still exists: {site}")
        else:
            print(f"   ✅ Nginx site config removed: {site}")
    
    # Check if default config is restored
    if os.path.exists("/etc/nginx/sites-available/default.backup"):
        print("   ✅ Default nginx config backup exists")
    else:
        print("   ℹ️  No default nginx config backup found")
    
    return issues

def check_project_files():
    """Check if project files are properly cleaned up."""
    print("🔍 Checking project files...")
    
    project_root = Path.cwd()
    files_to_check = [
        "db/lpr_data.db",
        "edge/db/lpr_data.db",
        "edge/installation/.env.production",
        ".env",
        "captured_images",
        "edge/captured_images",
        "logs",
        "edge/logs",
        "edge/src/logs"
    ]
    
    issues = []
    for file_path in files_to_check:
        full_path = project_root / file_path
        if full_path.exists():
            if full_path.is_file():
                issues.append(f"⚠️  File still exists: {file_path}")
            elif full_path.is_dir():
                # Check if directory is empty
                if any(full_path.iterdir()):
                    issues.append(f"⚠️  Directory not empty: {file_path}")
                else:
                    print(f"   ✅ Directory is empty: {file_path}")
        else:
            print(f"   ✅ File/directory removed: {file_path}")
    
    return issues

def check_virtual_environment():
    """Check virtual environment state."""
    print("🔍 Checking virtual environment...")
    
    venv_path = Path("edge/installation/venv_hailo")
    if venv_path.exists():
        return [f"⚠️  Virtual environment still exists: {venv_path}"]
    else:
        print("   ✅ Virtual environment removed")
        return []

def check_desktop_launcher():
    """Check desktop launcher state."""
    print("🔍 Checking desktop launcher...")
    
    launcher_path = Path("/home/camuser/Desktop/aicamera-browser.desktop")
    if launcher_path.exists():
        print(f"   ⚠️  Optional desktop launcher still exists: {launcher_path} (will be cleaned up)")
        return []
    else:
        print("   ✅ Optional desktop launcher removed")
        return []

def check_system_packages():
    """Check system packages state."""
    print("🔍 Checking system packages...")
    
    # Core packages (required)
    core_packages = [
        "nginx"
    ]
    
    # Optional packages
    optional_packages = [
        "chromium-browser"
    ]
    
    issues = []
    
    # Check core packages
    for package in core_packages:
        success, stdout, stderr = run_command(["dpkg", "-l", package])
        if success and package in stdout:
            print(f"   ℹ️  Core package {package} is installed (may be kept intentionally)")
        else:
            print(f"   ✅ Core package {package} is not installed")
    
    # Check optional packages
    for package in optional_packages:
        success, stdout, stderr = run_command(["dpkg", "-l", package])
        if success and package in stdout:
            print(f"   ℹ️  Optional package {package} is installed (may be kept intentionally)")
        else:
            print(f"   ✅ Optional package {package} is not installed")
    
    return issues

def check_unix_socket():
    """Check if Unix socket is removed."""
    print("🔍 Checking Unix socket...")
    
    socket_path = "/tmp/aicamera.sock"
    if os.path.exists(socket_path):
        return [f"⚠️  Unix socket still exists: {socket_path}"]
    else:
        print("   ✅ Unix socket removed")
        return []

def check_disk_space():
    """Check available disk space."""
    print("🔍 Checking disk space...")
    
    try:
        statvfs = os.statvfs('.')
        free_space_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
        print(f"   📊 Available disk space: {free_space_gb:.2f} GB")
        
        if free_space_gb < 1.0:
            return [f"⚠️  Low disk space: {free_space_gb:.2f} GB available"]
        else:
            print("   ✅ Sufficient disk space available")
            return []
    except Exception as e:
        return [f"⚠️  Could not check disk space: {e}"]

def check_system_requirements():
    """Check if system meets requirements for reinstallation."""
    print("🔍 Checking system requirements...")
    
    issues = []
    
    # Check Python version
    try:
        python_version = sys.version_info
        print(f"   📊 Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
        
        if python_version < (3, 8):
            issues.append(f"⚠️  Python version too old: {python_version.major}.{python_version.minor}.{python_version.micro}")
        else:
            print("   ✅ Python version is compatible")
    except Exception as e:
        issues.append(f"⚠️  Could not check Python version: {e}")
    
    # Check if user is camuser
    if os.getenv('USER') != 'camuser':
        issues.append("⚠️  Not running as camuser")
    else:
        print("   ✅ Running as camuser")
    
    # Check if we're in the right directory
    if not os.path.exists("install.sh"):
        issues.append("⚠️  install.sh not found - not in project root directory")
    else:
        print("   ✅ In project root directory")
    
    return issues

def main():
    """Main validation function."""
    print("🚀 AI Camera v1.3 Factory Reset Validation")
    print("=" * 50)
    
    all_issues = []
    
    # Run all checks
    checks = [
        check_system_requirements,
        check_system_services,
        check_systemd_files,
        check_nginx_config,
        check_project_files,
        check_virtual_environment,
        check_desktop_launcher,
        check_system_packages,
        check_unix_socket,
        check_disk_space
    ]
    
    for check in checks:
        try:
            issues = check()
            all_issues.extend(issues)
            print()
        except Exception as e:
            all_issues.append(f"⚠️  Check failed: {e}")
            print()
    
    # Summary
    print("=" * 50)
    print("📋 VALIDATION SUMMARY")
    print("=" * 50)
    
    if all_issues:
        print("❌ Issues found that may affect reinstallation:")
        for issue in all_issues:
            print(f"   {issue}")
        print()
        print("🔧 Recommended actions:")
        print("   1. Run factory reset script again: ./scripts/factory_reset.sh")
        print("   2. Reboot the system: sudo reboot")
        print("   3. Check for any remaining processes: ps aux | grep aicamera")
        print("   4. Manually remove any remaining files")
        print()
        return False
    else:
        print("✅ No issues found - system is ready for reinstallation")
        print()
        print("🚀 You can now run: ./install.sh")
        print()
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
