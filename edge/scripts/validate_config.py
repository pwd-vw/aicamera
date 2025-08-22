#!/usr/bin/env python3
"""
Configuration Validation Script for AI Camera v1.3

This script validates the environment configuration and system compatibility.
It checks:
- Environment variables are properly set
- Hailo device compatibility
- Model availability
- System requirements

Author: AI Camera Team
Version: 1.3
"""

import os
import sys
import subprocess
from pathlib import Path

def check_hailo_device():
    """Check Hailo device and determine architecture."""
    try:
        result = subprocess.run(['hailortcli', 'fw-control', 'identify'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            output = result.stdout
            if 'HAILO8L' in output:
                return 'HAILO8L'
            elif 'HAILO8' in output:
                return 'HAILO8'
            else:
                return 'UNKNOWN'
        else:
            return None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None

def validate_models(device_arch):
    """Validate that appropriate models are configured for the device."""
    print(f"🔍 Validating models for {device_arch} device...")
    
    # Get model configurations from environment
    vehicle_model = os.getenv('VEHICLE_DETECTION_MODEL', '')
    lp_model = os.getenv('LICENSE_PLATE_DETECTION_MODEL', '')
    ocr_model = os.getenv('LICENSE_PLATE_OCR_MODEL', '')
    
    print(f"   Vehicle Model: {vehicle_model}")
    print(f"   License Plate Model: {lp_model}")
    print(f"   OCR Model: {ocr_model}")
    
    # Check if models are appropriate for device architecture
    if device_arch == 'HAILO8L':
        if 'hailo8l' not in vehicle_model.lower():
            print("⚠️  Warning: Vehicle model may not be optimized for HAILO8L")
        if 'hailo8l' not in lp_model.lower():
            print("⚠️  Warning: License plate model may not be optimized for HAILO8L")
        if 'hailo8l' not in ocr_model.lower():
            print("⚠️  Warning: OCR model may not be optimized for HAILO8L")
    elif device_arch == 'HAILO8':
        if 'hailo8l' in vehicle_model.lower():
            print("⚠️  Warning: Vehicle model is for HAILO8L but device is HAILO8")
        if 'hailo8l' in lp_model.lower():
            print("⚠️  Warning: License plate model is for HAILO8L but device is HAILO8")
        if 'hailo8l' in ocr_model.lower():
            print("⚠️  Warning: OCR model is for HAILO8L but device is HAILO8")
    
    # Check if model files exist
    # Use absolute path strategy like the rest of the project
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # Go up from scripts/edge/aicamera
    resources_dir = project_root / 'resources'
    if resources_dir.exists():
        for model_name in [vehicle_model, lp_model, ocr_model]:
            if model_name:
                model_dir = resources_dir / model_name
                if model_dir.exists():
                    hef_file = list(model_dir.glob('*.hef'))
                    if hef_file:
                        print(f"   ✅ {model_name}: Found {hef_file[0].name}")
                    else:
                        print(f"   ❌ {model_name}: No .hef file found")
                else:
                    print(f"   ❌ {model_name}: Directory not found")
    else:
        print("   ❌ Resources directory not found")

def validate_environment():
    """Validate environment variables."""
    print("🔍 Validating environment configuration...")
    
    required_vars = [
        'AICAMERA_ID',
        'CHECKPOINT_ID',
        'LOCATION_LAT',
        'LOCATION_LON',
        'VEHICLE_DETECTION_MODEL',
        'LICENSE_PLATE_DETECTION_MODEL',
        'LICENSE_PLATE_OCR_MODEL'
    ]
    
    optional_vars = [
        'CAMERA_LOCATION',
        'WEBSOCKET_SERVER_URL',
        'CAMERA_RESOLUTION',
        'CAMERA_FPS',
        'DETECTION_CONFIDENCE_THRESHOLD',
        'PLATE_CONFIDENCE_THRESHOLD'
    ]
    
    print("Required variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
    
    print("\nOptional variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚪ {var}: Not set (using default)")

def validate_system():
    """Validate system requirements."""
    print("🔍 Validating system requirements...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 10):
        print(f"   ✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"   ❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} - requires 3.10+")
    
    # Check if running on ARM64
    import platform
    if platform.machine() == 'aarch64':
        print("   ✅ Architecture: ARM64 (Raspberry Pi compatible)")
    else:
        print(f"   ⚠️  Architecture: {platform.machine()} (not ARM64)")
    
    # Check available memory
    try:
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                if line.startswith('MemTotal:'):
                    mem_kb = int(line.split()[1])
                    mem_gb = mem_kb / 1024 / 1024
                    if mem_gb >= 4:
                        print(f"   ✅ Memory: {mem_gb:.1f} GB")
                    else:
                        print(f"   ⚠️  Memory: {mem_gb:.1f} GB (recommended: 4GB+)")
                    break
    except:
        print("   ⚠️  Could not check memory")
    
    # Check available disk space
    try:
        statvfs = os.statvfs('.')
        free_gb = (statvfs.f_bavail * statvfs.f_frsize) / (1024**3)
        if free_gb >= 10:
            print(f"   ✅ Disk space: {free_gb:.1f} GB free")
        else:
            print(f"   ⚠️  Disk space: {free_gb:.1f} GB free (recommended: 10GB+)")
    except:
        print("   ⚠️  Could not check disk space")

def main():
    """Main validation function."""
    print("🚀 AI Camera v1.3 Configuration Validation")
    print("=" * 50)
    
    # Load environment variables
    # Use absolute path strategy like the rest of the project
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent  # Go up from scripts/edge/aicamera
    env_file = project_root / 'edge' / 'installation' / '.env.production'
    if env_file.exists():
        print("📄 Loading environment from .env.production file...")
        from dotenv import load_dotenv
        load_dotenv(env_file)
    else:
        print(f"⚠️  No .env.production file found at {env_file} - using system environment variables")
    
    print()
    
    # Validate system
    validate_system()
    print()
    
    # Check Hailo device
    device_arch = check_hailo_device()
    if device_arch:
        print(f"✅ Hailo device detected: {device_arch}")
    else:
        print("❌ No Hailo device detected")
    print()
    
    # Validate environment
    validate_environment()
    print()
    
    # Validate models
    if device_arch:
        validate_models(device_arch)
    else:
        print("⚠️  Skipping model validation - no Hailo device detected")
    print()
    
    print("=" * 50)
    print("✅ Configuration validation completed!")
    print("\n📝 Next steps:")
    print("   1. Review any warnings or errors above")
    print(f"   2. Edit {env_file} file if needed")
    print("   3. Run ./install.sh to complete installation")
    print("   4. Start the service with: sudo systemctl start aicamera_v1.3.service")

if __name__ == "__main__":
    main()
