#!/usr/bin/env python3
"""
Fix numpy and Pillow compatibility issues for picamera2 and degirum

This script fixes the numpy binary compatibility issue that prevents picamera2 from working
and ensures Pillow version compatibility with degirum.
The error "numpy.dtype size changed, may indicate binary incompatibility" occurs when
numpy versions are mismatched between system and virtual environment.

Compatible versions:
- numpy==1.26.4 (compatible with both picamera2 and degirum)
- Pillow==10.4.0 (compatible with degirum requirements: <11.0,>=9.2)

Author: AI Camera Team
Version: 2.0
Date: September 2025
"""

import sys
import subprocess
import os

def fix_numpy_compatibility():
    """Fix numpy compatibility issues."""
    print("🔧 Fixing numpy compatibility for picamera2...")
    
    try:
        # Check if we're in a virtual environment
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            print(f"📋 Using virtual environment: {venv_path}")
            pip_cmd = f"{venv_path}/bin/python -m pip"
        else:
            print("📋 Using system Python (may need --break-system-packages)")
            pip_cmd = f"{sys.executable} -m pip"
        
        # Check current numpy version
        import numpy
        current_version = numpy.__version__
        print(f"📋 Current numpy version: {current_version}")
        
        # Force reinstall numpy with compatible version
        print("📦 Reinstalling numpy 1.26.4 for compatibility...")
        cmd = pip_cmd.split() + ["install", "--force-reinstall", "--no-cache-dir", "--no-deps", "numpy==1.26.4"]
        if not venv_path:
            cmd.append("--break-system-packages")
        subprocess.run(cmd, check=True)
        
        # Reinstall simplejpeg to ensure compatibility
        print("📦 Reinstalling simplejpeg for numpy compatibility...")
        cmd = pip_cmd.split() + ["install", "--force-reinstall", "--no-cache-dir", "simplejpeg"]
        if not venv_path:
            cmd.append("--break-system-packages")
        subprocess.run(cmd, check=True)
        
        # Reinstall Pillow for degirum compatibility
        print("📦 Reinstalling Pillow 10.4.0 for degirum compatibility...")
        cmd = pip_cmd.split() + ["install", "--force-reinstall", "--no-cache-dir", "Pillow==10.4.0"]
        if not venv_path:
            cmd.append("--break-system-packages")
        subprocess.run(cmd, check=True)
        
        print("✅ Numpy compatibility fix completed")
        
        # Test picamera2 import
        print("🔍 Testing picamera2 import...")
        try:
            from picamera2 import Picamera2
            print("✅ picamera2 import successful!")
        except Exception as e:
            print(f"❌ picamera2 import still failing: {e}")
            return False
        
        # Test degirum import
        print("🔍 Testing degirum import...")
        try:
            import degirum
            print("✅ degirum import successful!")
            return True
        except Exception as e:
            print(f"❌ degirum import still failing: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing numpy compatibility: {e}")
        return False

def main():
    """Main function."""
    print("🚀 Numpy & Pillow Compatibility Fix for AI Camera v2.0")
    print("=" * 60)
    
    if fix_numpy_compatibility():
        print("\n🎉 Numpy & Pillow compatibility fix successful!")
        print("📋 picamera2 and degirum should now work correctly")
    else:
        print("\n❌ Numpy & Pillow compatibility fix failed")
        print("📋 You may need to manually reinstall numpy, simplejpeg, and Pillow")
        sys.exit(1)

if __name__ == "__main__":
    main()
