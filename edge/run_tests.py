#!/usr/bin/env python3
"""
Test runner script for edge tests that handles import and path issues.
"""
import os
import sys
import subprocess
from pathlib import Path

def setup_test_environment():
    """Set up the test environment with proper paths."""
    # Get the edge directory
    edge_dir = Path(__file__).parent.absolute()
    project_root = edge_dir.parent
    
    # Add project root to Python path
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(edge_dir))
    
    # Set environment variables
    os.environ['PYTHONPATH'] = f"{project_root}:{edge_dir}:{os.environ.get('PYTHONPATH', '')}"
    os.environ['AICAMERA_TEST_MODE'] = 'true'
    
    print(f"🔧 Test environment setup:")
    print(f"   Project root: {project_root}")
    print(f"   Edge directory: {edge_dir}")
    print(f"   Python path: {os.environ['PYTHONPATH']}")

def run_tests():
    """Run the tests with proper configuration."""
    setup_test_environment()
    
    # Change to edge directory
    edge_dir = Path(__file__).parent.absolute()
    os.chdir(edge_dir)
    
    # For GitHub Actions, run a simple import test without pytest
    print(f"🚀 Running simple import test for GitHub Actions...")
    
    # Create a simple test script
    test_script = '''
import sys
import os
from pathlib import Path

# Add the edge directory to Python path
edge_dir = Path(__file__).parent
project_root = edge_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(edge_dir))

# Set environment variables
os.environ['AICAMERA_TEST_MODE'] = 'true'
os.environ['PYTHONPATH'] = f"{project_root}:{edge_dir}:{os.environ.get('PYTHONPATH', '')}"

print(f"🔧 Test environment setup:")
print(f"   Project root: {project_root}")
print(f"   Edge directory: {edge_dir}")
print(f"   Python path: {os.environ['PYTHONPATH']}")

# Test basic imports that don't require hardware
try:
    # Test core imports
    print("\\n📦 Testing Core Imports:")
    from edge.src.core.config import FLASK_HOST, FLASK_PORT
    print("  ✅ edge.src.core.config")
    
    from edge.src.core.utils.logging_config import setup_logging, get_logger
    print("  ✅ edge.src.core.utils.logging_config")
    
    # Test component imports (skip hardware-dependent ones)
    print("\\n🔧 Testing Component Imports:")
    from edge.src.components.database_manager import DatabaseManager
    print("  ✅ edge.src.components.database_manager")
    
    from edge.src.components.health_monitor import HealthMonitor
    print("  ✅ edge.src.components.health_monitor")
    
    # Test web imports
    print("\\n🌐 Testing Web Imports:")
    from edge.src.web.blueprints.main import main_bp
    print("  ✅ edge.src.web.blueprints.main")
    
    print("\\n✅ All import tests passed!")
    exit(0)
    
except ImportError as e:
    print(f"\\n❌ Import test failed: {e}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Python path: {sys.path}")
    exit(1)
except Exception as e:
    print(f"\\n❌ Unexpected error: {e}")
    exit(1)
'''
    
    # Write the test script
    test_file = edge_dir / 'simple_import_test.py'
    with open(test_file, 'w') as f:
        f.write(test_script)
    
    try:
        # Run the simple test
        result = subprocess.run([sys.executable, str(test_file)], check=True)
        print("✅ Simple import test completed successfully!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Simple import test failed with exit code: {e.returncode}")
        return e.returncode

if __name__ == '__main__':
    exit(run_tests())
