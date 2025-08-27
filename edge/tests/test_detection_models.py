#!/usr/bin/env python3
"""
Test script for Detection Models in AI Camera v1.3
Tests model loading, configuration, and basic functionality
"""

import sys
import os
from pathlib import Path

# Setup import paths first
from edge.src.core.utils.import_helper import setup_import_paths, validate_imports
setup_import_paths()

import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_config_loading():
    """Test configuration loading"""
    logger.info("=== Testing Configuration Loading ===")
    try:
        from edge.src.core.config import (
            BASE_DIR, IMAGE_SAVE_DIR, DATABASE_PATH,
            VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL, 
            LICENSE_PLATE_OCR_MODEL, HEF_MODEL_PATH, MODEL_ZOO_URL
        )
        
        logger.info(f"✅ BASE_DIR: {BASE_DIR}")
        logger.info(f"✅ IMAGE_SAVE_DIR: {IMAGE_SAVE_DIR}")
        logger.info(f"✅ DATABASE_PATH: {DATABASE_PATH}")
        logger.info(f"✅ VEHICLE_DETECTION_MODEL: {VEHICLE_DETECTION_MODEL}")
        logger.info(f"✅ LICENSE_PLATE_DETECTION_MODEL: {LICENSE_PLATE_DETECTION_MODEL}")
        logger.info(f"✅ LICENSE_PLATE_OCR_MODEL: {LICENSE_PLATE_OCR_MODEL}")
        logger.info(f"✅ HEF_MODEL_PATH: {HEF_MODEL_PATH}")
        logger.info(f"✅ MODEL_ZOO_URL: {MODEL_ZOO_URL}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Config loading failed: {e}")
        return False

def test_import_validation():
    """Test absolute imports validation"""
    logger.info("=== Testing Import Validation ===")
    try:
        errors = validate_imports()
        if errors:
            logger.warning(f"⚠️  Import errors found: {len(errors)}")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ All imports validated successfully")
        return len(errors) == 0
    except Exception as e:
        logger.error(f"❌ Import validation failed: {e}")
        return False

def test_degirum_availability():
    """Test degirum library availability"""
    logger.info("=== Testing Degirum Availability ===")
    try:
        import degirum as dg
        logger.info(f"✅ Degirum version: {dg.__version__}")
        logger.info(f"✅ Degirum path: {dg.__file__}")
        return True
    except ImportError as e:
        logger.error(f"❌ Degirum not available: {e}")
        logger.info("💡 Make sure to source setup_env.sh first")
        return False

def test_detection_processor():
    """Test DetectionProcessor initialization"""
    logger.info("=== Testing DetectionProcessor ===")
    try:
        from edge.src.components.detection_processor import DetectionProcessor
        
        # Create instance
        processor = DetectionProcessor()
        logger.info("✅ DetectionProcessor created successfully")
        
        # Get initial status
        status = processor.get_status()
        logger.info(f"✅ Initial status: {status}")
        
        # Try to load models
        logger.info("🔄 Attempting to load models...")
        success = processor.load_models()
        
        if success:
            logger.info("✅ Models loaded successfully!")
            final_status = processor.get_status()
            logger.info(f"✅ Final status: {final_status}")
        else:
            logger.error("❌ Model loading failed")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ DetectionProcessor test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_directory_creation():
    """Test if directories are created in correct locations"""
    logger.info("=== Testing Directory Creation ===")
    try:
        from edge.src.core.config import BASE_DIR, IMAGE_SAVE_DIR, DATABASE_PATH
        
        # Check BASE_DIR
        base_path = Path(BASE_DIR)
        logger.info(f"✅ BASE_DIR exists: {base_path.exists()} - {base_path}")
        
        # Check IMAGE_SAVE_DIR
        image_path = Path(IMAGE_SAVE_DIR)
        logger.info(f"✅ IMAGE_SAVE_DIR exists: {image_path.exists()} - {image_path}")
        
        # Check DATABASE directory
        db_path = Path(DATABASE_PATH)
        db_dir = db_path.parent
        logger.info(f"✅ Database directory exists: {db_dir.exists()} - {db_dir}")
        
        # Check log directory
        log_dir = base_path / 'log'
        logger.info(f"✅ Log directory exists: {log_dir.exists()} - {log_dir}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Directory test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting AI Camera v1.3 Detection Model Tests")
    logger.info(f"Test started at: {datetime.now()}")
    
    tests = [
        ("Configuration Loading", test_config_loading),
        ("Import Validation", test_import_validation),
        ("Directory Creation", test_directory_creation),
        ("Degirum Availability", test_degirum_availability),
        ("DetectionProcessor", test_detection_processor),
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("📊 TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if result:
            passed += 1
    
    logger.info(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Detection models should work correctly.")
    else:
        logger.warning(f"⚠️  {total - passed} test(s) failed. Check configuration and environment.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
