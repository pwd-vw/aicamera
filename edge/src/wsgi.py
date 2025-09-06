#!/usr/bin/env python3
"""
WSGI Entry Point for AI Camera v2.0.0

This is the WSGI entry point for the v2.0.0 application.
It can be used with Gunicorn or other WSGI servers.
"""

import os
import sys
from pathlib import Path

def setup_wsgi_paths():
    """
    Setup paths for WSGI environment.
    This function handles both development and production environments.
    """
    print("🔧 [WSGI] setup_wsgi_paths called")
    
    # Get the current file's directory
    current_file = Path(__file__)
    
    # Strategy 1: If we're in the edge/src directory, go up to find aicamera root
    if current_file.parent.name == 'src':
        # We're in edge/src/wsgi.py, so go up 2 levels to get aicamera root
        project_root = current_file.parent.parent.parent
        print(f"🔧 [WSGI] using strategy 1 - project_root: {project_root}")
    else:
        # Fallback: try to find aicamera root by looking for edge/ and server/ directories
        current = current_file.parent
        while current.parent != current:  # While not at root
            if (current / 'edge').exists() and (current / 'server').exists():
                project_root = current
                print(f"🔧 [WSGI] using fallback strategy - project_root: {project_root}")
                break
            current = current.parent
        else:
            # If we can't find it, use the current file's parent's parent
            project_root = current_file.parent.parent
            print(f"🔧 [WSGI] using default fallback - project_root: {project_root}")
    
    # Add project root to path
    project_root_str = str(project_root.absolute())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        print(f"🔧 [WSGI] added project_root to sys.path")
    
    # Add edge directory for edge.* imports
    edge_path = str(project_root / 'edge')
    if edge_path not in sys.path:
        sys.path.insert(0, edge_path)
        print(f"🔧 [WSGI] added edge_path to sys.path")
    
    # Add edge/src directory for src.* imports
    edge_src_path = str(project_root / 'edge' / 'src')
    if edge_src_path not in sys.path:
        sys.path.insert(0, edge_src_path)
        print(f"🔧 [WSGI] added edge_src_path to sys.path")
    
    print(f"🔧 [WSGI] setup_wsgi_paths completed")
    return project_root

# Setup paths first
project_root = setup_wsgi_paths()

# Now import the import helper and setup proper paths
print("🔧 [WSGI] importing import_helper")
try:
    from edge.src.core.utils.import_helper import setup_import_paths, validate_imports
    setup_import_paths()
    print("🔧 [WSGI] import_helper setup completed")
except ImportError as e:
    print(f"🔧 [WSGI] Warning: Could not import import_helper: {e}")

# Setup logging
print("🔧 [WSGI] setting up logging")
try:
    from edge.src.core.utils.logging_config import setup_logging, get_logger
    logger = setup_logging(level="INFO")
    print("🔧 [WSGI] logging setup completed")
except ImportError as e:
    print(f"🔧 [WSGI] Could not import logging_config: {e}, using fallback")
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import logging_config: {e}")

# Import the application
print("🔧 [WSGI] importing create_app")
logger.info("📥 importing create_app")
try:
    from edge.src.app import create_app
    print("🔧 [WSGI] create_app imported")
    logger.info("✅ create_app imported")
    print("🔧 [WSGI] calling create_app()")
    logger.info("🚀 calling create_app()")
    app, socketio = create_app()
    print(f"🔧 [WSGI] create_app() completed - App: {type(app).__name__}, SocketIO: {type(socketio).__name__}")
    logger.info("✅ create_app() completed")
    logger.info(f"📊 App: {type(app).__name__}, SocketIO: {type(socketio).__name__}")
except Exception as e:
    print(f"🔧 [WSGI] Failed to create app: {e}")
    logger.error(f"❌ Failed to create app: {e}")
    raise

# Validate imports if possible
try:
    import_errors = validate_imports()
    if import_errors:
        logger.warning("Some imports failed:")
        for error in import_errors:
            logger.warning(f"  {error}")
except Exception as e:
    logger.warning(f"Could not validate imports: {e}")

def application(environ, start_response):
    """
    WSGI application entry point
    
    This function is called by the WSGI server (e.g., Gunicorn)
    """
    method = environ.get('REQUEST_METHOD', 'UNKNOWN')
    path = environ.get('PATH_INFO', 'UNKNOWN')
    print(f"🔧 [WSGI] {method} {path}")
    try:
        result = app(environ, start_response)
        return result
    except Exception as e:
        print(f"🔧 [WSGI] error: {e}")
        raise

if __name__ == '__main__':
    # For direct execution
    logger.info("Starting AI Camera v2.0.0 WSGI")
    
    try:
        # Run with Flask development server
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)
