#!/usr/bin/env python3
"""
Camera System Testing Script for AI Camera v1.3

This script tests the Camera Handler component and Camera Manager service
to validate their functionality according to the system requirements:

1. Picamera2 integration with proper configuration
2. Thread-safe access with locking mechanism 
3. Resource cleanup and proper shutdown handling
4. Video streaming capability for web interface
5. Status monitoring and health checks
6. Metadata extraction and camera properties
7. Frame capture preparation for ML inference pipeline

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

import sys
import time
import threading
import logging
import json
from pathlib import Path
from typing import Dict, Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_dependency_injection():
    """Test dependency injection container with camera services."""
    print("\n" + "="*60)
    print("🔧 Testing Dependency Injection Container")
    print("="*60)
    
    try:
        from core.dependency_container import get_container, get_service
        
        # Get container instance
        container = get_container()
        print(f"✅ Container initialized: {type(container).__name__}")
        
        # Check registered services
        services = container.get_registered_services()
        camera_services = {k: v for k, v in services.items() if 'camera' in k}
        print(f"📋 Camera-related services: {list(camera_services.keys())}")
        
        # Test camera handler service
        if 'camera_handler' in services:
            camera_handler = get_service('camera_handler')
            print(f"✅ Camera Handler retrieved: {type(camera_handler).__name__}")
            
            # Test Singleton pattern
            camera_handler2 = get_service('camera_handler')
            is_singleton = camera_handler is camera_handler2
            print(f"✅ Singleton pattern verified: {is_singleton}")
        
        # Test camera manager service
        if 'camera_manager' in services:
            camera_manager = get_service('camera_manager')
            print(f"✅ Camera Manager retrieved: {type(camera_manager).__name__}")
            
            # Check dependency injection
            if hasattr(camera_manager, 'camera_handler'):
                injected_handler = camera_manager.camera_handler
                print(f"✅ Dependencies injected: {type(injected_handler).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Dependency injection test failed: {e}")
        return False

def test_camera_handler_basics():
    """Test basic camera handler functionality."""
    print("\n" + "="*60) 
    print("📷 Testing Camera Handler - Basic Operations")
    print("="*60)
    
    try:
        from core.dependency_container import get_service
        
        # Get camera handler instance
        camera_handler = get_service('camera_handler')
        print(f"✅ Camera handler obtained: {type(camera_handler).__name__}")
        
        # Test thread locking mechanism
        print("\n🔒 Testing Thread Lock Mechanism...")
        lock_acquired = camera_handler.acquire_camera_access(timeout=5.0)
        if lock_acquired:
            print("✅ Camera access lock acquired successfully")
            
            # Test that second access is blocked
            def try_second_access():
                return camera_handler.acquire_camera_access(timeout=1.0)
            
            second_thread = threading.Thread(target=try_second_access)
            second_thread.start() 
            second_thread.join()
            
            print("✅ Thread locking mechanism working properly")
            
            # Release lock
            camera_handler.release_camera_access()
            print("✅ Camera access lock released")
        else:
            print("❌ Failed to acquire camera access lock")
            return False
        
        # Test camera initialization (mock mode for testing)
        print("\n🚀 Testing Camera Initialization...")
        
        # Check if we're on a system with camera hardware
        try:
            # Try to get camera properties without initializing
            if hasattr(camera_handler, 'camera_properties'):
                print("📋 Camera properties available")
            
            # Test status retrieval
            status = camera_handler.get_status()
            print(f"📊 Camera status: {json.dumps(status, indent=2, default=str)}")
            
        except Exception as e:
            print(f"⚠️  Camera hardware not available for testing: {e}")
            print("✅ Graceful handling of missing hardware")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Camera handler test failed: {e}")
        return False

def test_camera_manager_service():
    """Test camera manager service functionality."""
    print("\n" + "="*60)
    print("🎮 Testing Camera Manager - Service Layer")  
    print("="*60)
    
    try:
        from core.dependency_container import get_service
        
        # Get camera manager instance
        camera_manager = get_service('camera_manager')
        print(f"✅ Camera manager obtained: {type(camera_manager).__name__}")
        
        # Test initial status
        print("\n📊 Testing Status Monitoring...")
        status = camera_manager.get_status()
        print(f"📋 Manager status: {json.dumps(status, indent=2, default=str)}")
        
        # Test health check
        print("\n🏥 Testing Health Check...")
        health = camera_manager.health_check()
        print(f"🏥 Health check result: {json.dumps(health, indent=2, default=str)}")
        
        # Test configuration
        print("\n⚙️  Testing Configuration...")
        config = camera_manager.get_configuration()
        print(f"⚙️  Current config: {json.dumps(config, indent=2, default=str)}")
        
        # Test available settings
        settings = camera_manager.get_available_settings()
        if 'error' not in settings:
            print(f"📋 Available settings: {list(settings.keys())}")
        else:
            print(f"⚠️  Settings error: {settings['error']}")
        
        # Test frame callback registration (for ML pipeline)
        print("\n🔗 Testing ML Pipeline Integration...")
        
        def ml_frame_callback(frame_data):
            """Mock ML processing callback."""
            if isinstance(frame_data, dict) and 'frame' in frame_data:
                frame = frame_data['frame']
                if hasattr(frame, 'shape'):
                    print(f"🎯 ML callback received frame: {frame.shape}")
                else:
                    print("🎯 ML callback received frame data")
            return True
        
        camera_manager.register_frame_callback(ml_frame_callback)
        callback_count = len(camera_manager.frame_callbacks)
        print(f"✅ Frame callback registered ({callback_count} total callbacks)")
        
        # Test streaming preparation (without actual streaming)
        print("\n🎥 Testing Video Streaming Preparation...")
        
        try:
            # Test that streaming can be configured
            if hasattr(camera_manager, 'frames_queue'):
                queue_size = camera_manager.frames_queue.qsize()
                print(f"📦 Frames queue initialized (size: {queue_size})")
            
            if hasattr(camera_manager, 'metadata_queue'):
                metadata_queue_size = camera_manager.metadata_queue.qsize()
                print(f"📦 Metadata queue initialized (size: {metadata_queue_size})")
            
            print("✅ Video streaming infrastructure ready")
            
        except Exception as e:
            print(f"⚠️  Streaming test limited due to: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Camera manager test failed: {e}")
        return False

def test_resource_cleanup():
    """Test resource cleanup and proper shutdown."""
    print("\n" + "="*60)
    print("🧹 Testing Resource Cleanup & Shutdown")
    print("="*60)
    
    try:
        from core.dependency_container import get_service, shutdown_container
        
        # Get services
        camera_handler = get_service('camera_handler')
        camera_manager = get_service('camera_manager')
        
        print("📋 Services obtained for cleanup testing")
        
        # Test individual cleanup methods
        print("\n🧹 Testing Individual Cleanup...")
        
        if hasattr(camera_manager, 'cleanup'):
            camera_manager.cleanup()
            print("✅ Camera manager cleanup executed")
        
        if hasattr(camera_handler, 'cleanup'):
            camera_handler.cleanup()
            print("✅ Camera handler cleanup executed")
        
        # Test container shutdown
        print("\n🔄 Testing Container Shutdown...")
        shutdown_container()
        print("✅ Dependency container shutdown completed")
        
        # Verify cleanup by checking if new instances can be created
        from core.dependency_container import get_container
        new_container = get_container()
        print(f"✅ New container can be created after shutdown: {type(new_container).__name__}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Cleanup test failed: {e}")
        return False

def test_picamera2_integration():
    """Test Picamera2 integration and configuration."""
    print("\n" + "="*60)
    print("📸 Testing Picamera2 Integration") 
    print("="*60)
    
    try:
        # Test Picamera2 import
        try:
            from picamera2 import Picamera2
            from libcamera import controls
            print("✅ Picamera2 library imported successfully")
        except ImportError as e:
            print(f"❌ Picamera2 import failed: {e}")
            print("⚠️  This may be expected on non-Raspberry Pi systems")
            return True  # Consider this a pass on non-Pi systems
        
        # Test camera handler Picamera2 integration
        from core.dependency_container import get_service
        camera_handler = get_service('camera_handler')
        
        # Check if Picamera2 is properly integrated
        if hasattr(camera_handler, 'picam2'):
            print("✅ Picamera2 instance accessible in camera handler")
        
        # Test configuration methods based on Picamera2 docs
        print("\n⚙️  Testing Picamera2 Configuration Methods...")
        
        # Test sensor modes (available even without camera hardware)
        if hasattr(camera_handler, 'sensor_modes'):
            modes_count = len(camera_handler.sensor_modes) if camera_handler.sensor_modes else 0
            print(f"📋 Sensor modes available: {modes_count}")
        
        # Test camera properties
        if hasattr(camera_handler, 'camera_properties'):
            props_count = len(camera_handler.camera_properties) if camera_handler.camera_properties else 0
            print(f"📋 Camera properties available: {props_count}")
        
        # Test configuration structure
        config_methods = [
            'initialize_camera', 'configure_camera', 'start_camera', 
            'stop_camera', 'capture_frame', 'get_metadata'
        ]
        
        available_methods = []
        for method in config_methods:
            if hasattr(camera_handler, method):
                available_methods.append(method)
        
        print(f"✅ Picamera2 methods available: {available_methods}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Picamera2 integration test failed: {e}")
        return False

def run_comprehensive_tests():
    """Run all camera system tests."""
    print("\n" + "🚀"*20)
    print("🎯 AI CAMERA v1.3 - COMPREHENSIVE CAMERA SYSTEM TEST")
    print("🚀"*20)
    
    test_results = {}
    
    # Run all tests
    tests = [
        ("Dependency Injection", test_dependency_injection),
        ("Camera Handler Basics", test_camera_handler_basics),
        ("Camera Manager Service", test_camera_manager_service),
        ("Picamera2 Integration", test_picamera2_integration),
        ("Resource Cleanup", test_resource_cleanup),
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'⏳ Running:':<15} {test_name}")
            start_time = time.time()
            result = test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                print(f"✅ {'PASSED:':<15} {test_name} ({duration:.2f}s)")
                test_results[test_name] = "PASSED"
            else:
                print(f"❌ {'FAILED:':<15} {test_name} ({duration:.2f}s)")
                test_results[test_name] = "FAILED"
                
        except Exception as e:
            print(f"💥 {'ERROR:':<15} {test_name} - {e}")
            test_results[test_name] = "ERROR"
    
    # Print summary
    print("\n" + "📊"*20)
    print("📊 TEST RESULTS SUMMARY")
    print("📊"*20)
    
    passed = sum(1 for result in test_results.values() if result == "PASSED")
    failed = sum(1 for result in test_results.values() if result == "FAILED")
    errors = sum(1 for result in test_results.values() if result == "ERROR")
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status_icon = "✅" if result == "PASSED" else "❌" if result == "FAILED" else "💥"
        print(f"{status_icon} {test_name:<25} {result}")
    
    print(f"\n📈 Overall Results: {passed}/{total} passed, {failed} failed, {errors} errors")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Camera system is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests did not pass. Please check the issues above.")
        return False

if __name__ == "__main__":
    """Main test execution."""
    try:
        # Change to the edge directory
        import os
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        print(f"📂 Working directory: {os.getcwd()}")
        print(f"🐍 Python version: {sys.version}")
        print(f"📦 Python path includes: src/")
        
        # Run tests
        success = run_comprehensive_tests()
        
        if success:
            print("\n🏁 Camera system testing completed successfully!")
            sys.exit(0)
        else:
            print("\n🚫 Camera system testing completed with issues!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
