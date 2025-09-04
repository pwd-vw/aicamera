#!/usr/bin/env python3
"""
Camera Handler Component for AI Camera v1.3

This component provides low-level camera operations using Picamera2
for Camera Module 3 on Raspberry Pi 5.

Features:
- Picamera2 integration with fallback support
- Camera configuration and control
- Frame capture and metadata handling
- Camera status monitoring
- Error handling and recovery
- Dynamic camera detection and connection

Author: AI Camera Team
Version: 1.3
Date: August 7, 2025
"""

import threading
import time
import multiprocessing
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import json
import queue

import os
import cv2
import numpy as np
from edge.src.core.utils.logging_config import get_logger
logger = get_logger(__name__)


def make_json_serializable(obj: Any) -> Any:
    """
    Convert any object to JSON-serializable format.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable object
    """
    if obj is None:
        return None
    elif isinstance(obj, (int, float, str, bool)):
        return obj
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif hasattr(obj, '__dict__'):
        # Handle objects with attributes
        if hasattr(obj, 'name'):
            return str(obj.name)
        elif hasattr(obj, '__str__'):
            return str(obj)
        else:
            return str(type(obj).__name__)
    else:
        return str(obj)


def check_camera_availability():
    """
    Check if camera hardware and software are available.
    
    Returns:
        Dict: Availability status with details
    """
    status = {
        'hardware_available': False,
        'software_available': False,
        'picamera2_available': False,
        'libcamera_available': False,
        'camera_ready': False,
        'details': {}
    }
    
    # Check for camera hardware
    try:
        # Check if camera device exists
        camera_devices = ['/dev/video0', '/dev/video1', '/dev/video2']
        for device in camera_devices:
            if os.path.exists(device):
                status['hardware_available'] = True
                status['details']['camera_device'] = device
                break
        
        if not status['hardware_available']:
            # Check for CSI camera interface
            if os.path.exists('/sys/class/video4linux'):
                status['hardware_available'] = True
                status['details']['camera_interface'] = 'CSI'
    except Exception as e:
        status['details']['hardware_check_error'] = str(e)
    
    # Check for libcamera
    try:
        import libcamera
        status['libcamera_available'] = True
        status['details']['libcamera_version'] = getattr(libcamera, '__version__', 'unknown')
    except ImportError:
        status['details']['libcamera_error'] = 'libcamera not available'
    except Exception as e:
        status['details']['libcamera_error'] = str(e)
    
    # Check for picamera2
    try:
        from picamera2 import Picamera2
        status['picamera2_available'] = True
        status['details']['picamera2_version'] = getattr(Picamera2, '__version__', 'unknown')
    except ImportError:
        status['details']['picamera2_error'] = 'picamera2 not available'
    except Exception as e:
        status['details']['picamera2_error'] = str(e)
    
    # Determine if camera is ready
    status['software_available'] = status['libcamera_available'] and status['picamera2_available']
    status['camera_ready'] = status['hardware_available'] and status['software_available']
    
    return status


