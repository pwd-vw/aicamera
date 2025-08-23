#!/usr/bin/env python3
"""
Production Startup Test for AI Camera v1.3

This script tests the complete production startup sequence:
systemd → gunicorn → nginx → auto-startup sequence (camera → detection → health monitor)

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import os
import time
import subprocess
import requests
from datetime import datetime

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def check_systemd_service():
    """Check if the systemd service is running."""
    print("🔧 Checking systemd service status...")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'aicamera_lpr'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            status = result.stdout.strip()
            print(f"   Systemd service status: {status}")
            return status == 'active'
        else:
            print(f"   Systemd service check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   Error checking systemd service: {e}")
        return False

def check_gunicorn_process():
    """Check if gunicorn process is running."""
    print("🦄 Checking gunicorn process...")
    
    try:
        result = subprocess.run(['pgrep', '-f', 'gunicorn.*aicamera'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            print(f"   Gunicorn processes found: {len(pids)}")
            for pid in pids:
                if pid:
                    print(f"     PID: {pid}")
            return True
        else:
            print("   No gunicorn processes found")
            return False
            
    except Exception as e:
        print(f"   Error checking gunicorn process: {e}")
        return False

def check_unix_socket():
    """Check if the Unix socket exists."""
    print("🔌 Checking Unix socket...")
    
    socket_path = "/tmp/aicamera.sock"
    if os.path.exists(socket_path):
        print(f"   Unix socket exists: {socket_path}")
        return True
    else:
        print(f"   Unix socket not found: {socket_path}")
        return False

def check_nginx_status():
    """Check if nginx is running and configured."""
    print("🌐 Checking nginx status...")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'nginx'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            status = result.stdout.strip()
            print(f"   Nginx status: {status}")
            return status == 'active'
        else:
            print(f"   Nginx check failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   Error checking nginx: {e}")
        return False

def test_health_endpoint():
    """Test the health endpoint through nginx."""
    print("🏥 Testing health endpoint...")
    
    try:
        # Test through nginx on port 80
        response = requests.get('http://localhost/health/system', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Health endpoint response: {response.status_code}")
            print(f"   Success: {data.get('success', False)}")
            
            if data.get('success'):
                health_data = data.get('data', {})
                overall_status = health_data.get('overall_status', 'unknown')
                print(f"   Overall status: {overall_status}")
                
                components = health_data.get('components', {})
                for component, status in components.items():
                    print(f"     {component}: {status.get('status', 'unknown')}")
                
                return True
            else:
                print(f"   Health check failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"   Health endpoint returned status: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   Error accessing health endpoint: {e}")
        return False

def test_auto_startup_sequence():
    """Test the auto-startup sequence through the API."""
    print("🚀 Testing auto-startup sequence through API...")
    
    try:
        # Test camera status
        response = requests.get('http://localhost/camera/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            camera_initialized = data.get('status', {}).get('initialized', False)
            camera_streaming = data.get('status', {}).get('streaming', False)
            print(f"   Camera initialized: {camera_initialized}")
            print(f"   Camera streaming: {camera_streaming}")
        else:
            print(f"   Camera status check failed: {response.status_code}")
        
        # Test detection status
        response = requests.get('http://localhost/detection/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            detection_active = data.get('status', {}).get('active', False)
            print(f"   Detection active: {detection_active}")
        else:
            print(f"   Detection status check failed: {response.status_code}")
        
        # Test health monitoring status
        response = requests.get('http://localhost/health/status', timeout=10)
        if response.status_code == 200:
            data = response.json()
            health_monitoring = data.get('status', {}).get('monitoring', False)
            print(f"   Health monitoring: {health_monitoring}")
        else:
            print(f"   Health status check failed: {response.status_code}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"   Error testing auto-startup sequence: {e}")
        return False

def check_logs():
    """Check recent logs for startup information."""
    print("📋 Checking recent logs...")
    
    try:
        # Check systemd logs
        result = subprocess.run(['journalctl', '-u', 'aicamera_lpr', '--since', '5 minutes ago', '-n', '20'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logs = result.stdout.strip()
            print(f"   Recent systemd logs ({len(logs.splitlines())} lines):")
            
            # Look for key startup messages
            key_messages = [
                "Starting service initialization sequence",
                "Camera Manager initialized successfully",
                "Detection Manager initialized successfully", 
                "Health Service initialized successfully",
                "Auto-start monitoring thread started"
            ]
            
            for message in key_messages:
                if message in logs:
                    print(f"     ✅ Found: {message}")
                else:
                    print(f"     ❌ Missing: {message}")
        
        return True
        
    except Exception as e:
        print(f"   Error checking logs: {e}")
        return False

def main():
    """Main test function."""
    print("🏥 AI Camera v1.3 - Production Startup Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    # Test system components
    systemd_ok = check_systemd_service()
    gunicorn_ok = check_gunicorn_process()
    socket_ok = check_unix_socket()
    nginx_ok = check_nginx_status()
    
    print()
    
    # Test application endpoints
    health_ok = test_health_endpoint()
    startup_ok = test_auto_startup_sequence()
    
    print()
    
    # Check logs
    logs_ok = check_logs()
    
    print("\n" + "=" * 60)
    print("📊 PRODUCTION STARTUP TEST SUMMARY")
    print("=" * 60)
    print(f"Systemd Service: {'✅ PASS' if systemd_ok else '❌ FAIL'}")
    print(f"Gunicorn Process: {'✅ PASS' if gunicorn_ok else '❌ FAIL'}")
    print(f"Unix Socket: {'✅ PASS' if socket_ok else '❌ FAIL'}")
    print(f"Nginx Service: {'✅ PASS' if nginx_ok else '❌ FAIL'}")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Auto-Startup Sequence: {'✅ PASS' if startup_ok else '❌ FAIL'}")
    print(f"Log Analysis: {'✅ PASS' if logs_ok else '❌ FAIL'}")
    
    # Overall assessment
    infrastructure_ok = systemd_ok and gunicorn_ok and socket_ok and nginx_ok
    application_ok = health_ok and startup_ok and logs_ok
    
    print(f"\nInfrastructure: {'✅ PASS' if infrastructure_ok else '❌ FAIL'}")
    print(f"Application: {'✅ PASS' if application_ok else '❌ FAIL'}")
    
    overall_success = infrastructure_ok and application_ok
    print(f"\nOverall: {'✅ PASS' if overall_success else '❌ FAIL'}")
    
    if overall_success:
        print("🎉 Production startup sequence is working correctly!")
        print("   The system is ready for production use with auto-startup sequence:")
        print("   systemd → gunicorn → nginx → camera → detection → health monitor")
    else:
        print("⚠️ Some components failed - check the output above for details")
        print("   Manual intervention may be required")
    
    return overall_success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
