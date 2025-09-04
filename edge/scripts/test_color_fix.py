#!/usr/bin/env python3
"""
Test script to verify the camera color fix implementation.

This script tests that:
1. Camera streams use consistent RGB888 format
2. Color conversion from RGB to BGR works correctly
3. No color inversion occurs in the pipeline

Usage:
    python3 test_color_fix.py
"""

import sys
import os
import time
import numpy as np

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_color_formats():
    """Test that camera configuration uses consistent color formats."""
    print("🔍 Testing Camera Color Format Configuration...")
    
    try:
        from components.camera_handler import CameraHandler
        
        # Get camera handler instance
        camera_handler = CameraHandler.get_instance()
        
        if not camera_handler.initialized:
            print("⚠️  Camera not initialized, attempting to initialize...")
            if not camera_handler.initialize_camera():
                print("❌ Failed to initialize camera")
                return False
        
        # Check current configuration
        config = camera_handler.current_config
        if not config:
            print("❌ No camera configuration available")
            return False
        
        print(f"📸 Camera Configuration:")
        print(f"   Main stream: {config.get('main', {}).get('format', 'Unknown')}")
        print(f"   Lores stream: {config.get('lores', {}).get('format', 'Unknown')}")
        
        # Verify both streams use RGB888
        main_format = config.get('main', {}).get('format')
        lores_format = config.get('lores', {}).get('format')
        
        if main_format == 'RGB888' and lores_format == 'RGB888':
            print("✅ Both streams use consistent RGB888 format")
            return True
        else:
            print(f"❌ Inconsistent formats: main={main_format}, lores={lores_format}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing color formats: {e}")
        return False

def test_color_conversion():
    """Test that color conversion from RGB to BGR works correctly."""
    print("\n🔍 Testing Color Conversion Logic...")
    
    try:
        import cv2
        
        # Create a test RGB image with known colors
        # Red pixel at (0,0), Green at (1,0), Blue at (2,0)
        test_rgb = np.array([
            [[255, 0, 0],    # Red
             [0, 255, 0],    # Green  
             [0, 0, 255]]    # Blue
        ], dtype=np.uint8)
        
        print(f"📊 Test RGB Image:")
        print(f"   Pixel (0,0): RGB{test_rgb[0,0]} (should be Red)")
        print(f"   Pixel (1,0): RGB{test_rgb[0,1]} (should be Green)")
        print(f"   Pixel (2,0): RGB{test_rgb[0,2]} (should be Blue)")
        
        # Convert RGB to BGR (same as detection processor)
        test_bgr = cv2.cvtColor(test_rgb, cv2.COLOR_RGB2BGR)
        
        print(f"\n📊 Converted BGR Image:")
        print(f"   Pixel (0,0): BGR{test_bgr[0,0]} (should be Red)")
        print(f"   Pixel (1,0): BGR{test_bgr[0,1]} (should be Green)")
        print(f"   Pixel (2,0): BGR{test_bgr[0,2]} (should be Blue)")
        
        # Verify the conversion is correct
        # In BGR: Red = [0,0,255], Green = [0,255,0], Blue = [255,0,0]
        expected_bgr = np.array([
            [[0, 0, 255],    # Red in BGR
             [0, 255, 0],    # Green in BGR
             [255, 0, 0]]    # Blue in BGR
        ], dtype=np.uint8)
        
        if np.array_equal(test_bgr, expected_bgr):
            print("✅ Color conversion RGB→BGR working correctly")
            return True
        else:
            print("❌ Color conversion failed")
            print(f"   Expected: {expected_bgr}")
            print(f"   Got:      {test_bgr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing color conversion: {e}")
        return False

def test_camera_capture():
    """Test that camera capture returns correct format information."""
    print("\n🔍 Testing Camera Capture Format Info...")
    
    try:
        from components.camera_handler import CameraHandler
        
        camera_handler = CameraHandler.get_instance()
        
        if not camera_handler.streaming:
            print("⚠️  Camera not streaming, attempting to start...")
            if not camera_handler.start_camera():
                print("❌ Failed to start camera")
                return False
        
        # Wait a moment for camera to stabilize
        time.sleep(2)
        
        # Capture a frame and check format info
        frame_data = camera_handler.capture_ml_frame()
        if not frame_data:
            print("❌ Failed to capture frame")
            return False
        
        print(f"📸 Captured Frame Info:")
        print(f"   Main format: {frame_data.get('main_format', 'Unknown')}")
        print(f"   Lores format: {frame_data.get('lores_format', 'Unknown')}")
        print(f"   Main size: {frame_data.get('main_size', 'Unknown')}")
        print(f"   Lores size: {frame_data.get('lores_size', 'Unknown')}")
        
        # Verify both formats are RGB888
        main_format = frame_data.get('main_format')
        lores_format = frame_data.get('lores_format')
        
        if main_format == 'RGB888' and lores_format == 'RGB888':
            print("✅ Frame capture returns consistent RGB888 format info")
            return True
        else:
            print(f"❌ Inconsistent frame formats: main={main_format}, lores={lores_format}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing camera capture: {e}")
        return False

def main():
    """Run all color fix tests."""
    print("🎨 Camera Color Fix Verification Tests")
    print("=" * 50)
    
    tests = [
        ("Color Format Configuration", test_color_formats),
        ("Color Conversion Logic", test_color_conversion),
        ("Camera Capture Format Info", test_camera_capture)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Color fix is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