class CameraHandler:
    """
    Camera Handler Component using Picamera2 with Singleton pattern and access control.
    
    This class provides low-level camera operations including:
    - Camera initialization and configuration
    - Frame capture and metadata handling
    - Camera controls (exposure, gain, focus, etc.)
    - Video recording and streaming
    - Error handling and recovery
    - Dynamic camera detection and connection
    
    Singleton pattern ensures only one camera instance exists across all workers.
    Thread-safe and multiprocessing-safe camera access using locks and queues.
    
    Attributes:
        picam2: Picamera2 instance
        logger: Logger instance
        initialized: Whether camera is initialized
        streaming: Whether camera is currently streaming
        current_config: Current camera configuration
        camera_properties: Camera sensor properties
        sensor_modes: Available sensor modes
        camera_status: Camera availability status
    """
    
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    
    # Global camera access control - Thread-safe only
    _camera_lock = threading.Lock()
    _camera_queue = queue.Queue(maxsize=1)  # Single slot queue for camera access
    _camera_queue.put(None)  # เติม slot แรกให้ queue พร้อมใช้งาน
    
    # Frame Buffer System for concurrent access
    _frame_buffer_lock = threading.Lock()
    _main_frame_buffer = None  # Latest main stream frame
    _lores_frame_buffer = None  # Latest lores stream frame
    _metadata_buffer = {}  # Latest metadata
    _capture_thread = None
    _capture_running = False
    _capture_interval = 0.033  # ~30 FPS capture rate
    
    def __new__(cls, *args, **kwargs):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize Camera Handler with robust camera detection."""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = get_logger(__name__)
        self.picam2 = None
        self.initialized = False
        self.streaming = False
        self.current_config = {}
        self.camera_properties = {}
        self.sensor_modes = []
        self.camera_status = check_camera_availability()
        
        # Frame buffer system attributes
        self._frame_buffer_lock = threading.Lock()
        self._main_frame_buffer = None
        self._lores_frame_buffer = None
        self._metadata_buffer = {}
        self._capture_thread = None
        self._capture_running = False
        self._capture_interval = 0.1  # 10 FPS
        
        # Performance tracking attributes
        self.frame_count = 0
        self.average_fps = 0.0
        self._frame_timestamps = []
        self._last_capture_time = time.time()
        self._last_fps_update = time.time()
        self._frame_count_since_update = 0
        
        # Camera connection retry settings
        self.connection_retry_count = 0
        self.max_retry_attempts = 5
        self.retry_delay = 2.0  # seconds
        
        self.logger.info("CameraHandler Singleton initialized")
        self.logger.info(f"Camera status: {self.camera_status}")
        
        self._initialized = True
    
    def _start_frame_capture_thread(self):
        """
        Start the frame capture thread that continuously captures frames.
        This eliminates concurrent access issues by having a single capture point.
        """
        if self._capture_thread and self._capture_thread.is_alive():
            self.logger.info("Frame capture thread already running")
            return True
        
        if not self.streaming or not self.picam2:
            self.logger.error("Cannot start capture thread - camera not streaming")
            return False
        
        self._capture_running = True
        self._capture_thread = threading.Thread(target=self._frame_capture_loop, daemon=True)
        self._capture_thread.start()
        self.logger.info("Frame capture thread started")
        return True
    
    def _stop_frame_capture_thread(self):
        """Stop the frame capture thread."""
        self._capture_running = False
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=2.0)
            self.logger.info("Frame capture thread stopped")
    
    def _frame_capture_loop(self):
        """
        Continuous frame capture loop for both main and lores streams.
        Captures frames and metadata in a single thread to avoid concurrent access.
        """
        self.logger.info("Starting frame capture loop")
        
        # Initialize frame timestamp tracking
        self._frame_timestamps = []
        self._last_capture_time = time.time()
        
        while self._capture_running:
            try:
                # Capture main frame and metadata
                main_frame_data = self._capture_main_frame_with_metadata()
                if main_frame_data:
                    with self._frame_buffer_lock:
                        self._main_frame_buffer = main_frame_data['frame']
                        self._metadata_buffer = main_frame_data['metadata']
                        self._last_capture_time = time.time()
                        
                        # Track frame timestamps for performance metrics
                        if main_frame_data['metadata'] and 'sensor_timestamp' in main_frame_data['metadata']:
                            self._frame_timestamps.append(main_frame_data['metadata']['sensor_timestamp'])
                            # Keep only last 100 timestamps to prevent memory growth
                            if len(self._frame_timestamps) > 100:
                                self._frame_timestamps = self._frame_timestamps[-100:]
                
                # Capture lores frame
                lores_frame = self._capture_lores_frame()
                if lores_frame is not None:
                    with self._frame_buffer_lock:
                        self._lores_frame_buffer = lores_frame
                
                # Update frame count and FPS
                self.frame_count += 1
                self._update_fps()
                
                # Sleep to control capture rate
                time.sleep(self._capture_interval)
                
            except Exception as e:
                self.logger.error(f"Error in frame capture loop: {e}")
                time.sleep(0.1)  # Brief pause on error
        
        self.logger.info("Frame capture loop stopped")
    
    def get_main_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest main stream frame from buffer.
        Thread-safe access to main stream for detection processing.
        
        Returns:
            Optional[np.ndarray]: Latest main frame or None
        """
        with self._frame_buffer_lock:
            if self._main_frame_buffer is not None:
                return self._main_frame_buffer.copy()
        return None
    
    def get_lores_frame(self) -> Optional[np.ndarray]:
        """
        Get the latest lores stream frame from buffer.
        Thread-safe access to lores stream for web interface.
        
        Returns:
            Optional[np.ndarray]: Latest lores frame or None
        """
        with self._frame_buffer_lock:
            if self._lores_frame_buffer is not None:
                return self._lores_frame_buffer.copy()
        return None
    
    def get_cached_metadata(self) -> Dict[str, Any]:
        """
        Get the latest metadata from buffer.
        Thread-safe access to metadata for status reporting.
        
        Returns:
            Dict[str, Any]: Latest metadata
        """
        with self._frame_buffer_lock:
            return self._metadata_buffer.copy()
    
    def is_frame_buffer_ready(self) -> bool:
        """
        Check if frame buffers have data.
        
        Returns:
            bool: True if buffers have frames, False otherwise
        """
        with self._frame_buffer_lock:
            return self._main_frame_buffer is not None and self._lores_frame_buffer is not None
    
    def try_connect_camera(self) -> bool:
        """
        Try to connect to camera if it becomes available.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        if self.connection_retry_count >= self.max_retry_attempts:
            self.logger.warning(f"Max retry attempts ({self.max_retry_attempts}) reached")
            return False
        
        self.connection_retry_count += 1
        self.logger.info(f"Attempting camera connection (attempt {self.connection_retry_count}/{self.max_retry_attempts})")
        
        # Check if camera is now available
        self.camera_status = check_camera_availability()
        
        if self.camera_status['camera_ready']:
            self.logger.info("Camera is now available - attempting to initialize")
            return self.initialize_camera()
        else:
            self.logger.info(f"Camera not ready yet - will retry in {self.retry_delay} seconds")
            return False
    
    def get_camera_status(self) -> Dict[str, Any]:
        """
        Get current camera status and availability.
        
        Returns:
            Dict: Camera status information
        """
        return {
            'initialized': self.initialized,
            'streaming': self.streaming,
            'camera_ready': self.camera_status['camera_ready'],
            'hardware_available': self.camera_status['hardware_available'],
            'software_available': self.camera_status['software_available'],
            'picamera2_available': self.camera_status['picamera2_available'],
            'libcamera_available': self.camera_status['libcamera_available'],
            'connection_retry_count': self.connection_retry_count,
            'max_retry_attempts': self.max_retry_attempts,
            'details': self.camera_status['details']
        }
    
    def initialize_camera(self) -> bool:
        """
        Initialize the camera with default configuration.
        Based on v1_2 successful implementation with Singleton protection and safe access.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        def _initialize_camera_internal():
                if self.initialized:
                    self.logger.warning("Camera already initialized (Singleton protection)")
                    return True
                
                # Clean up any existing camera instances first
                self._cleanup_existing_picamera2()
                
                # If camera exists, deactivate and re-initialize
                if self.picam2:
                    self.logger.info("Deactivating existing camera instance for re-initialization...")
                    try:
                        if self.picam2.started:
                            self.picam2.stop()
                        self.picam2.close()
                    except:
                        pass
                    self.picam2 = None
                    self.initialized = False
                    time.sleep(1.0)  # Give more time to release resources
                
                self.logger.info("Initializing camera...")

                # Check camera availability first
                self.camera_status = check_camera_availability()
                self.logger.info(f"Camera availability status: {self.camera_status}")
                
                # If camera is not ready, try to initialize in fallback mode
                if not self.camera_status['camera_ready']:
                    self.logger.warning("Camera not ready - hardware or software not available")
                    self.logger.info("Camera handler will run in fallback mode - ready for dynamic connection")
                    
                    # Initialize in fallback mode - ready but not connected
                    self.initialized = True
                    self.picam2 = None
                    self.camera_properties = {}
                    self.sensor_modes = []
                    self.current_config = {}
                    
                    self.logger.info("Camera handler initialized in fallback mode")
                    return True

                # Guard: ensure device present and modules available
                if not (os.path.exists('/dev/video0') or os.path.exists('/dev/media0')):
                    self.logger.warning("No camera device found (/dev/video0 or /dev/media0). Skipping camera initialization.")
                    return False

                try:
                    from picamera2 import Picamera2
                except Exception as e:
                    self.logger.warning(f"Picamera2 not available: {e}. Running without camera.")
                    return False

                # Create Picamera2 instance
                self.picam2 = Picamera2()
                
                # Get camera properties (available before configuration)
                self.camera_properties = self.picam2.camera_properties
                self.sensor_modes = self.picam2.sensor_modes
                
                self.logger.info(f"Camera properties: {self.camera_properties}")
                self.logger.info(f"Available sensor modes: {len(self.sensor_modes)}")
                
                # Create video configuration optimized for ML detection
                # According to Picamera2 manual, use proper stream configuration
                from edge.src.core.config import MAIN_RESOLUTION, LORES_RESOLUTION
                main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}
                lores_config = {"size": LORES_RESOLUTION, "format": "RGB888"}  # Changed from XBGR8888 to RGB888 for consistency
                
                # Create configuration with proper stream setup
                config = self.picam2.create_video_configuration(
                    main=main_config, 
                    lores=lores_config, 
                    encode="lores"
                )
                
                # Configure camera (this sets up the camera but doesn't start it)
                self.picam2.configure(config)
                
                # Get initial configuration after configure()
                self.current_config = self.picam2.camera_configuration()
                
                # Camera is now configured but not started
                self.initialized = True
                self.logger.info("Camera configured successfully (not started yet)")
                
                return True
                
        return self.safe_camera_operation(_initialize_camera_internal)
    
    def start_camera(self) -> bool:
        """
        Start the camera streaming with Singleton protection and safe access.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        def _start_camera_internal():
                if not self.initialized:
                    self.logger.error("Camera not initialized")
                    return False
                
                if self.streaming:
                    self.logger.warning("Camera already streaming (Singleton protection)")
                    return True
                
                # Check if camera is being used by another process
                self.logger.info("Checking camera availability...")
                if self._is_camera_in_use():
                    self.logger.warning("Camera is in use by another process, attempting to release...")
                    import subprocess
                    subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], capture_output=True)
                    subprocess.run(['sudo', 'fuser', '-k', '/dev/video*'], capture_output=True)
                    if not self._release_camera_resources():
                        self.logger.warning("Failed to release camera resources, attempting hardware reset...")
                        if not self._reset_camera_hardware():
                            self.logger.error("Failed to reset camera hardware")
                            return False
                        else:
                            self.logger.info("Camera hardware reset successful")
                
                # Cleanup previous camera instance if already started
                if self.picam2 and getattr(self.picam2, 'started', False):
                    self.logger.info("Camera already started, stopping before restart")
                    try:
                        self.picam2.stop()
                        self.logger.info("Camera stopped successfully before restart")
                    except Exception as e:
                        self.logger.warning(f"Error stopping camera before restart: {e}")
                    try:
                        self.picam2.close()
                        self.logger.info("Camera closed successfully before restart")
                    except Exception as e:
                        self.logger.warning(f"Error closing camera before restart: {e}")
                    self.picam2 = None
                    self.initialized = False
                    time.sleep(1.0)  # Give more time to release resources
                
                self.logger.info("Starting camera...")
                try:
                    # According to Picamera2 manual, start() should be called after configure()
                    self.logger.info(f"Picam2 object: {self.picam2}")
                    self.logger.info(f"Picam2 started: {getattr(self.picam2, 'started', 'N/A')}")
                    self.logger.info(f"Picam2 is_open: {getattr(self.picam2, 'is_open', 'N/A')}")
                    
                    # Check if camera is properly configured before starting
                    if not self.picam2.camera_configuration():
                        self.logger.error("Camera not properly configured")
                        return False
                    
                    self.logger.info(f"About to call picam2.start() - picam2 object: {self.picam2}")
                    self.logger.info(f"Picam2 state before start: started={getattr(self.picam2, 'started', 'N/A')}, is_open={getattr(self.picam2, 'is_open', 'N/A')}")
                    
                    # Start the camera according to Picamera2 manual
                    self.picam2.start()
                    self.logger.info("Picamera2 start() completed successfully")
                    
                    # Verify camera is started
                    if not self.picam2.started:
                        self.logger.error("Camera start() called but not actually started")
                        return False
                    
                    self.streaming = True
                    self.logger.info("Streaming flag set to True")
                    
                    # Wait for camera to stabilize (based on v1_2)
                    time.sleep(0.5)
                    
                    # Apply basic camera controls (based on v1_2 approach)
                    try:
                        self.picam2.set_controls({
                            "Brightness": 0.0,
                            "Contrast": 1.0,
                            "Saturation": 1.0,
                            "Sharpness": 1.0
                        })
                        self.logger.info("Basic camera controls applied")
                    except Exception as e:
                        self.logger.warning(f"Failed to apply basic controls: {e}")
                    
                    self.logger.info("Camera started successfully")
                    
                    # Start frame capture thread for concurrent access
                    if self._start_frame_capture_thread():
                        self.logger.info("Frame capture thread started successfully")
                    else:
                        self.logger.warning("Failed to start frame capture thread")
                    
                    return True
                    
                except Exception as e:
                    self.logger.error(f"Failed to start picam2: {e}")
                    self.streaming = False
                    return False
        
        return self.safe_camera_operation(_start_camera_internal)
    
    def stop_camera(self) -> bool:
        """
        Stop the camera streaming.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.warning("Camera not streaming")
                    return True
                
                self.logger.info("Stopping camera...")
                
                # Stop frame capture thread first
                self._stop_frame_capture_thread()
                
                # Stop recording if active
                if self.recording:
                    self.stop_recording()
                
                self.picam2.stop()
                self.streaming = False
                
                self.logger.info("Camera stopped successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop camera: {e}")
            return False
    
    def close_camera(self) -> bool:
        """
        Close the camera and cleanup resources.
        
        Returns:
            bool: True if closed successfully, False otherwise
        """
        try:
            with self._lock:
                self.logger.info("Closing camera...")
                
                # Stop camera if streaming
                if self.streaming:
                    self.stop_camera()
                
                # Close Picamera2
                if self.picam2:
                    self.picam2.close()
                    self.picam2 = None
                
                self.initialized = False
                self.logger.info("Camera closed successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to close camera: {e}")
            return False
    
    def capture_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture a single frame with metadata using frame buffer.
        Thread-safe access to main stream for detection processing.
        
        Returns:
            Optional[Dict[str, Any]]: Frame data with metadata, None if failed
        """
        try:
            # Get frame from buffer instead of direct camera access
            frame = self.get_main_frame()
            if frame is None:
                self.logger.warning("No main frame available in buffer")
                return None
            
            # Get metadata from buffer
            metadata = self.get_cached_metadata()
            
            return {
                'frame': frame,
                'metadata': metadata,
                'timestamp': time.time(),
                'format': 'RGB888',
                'size': frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture frame from buffer: {e}")
            return None
    
    def capture_lores_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture a low-resolution frame optimized for web interface.
        Thread-safe access to lores stream using frame buffer.
        
        Returns:
            Optional[Dict[str, Any]]: Low-res frame data, None if failed
        """
        try:
            # Get frame from buffer instead of direct camera access
            frame = self.get_lores_frame()
            if frame is None:
                self.logger.warning("No lores frame available in buffer")
                return None
            
            # Get metadata from buffer
            metadata = self.get_cached_metadata()
            
            return {
                'frame': frame,
                'metadata': metadata,
                'timestamp': time.time(),
                'format': 'RGB888',  # Changed from XBGR8888 to RGB888 for consistency
                'size': frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture lores frame from buffer: {e}")
            return None
    
    def capture_ml_frame(self) -> Optional[Dict[str, Any]]:
        """
        Capture frame optimized for machine learning detection.
        Based on Picamera2 ML integration best practices.
        
        Returns:
            Optional[Dict[str, Any]]: ML-optimized frame data, None if failed
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        request = None
        try:
            # Capture both main and lores streams for ML processing
            request = self.picam2.capture_request()
            
            # Get main frame for high-quality detection
            main_frame = request.make_array("main")
            # Get lores frame for fast processing
            lores_frame = request.make_array("lores")
            metadata = request.get_metadata()
            request.release()
            request = None
            
            return {
                'main_frame': main_frame,
                'lores_frame': lores_frame,
                'metadata': make_json_serializable(metadata),
                'timestamp': time.time(),
                'main_format': 'RGB888',
                'lores_format': 'RGB888',  # Changed from XBGR8888 to RGB888 for consistency
                'main_size': main_frame.shape[:2],
                'lores_size': lores_frame.shape[:2]
            }
                
        except Exception as e:
            self.logger.error(f"Failed to capture ML frame: {e}")
            return None
        finally:
            if request:
                request.release()
    
    def debug_metadata_capture(self) -> Dict[str, Any]:
        """
        Debug method to check metadata capture step by step.
        
        Returns:
            Dict[str, Any]: Debug information about metadata capture
        """
        debug_info = {
            'camera_initialized': self.initialized,
            'camera_streaming': self.streaming,
            'picam2_exists': self.picam2 is not None,
            'picam2_started': getattr(self.picam2, 'started', False) if self.picam2 else False,
            'steps': {},
            'error': None
        }
        
        try:
            # Step 1: Check if camera is ready
            if not self.streaming or not self.picam2:
                debug_info['error'] = "Camera not streaming or not initialized"
                return debug_info
            
            debug_info['steps']['step1_camera_ready'] = True
            
            # Step 2: Check if picam2 is started
            if not getattr(self.picam2, 'started', False):
                debug_info['error'] = "Picam2 not started"
                return debug_info
            
            debug_info['steps']['step2_picam2_started'] = True
            
            # Step 3: Try to capture request
            request = None
            try:
                request = self.picam2.capture_request()
                debug_info['steps']['step3_capture_request'] = True
                debug_info['steps']['request_object'] = str(type(request))
            except Exception as e:
                debug_info['error'] = f"Failed to capture request: {e}"
                return debug_info
            
            # Step 4: Try to get metadata
            try:
                metadata = request.get_metadata()
                debug_info['steps']['step4_get_metadata'] = True
                debug_info['steps']['metadata_type'] = str(type(metadata))
                debug_info['steps']['metadata_keys'] = list(metadata.keys()) if metadata else []
            except Exception as e:
                debug_info['error'] = f"Failed to get metadata: {e}"
                request.release()
                return debug_info
            
            # Step 5: Extract specific metadata fields
            try:
                extracted_metadata = {
                    'frame_timestamp': metadata.get("SensorTimestamp"),
                    'exposure_time': metadata.get("ExposureTime"),
                    'analogue_gain': metadata.get("AnalogueGain"),
                    'digital_gain': metadata.get("DigitalGain"),
                    'total_gain': metadata.get("AnalogueGain", 1.0) * metadata.get("DigitalGain", 1.0),
                    'awb_gains': metadata.get("AwbGains"),
                    'colour_gains': metadata.get("ColourGains"),
                    'focus_fom': metadata.get("FocusFoM"),
                    'af_state': metadata.get("AfState"),
                    'lens_position': metadata.get("LensPosition"),
                    'frame_duration': metadata.get("FrameDuration"),
                    'sensor_timestamp': metadata.get("SensorTimestamp"),
                    'request_timestamp': metadata.get("RequestTimestamp"),
                    'complete_metadata': make_json_serializable(metadata)
                }
                debug_info['steps']['step5_extract_metadata'] = True
                debug_info['extracted_metadata'] = extracted_metadata
            except Exception as e:
                debug_info['error'] = f"Failed to extract metadata: {e}"
                request.release()
                return debug_info
            
            # Step 6: Release request
            try:
                request.release()
                debug_info['steps']['step6_release_request'] = True
            except Exception as e:
                debug_info['error'] = f"Failed to release request: {e}"
                return debug_info
            
            debug_info['success'] = True
            
        except Exception as e:
            debug_info['error'] = f"Unexpected error in debug_metadata_capture: {e}"
        
        return debug_info

    def get_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive camera metadata from Picamera2 during video streaming.
        Follows proper Picamera2 workflow: capture_request() -> get_metadata() -> release()
        
        Returns:
            Optional[Dict[str, Any]]: Complete camera metadata including exposure, gain, timestamp
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        if not getattr(self.picam2, 'started', False):
            self.logger.error("Picam2 not started - cannot capture metadata")
            return None
            
        request = None
        try:
            # Step 1: Capture request from streaming camera
            self.logger.debug("Capturing request from Picam2...")
            request = self.picam2.capture_request()
            
            if not request:
                self.logger.error("Failed to capture request - request is None")
                return None
            
            # Step 2: Extract metadata using get_metadata()
            self.logger.debug("Extracting metadata from request...")
            metadata = request.get_metadata()
            
            if not metadata:
                self.logger.error("Failed to get metadata - metadata is None")
                request.release()
                return None
            
            # Step 3: Release the request
            request.release()
            request = None
            
            # Step 4: Extract key metadata fields for OCR correlation
            extracted_metadata = {
                'frame_timestamp': metadata.get("SensorTimestamp"),
                'exposure_time': metadata.get("ExposureTime"),
                'analogue_gain': metadata.get("AnalogueGain"),
                'digital_gain': metadata.get("DigitalGain"),
                'total_gain': metadata.get("AnalogueGain", 1.0) * metadata.get("DigitalGain", 1.0),
                'awb_gains': metadata.get("AwbGains"),
                'colour_gains': metadata.get("ColourGains"),
                'focus_fom': metadata.get("FocusFoM"),
                'af_state': metadata.get("AfState"),
                'lens_position': metadata.get("LensPosition"),
                'frame_duration': metadata.get("FrameDuration"),
                'sensor_timestamp': metadata.get("SensorTimestamp"),
                'request_timestamp': metadata.get("RequestTimestamp"),
                'complete_metadata': make_json_serializable(metadata)
            }
            
            # Log key metadata for OCR correlation
            self.logger.debug(f"Frame metadata - Timestamp: {extracted_metadata['frame_timestamp']}, "
                            f"Exposure: {extracted_metadata['exposure_time']}, "
                            f"Gain: {extracted_metadata['analogue_gain']}")
            
            return extracted_metadata
                
        except Exception as e:
            self.logger.error(f"Failed to get metadata: {e}")
            return None
        finally:
            if request:
                try:
                    request.release()
                except:
                    pass
    
    def set_controls(self, controls: Dict[str, Any]) -> bool:
        """
        Set camera controls.
        
        Args:
            controls: Dictionary of control values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                self.picam2.set_controls(controls)
                self.logger.info(f"Set camera controls: {controls}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set controls: {e}")
            return False
    
    def get_controls(self) -> Dict[str, Any]:
        """
        Get available camera controls.
        
        Returns:
            Dict[str, Any]: Available controls
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {}
                
                return self.picam2.camera_controls
                
        except Exception as e:
            self.logger.error(f"Failed to get controls: {e}")
            return {}
    
    def start_recording(self, filename: str, bitrate: int = 10000000) -> bool:
        """
        Start video recording.
        
        Args:
            filename: Output filename
            bitrate: Video bitrate
            
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                if self.recording:
                    self.logger.warning("Already recording")
                    return True
                
                self.logger.info(f"Starting recording: {filename}")
                
                # Create encoder and start recording
                try:
                    from picamera2.encoders import H264Encoder
                except Exception as e:
                    self.logger.error(f"Failed to import H264Encoder: {e}")
                    return False
                self.recording_encoder = H264Encoder(bitrate)
                self.recording_file = filename
                
                self.picam2.start_recording(self.recording_encoder, filename)
                self.recording = True
                
                self.logger.info("Recording started successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            return False
    
    def stop_recording(self) -> bool:
        """
        Stop video recording.
        
        Returns:
            bool: True if stopped successfully, False otherwise
        """
        try:
            with self._lock:
                if not self.recording:
                    self.logger.warning("Not recording")
                    return True
                
                self.logger.info("Stopping recording...")
                
                self.picam2.stop_recording()
                self.recording = False
                self.recording_encoder = None
                self.recording_file = None
                
                self.logger.info("Recording stopped successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera handler status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            with self._lock:
                status = {
                    'initialized': self.initialized,
                    'streaming': self.streaming,
                    'recording': self.recording,
                    'camera_properties': make_json_serializable(self.camera_properties),
                    'sensor_modes_count': len(self.sensor_modes),
                    'current_config': make_json_serializable(self.current_config),
                    'frame_count': getattr(self, 'frame_count', 0),  # Add frame count
                    'average_fps': getattr(self, 'average_fps', 0.0),  # Add average FPS
                    'configuration': self.get_configuration()  # Add configuration
                }
                
                if self.recording:
                    status['recording_file'] = self.recording_file
                
                if self.streaming:
                    try:
                        metadata = self.get_metadata()
                        if metadata:
                            status['metadata'] = metadata
                    except:
                        pass
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Dict[str, Any]: Configuration information
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {}
                
                config = {}
                
                # Get current configuration from picam2
                if self.current_config:
                    config = make_json_serializable(self.current_config)
                
                # Add basic configuration info
                if self.camera_properties:
                    config['camera_properties'] = make_json_serializable(self.camera_properties)
                
                return config
                
        except Exception as e:
            self.logger.error(f"Failed to get configuration: {e}")
            return {}
    
    def _update_frame_stats(self):
        """Update frame count and FPS statistics."""
        import time
        
        current_time = time.time()
        self.frame_count += 1
        
        if self._last_frame_time is not None:
            frame_interval = current_time - self._last_frame_time
            if frame_interval > 0:
                fps = 1.0 / frame_interval
                self._fps_samples.append(fps)
                
                # Keep only recent samples
                if len(self._fps_samples) > self._max_fps_samples:
                    self._fps_samples.pop(0)
                
                # Calculate average FPS
                if self._fps_samples:
                    self.average_fps = sum(self._fps_samples) / len(self._fps_samples)
        
        self._last_frame_time = current_time
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Dict[str, Any]: Current configuration
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {}
            
                # Get raw configuration and make it JSON serializable
                raw_config = self.picam2.camera_configuration()
                return make_json_serializable(raw_config)
            
        except Exception as e:
            self.logger.error(f"Failed to get configuration: {e}")
            return {}
    
    def update_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Update camera configuration.
        
        Args:
            config: New configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.initialized:
                    self.logger.error("Camera not initialized")
                    return False
            
                # Stop camera if streaming
                was_streaming = self.streaming
                if was_streaming:
                    self.logger.info("Stopping camera for configuration update...")
                    self.stop_camera()
                
                # Apply new configuration
                self.logger.info("Applying new camera configuration...")
                self.picam2.configure(config)
                self.current_config = self.picam2.camera_configuration()
                
                # Always restart camera after configuration update
                self.logger.info("Restarting camera with new configuration...")
                restart_success = self.start_camera()
                
                if restart_success:
                    self.logger.info("Configuration updated and camera restarted successfully")
                    return True
                else:
                    self.logger.error("Configuration updated but failed to restart camera")
                    return False
                
        except Exception as e:
            self.logger.error(f"Failed to update configuration: {e}")
            return False
    
    def autofocus_cycle(self) -> bool:
        """
        Perform autofocus cycle.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                self.logger.info("Starting autofocus cycle...")
                success = self.picam2.autofocus_cycle()
                
                if success:
                    self.logger.info("Autofocus cycle completed successfully")
                else:
                    self.logger.warning("Autofocus cycle failed")
                
                return success
                
        except Exception as e:
            self.logger.error(f"Failed to perform autofocus cycle: {e}")
            return False
    
    def set_autofocus_mode(self, mode: str) -> bool:
        """
        Set autofocus mode.
        
        Args:
            mode: Autofocus mode ('Manual', 'Auto', 'Continuous')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self._lock:
                if not self.streaming:
                    self.logger.error("Camera not streaming")
                    return False
                
                try:
                    from libcamera import controls as lc_controls
                except Exception as e:
                    self.logger.error(f"libcamera controls not available: {e}")
                    return False

                mode_map = {
                    'Manual': lc_controls.AfModeEnum.Manual,
                    'Auto': lc_controls.AfModeEnum.Auto,
                    'Continuous': lc_controls.AfModeEnum.Continuous
                }
                
                if mode not in mode_map:
                    self.logger.error(f"Invalid autofocus mode: {mode}")
                    return False
                
                self.picam2.set_controls({"AfMode": mode_map[mode]})
                self.logger.info(f"Set autofocus mode: {mode}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to set autofocus mode: {e}")
            return False
    
    def _cleanup_existing_picamera2(self):
        """
        Clean up any existing Picamera2 instances that might be holding resources.
        """
        try:
            self.logger.info("Attempting to cleanup existing Picamera2 instances...")
            
            # Check for Python processes that might be holding camera
            import subprocess
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'python' in line.lower() and ('picamera' in line.lower() or 'aicamera' in line.lower()):
                        self.logger.info(f"Found potential camera process: {line.strip()}")
            
            # Try to kill any processes using camera devices
            if self._is_camera_in_use():
                self.logger.warning("Camera devices in use, attempting to kill processes...")
                subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], 
                             capture_output=True, timeout=10)
                subprocess.run(['sudo', 'fuser', '-k', '/dev/video*'], 
                             capture_output=True, timeout=10)
                time.sleep(2)  # Wait for processes to be killed
                
        except Exception as e:
            self.logger.error(f"Error during Picamera2 cleanup: {e}")
    
    def _is_camera_in_use(self) -> bool:
        """
        Check if camera is being used by another process.
        
        Returns:
            bool: True if camera is in use, False otherwise
        """
        try:
            import subprocess
            import os
            
            # Check if media devices are being used
            result = subprocess.run(['sudo', 'fuser', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                # Parse PIDs that are using media devices
                pids = set()
                for line in result.stdout.split():
                    if line.isdigit():
                        pids.add(int(line))
                
                # Remove our own process from the list
                current_pid = os.getpid()
                pids.discard(current_pid)
                
                if pids:
                    self.logger.info(f"Camera in use by PIDs: {pids}")
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking camera usage: {e}")
            return False
    
    def _release_camera_resources(self) -> bool:
        """
        Release camera resources by stopping other processes.
        
        Returns:
            bool: True if resources released successfully, False otherwise
        """
        try:
            import subprocess
            import time
            
            self.logger.info("Attempting to release camera resources...")
            
            # First, try to gracefully stop other camera processes
            result = subprocess.run(['sudo', 'fuser', '-k', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                self.logger.info("Sent SIGKILL to processes using camera")
                time.sleep(2)  # Wait for processes to terminate
                
                # Check if camera is still in use
                if not self._is_camera_in_use():
                    self.logger.info("Camera resources released successfully")
                    return True
                else:
                    self.logger.warning("Camera still in use after SIGKILL")
            
            # If graceful termination failed, try force kill
            self.logger.info("Attempting force kill of camera processes...")
            result = subprocess.run(['sudo', 'fuser', '-9', '/dev/media*'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                time.sleep(3)  # Wait longer for force kill
                
                if not self._is_camera_in_use():
                    self.logger.info("Camera resources released with force kill")
                    return True
            
            self.logger.error("Failed to release camera resources")
            return False
            
        except Exception as e:
            self.logger.error(f"Error releasing camera resources: {e}")
            return False
    
    def _reset_camera_hardware(self) -> bool:
        """
        Reset camera hardware by unloading and reloading modules.
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            import subprocess
            import time
            
            self.logger.info("Attempting to reset camera hardware...")
            
            # Unload camera modules
            modules_to_unload = ['bcm2835-v4l2', 'imx708']
            for module in modules_to_unload:
                try:
                    subprocess.run(['sudo', 'modprobe', '-r', module], 
                                 capture_output=True, timeout=5)
                    self.logger.info(f"Unloaded module: {module}")
                except:
                    pass  # Module might not be loaded
            
            time.sleep(2)
            
            # Reload camera modules
            for module in reversed(modules_to_unload):
                try:
                    subprocess.run(['sudo', 'modprobe', module], 
                                 capture_output=True, timeout=5)
                    self.logger.info(f"Reloaded module: {module}")
                except:
                    pass
            
            time.sleep(3)  # Wait for modules to initialize
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting camera hardware: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get camera handler status.
        
        Returns:
            Dict[str, Any]: Status information
        """
        try:
            with self._lock:
                status = {
                    'initialized': self.initialized,
                    'streaming': self.streaming,
                    'camera_ready': self.camera_status['camera_ready'],
                    'hardware_available': self.camera_status['hardware_available'],
                    'software_available': self.camera_status['software_available'],
                    'picamera2_available': self.camera_status['picamera2_available'],
                    'libcamera_available': self.camera_status['libcamera_available'],
                    'camera_properties': make_json_serializable(self.camera_properties),
                    'sensor_modes_count': len(self.sensor_modes),
                    'current_config': make_json_serializable(self.current_config),
                    'connection_retry_count': self.connection_retry_count,
                    'max_retry_attempts': self.max_retry_attempts,
                    'details': self.camera_status['details']
                }
                
                return status
                
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def get_configuration(self) -> Dict[str, Any]:
        """
        Get current camera configuration.
        
        Returns:
            Dict[str, Any]: Configuration information
        """
        try:
            with self._lock:
                if not self.initialized:
                    return {
                        'initialized': False,
                        'streaming': False,
                        'error': 'Camera not initialized'
                    }
                
                # Get the actual camera configuration
                config = make_json_serializable(self.current_config)
                
                # Add camera properties and status
                config.update({
                    'initialized': self.initialized,
                    'streaming': self.streaming,
                    'camera_properties': make_json_serializable(self.camera_properties),
                    'sensor_modes_count': len(self.sensor_modes),
                    'camera_status': self.camera_status
                })
                
                return config
                
        except Exception as e:
            self.logger.error(f"Failed to get configuration: {e}")
            return {
                'initialized': False,
                'streaming': False,
                'error': str(e)
            }
    
    def get_comprehensive_metadata(self) -> Dict[str, Any]:
        """
        Get comprehensive camera metadata optimized for experimental efficiency.
        Provides detailed information for image processing experiments and analysis.
        
        Returns:
            Dict[str, Any]: Comprehensive metadata with experimental data
        """
        if not self.streaming or not self.picam2:
            self.logger.error("Camera not streaming or not initialized")
            return None
            
        if not getattr(self.picam2, 'started', False):
            self.logger.error("Picam2 not started - cannot capture metadata")
            return None
            
        request = None
        try:
            # Capture request from streaming camera
            request = self.picam2.capture_request()
            
            if not request:
                self.logger.error("Failed to capture request - request is None")
                return None
            
            # Extract complete metadata
            metadata = request.get_metadata()
            
            if not metadata:
                self.logger.error("Failed to get metadata - metadata is None")
                request.release()
                return None
            
            # Release the request
            request.release()
            request = None
            
            # Comprehensive metadata extraction for experiments
            comprehensive_metadata = {
                # Timing Information
                'timing': {
                    'frame_timestamp': metadata.get("SensorTimestamp"),
                    'sensor_timestamp': metadata.get("SensorTimestamp"),
                    'request_timestamp': metadata.get("RequestTimestamp"),
                    'frame_duration': metadata.get("FrameDuration"),
                    'exposure_time': metadata.get("ExposureTime"),
                    'timestamp_ns': metadata.get("SensorTimestamp"),
                    'timestamp_ms': metadata.get("SensorTimestamp", 0) / 1000000 if metadata.get("SensorTimestamp") else 0,
                    'capture_latency': time.time() * 1000000 - metadata.get("SensorTimestamp", 0) if metadata.get("SensorTimestamp") else 0
                },
                
                # Exposure and Gain Information
                'exposure': {
                    'exposure_time': metadata.get("ExposureTime"),
                    'exposure_time_ms': metadata.get("ExposureTime", 0) / 1000 if metadata.get("ExposureTime") else 0,
                    'analogue_gain': metadata.get("AnalogueGain"),
                    'digital_gain': metadata.get("DigitalGain"),
                    'total_gain': metadata.get("AnalogueGain", 1.0) * metadata.get("DigitalGain", 1.0),
                    'gain_db': 20 * np.log10(metadata.get("AnalogueGain", 1.0) * metadata.get("DigitalGain", 1.0)),
                    'exposure_index': metadata.get("ExposureTime", 0) * metadata.get("AnalogueGain", 1.0) * metadata.get("DigitalGain", 1.0) / 1000
                },
                
                # Color and White Balance
                'color': {
                    'awb_gains': metadata.get("AwbGains"),
                    'colour_gains': metadata.get("ColourGains"),
                    'color_temperature': self._estimate_color_temperature(metadata.get("AwbGains")),
                    'red_gain': metadata.get("AwbGains", [1.0, 1.0])[0] if metadata.get("AwbGains") else 1.0,
                    'blue_gain': metadata.get("AwbGains", [1.0, 1.0])[1] if metadata.get("AwbGains") else 1.0,
                    'green_gain': 1.0,  # Reference gain
                    'wb_ratio': metadata.get("AwbGains", [1.0, 1.0])[0] / metadata.get("AwbGains", [1.0, 1.0])[1] if metadata.get("AwbGains") and len(metadata.get("AwbGains")) >= 2 else 1.0
                },
                
                # Focus and Lens Information
                'focus': {
                    'focus_fom': metadata.get("FocusFoM"),
                    'af_state': metadata.get("AfState"),
                    'lens_position': metadata.get("LensPosition"),
                    'focus_distance': self._estimate_focus_distance(metadata.get("LensPosition")),
                    'focus_confidence': metadata.get("FocusFoM", 0) / 1000 if metadata.get("FocusFoM") else 0,
                    'autofocus_active': metadata.get("AfState") in [1, 2, 3] if metadata.get("AfState") is not None else False
                },
                
                # Sensor Information
                'sensor': {
                    'sensor_id': metadata.get("SensorId"),
                    'sensor_mode': metadata.get("SensorMode"),
                    'sensor_timestamp': metadata.get("SensorTimestamp"),
                    'sensor_line_length': metadata.get("SensorLineLength"),
                    'sensor_frame_length': metadata.get("SensorFrameLength"),
                    'sensor_exposure_time': metadata.get("SensorExposureTime")
                },
                
                # Image Quality Metrics
                'quality': {
                    'sharpness': metadata.get("Sharpness"),
                    'contrast': metadata.get("Contrast"),
                    'brightness': metadata.get("Brightness"),
                    'saturation': metadata.get("Saturation"),
                    'noise_reduction': metadata.get("NoiseReduction"),
                    'dynamic_range': self._estimate_dynamic_range(metadata.get("ExposureTime"), metadata.get("AnalogueGain")),
                    'signal_to_noise': self._estimate_snr(metadata.get("ExposureTime"), metadata.get("AnalogueGain"))
                },
                
                # Performance Metrics
                'performance': {
                    'frame_count': self.frame_count,
                    'average_fps': self.average_fps,
                    'buffer_ready': self.is_frame_buffer_ready(),
                    'main_frame_available': self.get_main_frame() is not None,
                    'lores_frame_available': self.get_lores_frame() is not None,
                    'capture_thread_active': self._capture_running,
                    'buffer_latency': self._calculate_buffer_latency()
                },
                
                # Camera Properties
                'camera_properties': {
                    'model': self.camera_properties.get('Model'),
                    'location': self.camera_properties.get('Location'),
                    'rotation': self.camera_properties.get('Rotation'),
                    'pixel_array_size': self.camera_properties.get('PixelArraySize'),
                    'unit_cell_size': self.camera_properties.get('UnitCellSize'),
                    'color_filter_arrangement': self.camera_properties.get('ColorFilterArrangement')
                },
                
                # Current Configuration
                'configuration': {
                    'resolution': self.current_config.get('main', {}).get('size'),
                    'format': self.current_config.get('main', {}).get('format'),
                    'framerate': self._calculate_framerate(),
                    'buffer_count': self.current_config.get('buffer_count'),
                    'use_case': self.current_config.get('use_case'),
                    'transform': str(self.current_config.get('transform')),
                    'colour_space': str(self.current_config.get('colour_space'))
                },
                
                # Experimental Data
                'experimental': {
                    'lighting_condition': self._classify_lighting_condition(metadata),
                    'motion_detected': self._detect_motion(),
                    'image_stability': self._calculate_image_stability(),
                    'exposure_adequacy': self._assess_exposure_adequacy(metadata),
                    'focus_quality': self._assess_focus_quality(metadata),
                    'noise_level': self._estimate_noise_level(metadata),
                    'dynamic_range_utilization': self._calculate_dr_utilization(metadata)
                },
                
                # Raw Metadata (for advanced analysis)
                'raw_metadata': make_json_serializable(metadata),
                
                # Metadata Collection Info
                'metadata_info': {
                    'collection_time': time.time(),
                    'collection_method': 'comprehensive_experimental',
                    'version': '2.0',
                    'source': 'camera_handler'
                }
            }
            
            return comprehensive_metadata
                
        except Exception as e:
            self.logger.error(f"Failed to get comprehensive metadata: {e}")
            return None
        finally:
            if request:
                try:
                    request.release()
                except:
                    pass

    def _estimate_color_temperature(self, awb_gains) -> float:
        """Estimate color temperature from AWB gains."""
        if not awb_gains or len(awb_gains) < 2:
            return 5500.0  # Default daylight temperature
        
        red_gain, blue_gain = awb_gains[0], awb_gains[1]
        if red_gain <= 0 or blue_gain <= 0:
            return 5500.0
        
        # Simple estimation based on gain ratio
        ratio = red_gain / blue_gain
        if ratio > 1.5:
            return 3000.0  # Warm light
        elif ratio < 0.7:
            return 7500.0  # Cool light
        else:
            return 5500.0  # Neutral light

    def _estimate_focus_distance(self, lens_position) -> float:
        """Estimate focus distance from lens position."""
        if lens_position is None:
            return 0.0
        
        # Simple linear estimation (would need calibration for accuracy)
        # Assuming lens_position 0 = infinity, 1000 = closest focus
        if lens_position == 0:
            return float('inf')
        else:
            return 1000.0 / lens_position if lens_position > 0 else 0.0

    def _estimate_dynamic_range(self, exposure_time, analogue_gain) -> float:
        """Estimate dynamic range based on exposure and gain."""
        if not exposure_time or not analogue_gain:
            return 10.0  # Default DR in stops
        
        # Simplified DR estimation
        base_dr = 10.0  # Base DR for sensor
        gain_factor = np.log2(analogue_gain) if analogue_gain > 0 else 0
        exposure_factor = np.log2(exposure_time / 1000) if exposure_time > 0 else 0
        
        return max(6.0, base_dr - gain_factor + exposure_factor)

    def _estimate_snr(self, exposure_time, analogue_gain) -> float:
        """Estimate signal-to-noise ratio."""
        if not exposure_time or not analogue_gain:
            return 20.0  # Default SNR in dB
        
        # Simplified SNR estimation
        signal = exposure_time * analogue_gain
        noise = np.sqrt(exposure_time * analogue_gain**2)
        
        if noise > 0:
            return 20 * np.log10(signal / noise)
        return 20.0

    def _calculate_framerate(self) -> float:
        """Calculate actual framerate from frame timing."""
        if not hasattr(self, '_frame_timestamps') or len(self._frame_timestamps) < 2:
            return self.average_fps
        
        recent_timestamps = self._frame_timestamps[-10:]  # Last 10 frames
        if len(recent_timestamps) < 2:
            return self.average_fps
        
        intervals = [recent_timestamps[i] - recent_timestamps[i-1] for i in range(1, len(recent_timestamps))]
        avg_interval = np.mean(intervals)
        
        if avg_interval > 0:
            return 1000000.0 / avg_interval  # Convert microseconds to FPS
        return self.average_fps

    def _calculate_buffer_latency(self) -> float:
        """Calculate buffer latency in milliseconds."""
        if not hasattr(self, '_last_capture_time'):
            return 0.0
        
        return (time.time() - self._last_capture_time) * 1000

    def _classify_lighting_condition(self, metadata) -> str:
        """Classify lighting condition based on exposure and gain."""
        exposure_time = metadata.get("ExposureTime", 0)
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        
        if exposure_time < 1000 and analogue_gain < 2.0:
            return "bright"
        elif exposure_time > 10000 or analogue_gain > 4.0:
            return "low_light"
        else:
            return "normal"

    def _detect_motion(self) -> bool:
        """Detect motion based on frame differences."""
        # This would require frame comparison - simplified for now
        return False

    def _calculate_image_stability(self) -> float:
        """Calculate image stability score."""
        # This would require frame analysis - simplified for now
        return 0.95  # High stability

    def _assess_exposure_adequacy(self, metadata) -> str:
        """Assess if exposure is adequate."""
        exposure_time = metadata.get("ExposureTime", 0)
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        
        if exposure_time < 500:
            return "overexposed"
        elif exposure_time > 20000 or analogue_gain > 8.0:
            return "underexposed"
        else:
            return "adequate"

    def _assess_focus_quality(self, metadata) -> str:
        """Assess focus quality."""
        focus_fom = metadata.get("FocusFoM", 0)
        
        if focus_fom > 800:
            return "excellent"
        elif focus_fom > 600:
            return "good"
        elif focus_fom > 400:
            return "fair"
        else:
            return "poor"

    def _estimate_noise_level(self, metadata) -> str:
        """Estimate noise level."""
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        
        if analogue_gain < 2.0:
            return "low"
        elif analogue_gain < 4.0:
            return "moderate"
        else:
            return "high"

    def _calculate_dr_utilization(self, metadata) -> float:
        """Calculate dynamic range utilization percentage."""
        exposure_time = metadata.get("ExposureTime", 0)
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        
        # Simplified calculation
        exposure_factor = min(1.0, exposure_time / 10000)
        gain_factor = min(1.0, analogue_gain / 4.0)
        
        return (exposure_factor + gain_factor) / 2 * 100

    def _capture_main_frame_with_metadata(self) -> Optional[Dict[str, Any]]:
        """
        Capture main frame with metadata in a single request.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary with 'frame' and 'metadata' keys
        """
        if not self.streaming or not self.picam2 or not self.picam2.started:
            return None
        
        request = None
        try:
            request = self.picam2.capture_request()
            if not request:
                return None
            
            # Get main stream frame
            main_frame = request.make_array("main")
            if main_frame is None:
                return None
            
            # Get metadata
            metadata = request.get_metadata()
            if metadata:
                metadata = make_json_serializable(metadata)
            
            return {
                'frame': main_frame.copy(),
                'metadata': metadata
            }
            
        except Exception as e:
            self.logger.error(f"Error capturing main frame with metadata: {e}")
            return None
        finally:
            if request:
                try:
                    request.release()
                except:
                    pass

    def _capture_lores_frame(self) -> Optional[np.ndarray]:
        """
        Capture lores frame for video streaming.
        
        Returns:
            Optional[np.ndarray]: Lores frame data
        """
        if not self.streaming or not self.picam2 or not self.picam2.started:
            return None
        
        request = None
        try:
            request = self.picam2.capture_request()
            if not request:
                return None
            
            # Get lores stream frame
            lores_frame = request.make_array("lores")
            if lores_frame is None:
                return None
            
            return lores_frame.copy()
            
        except Exception as e:
            self.logger.error(f"Error capturing lores frame: {e}")
            return None
        finally:
            if request:
                try:
                    request.release()
                except:
                    pass

    def _update_fps(self):
        """Update average FPS calculation."""
        current_time = time.time()
        if hasattr(self, '_last_fps_update'):
            time_diff = current_time - self._last_fps_update
            if time_diff >= 1.0:  # Update every second
                if hasattr(self, '_frame_count_since_update'):
                    self.average_fps = self._frame_count_since_update / time_diff
                    self._frame_count_since_update = 0
                    self._last_fps_update = current_time
                else:
                    self._frame_count_since_update = 0
                    self._last_fps_update = current_time
        else:
            self._last_fps_update = current_time
            self._frame_count_since_update = 0
        
        if hasattr(self, '_frame_count_since_update'):
            self._frame_count_since_update += 1
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            with self._lock:
                self.logger.info("Cleaning up camera handler...")
                self.close_camera()
                self.logger.info("Camera handler cleanup completed")
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    @classmethod
    def reset_instance(cls):
        """Reset the Singleton instance (for testing/debugging)."""
        with cls._lock:
            if cls._instance:
                cls._instance.cleanup()
                cls._instance = None
                cls._initialized = False
                logger.info("CameraHandler Singleton instance reset")
    
    @classmethod
    def get_instance(cls, **kwargs):
        """Get the Singleton instance."""
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    def safe_camera_operation(self, operation_func):
        """
        Execute camera operations safely with proper error handling and resource management.
        
        This method provides:
        - Thread-safe camera access using locks
        - Proper error handling and recovery
        - Resource cleanup on failure
        - Logging of operation results
        
        Args:
            operation_func: Function to execute (should be a lambda or inner function)
            
        Returns:
            bool: True if operation successful, False otherwise
        """
        try:
            # Acquire camera access lock for thread safety
            with self._lock:
                self.logger.debug("Acquired camera access lock")
                
                # Execute the operation
                result = operation_func()
                
                self.logger.debug(f"Camera operation completed with result: {result}")
                return result
                
        except Exception as e:
            self.logger.error(f"Camera operation failed: {e}")
            
            # Attempt to recover from failure
            try:
                self.logger.info("Attempting camera operation recovery...")
                
                # Reset camera state on failure
                self.initialized = False
                self.streaming = False
                
                # Clean up any existing camera resources
                if self.picam2:
                    try:
                        if getattr(self.picam2, 'started', False):
                            self.picam2.stop()
                        self.picam2.close()
                    except:
                        pass
                    self.picam2 = None
                
                self.logger.info("Camera operation recovery completed")
                
            except Exception as recovery_error:
                self.logger.error(f"Camera operation recovery failed: {recovery_error}")
            
            return False