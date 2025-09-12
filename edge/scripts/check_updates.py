#!/usr/bin/env python3
"""
AI Camera Update Checker

This script checks for available updates and compares current version
with the latest version from the repository.

Author: AI Camera Team
Version: 2.0.0
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def run_command(cmd, capture_output=True, text=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, capture_output=capture_output, text=text, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def get_current_version():
    """Get current version from various sources."""
    versions = {}
    
    # Try to get version from git
    success, stdout, stderr = run_command(["git", "describe", "--tags", "--always"])
    if success:
        versions['git'] = stdout.strip()
    
    # Try to get version from package.json
    package_json = Path(__file__).parent.parent.parent / 'server' / 'package.json'
    if package_json.exists():
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)
                versions['package'] = data.get('version', 'unknown')
        except Exception:
            versions['package'] = 'unknown'
    
    # Try to get version from environment file
    env_file = Path(__file__).parent.parent / 'installation' / '.env.production'
    if env_file.exists():
        try:
            with open(env_file, 'r') as f:
                for line in f:
                    if line.startswith('DEVICE_VERSION='):
                        versions['env'] = line.split('=')[1].strip().strip('"')
                        break
        except Exception:
            pass
    
    return versions

def check_git_updates():
    """Check for updates from git repository."""
    print("🔍 Checking for git updates...")
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        print("   ⚠️  Not in a git repository")
        return False, "Not in git repository"
    
    # Fetch latest changes
    success, stdout, stderr = run_command(["git", "fetch", "origin"])
    if not success:
        print(f"   ❌ Failed to fetch updates: {stderr}")
        return False, f"Git fetch failed: {stderr}"
    
    # Check current branch
    success, stdout, stderr = run_command(["git", "branch", "--show-current"])
    if not success:
        print(f"   ❌ Failed to get current branch: {stderr}")
        return False, f"Git branch check failed: {stderr}"
    
    current_branch = stdout.strip()
    print(f"   📋 Current branch: {current_branch}")
    
    # Check for updates
    success, stdout, stderr = run_command(["git", "rev-list", "--count", f"HEAD..origin/{current_branch}"])
    if not success:
        # Try alternative method
        success, stdout, stderr = run_command(["git", "log", "--oneline", f"HEAD..origin/{current_branch}"])
        if not success:
            print(f"   ⚠️  Could not check for updates: {stderr}")
            return False, f"Git update check failed: {stderr}"
        commits_behind = len([line for line in stdout.split('\n') if line.strip()])
    else:
        commits_behind = int(stdout.strip())
    
    if commits_behind > 0:
        print(f"   🔄 {commits_behind} commits behind origin/{current_branch}")
        return True, f"{commits_behind} commits behind"
    else:
        print("   ✅ Up to date with origin")
        return False, "Up to date"

def check_system_packages():
    """Check for system package updates."""
    print("🔍 Checking for system package updates...")
    
    # Update package lists
    success, stdout, stderr = run_command(["sudo", "apt-get", "update"], capture_output=True)
    if not success:
        print(f"   ⚠️  Failed to update package lists: {stderr}")
        return False, "Package list update failed"
    
    # Check for upgradable packages
    success, stdout, stderr = run_command(["apt", "list", "--upgradable"])
    if not success:
        print(f"   ⚠️  Failed to check upgradable packages: {stderr}")
        return False, "Package check failed"
    
    # Count upgradable packages
    upgradable_lines = [line for line in stdout.split('\n') if 'upgradable' in line]
    upgradable_count = len(upgradable_lines)
    
    if upgradable_count > 0:
        print(f"   🔄 {upgradable_count} packages can be upgraded")
        return True, f"{upgradable_count} packages upgradable"
    else:
        print("   ✅ All system packages are up to date")
        return False, "All packages up to date"

def check_python_packages():
    """Check for Python package updates."""
    print("🔍 Checking for Python package updates...")
    
    venv_path = Path("edge/installation/venv_hailo")
    if not venv_path.exists():
        print("   ⚠️  Virtual environment not found")
        return False, "Virtual environment not found"
    
    # Activate virtual environment and check for updates
    pip_cmd = str(venv_path / "bin" / "pip")
    
    # Check for outdated packages
    success, stdout, stderr = run_command([pip_cmd, "list", "--outdated"])
    if not success:
        print(f"   ⚠️  Failed to check outdated packages: {stderr}")
        return False, "Python package check failed"
    
    # Count outdated packages
    outdated_lines = [line for line in stdout.split('\n') if line.strip() and not line.startswith('Package')]
    outdated_count = len(outdated_lines)
    
    if outdated_count > 0:
        print(f"   🔄 {outdated_count} Python packages can be upgraded")
        return True, f"{outdated_count} Python packages outdated"
    else:
        print("   ✅ All Python packages are up to date")
        return False, "All Python packages up to date"

def check_service_status():
    """Check service status."""
    print("🔍 Checking service status...")
    
    services = [
        "aicamera_lpr.service",
        "nginx"
    ]
    
    all_running = True
    for service in services:
        success, stdout, stderr = run_command(["systemctl", "is-active", service])
        if success and stdout.strip() == "active":
            print(f"   ✅ {service} is running")
        else:
            print(f"   ❌ {service} is not running")
            all_running = False
    
    return all_running, "All services running" if all_running else "Some services not running"

def main():
    """Main function to check for updates."""
    print("🚀 AI Camera Update Checker")
    print("=" * 40)
    print(f"📅 Check time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Get current version information
    versions = get_current_version()
    print("📋 Current Version Information:")
    for source, version in versions.items():
        print(f"   - {source}: {version}")
    print()
    
    # Check for updates
    updates_available = False
    update_summary = []
    
    # Check git updates
    git_updates, git_message = check_git_updates()
    if git_updates:
        updates_available = True
        update_summary.append(f"Git: {git_message}")
    print()
    
    # Check system packages
    system_updates, system_message = check_system_packages()
    if system_updates:
        updates_available = True
        update_summary.append(f"System: {system_message}")
    print()
    
    # Check Python packages
    python_updates, python_message = check_python_packages()
    if python_updates:
        updates_available = True
        update_summary.append(f"Python: {python_message}")
    print()
    
    # Check service status
    services_ok, service_message = check_service_status()
    print()
    
    # Summary
    print("=" * 40)
    print("📋 UPDATE CHECK SUMMARY")
    print("=" * 40)
    
    if updates_available:
        print("🔄 Updates Available:")
        for update in update_summary:
            print(f"   - {update}")
        print()
        print("🚀 To update your system, run:")
        print("   ./edge/scripts/update_system.sh")
        print()
        print("📋 Update options:")
        print("   - Standard update: ./edge/scripts/update_system.sh")
        print("   - Fast update (no backup): ./edge/scripts/update_system.sh --no-backup")
        print("   - Maintenance mode: ./edge/scripts/update_system.sh --skip-services")
    else:
        print("✅ No updates available - system is up to date")
    
    if not services_ok:
        print()
        print("⚠️  Service Issues Detected:")
        print(f"   - {service_message}")
        print()
        print("🔧 To fix service issues:")
        print("   sudo systemctl restart aicamera_lpr.service")
        print("   sudo systemctl status aicamera_lpr.service")
    
    print()
    print("📚 For more information:")
    print("   - Update script: ./edge/scripts/update_system.sh --help")
    print("   - Factory reset: ./edge/scripts/factory_reset.sh")
    print("   - Service logs: sudo journalctl -u aicamera_lpr.service -f")
    
    return 0 if not updates_available else 1

if __name__ == "__main__":
    sys.exit(main())
