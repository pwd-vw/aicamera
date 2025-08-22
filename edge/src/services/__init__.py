"""
Services Module for AI Camera v1.3

This module contains service layer components that implement
business logic and coordinate between different components.

Services:
- CameraManager: Camera operations and management
- DetectionManager: AI detection operations
- VideoStreamingService: Video streaming operations
- WebSocketSender: WebSocket communication

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

from edge.src.services.camera_manager import CameraManager, create_camera_manager
from edge.src.services.detection_manager import DetectionManager, create_detection_manager
from edge.src.services.video_streaming import VideoStreamingService, create_video_streaming_service
from edge.src.services.websocket_sender import WebSocketSender, create_websocket_sender
from edge.src.services.health_service import HealthService, create_health_service
from edge.src.services.storage_service import StorageService, create_storage_service

__all__ = [
    'CameraManager',
    'DetectionManager',
    'VideoStreamingService',
    'WebSocketSender',
    'HealthService',
    'StorageService',
    'create_camera_manager',
    'create_detection_manager',
    'create_video_streaming_service',
    'create_websocket_sender',
    'create_health_service',
    'create_storage_service',
]

__version__ = "1.3"
__author__ = "AI Camera Team"
