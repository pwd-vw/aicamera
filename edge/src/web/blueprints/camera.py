#!/usr/bin/env python3
"""
Camera Blueprint for AI Camera v2.0.0

This blueprint provides camera control and video streaming functionality:
- Video streaming endpoints
- Camera configuration management
- Camera status monitoring
- WebSocket events for real-time updates
- Auto-start status display

Author: AI Camera Team
Version: 2.0.0
Date: August 23, 2025
"""

import cv2
import numpy as np
import json
import time
from datetime import datetime
from flask import Blueprint, render_template, jsonify, request, Response, current_app
from flask_socketio import emit, join_room, leave_room

# Use absolute imports
from edge.src.core.dependency_container import get_service
from edge.src.core.utils.logging_config import get_logger
from edge.src.components.camera_handler import make_json_serializable

# Create blueprint
camera_bp = Blueprint('camera', __name__, url_prefix='/camera')

logger = get_logger(__name__)


@camera_bp.route('/')
def camera_dashboard():
    """
    Camera dashboard page with auto-start status.
    
    Returns:
        str: Rendered HTML template
    """
    try:
        camera_manager = get_service('camera_manager')
        camera_status = camera_manager.get_status() if camera_manager else {}
        camera_settings = camera_manager.get_available_settings() if camera_manager else {}
        
        # Add auto-start information to template context
        auto_start_info = {
            'enabled': camera_status.get('auto_start_enabled', False),
            'uptime': camera_status.get('uptime', 0)
        }
        
        return render_template('camera/dashboard.html',
                             camera_status=camera_status,
                             camera_settings=camera_settings,
                             auto_start_info=auto_start_info,
                             title="Camera Dashboard",
                             timestamp=int(time.time()))
    except Exception as e:
        logger.error(f"Error in camera dashboard: {e}")
        return render_template('camera/dashboard.html',
                             camera_status={},
                             camera_settings={},
                             auto_start_info={'enabled': False, 'uptime': 0},
                             title="Camera Dashboard",
                             timestamp=int(time.time()))


@camera_bp.route('/status')
def get_camera_status():
    """
    Get current camera status including auto-start information.
    
    Returns:
        dict: JSON response with camera status
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        status = camera_manager.get_status()
        
        # Ensure all status data is JSON serializable
        serializable_status = make_json_serializable(status)
        
        return jsonify({
            'success': True,
            'status': serializable_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting camera status: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/start', methods=['POST'])
def start_camera():
    """
    Start camera streaming (manual start).
    
    Returns:
        dict: JSON response with start result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.start()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera started successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error starting camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/stop', methods=['POST'])
