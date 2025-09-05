#!/usr/bin/env python3
"""
Libcamera Validation Script for AI Camera v2.0

This script validates that libcamera is properly installed and accessible
in the virtual environment for camera control and configuration.

Author: AI Camera Team
Version: 2.0
Date: September 2025
"""

import sys
import os
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


def check_installation_methods():
    """Check different installation methods for libcamera."""
    print("🔍 Checking libcamera installation methods...")
    
    # Check apt packages
    try:
        import subprocess
        
        packages = ['python3-libcamera', 'libcamera-tools']
        for package in packages:
            result = subprocess.run(['dpkg', '-l', package], capture_output=True, text=True)
            if result.returncode == 0 and 'ii' in result.stdout:
                print(f"✅ {package} installed via apt")
            else:
                print(f"❌ {package} not installed via apt")
                
    except Exception as e:
        print(f"⚠️  Could not check apt packages: {e}")


def main():
    """Main validation function."""
    print("🚀 Starting Libcamera Validation for AI Camera v1.3...")
    print("="*60)
    
    all_passed = True
    
    # Run all checks
    if not check_system_libcamera():
        all_passed = False
    
    if not check_virtual_env_libcamera():
        all_passed = False
    
    if not check_picamera2_libcamera():
        all_passed = False
    
    if not check_camera_hardware():
        all_passed = False
    
    if not check_camera_controls():
        all_passed = False
    
    check_installation_methods()
    
    # Summary
    print("\n" + "="*60)
    if all_passed:
        print("✅ All libcamera validations passed!")
        print("🎉 Libcamera is properly installed and ready for camera control")
        return 0
    else:
        print("❌ Some libcamera validations failed")
        print("🔧 Please check the following:")
        print("   1. Install libcamera: sudo apt-get install python3-libcamera")
        print("   2. Ensure virtual environment has system site-packages access")
        print("   3. Check camera hardware connections")
        print("   4. Verify camera device permissions")
        print("   5. Run: python edge/scripts/validate_libcamera.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
