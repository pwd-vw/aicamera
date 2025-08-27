#!/usr/bin/env python3
"""
Import Helper for AI Camera v1.3

This module provides utilities for managing import paths and ensuring
consistent absolute imports across the application.

Author: AI Camera Team
Version: 1.3
Date: August 8, 2025
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
from src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


def setup_import_paths(base_path: Optional[str] = None) -> None:
    """
    Setup import paths for absolute imports.
    
    Args:
        base_path: Base path to add to sys.path (defaults to project root)
    """
    if base_path is None:
        # Get the project root directory (aicamera/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent  # Go up from utils/core/src/edge
        logger.info(f"Auto-detected project root: {project_root.absolute()}")
    else:
        project_root = Path(base_path)
        logger.info(f"Using provided project root: {project_root.absolute()}")
    
    # Add project root to sys.path for absolute imports
    project_root_str = str(project_root.absolute())
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        logger.debug(f"Added project root: {project_root_str}")
    
    # Add edge directory for edge.* imports
    edge_path = str(project_root / 'edge')
    if edge_path not in sys.path:
        sys.path.insert(0, edge_path)
        logger.debug(f"Added edge path: {edge_path}")
    
    # Add edge/src directory for src.* imports
    edge_src_path = str(project_root / 'edge' / 'src')
    if edge_src_path not in sys.path:
        sys.path.insert(0, edge_src_path)
        logger.debug(f"Added edge/src path: {edge_src_path}")
    
    # Add current working directory
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
        logger.debug(f"Added CWD: {cwd}")


def get_absolute_import_path(module_name: str) -> str:
    """
    Get absolute import path for a module.
    
    Args:
        module_name: Module name (e.g., 'core', 'components', 'services')
        
    Returns:
        Absolute import path
    """
    # Map relative module names to absolute paths
    module_mapping = {
        'core': 'edge.src.core',
        'components': 'edge.src.components', 
        'services': 'edge.src.services',
        'web': 'edge.src.web',
        'utils': 'edge.src.core.utils'
    }
    
    return module_mapping.get(module_name, f'edge.src.{module_name}')


def validate_imports() -> List[str]:
    """
    Validate that all required modules can be imported using absolute paths.
    
    Returns:
        List of import errors (empty if all imports successful)
    """
    errors = []
    required_modules = [
        # Core modules
        'edge.src.core.config',
        'edge.src.core.dependency_container',
        'edge.src.core.utils.logging_config',
        'edge.src.core.utils.import_helper',
        
        # Component modules
        'edge.src.components.camera_handler',
        'edge.src.components.detection_processor',
        'edge.src.components.health_monitor',
        'edge.src.components.database_manager',
        'edge.src.components.improved_camera_manager',
        
        # Service modules
        'edge.src.services.camera_manager',
        'edge.src.services.detection_manager',
        'edge.src.services.video_streaming',
        'edge.src.services.websocket_sender',
        'edge.src.services.health_service',
        
        # Web blueprint modules
        'edge.src.web.blueprints.main',
        'edge.src.web.blueprints.camera',
        'edge.src.web.blueprints.detection',
        'edge.src.web.blueprints.detection_results',
        'edge.src.web.blueprints.health',
        'edge.src.web.blueprints.streaming',
        'edge.src.web.blueprints.websocket',
        'edge.src.web.blueprints.websocket_sender',
        
        # Main application modules
        'edge.src.app',
        'edge.src.wsgi'
    ]
    
    for module_name in required_modules:
        try:
            __import__(module_name)
            logger.debug(f"✓ Successfully imported {module_name}")
        except ImportError as e:
            error_msg = f"✗ Failed to import {module_name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"✗ Unexpected error importing {module_name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
    
    return errors


def safe_import(module_name: str, default=None):
    """
    Safely import a module with fallback.
    
    Args:
        module_name: Name of the module to import
        default: Default value to return if import fails
        
    Returns:
        Imported module or default value
    """
    try:
        return __import__(module_name, fromlist=['*'])
    except ImportError as e:
        logger.warning(f"Failed to import {module_name}: {e}")
        return default


# Auto-setup import paths when this module is imported
setup_import_paths() 