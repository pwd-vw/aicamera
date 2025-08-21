#!/usr/bin/env python3
"""
Test script to verify health monitor integration with detection processor
"""

import sys
import os

# Add the correct paths for production environment
# Root: aicamera/, Working: aicamera/edge/
current_dir = os.path.dirname(os.path.abspath(__file__))  # aicamera/edge/
root_dir = os.path.dirname(current_dir)  # aicamera/
sys.path.insert(0, root_dir)  # Add aicamera/ to path
sys.path.insert(0, current_dir)  # Add aicamera/edge/ to path
sys.path.insert(0, os.path.join(current_dir, 'src'))  # Add aicamera/edge/src/ to path

def test_detection_processor_access():
    """Test if health monitor can access detection processor service."""
    print("🔍 Testing Detection Processor Access...")
    
    try:
        from edge.src.core.dependency_container import get_service
        print("✅ Dependency container imported successfully")
        
        detection_processor = get_service('detection_processor')
        if detection_processor:
            print("✅ Detection processor service available")
            
            status = detection_processor.get_status()
            print(f"📊 Detection Processor Status:")
            print(f"   Models Loaded: {status.get('models_loaded', False)}")
            print(f"   Vehicle Model: {status.get('vehicle_model_available', False)}")
            print(f"   LP Detection Model: {status.get('lp_detection_model_available', False)}")
            print(f"   LP OCR Model: {status.get('lp_ocr_model_available', False)}")
            print(f"   EasyOCR: {status.get('easyocr_available', False)}")
            
            return True
        else:
            print("❌ Detection processor service not available")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing detection processor: {e}")
        return False

def test_health_monitor_model_check():
    """Test health monitor model checking logic."""
    print("\n🔍 Testing Health Monitor Model Check...")
    
    try:
        from edge.src.components.health_monitor import HealthMonitor
        print("✅ Health monitor imported successfully")
        
        health_monitor = HealthMonitor()
        result = health_monitor.check_model_loading()
        
        print(f"📊 Model Check Result: {'PASS' if result else 'FAIL'}")
        
        # Get latest health check logs
        latest_checks = health_monitor.get_latest_health_checks(5)
        for check in latest_checks:
            if check.get('component') == 'Detection Models':
                print(f"📝 Latest Detection Models Check:")
                print(f"   Status: {check.get('status')}")
                print(f"   Message: {check.get('message')}")
                print(f"   Details: {check.get('details')}")
                break
        
        return result
        
    except Exception as e:
        print(f"❌ Error in health monitor model check: {e}")
        return False

def test_degirum_direct_access():
    """Test direct degirum access."""
    print("\n🔍 Testing Direct Degirum Access...")
    
    try:
        import degirum as dg
        print("✅ Degirum imported successfully")
        
        from edge.src.core.config import (
            VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL,
            HEF_MODEL_PATH, MODEL_ZOO_URL
        )
        
        print(f"📋 Model Configuration:")
        print(f"   Vehicle Model: {VEHICLE_DETECTION_MODEL}")
        print(f"   LP Model: {LICENSE_PLATE_DETECTION_MODEL}")
        print(f"   Model Path: {HEF_MODEL_PATH}")
        print(f"   Zoo URL: {MODEL_ZOO_URL}")
        
        # Try to load vehicle model
        try:
            vehicle_model = dg.load_model(
                model_name=VEHICLE_DETECTION_MODEL,
                inference_host_address=HEF_MODEL_PATH,
                zoo_url=MODEL_ZOO_URL
            )
            if vehicle_model:
                print("✅ Vehicle model loaded successfully via degirum")
                return True
            else:
                print("❌ Vehicle model failed to load via degirum")
                return False
        except Exception as e:
            print(f"❌ Error loading vehicle model via degirum: {e}")
            return False
            
    except ImportError:
        print("❌ Degirum not available")
        return False
    except Exception as e:
        print(f"❌ Error in degirum test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Health Monitor Detection Integration Test")
    print("=" * 50)
    
    # Test 1: Detection processor access
    test1_result = test_detection_processor_access()
    
    # Test 2: Health monitor model check
    test2_result = test_health_monitor_model_check()
    
    # Test 3: Direct degirum access
    test3_result = test_degirum_direct_access()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Detection Processor Access: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"   Health Monitor Model Check: {'✅ PASS' if test2_result else '❌ FAIL'}")
    print(f"   Direct Degirum Access: {'✅ PASS' if test3_result else '❌ FAIL'}")
    
    if test1_result and test2_result and test3_result:
        print("\n🎉 All tests passed! Health monitor should work correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the issues above.")
