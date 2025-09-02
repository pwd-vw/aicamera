#!/usr/bin/env python3
"""
Simple test for manual capture functionality
"""

import os
import sys
from datetime import datetime

def test_manual_capture_directory():
    """Test manual capture directory"""
    manual_capture_dir = os.path.join(os.path.dirname(__file__), 'manual_capture')
    
    print(f"Testing manual capture directory: {manual_capture_dir}")
    
    # Check if directory exists
    if os.path.exists(manual_capture_dir):
        print(f"✅ Directory exists: {manual_capture_dir}")
    else:
        print(f"❌ Directory does not exist: {manual_capture_dir}")
        return False
    
    # Check if directory is writable
    if os.access(manual_capture_dir, os.W_OK):
        print(f"✅ Directory is writable")
    else:
        print(f"❌ Directory is not writable")
        return False
    
    return True

def test_file_creation():
    """Test creating a test file"""
    manual_capture_dir = os.path.join(os.path.dirname(__file__), 'manual_capture')
    
    print(f"\nTesting file creation in: {manual_capture_dir}")
    
    # Create a test file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    test_filename = f"test_capture_{timestamp}.txt"
    test_filepath = os.path.join(manual_capture_dir, test_filename)
    
    try:
        with open(test_filepath, 'w') as f:
            f.write(f"Test capture file created at {timestamp}")
        
        print(f"✅ Test file created: {test_filename}")
        
        # Check file size
        file_size = os.path.getsize(test_filepath)
        print(f"File size: {file_size} bytes")
        
        # Clean up test file
        os.remove(test_filepath)
        print(f"✅ Test file cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create test file: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Manual Capture System (Simple)")
    print("=" * 50)
    
    tests = [
        ("Manual Capture Directory", test_manual_capture_directory),
        ("File Creation", test_file_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running test: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name} PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Manual capture system is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
