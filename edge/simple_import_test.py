
import sys
import os
from pathlib import Path

# Add the edge directory to Python path
# This script is run from project root, so edge_dir is the edge subdirectory
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
print(f"   Current working directory: {os.getcwd()}")
print(f"   Python path: {os.environ['PYTHONPATH']}")

# Test basic imports that don't require hardware
try:
    # Test core imports
    print("\n📦 Testing Core Imports:")
    from edge.src.core.config import FLASK_HOST, FLASK_PORT
    print("  ✅ edge.src.core.config")
    
    from edge.src.core.utils.logging_config import setup_logging, get_logger
    print("  ✅ edge.src.core.utils.logging_config")
    
    # Test component imports (skip hardware-dependent ones)
    print("\n🔧 Testing Component Imports:")
    from edge.src.components.database_manager import DatabaseManager
    print("  ✅ edge.src.components.database_manager")
    
    from edge.src.components.health_monitor import HealthMonitor
    print("  ✅ edge.src.components.health_monitor")
    
    # Test web imports
    print("\n🌐 Testing Web Imports:")
    from edge.src.web.blueprints.main import main_bp
    print("  ✅ edge.src.web.blueprints.main")
    
    print("\n✅ All import tests passed!")
    exit(0)
    
except ImportError as e:
    print(f"\n❌ Import test failed: {e}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   Python path: {sys.path}")
    print(f"   Available modules: {[m for m in sys.modules.keys() if 'edge' in m]}")
    exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    exit(1)
