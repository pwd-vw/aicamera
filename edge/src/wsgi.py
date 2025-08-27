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
    # Get the current file's directory
    current_file = Path(__file__)
    
    # Strategy 1: If we're in the edge/src directory, go up to find aicamera root
    if current_file.parent.name == 'src':
        # We're in edge/src/wsgi.py, so go up 2 levels to get aicamera root
        project_root = current_file.parent.parent.parent
    else:
        # Fallback: try to find aicamera root by looking for edge/ and server/ directories
        current = current_file.parent
        while current.parent != current:  # While not at root
            if (current / 'edge').exists() and (current / 'server').exists():
                project_root = current
                break
            current = current.parent
        else:
            # If we can't find it, use the current file's parent's parent
            project_root = current_file.parent.parent
    
    # Add project root to path
    project_root_str = str(project_root.absolute())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
    
    # Add edge directory for edge.* imports
    edge_path = str(project_root / 'edge')
    if edge_path not in sys.path:
        sys.path.insert(0, edge_path)
    
    # Add edge/src directory for src.* imports
    edge_src_path = str(project_root / 'edge' / 'src')
    if edge_src_path not in sys.path:
        sys.path.insert(0, edge_src_path)
    
    return project_root

# Setup paths first
project_root = setup_wsgi_paths()

# Now import the import helper and setup proper paths
try:
    from edge.src.core.utils.import_helper import setup_import_paths, validate_imports
    setup_import_paths()
except ImportError as e:
    # Fallback if import helper is not available
    print(f"Warning: Could not import import_helper: {e}")
    print(f"Using basic path setup with project_root: {project_root}")

# Setup logging
try:
    from edge.src.core.utils.logging_config import setup_logging, get_logger
    logger = setup_logging(level="INFO")
except ImportError as e:
    # Fallback logging setup
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.warning(f"Could not import logging_config: {e}")

# Import the application
logger.info("📥 === ABOUT TO IMPORT create_app ===")
try:
    from edge.src.app import create_app
    logger.info("✅ === create_app IMPORTED SUCCESSFULLY ===")
    logger.info("🚀 === ABOUT TO CALL create_app() ===")
    app, socketio = create_app()
    logger.info("✅ === create_app() COMPLETED SUCCESSFULLY ===")
    logger.info(f"📊 App type: {type(app)}, SocketIO type: {type(socketio)}")
except Exception as e:
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
    return app(environ, start_response)

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
