#!/usr/bin/env python3
"""
EasyOCR Validation Script for AI Camera v1.3

This script validates that EasyOCR is properly installed and working
with the correct dependencies, especially typing_extensions.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from v1_3.src.core.config import EASYOCR_LANGUAGES
    from v1_3.src.core.utils.logging_config import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def validate_typing_extensions():
    """Validate that typing_extensions is properly installed with deprecated function."""
    print("🔍 Validating typing_extensions...")
    
    try:
        import typing_extensions
        print(f"✅ typing_extensions imported successfully")
        print(f"📋 typing_extensions path: {typing_extensions.__file__}")
        
        # Check if deprecated function is available
        try:
            from typing_extensions import deprecated
            print("✅ deprecated function available in typing_extensions")
            return True
        except ImportError as e:
            print(f"❌ deprecated function not available: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ typing_extensions import failed: {e}")
        return False


def validate_easyocr_import():
    """Validate that EasyOCR can be imported."""
    print("🔍 Validating EasyOCR import...")
    
    try:
        import easyocr
        print(f"✅ EasyOCR imported successfully")
        print(f"📋 EasyOCR version: {easyocr.__version__ if hasattr(easyocr, '__version__') else 'unknown'}")
        print(f"📋 EasyOCR path: {easyocr.__file__}")
        return True
        
    except ImportError as e:
        print(f"❌ EasyOCR import failed: {e}")
        return False


def validate_easyocr_initialization():
    """Validate that EasyOCR can be initialized with supported languages."""
    print("🔍 Validating EasyOCR initialization...")
    
    try:
        import easyocr
        
        # Test initialization with supported languages
        print(f"📋 Initializing EasyOCR with languages: {EASYOCR_LANGUAGES}")
        reader = easyocr.Reader(EASYOCR_LANGUAGES)
        print("✅ EasyOCR Reader initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ EasyOCR initialization failed: {e}")
        return False


def validate_easyocr_ocr():
    """Validate that EasyOCR can perform OCR on a simple test."""
    print("🔍 Validating EasyOCR OCR functionality...")
    
    try:
        import easyocr
        import numpy as np
        
        # Create a simple test image (white background with black text)
        test_image = np.ones((100, 300, 3), dtype=np.uint8) * 255
        
        # Add some text-like patterns (simple rectangles)
        test_image[40:60, 50:250] = 0  # Black rectangle
        
        reader = easyocr.Reader(['en'])
        
        # Try to read the test image
        results = reader.readtext(test_image)
        print(f"✅ EasyOCR OCR test completed (found {len(results)} text regions)")
        return True
        
    except Exception as e:
        print(f"❌ EasyOCR OCR test failed: {e}")
        return False


def validate_health_monitor_easyocr():
    """Validate that health monitor can check EasyOCR."""
    print("🔍 Validating health monitor EasyOCR check...")
    
    try:
        from v1_3.src.components.health_monitor import HealthMonitor
        
        health_monitor = HealthMonitor()
        
        # Test EasyOCR initialization check
        easyocr_ok = health_monitor.check_easyocr_init()
        if not easyocr_ok:
            print("❌ Health monitor EasyOCR check failed")
            return False
        
        print("✅ Health monitor EasyOCR validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Health monitor EasyOCR validation failed: {e}")
        return False


def validate_detection_processor_easyocr():
    """Validate that detection processor can use EasyOCR."""
    print("🔍 Validating detection processor EasyOCR integration...")
    
    try:
        from v1_3.src.components.detection_processor import DetectionProcessor
        
        processor = DetectionProcessor()
        
        # Test model loading (which includes EasyOCR)
        models_loaded = processor.load_models()
        if not models_loaded:
            print("❌ Detection processor model loading failed")
            return False
        
        # Check if EasyOCR reader is available
        if not processor.ocr_reader:
            print("❌ EasyOCR reader not available in detection processor")
            return False
        
        print("✅ Detection processor EasyOCR validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Detection processor EasyOCR validation failed: {e}")
        return False


def check_python_environment():
    """Check Python environment details."""
    print("🔍 Checking Python environment...")
    
    import sys
    print(f"📋 Python executable: {sys.executable}")
    print(f"📋 Python version: {sys.version}")
    print(f"📋 Python path: {sys.path[:3]}...")  # Show first 3 paths
    
    # Check if we're in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Running in virtual environment")
    else:
        print("⚠️  Not running in virtual environment")


def main():
    """Main validation function."""
    print("🚀 Starting EasyOCR Validation for AI Camera v1.3...")
    print(f"📋 Supported languages: {EASYOCR_LANGUAGES}")
    
    # Check Python environment first
    check_python_environment()
    print()
    
    all_passed = True
    
    # Run all validations
    if not validate_typing_extensions():
        all_passed = False
    
    if not validate_easyocr_import():
        all_passed = False
    
    if not validate_easyocr_initialization():
        all_passed = False
    
    if not validate_easyocr_ocr():
        all_passed = False
    
    if not validate_health_monitor_easyocr():
        all_passed = False
    
    if not validate_detection_processor_easyocr():
        all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("✅ All EasyOCR validations passed!")
        print("🎉 EasyOCR is ready for production use")
        return 0
    else:
        print("❌ Some EasyOCR validations failed")
        print("🔧 Please check the following:")
        print("   1. Ensure typing-extensions>=4.0.0 is installed")
        print("   2. Ensure EasyOCR>=1.7.0 is installed")
        print("   3. Check Python environment and virtual environment")
        print("   4. Run: pip install --upgrade typing-extensions easyocr")
        return 1


if __name__ == "__main__":
    sys.exit(main())
