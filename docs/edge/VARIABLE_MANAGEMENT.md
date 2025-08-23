# AI Camera v2.0 - Variable Management Standards

**Version:** 2.0.0  
**Last Updated:** 2025-08-23  
**Author:** AI Camera Team  
**Category:** Development Standards  
**Status:** Active

## Overview

เอกสารนี้กำหนดมาตรฐานการจัดการตัวแปรและการเข้าถึงข้อมูลใน AI Camera v2.0 เพื่อป้องกันความขัดแย้งของตัวแปรและรักษาความเสถียรของระบบ

## Singleton Camera Access Rules

**🚨 CRITICAL**: The camera system uses a singleton pattern to prevent multiple concurrent access to Picamera2. All components must follow these access rules strictly.

### Camera Access Architecture

#### Core Components:
- **CameraHandler**: Singleton low-level camera operations (Picamera2 interface)
- **CameraManager**: High-level camera service management (accesses CameraHandler)
- **Frame Buffer System**: Single capture thread provides frames and metadata to all consumers

#### Frame Buffer System:
- **Single Capture Thread**: Continuously captures main and lores frames + metadata
- **Thread-Safe Buffers**: Shared memory for frames and metadata
- **Multiple Consumers**: Detection Manager, Video Streaming, Health Monitor read from buffers
- **No Direct Access**: Components use `get_main_frame()`, `get_lores_frame()`, `get_cached_metadata()`

### Component Access Rules

#### ✅ Allowed Access Patterns:
```python
# Detection Manager - Main stream for AI processing
frame_data = camera_manager.capture_frame()

# Video Streaming - Lores stream for web interface
lores_frame = camera_manager.capture_lores_frame()

# Health Monitor - Status and metadata
status = camera_manager.get_status()
config = camera_manager.get_config()

# Experimental Components - Metadata through API
metadata = camera_manager.get_status()['camera_handler']
```

#### ❌ Forbidden Access Patterns:
```python
# NEVER access CameraHandler directly
camera_handler = get_service('camera_handler')  # ❌ WRONG
frame = camera_handler.capture_frame()          # ❌ WRONG

# NEVER call Picamera2 directly
picam2.capture_request()                        # ❌ WRONG

# NEVER access from multiple processes
# Multiple gunicorn workers accessing camera   # ❌ WRONG
```

### Frame Buffer Methods

#### CameraHandler Interface:
```python
# Thread-safe frame access
get_main_frame() -> np.ndarray
get_lores_frame() -> np.ndarray
get_cached_metadata() -> dict
is_frame_buffer_ready() -> bool

# Frame capture methods (use buffer)
capture_frame() -> np.ndarray      # Returns from main buffer
capture_lores_frame() -> np.ndarray # Returns from lores buffer
```

#### CameraManager Interface:
```python
# High-level camera operations
capture_frame() -> np.ndarray      # For detection
capture_lores_frame() -> np.ndarray # For video streaming
get_status() -> dict              # For health monitoring
get_config() -> dict              # For configuration
```

### Enforcement Guidelines

#### Development Rules:
1. **Always use CameraManager**: Never access CameraHandler directly
2. **Use Frame Buffer**: All frame access goes through buffer system
3. **Single Process**: Ensure only one process accesses camera
4. **Thread Safety**: Use provided thread-safe methods
5. **Error Handling**: Handle camera access errors gracefully

#### Code Review Checklist:
- [ ] No direct CameraHandler access
- [ ] No direct Picamera2 calls
- [ ] Uses CameraManager methods
- [ ] Uses frame buffer methods
- [ ] Proper error handling
- [ ] Thread-safe operations

## Variable Naming Conventions

### Camera-Related Variables

#### Status Variables:
```python
# Camera status
camera_initialized: bool
camera_streaming: bool
camera_online: bool
camera_error: str

# Frame status
frame_count: int
average_fps: float
frame_buffer_ready: bool
last_frame_time: datetime

# Configuration
camera_config: dict
camera_properties: dict
current_config: dict
```

#### Metadata Variables:
```python
# Camera metadata
camera_metadata: dict
frame_metadata: dict
lens_metadata: dict
exposure_metadata: dict

# Buffer metadata
main_frame_buffer: np.ndarray
lores_frame_buffer: np.ndarray
metadata_buffer: dict
```

### Detection Variables

#### Processing Variables:
```python
# Detection status
detection_active: bool
detection_running: bool
detection_error: str

# Detection results
detection_results: list
vehicle_detections: list
plate_detections: list
ocr_results: list

# Performance metrics
processing_time: float
detection_confidence: float
fps_actual: float
```

### Health Monitoring Variables

#### System Health:
```python
# Component status
health_status: dict
component_status: dict
service_status: dict

# Performance metrics
cpu_usage: float
memory_usage: float
disk_usage: float
temperature: float

# Error tracking
error_count: int
last_error: str
error_history: list
```

## Data Flow Standards

### Camera Data Flow

#### Frame Capture Flow:
```
1. CameraHandler (Singleton)
   ├── Single capture thread
   ├── Main stream capture
   ├── Lores stream capture
   └── Metadata capture

2. Frame Buffer System
   ├── Main frame buffer
   ├── Lores frame buffer
   └── Metadata buffer

3. CameraManager (Access Layer)
   ├── capture_frame() -> main buffer
   ├── capture_lores_frame() -> lores buffer
   └── get_status() -> metadata buffer

4. Consumer Components
   ├── Detection Manager -> main frame
   ├── Video Streaming -> lores frame
   └── Health Monitor -> status/metadata
```

