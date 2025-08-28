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
    
    # Run pytest with hardware tests disabled
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/test_imports.py',  # Only run import tests that don't need hardware
        '-v',
        '--tb=short',
        '--disable-warnings',
    ]
    
    print(f"🚀 Running tests with command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ All tests passed!")
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Some tests failed with exit code: {e.returncode}")
        return e.returncode

if __name__ == '__main__':
    exit(run_tests())
