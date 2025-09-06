#!/usr/bin/env python3
"""
Debug Camera Status Methods - Isolate hanging issue
"""

import sys
import os
import time
import signal
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'edge'))

def timeout_handler(signum, frame):
    raise TimeoutError("Method call timed out")

def test_method_with_timeout(method, timeout=5, *args, **kwargs):
    """Test a method with timeout to catch hanging calls."""
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        result = method(*args, **kwargs)
        signal.alarm(0)  # Cancel timeout
        return result, None
    except TimeoutError:
        signal.alarm(0)  # Cancel timeout
        return None, f"Method timed out after {timeout} seconds"
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        return None, str(e)

def debug_camera_status():
    """Debug camera status methods to find hanging issue."""
    
    print("🔍 === DEBUGGING CAMERA STATUS METHODS ===")
    print("=" * 50)
    
    try:
        from edge.src.components.camera_handler import CameraHandler
        print("✅ Successfully imported CameraHandler")
        
        # Create camera handler instance
        camera_handler = CameraHandler()
        print(f"✅ CameraHandler instance created")
        print(f"   - Initialized: {camera_handler.initialized}")
        print(f"   - Streaming: {camera_handler.streaming}")
        
        # Test get_camera_status() with timeout
        print("\n📋 Testing get_camera_status() with 5s timeout...")
        result, error = test_method_with_timeout(camera_handler.get_camera_status, 5)
        if error:
            print(f"❌ get_camera_status() failed: {error}")
        else:
            print(f"✅ get_camera_status() succeeded: {type(result)}")
            print(f"   - Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Test get_status() with timeout
        print("\n📋 Testing get_status() with 5s timeout...")
        result, error = test_method_with_timeout(camera_handler.get_status, 5)
        if error:
            print(f"❌ get_status() failed: {error}")
        else:
            print(f"✅ get_status() succeeded: {type(result)}")
            print(f"   - Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Test individual status components
        print("\n📋 Testing individual status components...")
        
        # Test camera_status attribute access
        print("   - Testing camera_status attribute...")
        try:
            status = camera_handler.camera_status
            print(f"   ✅ camera_status: {type(status)}")
        except Exception as e:
            print(f"   ❌ camera_status access failed: {e}")
        
        # Test camera_properties attribute access
        print("   - Testing camera_properties attribute...")
        try:
            props = camera_handler.camera_properties
            print(f"   ✅ camera_properties: {type(props)}")
        except Exception as e:
            print(f"   ❌ camera_properties access failed: {e}")
        
        # Test current_config attribute access
        print("   - Testing current_config attribute...")
        try:
            config = camera_handler.current_config
            print(f"   ✅ current_config: {type(config)}")
        except Exception as e:
            print(f"   ❌ current_config access failed: {e}")
        
        # Test make_json_serializable function
        print("\n📋 Testing make_json_serializable function...")
        try:
            from edge.src.components.camera_handler import make_json_serializable
            test_obj = {"test": "value", "nested": {"key": "value"}}
            result = make_json_serializable(test_obj)
            print(f"   ✅ make_json_serializable: {type(result)}")
        except Exception as e:
            print(f"   ❌ make_json_serializable failed: {e}")
        
        print("\n🎉 === DEBUGGING COMPLETED ===")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    debug_camera_status()
