#!/usr/bin/env python3
"""
Libcamera Validation Script for AI Camera v2.0

This script validates that libcamera and rpicam are properly installed and accessible
in the virtual environment for camera control and configuration.

Author: AI Camera Team
Version: 2.0
Date: September 2025
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from edge.src.core.utils.logging_config import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def check_system_libcamera():
    """Check if libcamera is available in system Python."""
    print("🔍 Checking system libcamera...")
    
    try:
        import libcamera
        print(f"✅ libcamera imported successfully")
        print(f"📋 libcamera path: {libcamera.__file__}")
        
        # Check for controls module
        try:
            from libcamera import controls
            print("✅ libcamera.controls available")
            
            # Check for common control enums
            if hasattr(controls, 'AwbModeEnum'):
                print("✅ libcamera.controls.AwbModeEnum available")
            if hasattr(controls, 'AeEnableEnum'):
                print("✅ libcamera.controls.AeEnableEnum available")
            if hasattr(controls, 'AfModeEnum'):
                print("✅ libcamera.controls.AfModeEnum available")
                
            return True
        except ImportError as e:
            print(f"❌ libcamera.controls not available: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ libcamera import failed: {e}")
        return False


def check_virtual_env_libcamera():
    """Check if libcamera is accessible in virtual environment."""
    print("🔍 Checking virtual environment libcamera...")
    
    try:
        import libcamera
        print(f"✅ libcamera accessible in virtual environment")
        print(f"📋 libcamera path: {libcamera.__file__}")
        
        # Check if it's the same as system libcamera
        system_libcamera_path = None
        try:
            import subprocess
            result = subprocess.run([
                '/usr/bin/python3', '-c', 
                'import libcamera; print(libcamera.__file__)'
            ], capture_output=True, text=True)
            if result.returncode == 0:
                system_libcamera_path = result.stdout.strip()
                print(f"📋 System libcamera path: {system_libcamera_path}")
                
                if libcamera.__file__ == system_libcamera_path:
                    print("✅ Virtual environment using system libcamera")
                else:
                    print("⚠️  Virtual environment using different libcamera")
        except Exception as e:
            print(f"⚠️  Could not check system libcamera path: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ libcamera not accessible in virtual environment: {e}")
        return False


def check_picamera2_libcamera():
    """Check if picamera2 can access libcamera."""
    print("🔍 Checking picamera2 libcamera integration...")
    
    try:
        from picamera2 import Picamera2
        print("✅ picamera2 imported successfully")
        
        # Check if picamera2 can create instance (this requires libcamera)
        try:
            picam2 = Picamera2()
            print("✅ picamera2 instance created successfully")
            
            # Check camera properties (this requires libcamera)
            try:
                properties = picam2.camera_properties
                print(f"✅ Camera properties available: {len(properties)} properties")
                return True
            except Exception as e:
                print(f"⚠️  Camera properties not available: {e}")
                return False
                
        except Exception as e:
            print(f"❌ picamera2 instance creation failed: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ picamera2 import failed: {e}")
        return False


def check_camera_hardware():
    """Check if camera hardware is available."""
    print("🔍 Checking camera hardware...")
    
    # Check for camera devices
    camera_devices = ['/dev/video0', '/dev/video1', '/dev/video2']
    found_devices = []
    
    for device in camera_devices:
        if os.path.exists(device):
            found_devices.append(device)
    
    if found_devices:
        print(f"✅ Camera devices found: {found_devices}")
        
        # Check device permissions
        for device in found_devices:
            if os.access(device, os.R_OK | os.W_OK):
                print(f"✅ {device} is accessible")
            else:
                print(f"⚠️  {device} is not accessible (permission issue)")
        
        return True
    else:
        print("❌ No camera devices found")
        
        # Check for CSI camera interface
        if os.path.exists('/sys/class/video4linux'):
            print("✅ Video4Linux interface available")
            return True
        else:
            print("❌ No camera hardware detected")
            return False


def check_camera_controls():
    """Check if camera controls are working."""
    print("🔍 Checking camera controls...")
    
    try:
        from libcamera import controls
        
        # Define critical vs non-critical controls
        critical_controls = [
            'AwbModeEnum', 'AfModeEnum', 'AeEnableEnum', 'AeMeteringModeEnum',
            'AeExposureModeEnum', 'AeConstraintModeEnum', 'AeFlickerModeEnum',
            'AfRangeEnum', 'AfSpeedEnum', 'AfMeteringEnum', 'AfTriggerEnum',
            'AfPauseEnum'
        ]
        
        non_critical_controls = [
            'AwbEnableEnum', 'ColourGainsEnum', 'ColourTemperatureEnum',
            'ScalerCrop', 'SensorExposureTime', 'AnalogueGain', 'DigitalGain',
            'FrameDurationLimits', 'SensorBlackLevels', 'SensorTestPatternModeEnum'
        ]
        
        print("📋 Checking critical camera controls:")
        critical_available = []
        for control_name in critical_controls:
            if hasattr(controls, control_name):
                
                print(f"  ✅ {control_name} available")
                critical_available.append(control_name)
            else:
                print(f"  ❌ {control_name} not available")
        
        print(f"📊 Critical controls available: {len(critical_available)}/{len(critical_controls)}")
        
        print("\n📋 Checking non-critical camera controls (optional):")
        non_critical_available = []
        for control_name in non_critical_controls:
            if hasattr(controls, control_name):
                print(f"  ✅ {control_name} available")
                non_critical_available.append(control_name)
            else:
                print(f"  ⚪ {control_name} not available (non-critical)")
        
        print(f"📊 Non-critical controls available: {len(non_critical_available)}/{len(non_critical_controls)}")
        
        # Determine if validation passes based on critical controls
        critical_threshold = 3  # Need at least 3 critical controls
        if len(critical_available) >= critical_threshold:
            print(f"✅ Camera controls validation PASSED ({len(critical_available)} critical controls available)")
            return True
        else:
            print(f"❌ Camera controls validation FAILED (only {len(critical_available)} critical controls available, need {critical_threshold})")
            return False
        
    except Exception as e:
        print(f"❌ Camera controls test failed: {e}")
        return False


def check_system_architecture():
    """Check system architecture and Raspberry Pi compatibility."""
    print("🔍 Checking system architecture...")
    
    # Get system information
    arch = platform.machine()
    system = platform.system()
    release = platform.release()
    
    print(f"📋 System: {system} {release}")
    print(f"📋 Architecture: {arch}")
    
    # Check if this is a Raspberry Pi
    is_raspberry_pi = False
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'BCM' in cpuinfo or 'Raspberry Pi' in cpuinfo:
                is_raspberry_pi = True
                print("✅ Raspberry Pi detected")
            else:
                print("⚠️  Not a Raspberry Pi - some camera features may be limited")
    except Exception as e:
        print(f"⚠️  Could not detect Raspberry Pi: {e}")
    
    # Check for Raspberry Pi specific files
    rpi_files = [
        '/boot/config.txt',
        '/boot/cmdline.txt',
        '/proc/device-tree/model'
    ]
    
    rpi_files_found = 0
    for file_path in rpi_files:
        if os.path.exists(file_path):
            rpi_files_found += 1
    
    if rpi_files_found >= 2:
        print("✅ Raspberry Pi system files detected")
        is_raspberry_pi = True
    else:
        print("⚠️  Limited Raspberry Pi system files found")
    
    return is_raspberry_pi


def check_rpicam_tools():
    """Check if rpicam tools are available and working."""
    print("🔍 Checking rpicam tools...")
    
    rpicam_tools = [
        'rpicam-hello',
        'rpicam-still', 
        'rpicam-vid',
        'rpicam-raw',
        'rpicam-jpeg',
        'rpicam-detect'
    ]
    
    available_tools = []
    for tool in rpicam_tools:
        try:
            result = subprocess.run([tool, '--help'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 or 'usage:' in result.stdout.lower():
                available_tools.append(tool)
                print(f"✅ {tool} available")
            else:
                print(f"❌ {tool} not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.CalledProcessError):
            print(f"❌ {tool} not found or not working")
    
    if available_tools:
        print(f"📊 rpicam tools available: {len(available_tools)}/{len(rpicam_tools)}")
        
        # Test rpicam-hello if available
        if 'rpicam-hello' in available_tools:
            try:
                print("🔍 Testing rpicam-hello camera detection...")
                result = subprocess.run(['rpicam-hello', '--list-cameras'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    if 'Available cameras' in result.stdout:
                        print("✅ rpicam-hello can detect cameras")
                        # Extract camera count
                        lines = result.stdout.split('\n')
                        camera_count = 0
                        for line in lines:
                            if 'camera' in line.lower() and any(char.isdigit() for char in line):
                                camera_count += 1
                        if camera_count > 0:
                            print(f"📷 Detected {camera_count} camera(s)")
                        else:
                            print("⚠️  No cameras detected by rpicam-hello")
                    else:
                        print("⚠️  rpicam-hello output unclear")
                else:
                    print(f"⚠️  rpicam-hello failed: {result.stderr}")
            except Exception as e:
                print(f"⚠️  rpicam-hello test failed: {e}")
        
        return True
    else:
        print("❌ No rpicam tools available")
        return False


def check_libcamera_version():
    """Check libcamera version and compare with latest."""
    print("🔍 Checking libcamera version...")
    
    try:
        # Check system libcamera version
        result = subprocess.run(['libcamera-hello', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            version_info = result.stdout.strip()
            print(f"✅ libcamera-hello version: {version_info}")
            
            # Extract version number
            import re
            version_match = re.search(r'(\d+\.\d+\.\d+)', version_info)
            if version_match:
                version = version_match.group(1)
                print(f"📋 Detected version: {version}")
                
                # Compare with known versions
                if version >= "0.5.0":
                    print("✅ Using recent libcamera version (0.5.0+)")
                elif version >= "0.4.0":
                    print("⚠️  Using older libcamera version (0.4.x) - consider upgrading")
                else:
                    print("❌ Using very old libcamera version - upgrade recommended")
                
                return version
            else:
                print("⚠️  Could not parse version number")
                return None
        else:
            print("❌ libcamera-hello not available for version check")
            return None
    except Exception as e:
        print(f"⚠️  Version check failed: {e}")
        return None


def check_installation_methods():
    """Check different installation methods for libcamera."""
    print("🔍 Checking libcamera installation methods...")
    
    # Check apt packages
    try:
        packages = {
            'python3-libcamera': 'Python libcamera bindings',
            'libcamera-tools': 'libcamera command line tools',
            'libcamera-dev': 'libcamera development files',
            'libcamera-apps': 'libcamera applications',
            'rpicam-apps': 'Raspberry Pi camera applications'
        }
        
        installed_packages = []
        for package, description in packages.items():
            result = subprocess.run(['dpkg', '-l', package], capture_output=True, text=True)
            if result.returncode == 0 and 'ii' in result.stdout:
                print(f"✅ {package} installed ({description})")
                installed_packages.append(package)
            else:
                print(f"❌ {package} not installed ({description})")
        
        print(f"📊 Installed packages: {len(installed_packages)}/{len(packages)}")
        
        # Check repository sources
        print("🔍 Checking package repository sources...")
        try:
            result = subprocess.run(['grep', '-r', 'raspberrypi.org', '/etc/apt/sources.list*'], 
                                  capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                print("✅ Raspberry Pi repository configured")
            else:
                print("⚠️  Raspberry Pi repository not configured - may have older libcamera")
        except Exception as e:
            print(f"⚠️  Could not check repository sources: {e}")
                
    except Exception as e:
        print(f"⚠️  Could not check apt packages: {e}")


def main():
    """Main validation function."""
    print("🚀 Starting Libcamera & rpicam Validation for AI Camera v2.0...")
    print("="*70)
    
    all_passed = True
    validation_results = {}
    
    # System architecture check
    print("\n📋 SYSTEM ARCHITECTURE CHECK")
    print("-" * 40)
    is_raspberry_pi = check_system_architecture()
    validation_results['system_architecture'] = is_raspberry_pi
    
    # Version check
    print("\n📋 VERSION CHECK")
    print("-" * 40)
    version = check_libcamera_version()
    validation_results['libcamera_version'] = version
    
    # Installation methods check
    print("\n📋 INSTALLATION METHODS CHECK")
    print("-" * 40)
    check_installation_methods()
    
    # System libcamera check
    print("\n📋 SYSTEM LIBCAMERA CHECK")
    print("-" * 40)
    system_libcamera_ok = check_system_libcamera()
    validation_results['system_libcamera'] = system_libcamera_ok
    if not system_libcamera_ok:
        all_passed = False
    
    # Virtual environment libcamera check
    print("\n📋 VIRTUAL ENVIRONMENT LIBCAMERA CHECK")
    print("-" * 40)
    venv_libcamera_ok = check_virtual_env_libcamera()
    validation_results['venv_libcamera'] = venv_libcamera_ok
    if not venv_libcamera_ok:
        all_passed = False
    
    # Picamera2 integration check
    print("\n📋 PICAMERA2 INTEGRATION CHECK")
    print("-" * 40)
    picamera2_ok = check_picamera2_libcamera()
    validation_results['picamera2'] = picamera2_ok
    if not picamera2_ok:
        all_passed = False
    
    # Camera hardware check
    print("\n📋 CAMERA HARDWARE CHECK")
    print("-" * 40)
    hardware_ok = check_camera_hardware()
    validation_results['camera_hardware'] = hardware_ok
    if not hardware_ok:
        all_passed = False
    
    # Camera controls check
    print("\n📋 CAMERA CONTROLS CHECK")
    print("-" * 40)
    controls_ok = check_camera_controls()
    validation_results['camera_controls'] = controls_ok
    if not controls_ok:
        all_passed = False
    
    # rpicam tools check (only on Raspberry Pi)
    if is_raspberry_pi:
        print("\n📋 RPICAM TOOLS CHECK")
        print("-" * 40)
        rpicam_ok = check_rpicam_tools()
        validation_results['rpicam_tools'] = rpicam_ok
        if not rpicam_ok:
            all_passed = False
    else:
        print("\n📋 RPICAM TOOLS CHECK")
        print("-" * 40)
        print("⚠️  Skipping rpicam tools check - not a Raspberry Pi system")
        validation_results['rpicam_tools'] = None
    
    # Summary
    print("\n" + "="*70)
    print("📊 VALIDATION SUMMARY")
    print("="*70)
    
    for check, result in validation_results.items():
        if result is True:
            print(f"✅ {check.replace('_', ' ').title()}: PASSED")
        elif result is False:
            print(f"❌ {check.replace('_', ' ').title()}: FAILED")
        elif result is None:
            print(f"⚠️  {check.replace('_', ' ').title()}: SKIPPED")
        else:
            print(f"📋 {check.replace('_', ' ').title()}: {result}")
    
    if all_passed:
        print("\n🎉 All libcamera validations passed!")
        print("✅ Libcamera and rpicam are properly installed and ready for camera control")
        if is_raspberry_pi:
            print("🚀 Raspberry Pi camera system is fully operational")
        else:
            print("⚠️  Running on non-Raspberry Pi system - some features may be limited")
        return 0
    else:
        print("\n❌ Some libcamera validations failed")
        print("🔧 Troubleshooting steps:")
        
        if not validation_results.get('system_libcamera', False):
            print("   1. Install libcamera: sudo apt-get install python3-libcamera libcamera-tools")
        
        if not validation_results.get('venv_libcamera', False):
            print("   2. Ensure virtual environment has system site-packages access")
            print("      Recreate venv: python3 -m venv --system-site-packages venv")
        
        if not validation_results.get('camera_hardware', False):
            print("   3. Check camera hardware connections")
            print("   4. Verify camera device permissions: sudo chmod 666 /dev/video*")
        
        if is_raspberry_pi and not validation_results.get('rpicam_tools', False):
            print("   5. Install rpicam tools: sudo apt-get install rpicam-apps")
            print("   6. Add Raspberry Pi repository for latest packages")
        
        print("   7. Run validation again: python edge/scripts/validate_libcamera.py")
        print("   8. Check system logs: dmesg | grep -i camera")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