#### Metadata Flow:
```
1. CameraHandler
   ├── Capture metadata from Picamera2
   ├── Store in metadata buffer
   └── Update timestamp

2. CameraManager
   ├── Access cached metadata
   ├── Format for API response
   └── Provide to consumers

3. API Endpoints
   ├── /camera/status -> basic status
   ├── /camera/api/metadata -> detailed metadata
   └── /camera/debug_metadata -> debug info
```

### Detection Data Flow

#### Processing Pipeline:
```
1. Frame Input
   ├── camera_manager.capture_frame()
   ├── Frame validation
   └── Preprocessing

2. AI Processing
   ├── Vehicle detection
   ├── License plate detection
   └── OCR processing

3. Result Output
   ├── Detection results
   ├── Confidence scores
   └── Metadata tracking
```

## Error Handling Standards

### Camera Access Errors

#### Common Errors:
```python
# Camera not available
CameraNotAvailableError: "Camera handler not available"
CameraNotInitializedError: "Camera not initialized"
CameraNotStreamingError: "Camera not streaming"

# Frame buffer errors
FrameBufferNotReadyError: "Frame buffer not ready"
FrameCaptureError: "Frame capture failed"
MetadataCaptureError: "Metadata capture failed"

# Access violation errors
MultipleAccessError: "Multiple access to camera detected"
DirectAccessError: "Direct camera access not allowed"
```

#### Error Handling Patterns:
```python
try:
    frame_data = camera_manager.capture_frame()
    if frame_data is None:
        logger.warning("No frame data available")
        return None
except Exception as e:
    logger.error(f"Camera access error: {e}")
    return None
```

### Detection Errors

#### Processing Errors:
```python
# Model errors
ModelNotLoadedError: "AI model not loaded"
ModelInferenceError: "Model inference failed"

# Processing errors
FrameProcessingError: "Frame processing failed"
DetectionTimeoutError: "Detection timeout"

# Result errors
InvalidResultError: "Invalid detection result"
ConfidenceTooLowError: "Detection confidence too low"
```

## Configuration Management

### Camera Configuration

#### Configuration Structure:
```python
camera_config = {
    'resolution': [1280, 720],
    'framerate': 30,
    'buffer_count': 4,
    'use_case': 'video',
    'controls': {
        'FrameDurationLimits': [33333, 33333],
        'NoiseReductionMode': 'Fast'
    }
}
```

#### Configuration Access:
```python
# Get current configuration
config = camera_manager.get_config()

# Update configuration
camera_manager.update_config(new_config)

# Validate configuration
is_valid = camera_manager.validate_config(config)
```

### System Configuration

#### Environment Variables:
```python
# Camera settings
CAMERA_RESOLUTION = "1280x720"
CAMERA_FRAMERATE = "30"
CAMERA_BUFFER_COUNT = "4"

# Detection settings
DETECTION_CONFIDENCE = "0.8"
DETECTION_TIMEOUT = "5.0"

# System settings
LOG_LEVEL = "INFO"
DEBUG_MODE = "False"
```

## Performance Optimization

### Memory Management

#### Frame Buffer Optimization:
```python
# Efficient frame storage
frame_buffer_size = 1  # Single frame buffer
metadata_cache_size = 10  # Metadata history

# Memory cleanup
def cleanup_old_frames():
    # Remove old frames from buffer
    pass

def cleanup_metadata_cache():
    # Remove old metadata
    pass
```

#### Variable Cleanup:
```python
# Explicit cleanup
def cleanup_resources():
    # Clear frame buffers
    # Clear metadata cache
    # Reset counters
    pass
```

### Caching Strategies

#### Metadata Caching:
```python
# Cache frequently accessed metadata
metadata_cache = {
    'camera_properties': cached_properties,
    'current_config': cached_config,
    'frame_statistics': cached_stats
}

# Cache invalidation
def invalidate_cache():
    # Clear cached data
    pass
```

## Testing Standards

### Unit Testing

#### Camera Access Testing:
```python
def test_camera_manager_access():
    # Test CameraManager methods
    # Verify no direct CameraHandler access
    # Test frame buffer access
    pass

def test_singleton_pattern():
    # Verify singleton implementation
    # Test thread safety
    # Test concurrent access prevention
    pass
```

#### Integration Testing:
```python
def test_camera_data_flow():
    # Test complete data flow
    # Test frame capture pipeline
    # Test metadata flow
    pass
```

### Performance Testing

#### Frame Rate Testing:
```python
def test_frame_rate():
    # Test frame capture rate
    # Test buffer performance
    # Test memory usage
    pass
```

## Documentation Standards

### Code Documentation

#### Function Documentation:
```python
def capture_frame(self) -> np.ndarray:
    """
    Capture frame from camera using frame buffer system.
    
    Returns:
        np.ndarray: Frame data from main buffer
        
    Raises:
        CameraNotAvailableError: If camera not available
        FrameBufferNotReadyError: If frame buffer not ready
    """
    pass
```

#### Variable Documentation:
```python
# Camera status tracking
camera_initialized: bool = False  # Camera initialization status
camera_streaming: bool = False    # Camera streaming status
frame_count: int = 0              # Total frames captured
```

### API Documentation

#### Endpoint Documentation:
```python
"""
GET /camera/status
Get camera status and metadata.

Response:
    dict: Camera status with metadata
"""
```

## Compliance Checklist

### Development Compliance:
- [ ] Follow singleton camera access rules
- [ ] Use proper variable naming conventions
- [ ] Implement proper error handling
- [ ] Follow data flow standards
- [ ] Use configuration management
- [ ] Implement performance optimization
- [ ] Write comprehensive tests
- [ ] Document code properly

### Code Review Compliance:
- [ ] No direct camera access violations
- [ ] Proper variable naming
- [ ] Error handling implemented
- [ ] Performance considerations
- [ ] Test coverage adequate
- [ ] Documentation complete
