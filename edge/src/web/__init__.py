"""
Web Module for AI Camera v2.0.0

This module provides the web interface for the AI Camera system.
This module contains web-related components including:
- Flask blueprints
- WebSocket handlers
- Template utilities
- Web interface components

Author: AI Camera Team
Version: 2.0
Date: August 2025
"""

from edge.src.web.blueprints import (
    main_bp,
    camera_bp,
    detection_bp,
    streaming_bp,
    health_bp,
    websocket_bp
)

__all__ = [
    'main_bp',
    'camera_bp',
    'detection_bp',
    'streaming_bp',
    'health_bp',
    'websocket_bp'
]

__version__ = "1.3"
__author__ = "AI Camera Team"