def stop_camera():
    """
    Stop camera streaming.
    
    Returns:
        dict: JSON response with stop result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.stop()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera stopped successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to stop camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error stopping camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/restart', methods=['POST'])
def restart_camera():
    """
    Restart camera.
    
    Returns:
        dict: JSON response with restart result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        success = camera_manager.restart()
        if success:
            return jsonify({
                'success': True,
                'message': 'Camera restarted successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to restart camera',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error restarting camera: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/config', methods=['GET', 'POST'])
def camera_config():
    """
    Camera configuration management.
    
    Returns:
        dict: JSON response with configuration data
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        if request.method == 'GET':
            # Get current configuration
            config = camera_manager.get_configuration()
            
            return jsonify({
                'success': True,
                'config': config,
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Update configuration
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No configuration data provided'}), 400
            
            result = camera_manager.update_configuration(data)
            
            return jsonify({
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'error': result.get('error', ''),
                'timestamp': datetime.now().isoformat()
            })
    except Exception as e:
        logger.error(f"Error in camera config: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/capture', methods=['POST'])
def capture_image():
    """
    Capture a single image.
    
    Returns:
        dict: JSON response with capture result
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        image_data = camera_manager.capture_image()
        if image_data:
            return jsonify({
                'success': True,
                'message': 'Image captured successfully',
                'image_path': image_data.get('saved_path'),
                'size': image_data.get('size'),
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to capture image',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error capturing image: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/health')
def camera_health():
    """
    Camera health check endpoint.
    
    Returns:
        dict: JSON response with health status
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        health = camera_manager.health_check()
        
        return jsonify({
            'success': True,
            'health': health,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error in camera health check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def generate_frames():
    """
    Generate video frames for streaming using camera manager data.
    Implements comprehensive error handling with retry mechanisms and graceful degradation.
    
    Yields:
        bytes: Frame data in multipart format
    """
    # Error handling configuration
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1.0  # seconds
    ERROR_FRAME_INTERVAL = 2.0  # seconds between error frames
    HEALTH_CHECK_INTERVAL = 30  # seconds between health checks
    
    retry_count = 0
    last_error_time = 0
    last_health_check = 0
    consecutive_errors = 0
    frame_count = 0
    
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            logger.error("Camera manager not available for streaming")
            yield _generate_error_placeholder("Camera manager not available")
            return
        
        # Initial health check
        manager_status = camera_manager.get_status()
        if not manager_status.get('initialized', False):
            logger.warning("Camera not initialized according to manager")
            yield _generate_error_placeholder("Camera not initialized")
            return
        
        if not manager_status.get('streaming', False):
            logger.warning("Camera not streaming according to manager")
            yield _generate_error_placeholder("Camera not streaming")
            return
        
        logger.info("Starting video stream generation using camera manager")
        
        while True:
            try:
                current_time = time.time()
                
                # Periodic health check
                if current_time - last_health_check > HEALTH_CHECK_INTERVAL:
                    try:
                        manager_status = camera_manager.get_status()
                        if not manager_status.get('initialized', False):
                            logger.warning("Camera lost initialization during streaming")
                            yield _generate_error_placeholder("Camera lost initialization")
                            time.sleep(RETRY_DELAY)
                            continue
                        
                        if not manager_status.get('streaming', False):
                            logger.warning("Camera stopped streaming during operation")
                            yield _generate_error_placeholder("Camera stopped streaming")
                            time.sleep(RETRY_DELAY)
                            continue
                        
                        last_health_check = current_time
                        consecutive_errors = 0  # Reset error counter on successful health check
                        
                    except Exception as health_error:
                        logger.error(f"Health check failed: {health_error}")
                        consecutive_errors += 1
                
                # Get lores frame from camera manager
                frame_data = camera_manager.capture_lores_frame()
                
                if frame_data is None:
                    consecutive_errors += 1
                    if consecutive_errors > MAX_RETRY_ATTEMPTS:
                        logger.error(f"Too many consecutive errors ({consecutive_errors}), sending error frame")
                        yield _generate_error_placeholder("Camera temporarily unavailable")
                        time.sleep(ERROR_FRAME_INTERVAL)
                    else:
                        logger.warning(f"No lores frame data (attempt {consecutive_errors}/{MAX_RETRY_ATTEMPTS})")
                        yield _generate_error_placeholder("No frame data available")
                        time.sleep(RETRY_DELAY)
                    continue
                
                # Handle different frame data formats with validation
                frame = None
                if isinstance(frame_data, dict) and 'frame' in frame_data:
                    frame = frame_data['frame']
                elif isinstance(frame_data, np.ndarray):
                    frame = frame_data
                else:
                    consecutive_errors += 1
                    logger.warning(f"Invalid frame data format: {type(frame_data)}")
                    yield _generate_error_placeholder("Invalid frame format")
                    time.sleep(RETRY_DELAY)
                    continue
                
                # Validate frame data
                if frame is None or not isinstance(frame, np.ndarray):
                    consecutive_errors += 1
                    logger.warning("Frame is None or not a numpy array")
                    yield _generate_error_placeholder("Invalid frame data")
                    time.sleep(RETRY_DELAY)
                    continue
                
                if frame.size == 0 or len(frame.shape) != 3:
                    consecutive_errors += 1
                    logger.warning(f"Invalid frame shape: {frame.shape}")
                    yield _generate_error_placeholder("Invalid frame dimensions")
                    time.sleep(RETRY_DELAY)
                    continue
                
                # Encode frame with error handling
                try:
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                    if not ret or buffer is None:
                        consecutive_errors += 1
                        logger.warning("Frame encoding failed")
                        yield _generate_error_placeholder("Frame encoding failed")
                        time.sleep(RETRY_DELAY)
                        continue
                    
                    frame_bytes = buffer.tobytes()
                    if len(frame_bytes) == 0:
                        consecutive_errors += 1
                        logger.warning("Encoded frame is empty")
                        yield _generate_error_placeholder("Empty encoded frame")
                        time.sleep(RETRY_DELAY)
                        continue
                    
                    # Success - reset error counters
                    consecutive_errors = 0
                    retry_count = 0
                    frame_count += 1
                    
                    # Log progress every 100 frames
                    if frame_count % 100 == 0:
                        logger.info(f"Successfully generated {frame_count} frames")
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                except Exception as encode_error:
                    consecutive_errors += 1
                    logger.error(f"Frame encoding error: {encode_error}")
                    yield _generate_error_placeholder("Frame encoding error")
                    time.sleep(RETRY_DELAY)
                    continue
                
                # Control frame rate
                time.sleep(0.1)  # 10 FPS
                
            except Exception as frame_error:
                consecutive_errors += 1
                current_time = time.time()
                
                # Rate limit error logging
                if current_time - last_error_time > 5.0:  # Log errors at most every 5 seconds
                    logger.error(f"Error generating frame: {frame_error}")
                    last_error_time = current_time
                
                # Handle different types of errors
                if "camera" in str(frame_error).lower():
                    error_message = "Camera hardware error"
                elif "memory" in str(frame_error).lower():
                    error_message = "Memory allocation error"
                elif "timeout" in str(frame_error).lower():
                    error_message = "Camera timeout"
                else:
                    error_message = "Frame generation error"
                
                yield _generate_error_placeholder(error_message)
                
                # Adaptive retry delay based on error frequency
                if consecutive_errors > MAX_RETRY_ATTEMPTS:
                    time.sleep(ERROR_FRAME_INTERVAL)
                else:
                    time.sleep(RETRY_DELAY)
                
    except Exception as stream_error:
        logger.error(f"Critical error in generate_frames: {stream_error}")
        yield _generate_error_placeholder("Critical streaming error")
    finally:
        logger.info("Video stream generation ended")


def _generate_status_frame(manager_status, frame_count):
    """
    Generate a status frame showing camera information.
    
    Args:
        manager_status: Camera manager status
        frame_count: Current frame count
    
    Returns:
        numpy.ndarray: Status frame image
    """
    try:
        # Create a simple status display frame
        width, height = 640, 480
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Fill with dark background
        frame[:] = (20, 20, 20)
        
        # Add status information
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        color = (255, 255, 255)
        thickness = 2
        
        # Title
        cv2.putText(frame, "AI Camera Status", (50, 50), font, 1.2, (0, 255, 0), 2)
        
        # Status information
        y_position = 100
        line_height = 35
        
        status_info = [
            f"Camera Available: {manager_status.get('camera_available', 'Unknown')}",
            f"Streaming: {manager_status.get('streaming', 'Unknown')}",
            f"Initialized: {manager_status.get('initialized', 'Unknown')}",
            f"Frame Count: {frame_count}",
            f"Uptime: {manager_status.get('uptime', 'Unknown')}",
            f"Auto Start: {manager_status.get('auto_start_enabled', 'Unknown')}",
            f"Auto Streaming: {manager_status.get('auto_streaming_enabled', 'Unknown')}"
        ]
        
        for info in status_info:
            cv2.putText(frame, info, (50, y_position), font, font_scale, color, thickness)
            y_position += line_height
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, f"Last Update: {timestamp}", (50, height - 30), font, 0.6, (150, 150, 150), 1)
        
        return frame
        
    except Exception as e:
        logger.error(f"Error generating status frame: {e}")
        return None


def _generate_error_placeholder(message):
    """
    Generate a placeholder image for error states with improved visual feedback.
    
    Args:
        message (str): Error message to display
        
    Returns:
        bytes: Placeholder frame data
    """
    try:
        # Create a simple error placeholder image
        import numpy as np
        
        # Create a 640x480 image with gradient background
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Create gradient background (dark to lighter)
        for y in range(480):
            intensity = int(20 + (y / 480) * 40)  # 20 to 60
            img[y, :] = (intensity, intensity, intensity)
        
        # Add text to the image
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.8
        color = (255, 255, 255)  # White text
        thickness = 2
        
        # Add error icon/indicator
        cv2.circle(img, (320, 120), 40, (0, 0, 255), 3)  # Red circle
        cv2.putText(img, "!", (310, 140), font, 1.5, (0, 0, 255), 3)  # Exclamation mark
        
        # Add title
        cv2.putText(img, "Camera Error", (200, 200), font, 1.2, (0, 0, 255), 2)
        
        # Split message into lines for better readability
        words = message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            # Estimate text width (rough calculation)
            if len(test_line) > 30:  # Approximate character limit
                lines.append(current_line)
                current_line = word
            else:
                current_line = test_line
        
        if current_line:
            lines.append(current_line)
        
        # Display message lines
        y_position = 250
        line_height = 35
        
        for line in lines:
            # Get text size for centering
            (text_width, text_height), baseline = cv2.getTextSize(line, font, font_scale, thickness)
            x_position = (640 - text_width) // 2
            cv2.putText(img, line, (x_position, y_position), font, font_scale, color, thickness)
            y_position += line_height
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        cv2.putText(img, f"Time: {timestamp}", (50, 450), font, 0.6, (150, 150, 150), 1)
        
        # Add retry indicator
        cv2.putText(img, "Retrying...", (500, 450), font, 0.6, (0, 255, 0), 1)
        
        # Encode to JPEG with good quality
        ret, buffer = cv2.imencode('.jpg', img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if ret:
            frame_bytes = buffer.tobytes()
            return (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            # Fallback to simple text response
            return (b'--frame\r\n'
                   b'Content-Type: text/plain\r\n\r\n' + message.encode() + b'\r\n')
    except Exception as e:
        logger.error(f"Error generating placeholder: {e}")
        # Ultimate fallback - simple text response
        return (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\nCamera Error: ' + message.encode() + b'\r\n')


@camera_bp.route('/video_feed')
def video_feed():
    """
    Video streaming endpoint - uses cached data to avoid singleton conflicts.
    
    Returns:
        Response: Multipart video stream
    """
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def generate_lores_frames():
    """
    Generate low resolution video frames for streaming.
    Implements comprehensive error handling with retry mechanisms and graceful degradation.
    
    Yields:
        bytes: Frame data in multipart format
    """
    # Error handling configuration
    MAX_RETRY_ATTEMPTS = 3
    RETRY_DELAY = 1.0  # seconds
    ERROR_FRAME_INTERVAL = 2.0  # seconds between error frames
    HEALTH_CHECK_INTERVAL = 30  # seconds between health checks
    
    retry_count = 0
    last_error_time = 0
    last_health_check = 0
    consecutive_errors = 0
    frame_count = 0
    
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager or not camera_manager.camera_handler:
            logger.error("Camera manager or handler not available for lores streaming")
            yield _generate_error_placeholder("Camera manager not available")
            return
        
        camera_handler = camera_manager.camera_handler
        
        # Initial health check
        camera_status = camera_handler.get_status()
        if not camera_status.get('initialized', False):
            logger.warning("Camera not initialized for lores streaming")
            yield _generate_error_placeholder("Camera not initialized")
            return
        
        if not camera_status.get('streaming', False):
            logger.warning("Camera not streaming for lores, attempting to start...")
            # Try to start the camera if it's not streaming
            try:
                # Use camera manager to ensure camera is streaming
                if camera_manager.ensure_camera_streaming():
                    logger.info("Camera streaming started successfully for lores")
                    # Get updated status
                    camera_status = camera_handler.get_status()
                else:
                    logger.warning("Failed to start camera streaming for lores, sending placeholder")
                    yield _generate_error_placeholder("Camera not streaming - failed to start")
                    return
            except Exception as e:
                logger.error(f"Error starting camera for lores: {e}")
                yield _generate_error_placeholder(f"Camera start error: {str(e)}")
                return
        
        logger.info("Starting low-resolution video stream generation")
        
        while True:
            try:
                current_time = time.time()
                
                # Periodic health check
                if current_time - last_health_check > HEALTH_CHECK_INTERVAL:
                    try:
                        camera_status = camera_handler.get_status()
                        if not camera_status.get('initialized', False):
                            logger.warning("Camera lost initialization during lores streaming")
                            yield _generate_error_placeholder("Camera lost initialization")
                            time.sleep(RETRY_DELAY)
                            continue
                        
                        if not camera_status.get('streaming', False):
                            logger.warning("Camera stopped streaming during lores operation")
                            yield _generate_error_placeholder("Camera stopped streaming")
                            time.sleep(RETRY_DELAY)
                            continue
                        
                        last_health_check = current_time
                        consecutive_errors = 0  # Reset error counter on successful health check
                        
                    except Exception as health_error:
                        logger.error(f"Lores health check failed: {health_error}")
                        consecutive_errors += 1
                
                # Use camera manager to capture lores frame
                frame_data = camera_manager.capture_lores_frame()
                
                if frame_data is None:
                    consecutive_errors += 1
                    if consecutive_errors > MAX_RETRY_ATTEMPTS:
                        logger.error(f"Too many consecutive lores errors ({consecutive_errors}), sending error frame")
                        yield _generate_error_placeholder("Camera temporarily unavailable")
                        time.sleep(ERROR_FRAME_INTERVAL)
                    else:
                        logger.warning(f"No lores frame data (attempt {consecutive_errors}/{MAX_RETRY_ATTEMPTS})")
                        yield _generate_error_placeholder("No lores frame data")
                        time.sleep(RETRY_DELAY)
                    continue
                
                # Handle different frame data formats with validation
                frame = None
                if isinstance(frame_data, dict) and 'frame' in frame_data:
                    frame = frame_data['frame']
                elif isinstance(frame_data, np.ndarray):
                    frame = frame_data
                else:
                    consecutive_errors += 1
                    logger.warning(f"Invalid lores frame data format: {type(frame_data)}")
                    yield _generate_error_placeholder("Invalid lores frame format")
                    time.sleep(RETRY_DELAY)
                    continue
                
                # Validate frame data
                if frame is None or not isinstance(frame, np.ndarray):
                    consecutive_errors += 1
                    logger.warning("Lores frame is None or not a numpy array")
                    yield _generate_error_placeholder("Invalid lores frame data")
                    time.sleep(RETRY_DELAY)
                    continue
                
                if frame.size == 0 or len(frame.shape) != 3:
                    consecutive_errors += 1
                    logger.warning(f"Invalid lores frame shape: {frame.shape}")
                    yield _generate_error_placeholder("Invalid lores frame dimensions")
                    time.sleep(RETRY_DELAY)
                    continue
                
                # Encode frame with error handling
                try:
                    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    if not ret or buffer is None:
                        consecutive_errors += 1
                        logger.warning("Lores frame encoding failed")
                        yield _generate_error_placeholder("Lores frame encoding failed")
                        time.sleep(RETRY_DELAY)
                        continue
                    
                    frame_bytes = buffer.tobytes()
                    if len(frame_bytes) == 0:
                        consecutive_errors += 1
                        logger.warning("Encoded lores frame is empty")
                        yield _generate_error_placeholder("Empty encoded lores frame")
                        time.sleep(RETRY_DELAY)
                        continue
                    
                    # Success - reset error counters
                    consecutive_errors = 0
                    retry_count = 0
                    frame_count += 1
                    
                    # Log progress every 100 frames
                    if frame_count % 100 == 0:
                        logger.info(f"Successfully generated {frame_count} lores frames")
                    
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                    
                except Exception as encode_error:
                    consecutive_errors += 1
                    logger.error(f"Lores frame encoding error: {encode_error}")
                    yield _generate_error_placeholder("Lores frame encoding error")
                    time.sleep(RETRY_DELAY)
                    continue
                
                time.sleep(0.1)  # ~10 FPS for lores
                
            except Exception as frame_error:
                consecutive_errors += 1
                current_time = time.time()
                
                # Rate limit error logging
                if current_time - last_error_time > 5.0:  # Log errors at most every 5 seconds
                    logger.error(f"Error generating lores frame: {frame_error}")
                    last_error_time = current_time
                
                # Handle different types of errors
                if "camera" in str(frame_error).lower():
                    error_message = "Camera hardware error"
                elif "memory" in str(frame_error).lower():
                    error_message = "Memory allocation error"
                elif "timeout" in str(frame_error).lower():
                    error_message = "Camera timeout"
                else:
                    error_message = "Lores frame generation error"
                
                yield _generate_error_placeholder(error_message)
                
                # Adaptive retry delay based on error frequency
                if consecutive_errors > MAX_RETRY_ATTEMPTS:
                    time.sleep(ERROR_FRAME_INTERVAL)
                else:
                    time.sleep(RETRY_DELAY)
                
    except Exception as e:
        logger.error(f"Critical error in generate_lores_frames: {e}")
        yield _generate_error_placeholder(f"Critical lores stream error: {str(e)}")
    finally:
        logger.info("Lores video stream generation ended")


@camera_bp.route('/video_feed_lores')
def video_feed_lores():
    """
    Low resolution video streaming endpoint.
    
    Returns:
        Response: Multipart video stream
    """
    return Response(generate_lores_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@camera_bp.route('/ml_frame')
def get_ml_frame():
    """
    Get ML-optimized frame for AI processing.
    
    Returns:
        dict: JSON response with frame data
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager or not camera_manager.camera_handler:
            return jsonify({'error': 'Camera manager or handler not available'}), 500
        
        camera_handler = camera_manager.camera_handler
        frame_data = camera_handler.capture_ml_frame()
        
        if frame_data and 'main_frame' in frame_data:
            main_frame = frame_data['main_frame']
            if main_frame is not None:
                # Convert to base64 for JSON response
                ret, buffer = cv2.imencode('.jpg', main_frame)
                if ret:
                    import base64
                    frame_base64 = base64.b64encode(buffer).decode('utf-8')
                    return jsonify({
                        'success': True,
                        'frame': frame_base64,
                        'metadata': frame_data.get('metadata', {}),
                        'timestamp': datetime.now().isoformat()
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Failed to encode frame',
                        'timestamp': datetime.now().isoformat()
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'Empty frame received',
                    'timestamp': datetime.now().isoformat()
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'No frame data available',
                'timestamp': datetime.now().isoformat()
            }), 500
    except Exception as e:
        logger.error(f"Error getting ML frame: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


def register_camera_events(socketio):
    """
    Register WebSocket events for camera functionality.
    
    Args:
        socketio: Flask-SocketIO instance
    """
    logger = get_logger(__name__)
    
    @socketio.on('connect', namespace='/camera')
    def handle_camera_connect():
        """Handle camera namespace connection."""
        logger.info("Client connected to camera namespace")
        emit('camera_connected', {
            'success': True,
            'message': 'Connected to camera service',
            'timestamp': datetime.now().isoformat()
        })
    
    @socketio.on('disconnect', namespace='/camera')
    def handle_camera_disconnect():
        """Handle camera namespace disconnection."""
        logger.info("Client disconnected from camera namespace")
    
    @socketio.on('camera_status_request', namespace='/camera')
    def handle_camera_status_request():
        """Handle camera status request."""
        try:
            camera_manager = get_service('camera_manager')
            if not camera_manager:
                emit('camera_status_update', {
                    'success': False,
                    'error': 'Camera manager not available'
                })
                return
            
            status = camera_manager.get_status()
            config = camera_manager.get_configuration()
            
            emit('camera_status_update', {
                'success': True,
                'status': status,
                'config': config
            })
        except Exception as e:
            logger.error(f"Error handling camera status request: {e}")
            emit('camera_status_update', {
                'success': False,
                'error': str(e)
            })
    
    @socketio.on('camera_control', namespace='/camera')
    def handle_camera_control(data):
        """Handle camera control commands."""
        try:
            command = data.get('command')
            if not command:
                emit('camera_control_response', {
                    'success': False,
                    'error': 'No command specified'
                })
                return
            
            camera_manager = get_service('camera_manager')
            if not camera_manager:
                emit('camera_control_response', {
                    'success': False,
                    'error': 'Camera manager not available'
                })
                return
            
            # Execute command based on type
            if command == 'start':
                success = camera_manager.start()
                message = 'Camera started successfully' if success else 'Failed to start camera'
            elif command == 'stop':
                success = camera_manager.stop()
                message = 'Camera stopped successfully' if success else 'Failed to stop camera'
            elif command == 'restart':
                success = camera_manager.restart()
                message = 'Camera restarted successfully' if success else 'Failed to restart camera'
            elif command == 'capture':
                image_data = camera_manager.capture_image()
                if image_data:
                    success = True
                    message = 'Image captured successfully'
                else:
                    success = False
                    message = 'Failed to capture image'
            else:
                success = False
                message = f'Unknown command: {command}'
            
            emit('camera_control_response', {
                'success': success,
                'message': message,
                'command': command
            })
            
            # Send updated status after command
            if success:
                status = camera_manager.get_status()
                config = camera_manager.get_configuration()
                emit('camera_status_update', {
                    'success': True,
                    'status': status,
                    'config': config
                })
                
        except Exception as e:
            logger.error(f"Error handling camera control: {e}")
            emit('camera_control_response', {
                'success': False,
                'error': str(e),
                'command': data.get('command', 'unknown')
            })
    
    @socketio.on('camera_config_update', namespace='/camera')
    def handle_camera_config_update(data):
        """Handle camera configuration updates."""
        try:
            config = data.get('config')
            if not config:
                emit('camera_config_response', {
                    'success': False,
                    'error': 'No configuration data provided'
                })
                return
            
            camera_manager = get_service('camera_manager')
            if not camera_manager:
                emit('camera_config_response', {
                    'success': False,
                    'error': 'Camera manager not available'
                })
                return
            
            result = camera_manager.update_configuration(config)
            
            emit('camera_config_response', {
                'success': result.get('success', False),
                'message': result.get('message', ''),
                'error': result.get('error', '')
            })
            
            # Send updated status after config change
            if result.get('success', False):
                status = camera_manager.get_status()
                updated_config = camera_manager.get_configuration()
                emit('camera_status_update', {
                    'success': True,
                    'status': status,
                    'config': updated_config
                })
                
        except Exception as e:
            logger.error(f"Error handling camera config update: {e}")
            emit('camera_config_response', {
                'success': False,
                'error': str(e)
            })
    
    logger.info("Camera WebSocket events registered successfully")


@camera_bp.route('/debug')
def camera_debug():
    """
    Debug endpoint to check camera status and frame capture.
    
    Returns:
        dict: JSON response with debug information
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({'error': 'Camera manager not available'}), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({'error': 'Camera handler not available'}), 500
        
        # Get camera status from both manager and handler
        manager_status = camera_manager.get_status()
        handler_status = camera_handler.get_status()
        handler_config = camera_handler.get_configuration()
        
        # Test frame capture
        test_frame = None
        frame_shape = None
        frame_error = None
        
        try:
            test_frame = camera_handler.capture_frame()
            if test_frame and 'frame' in test_frame:
                frame_shape = test_frame['frame'].shape if test_frame['frame'] is not None else None
        except Exception as e:
            frame_error = str(e)
        
        debug_info = {
            'manager_status': manager_status,
            'handler_status': handler_status,
            'handler_config': handler_config,
            'frame_capture_success': test_frame is not None,
            'frame_shape': frame_shape,
            'frame_error': frame_error,
            'camera_initialized': handler_status.get('initialized', False),
            'camera_streaming': handler_status.get('streaming', False),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'debug': debug_info
        })
        
    except Exception as e:
        logger.error(f"Error in camera debug: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/metadata')
def camera_metadata():
    """
    Camera metadata viewer page.
    
    Returns:
        str: Rendered metadata template
    """
    return render_template('camera/metadata.html')


@camera_bp.route('/debug_metadata')
def debug_camera_metadata():
    """
    ข้อมูล debug metadata ของกล้อง
    
    Returns:
        dict: JSON response with debug information
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get debug information from camera handler
        debug_info = camera_handler.debug_metadata_capture()
        
        return jsonify({
            'success': True,
            'debug_info': debug_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in debug metadata: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/api/metadata')
def get_camera_metadata_api():
    """
    API endpoint สำหรับ metadata ของกล้อง
    
    Returns:
        dict: JSON response with camera metadata
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get comprehensive camera status and metadata
        camera_status = camera_manager.get_status()
        
        # Prepare metadata for API response
        metadata_response = {
            'success': True,
            'camera_status': camera_status,
            'camera_properties': camera_status.get('camera_handler', {}).get('camera_properties', {}),
            'current_config': camera_status.get('camera_handler', {}).get('current_config', {}),
            'camera_controls': camera_status.get('camera_handler', {}).get('configuration', {}).get('controls', {}),
            'frame_metadata': camera_status.get('metadata', {}),
            'frame_statistics': {
                'frame_count': camera_status.get('frame_count', 0),
                'average_fps': camera_status.get('average_fps', 0.0),
                'last_frame_time': camera_status.get('timestamp', 'N/A')
            },
            'available_modes': camera_status.get('camera_handler', {}).get('sensor_modes', []),
            'sensor_modes_count': camera_status.get('camera_handler', {}).get('sensor_modes_count', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(metadata_response)
        
    except Exception as e:
        logger.error(f"Error getting camera metadata API: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/api/experimental_metadata')
def get_experimental_metadata():
    """
    API endpoint สำหรับ comprehensive experimental metadata ของกล้อง
    
    Returns:
        dict: JSON response with comprehensive experimental metadata
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get comprehensive experimental metadata
        comprehensive_metadata = camera_handler.get_comprehensive_metadata()
        
        if comprehensive_metadata is None:
            return jsonify({
                'success': False,
                'error': 'Failed to capture comprehensive metadata',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        return jsonify({
            'success': True,
            'experimental_metadata': comprehensive_metadata,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting experimental metadata: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/api/metadata_summary')
def get_metadata_summary():
    """
    API endpoint สำหรับ metadata summary สำหรับ experimental efficiency
    
    Returns:
        dict: JSON response with metadata summary
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get comprehensive metadata
        comprehensive_metadata = camera_handler.get_comprehensive_metadata()
        
        if comprehensive_metadata is None:
            return jsonify({
                'success': False,
                'error': 'Failed to capture metadata',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Create summary for experimental efficiency
        metadata_summary = {
            'camera_status': {
                'initialized': camera_handler.initialized,
                'streaming': camera_handler.streaming,
                'frame_count': camera_handler.frame_count,
                'average_fps': camera_handler.average_fps
            },
            'image_quality': {
                'exposure_adequacy': comprehensive_metadata.get('experimental', {}).get('exposure_adequacy', 'unknown'),
                'focus_quality': comprehensive_metadata.get('experimental', {}).get('focus_quality', 'unknown'),
                'lighting_condition': comprehensive_metadata.get('experimental', {}).get('lighting_condition', 'unknown'),
                'noise_level': comprehensive_metadata.get('experimental', {}).get('noise_level', 'unknown'),
                'dynamic_range_utilization': comprehensive_metadata.get('experimental', {}).get('dynamic_range_utilization', 0)
            },
            'performance_metrics': {
                'buffer_ready': comprehensive_metadata.get('performance', {}).get('buffer_ready', False),
                'buffer_latency_ms': comprehensive_metadata.get('performance', {}).get('buffer_latency', 0),
                'capture_thread_active': comprehensive_metadata.get('performance', {}).get('capture_thread_active', False),
                'actual_framerate': comprehensive_metadata.get('configuration', {}).get('framerate', 0)
            },
            'camera_settings': {
                'resolution': comprehensive_metadata.get('configuration', {}).get('resolution', [0, 0]),
                'exposure_time_ms': comprehensive_metadata.get('exposure', {}).get('exposure_time_ms', 0),
                'total_gain': comprehensive_metadata.get('exposure', {}).get('total_gain', 1.0),
                'color_temperature': comprehensive_metadata.get('color', {}).get('color_temperature', 5500),
                'focus_distance': comprehensive_metadata.get('focus', {}).get('focus_distance', 0)
            },
            'experimental_indicators': {
                'image_stability': comprehensive_metadata.get('experimental', {}).get('image_stability', 0),
                'signal_to_noise_db': comprehensive_metadata.get('quality', {}).get('signal_to_noise', 0),
                'dynamic_range_stops': comprehensive_metadata.get('quality', {}).get('dynamic_range', 0),
                'focus_confidence': comprehensive_metadata.get('focus', {}).get('focus_confidence', 0)
            }
        }
        
        return jsonify({
            'success': True,
            'metadata_summary': metadata_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting metadata summary: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/test')
def test_camera():
    """
    ทดสอบการทำงานของกล้อง
    
    Returns:
        dict: JSON response with test results
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        camera_handler = camera_manager.camera_handler
        if not camera_handler:
            return jsonify({
                'success': False,
                'error': 'Camera handler not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get camera status
        camera_status = camera_manager.get_status()
        
        test_results = {
            'handler_initialized': camera_handler.initialized,
            'handler_streaming': camera_handler.streaming,
            'manager_initialized': camera_status.get('initialized', False),
            'manager_streaming': camera_status.get('streaming', False),
            'auto_start_enabled': camera_status.get('auto_start_enabled', False),
            'uptime': camera_status.get('uptime', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'test_results': test_results
        })
        
    except Exception as e:
        logger.error(f"Error in camera test: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/video_test')
def test_video_feed():
    """
    ทดสอบการทำงานของ video feed
    
    Returns:
        dict: JSON response with video test results
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Test frame capture
        frame_data = camera_manager.capture_lores_frame()
        
        video_test_results = {
            'camera_initialized': camera_manager.camera_handler.initialized if camera_manager.camera_handler else False,
            'camera_streaming': camera_manager.camera_handler.streaming if camera_manager.camera_handler else False,
            'frame_capture_success': frame_data is not None,
            'frame_shape': frame_data.shape if frame_data is not None else None,
            'frame_error': None,
            'video_feed_url': '/camera/video_feed',
            'video_feed_lores_url': '/camera/video_feed_lores',
            'timestamp': datetime.now().isoformat()
        }
        
        if frame_data is None:
            video_test_results['frame_error'] = 'No frame data available'
        
        return jsonify({
            'success': True,
            'video_test_results': video_test_results
        })
        
    except Exception as e:
        logger.error(f"Error in video test: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@camera_bp.route('/video_feed_health')
def video_feed_health():
    """
    Video feed health check endpoint.
    
    Returns:
        dict: JSON response with video feed health status
    """
    try:
        camera_manager = get_service('camera_manager')
        if not camera_manager:
            return jsonify({
                'success': False,
                'error': 'Camera manager not available',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Get camera status
        camera_status = camera_manager.get_status()
        
        # Check frame buffer status
        frame_buffer_ready = False
        frame_count = 0
        last_frame_time = None
        
        try:
            if camera_manager.camera_handler:
                frame_buffer_ready = camera_manager.camera_handler.is_frame_buffer_ready()
                frame_count = getattr(camera_manager.camera_handler, 'frame_count', 0)
                last_frame_time = getattr(camera_manager.camera_handler, '_last_capture_time', None)
        except Exception as e:
            logger.warning(f"Error checking frame buffer: {e}")
        
        # Determine health status
        health_status = 'healthy'
        issues = []
        
        if not camera_status.get('initialized', False):
            health_status = 'unhealthy'
            issues.append('Camera not initialized')
        
        if not camera_status.get('streaming', False):
            health_status = 'unhealthy'
            issues.append('Camera not streaming')
        
        if not frame_buffer_ready:
            health_status = 'degraded'
            issues.append('Frame buffer not ready')
        
        # Check if frames are being captured recently
        if last_frame_time:
            time_since_last_frame = time.time() - last_frame_time
            if time_since_last_frame > 5.0:  # More than 5 seconds since last frame
                health_status = 'degraded'
                issues.append(f'No recent frames (last: {time_since_last_frame:.1f}s ago)')
        
        return jsonify({
            'success': True,
            'health_status': health_status,
            'issues': issues,
            'camera_status': {
                'initialized': camera_status.get('initialized', False),
                'streaming': camera_status.get('streaming', False),
                'uptime': camera_status.get('uptime', 0)
            },
            'frame_buffer': {
                'ready': frame_buffer_ready,
                'frame_count': frame_count,
                'last_frame_time': last_frame_time,
                'time_since_last_frame': time.time() - last_frame_time if last_frame_time else None
            },
            'streaming_info': {
                'video_feed_url': '/camera/video_feed',
                'video_feed_lores_url': '/camera/video_feed_lores',
                'health_check_url': '/camera/video_feed_health'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in video feed health check: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'health_status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500