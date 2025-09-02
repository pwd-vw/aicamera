# AI Camera v2.0 - Variable Management Standards

**Version:** 2.0.0  
**Last Updated:** 2025-09-02  
**Author:** AI Camera Team  
**Category:** Development Standards  
**Status:** Active

## Overview

เอกสารนี้กำหนดมาตรฐานการจัดการตัวแปรและการเข้าถึงข้อมูลใน AI Camera v2.0 เพื่อป้องกันความขัดแย้งของตัวแปรและรักษาความเสถียรของระบบ

## 🚀 System Optimization Notice

**CORE COMPONENTS PRIORITY STRATEGY**

This system has been optimized to prioritize core camera and detection functionality while reducing resource usage for non-essential services. All variable mapping must follow these optimization principles:

### **Core Components (High Priority - Full Performance)**
- **Camera Handler** - Low-level camera operations
- **Camera Manager** - High-level camera service management  
- **Detection Processor** - AI inference pipeline
- **Detection Manager** - Detection orchestration
- **Video Streaming** - Real-time video feed

### **Non-Essential Services (Reduced Resource Usage)**
- **Health Monitor** - 2-hour intervals (was 1 hour)
- **WebSocket Sender** - 5-30 minute intervals (was 1-5 minutes)
- **Storage Monitor** - 30-minute intervals (was 5 minutes)
- **UI Updates** - 30-60 second intervals (was 5-10 seconds)

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

## Backend-Frontend Variable Mapping

### **🚨 CRITICAL: Variable Mapping Standards**

**MANDATORY**: All backend API responses and frontend JavaScript must follow these exact variable mapping standards to prevent UI failures.

### **Standard API Response Format**

#### **Success Response Structure:**
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": {
        // Response data here
    },
    "timestamp": "2025-08-23T10:30:00Z"
}
```

#### **Error Response Structure:**
```json
{
    "success": false,
    "error": "Error description",
    "error_code": "ERROR_CODE",
    "timestamp": "2025-08-23T10:30:00Z"
}
```

### **Camera API Variable Mapping**

#### **GET /camera/status - Backend Response:**
```json
{
    "success": true,
    "camera_status": {
        "is_running": boolean,
        "camera_handler": {
            "camera_properties": {
                "Model": string,
                "Location": string,
                "Revision": string
            },
            "current_config": {
                "resolution": [width, height],
                "framerate": number,
                "brightness": number,
                "contrast": number,
                "saturation": number,
                "awb_mode": number
            },
            "configuration": {
                "controls": {
                    "FrameDurationLimits": [number],
                    "Brightness": number,
                    "Contrast": number,
                    "Saturation": number,
                    "AwbMode": number
                }
            },
            "sensor_modes": [...],
            "sensor_modes_count": number
        },
        "metadata": {...},
        "frame_count": number,
        "average_fps": number,
        "timestamp": string
    },
    "timestamp": "2025-08-23T10:30:00Z"
}
```

#### **Frontend JavaScript Mapping:**
```javascript
// Camera status mapping
const status = data.camera_status;
const isRunning = status.is_running;
const cameraHandler = status.camera_handler;
const cameraProperties = cameraHandler.camera_properties;
const currentConfig = cameraHandler.current_config;
const controls = cameraHandler.configuration.controls;

// Camera properties mapping
const model = cameraProperties.Model;
const location = cameraProperties.Location;
const revision = cameraProperties.Revision;

// Configuration mapping
const resolution = currentConfig.resolution;
const framerate = currentConfig.framerate;
const brightness = currentConfig.brightness;
const contrast = currentConfig.contrast;
const saturation = currentConfig.saturation;
const awbMode = currentConfig.awb_mode;

// Frame statistics mapping
const frameCount = status.frame_count;
const averageFps = status.average_fps;
```

### **Camera Metadata API Variable Mapping**

#### **GET /camera/api/metadata - Backend Response:**
```json
{
    "success": true,
    "camera_status": {...},
    "camera_properties": {
        "Model": string,
        "Location": string,
        "Revision": string
    },
    "current_config": {
        "resolution": [width, height],
        "framerate": number,
        "brightness": number,
        "contrast": number,
        "saturation": number,
        "awb_mode": number
    },
    "camera_controls": {
        "FrameDurationLimits": [number],
        "Brightness": number,
        "Contrast": number,
        "Saturation": number,
        "AwbMode": number
    },
    "frame_metadata": {...},
    "frame_statistics": {
        "frame_count": number,
        "average_fps": number,
        "last_frame_time": string
    },
    "available_modes": [...],
    "sensor_modes_count": number,
    "timestamp": "2025-08-23T10:30:00Z"
}
```

#### **Frontend JavaScript Mapping:**
```javascript
// Metadata API mapping
const cameraProperties = data.camera_properties;
const currentConfig = data.current_config;
const cameraControls = data.camera_controls;
const frameMetadata = data.frame_metadata;
const frameStatistics = data.frame_statistics;
const availableModes = data.available_modes;
const sensorModesCount = data.sensor_modes_count;

// Properties mapping
const model = cameraProperties.Model;
const location = cameraProperties.Location;
const revision = cameraProperties.Revision;

// Configuration mapping
const resolution = currentConfig.resolution;
const framerate = currentConfig.framerate;
const brightness = currentConfig.brightness;
const contrast = currentConfig.contrast;
const saturation = currentConfig.saturation;
const awbMode = currentConfig.awb_mode;

// Controls mapping
const frameDurationLimits = cameraControls.FrameDurationLimits;
const brightnessControl = cameraControls.Brightness;
const contrastControl = cameraControls.Contrast;
const saturationControl = cameraControls.Saturation;
const awbModeControl = cameraControls.AwbMode;

// Statistics mapping
const frameCount = frameStatistics.frame_count;
const averageFps = frameStatistics.average_fps;
const lastFrameTime = frameStatistics.last_frame_time;
```

### **Debug Metadata API Variable Mapping**

#### **GET /camera/debug_metadata - Backend Response:**
```json
{
    "success": true,
    "debug_info": {
        "extracted_metadata": {
            "complete_metadata": {
                "Camera": {...},
                "Image": {...},
                "Sensor": {...},
                "Lens": {...},
                "Processing": {...}
            },
            "debug_steps": [...],
            "metadata_keys": [...]
        },
        "camera_properties": {...},
        "current_config": {...},
        "frame_metadata": {...}
    },
    "timestamp": "2025-08-23T10:30:00Z"
}
```

#### **Frontend JavaScript Mapping:**
```javascript
// Debug metadata mapping
const debugInfo = data.debug_info;
const extractedMetadata = debugInfo.extracted_metadata;
const completeMetadata = extractedMetadata.complete_metadata;
const debugSteps = extractedMetadata.debug_steps;
const metadataKeys = extractedMetadata.metadata_keys;

// Complete metadata mapping
const cameraMetadata = completeMetadata.Camera;
const imageMetadata = completeMetadata.Image;
const sensorMetadata = completeMetadata.Sensor;
const lensMetadata = completeMetadata.Lens;
const processingMetadata = completeMetadata.Processing;
```

### **WebSocket Event Variable Mapping**

#### **Camera Status Update Event:**
```javascript
// Backend emits: 'camera_status_update'
socket.on('camera_status_update', function(data) {
    // Data follows same structure as /camera/status
    const status = data.camera_status;
    const isRunning = status.is_running;
    const cameraHandler = status.camera_handler;
    // ... same mapping as above
});
```

#### **Camera Control Response Event:**
```javascript
// Backend emits: 'camera_control_response'
socket.on('camera_control_response', function(data) {
    const success = data.success;
    const message = data.message;
    const error = data.error;
    const timestamp = data.timestamp;
});
```

#### **Camera Config Response Event:**
```javascript
// Backend emits: 'camera_config_response'
socket.on('camera_config_response', function(data) {
    const success = data.success;
    const config = data.config;
    const message = data.message;
    const error = data.error;
    const timestamp = data.timestamp;
});
```

### **Configuration Form Variable Mapping**

#### **Frontend Form Submission:**
```javascript
// Form data mapping
const config = {
    resolution: [width, height],  // Parsed from "(width, height)" string
    framerate: number,            // Calculated from FrameDurationLimits
    brightness: number,           // -1.0 to 1.0
    contrast: number,             // 0.0 to 2.0
    saturation: number,           // 0.0 to 2.0
    awb_mode: number             // 0=auto, 1=fluorescent, etc.
};

// WebSocket emission
socket.emit('camera_config_update', { config: config });
```

#### **Backend Configuration Processing:**
```python
# Backend receives and processes
config_data = request.get_json()['config']
resolution = config_data.get('resolution')  # [width, height]
framerate = config_data.get('framerate')    # number
brightness = config_data.get('brightness')  # number
contrast = config_data.get('contrast')      # number
saturation = config_data.get('saturation')  # number
awb_mode = config_data.get('awb_mode')      # number
```

### **Error Handling Variable Mapping**

#### **Frontend Error Handling:**
```javascript
// Standard error response mapping
if (!data.success) {
    const error = data.error;
    const errorCode = data.error_code;
    const timestamp = data.timestamp;
    
    // Display error to user
    AICameraUtils.showToast(error, 'error');
}
```

#### **Server Connection Status Variables (Updated 2025-09-02):**
```javascript
// Server connection status priority mapping
const connectionStatusPriority = {
    'connected': {
        className: 'status-indicator status-online',
        text: 'Connected',
        priority: 1  // Highest priority
    },
    'offline_mode': {
        className: 'status-indicator status-warning', 
        text: 'Offline Mode',
        priority: 2  // Medium priority
    },
    'disconnected': {
        className: 'status-indicator status-warning',
        text: 'Disconnected', 
        priority: 3  // Medium priority
    },
    'not_running': {
        className: 'status-indicator status-offline',
        text: 'Not Running',
        priority: 4  // Lowest priority
    }
};

// Data sending status variables
const dataSendingStatus = {
    'active': {
        condition: 'status.running && (status.total_detections_sent > 0 || status.total_health_sent > 0)',
        className: 'status-indicator status-online',
        text: 'Active'
    },
    'ready': {
        condition: 'status.running',
        className: 'status-indicator status-warning',
        text: 'Ready'
    },
    'inactive': {
        condition: 'default',
        className: 'status-indicator status-offline', 
        text: 'Inactive'
    }
};
```

#### **Backend Error Response:**
```python
# Standard error response structure
return jsonify({
    'success': False,
    'error': str(e),
    'error_code': 'CAMERA_ERROR',
    'timestamp': datetime.now().isoformat()
}), 500
```

### **Performance Optimization Variable Mapping**

#### **UI Update Intervals (Optimized):**
```javascript
// Reduced polling frequency for non-essential updates
statusUpdateThrottle: 30000,      // 30 seconds (was 5 seconds)
videoRefreshCooldown: 15000,      // 15 seconds (was 5 seconds)
dashboardUpdates: 60000,          // 60 seconds (was 10 seconds)
```

#### **Cache-Control Headers (Updated 2025-09-02):**
```python
# Optimized cache-control headers for better performance
optimized_headers = {
    'Cache-Control': 'no-cache',  # Simplified from 'no-cache, no-store, must-revalidate, max-age=0'
    # Removed deprecated 'Pragma': 'no-cache'
    # Removed conflicting 'Expires': '0'
}

# Applied to endpoints:
# - /camera/* - All camera endpoints
# - /websocket-sender/* - WebSocket sender endpoints  
# - /storage/* - Storage management endpoints
# - /health/* - Health monitoring endpoints
```

#### **CSS Performance Variables (Updated 2025-09-02):**
```css
/* Optimized animations using transform instead of left */
@keyframes shimmer {
    0% { transform: translateX(-100%); }  /* was: left: -100%; */
    100% { transform: translateX(100%); } /* was: left: 100%; */
}

@keyframes loading {
    0% { transform: translateX(-100%); }  /* was: left: -100%; */
    100% { transform: translateX(100%); } /* was: left: 100%; */
}

/* Button hover effects using transform */
.btn::before {
    transform: translateX(-100%);        /* was: left: -100%; */
    transition: transform 0.3s ease;     /* was: transition: left 0.3s ease; */
}
```

#### **Backend Service Intervals (Optimized):**
```python
# Reduced frequency for non-essential services
HEALTH_CHECK_INTERVAL = 7200      # 2 hours (was 1 hour)
SENDER_INTERVAL = 300.0           # 5 minutes (was 1 minute)
HEALTH_SENDER_INTERVAL = 1800.0   # 30 minutes (was 5 minutes)
STORAGE_MONITOR_INTERVAL = 1800   # 30 minutes (was 5 minutes)
```

#### **Manual Capture System Variables (Added 2025-09-02):**
```python
# Manual capture endpoint variables
capture_response = {
    'success': bool,
    'message': str,
    'timestamp': str  # ISO format
}

# Frontend capture handling
capture_status_messages = {
    'success': 'Image captured successfully',
    'error': 'Failed to capture image',
    'loading': 'Capturing image...'
}

# File naming convention
manual_capture_filename = f"manual_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
manual_capture_directory = "/edge/manual_capture/"
```

### **Variable Mapping Validation**

#### **Required Field Validation:**
- **success**: Always present in all responses
- **timestamp**: Always present in all responses (ISO 8601 format)
- **error**: Present in error responses
- **message**: Present in success responses
- **data**: Present in success responses with actual data

#### **Data Type Validation:**
- **boolean**: is_running, success
- **number**: frame_count, average_fps, brightness, contrast, saturation, awb_mode
- **array**: resolution, FrameDurationLimits, sensor_modes
- **object**: camera_properties, current_config, configuration
- **string**: Model, Location, timestamp, error, message

#### **Frontend Compatibility:**
- **JavaScript parsing**: All fields must be parseable by JSON.parse()
- **Null safety**: Check for undefined/null before accessing nested properties
- **Type conversion**: Handle number/string conversions appropriately
- **Error boundaries**: Implement proper error handling for malformed responses

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

#### Health Monitor Status Display (Updated 2025-09-02):
```javascript
// Main dashboard health status variables
main_health_status: string           // 'status-online', 'status-warning', 'status-offline'
main_health_status_text: string      // 'Online', 'Warning', 'Offline'
main_health_status_text_detail: string // Status detail message

// Health status detail messages based on component status
const healthStatusMessages = {
    'healthy': 'ตรวจสอบทุก 60 วินาที',
    'camera_not_initialized': 'Camera not initialized',
    'camera_not_streaming': 'Camera not streaming', 
    'ai_models_not_loaded': 'AI models not loaded',
    'detection_not_active': 'Detection not active',
    'database_disconnected': 'Database disconnected',
    'system_resources_critical': 'System resources critical',
    'service_unavailable': 'Service unavailable',
    'not_running': 'Not Running'
};
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

## Detection API Variable Mapping

### **Detection Status API (`/detection/status`)**

#### **Backend Response Structure:**
```python
{
    "success": True,
    "detection_status": {
        "service_running": bool,
        "detection_processor_status": {
            "models_loaded": bool,
            "vehicle_model_available": bool,
            "lp_detection_model_available": bool,
            "lp_ocr_model_available": bool,
            "easyocr_available": bool,
            "confidence_threshold": float,
            "detection_resolution": [int, int]
        },
        "detection_interval": float,
        "auto_start": bool
    },
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Frontend Variable Mapping:**
```javascript
// Detection status mapping
const status = data.detection_status;
const serviceRunning = status.service_running;
const processorStatus = status.detection_processor_status;
const modelsLoaded = processorStatus.models_loaded;
const detectionInterval = status.detection_interval;
const autoStart = status.auto_start;

// Update UI elements
document.getElementById('service-status').textContent = 
    serviceRunning ? 'Running' : 'Stopped';
document.getElementById('models-status').textContent = 
    modelsLoaded ? 'Loaded' : 'Not Loaded';
```

### **Detection Configuration API (`/detection/config`)**

#### **Backend Response Structure:**
```python
{
    "success": True,
    "config": {
        "detection_interval": float,
        "vehicle_confidence": float,
        "plate_confidence": float,
        "detection_resolution": [int, int]
    },
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Frontend Variable Mapping:**
```javascript
// Configuration mapping
const config = data.config;
const interval = config.detection_interval;
const vehicleConf = config.vehicle_confidence;
const plateConf = config.plate_confidence;
const resolution = config.detection_resolution;

// Update form fields
document.getElementById('detection-interval').value = interval;
document.getElementById('vehicle-confidence').value = vehicleConf;
document.getElementById('plate-confidence').value = plateConf;
```

### **Detection Statistics API (`/detection/statistics`)**

#### **Backend Response Structure:**
```python
{
    "success": True,
    "statistics": {
        "total_frames_processed": int,
        "total_vehicles_detected": int,
        "total_plates_detected": int,
        "successful_ocr": int,
        "detection_rate_percent": float,
        "avg_processing_time_ms": float
    },
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Frontend Variable Mapping:**
```javascript
// Statistics mapping
const stats = data.statistics;
const framesProcessed = stats.total_frames_processed;
const vehiclesDetected = stats.total_vehicles_detected;
const platesDetected = stats.total_plates_detected;
const successfulOcr = stats.successful_ocr;
const detectionRate = stats.detection_rate_percent;
const avgProcessingTime = stats.avg_processing_time_ms;

// Update statistics display
document.getElementById('frames-processed').textContent = framesProcessed;
document.getElementById('vehicles-detected').textContent = vehiclesDetected;
document.getElementById('plates-detected').textContent = platesDetected;
```

### **Detection Results API (`/detection/results/recent`)**

#### **Backend Response Structure:**
```python
{
    "success": True,
    "results": [
        {
            "id": int,
            "timestamp": str,
            "image_path": str,
            "vehicles_detected": int,
            "plates_detected": int,
            "confidence_scores": list,
            "processing_time_ms": float
        }
    ],
    "count": int,
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Frontend Variable Mapping:**
```javascript
// Results mapping
const results = data.results;
const resultCount = data.count;

// Process each result
results.forEach(result => {
    const id = result.id;
    const timestamp = result.timestamp;
    const imagePath = result.image_path;
    const vehiclesDetected = result.vehicles_detected;
    const platesDetected = result.plates_detected;
    const confidenceScores = result.confidence_scores;
    const processingTime = result.processing_time_ms;
    
    // Create result display element
    createResultElement(result);
});
```

### **UI Dashboard Toggle Variables (Added 2025-09-02)**

#### **Toggle Control Variables:**
```javascript
// Toggle state management
let systemInfoVisible = true;
let developmentRefVisible = true;

// Toggle control elements
const toggleElements = {
    'system-info': {
        button: 'toggle-system-info',
        section: 'system-info-section', 
        content: 'system-info-content',
        toggleBtn: 'toggle-system-info-content'
    },
    'development-ref': {
        button: 'toggle-development-ref',
        section: 'development-ref-section',
        content: 'development-ref-content', 
        toggleBtn: 'toggle-development-ref-content'
    }
};

// Global toggle controls
const globalControls = {
    'show-all': 'toggle-all',
    'hide-all': 'hide-all'
};
```

#### **Accessibility Variables:**
```javascript
// Accessibility attributes for toggle buttons
const accessibilityAttributes = {
    'title': 'Toggle [Section Name] content visibility',
    'aria-label': 'Toggle [Section Name] content visibility',
    'aria-expanded': 'true|false',  // Dynamic based on visibility state
    'aria-controls': '[content-element-id]'
};

// Chevron icon states
const chevronStates = {
    'expanded': '<i class="fas fa-chevron-up"></i>',
    'collapsed': '<i class="fas fa-chevron-down"></i>'
};
```

### **Detection Control APIs**

#### **Start Detection (`POST /detection/start`):**
```python
# Backend Response
{
    "success": True,
    "message": "Detection service started successfully",
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Stop Detection (`POST /detection/stop`):**
```python
# Backend Response
{
    "success": True,
    "message": "Detection service stopped successfully",
    "timestamp": "2025-08-24T10:02:28Z"
}
```

#### **Process Frame (`POST /detection/process_frame`):**
```python
# Backend Response
{
    "success": True,
    "detection_result": {
        "vehicles_detected": int,
        "plates_detected": int,
        "processing_time_ms": float,
        "confidence_scores": list
    },
    "timestamp": "2025-08-24T10:02:28Z"
}
```

### **WebSocket Event Mapping**

#### **Detection Status Updates:**
```javascript
// WebSocket event handling
socket.on('detection_status_update', (data) => {
    if (data && data.success && data.detection_status) {
        updateDetectionStatus(data.detection_status);
    } else {
        console.error('Invalid detection status update:', data);
    }
});
```

#### **Detection Control Events:**
```javascript
// Request status update
socket.emit('detection_status_request');

// Control detection
socket.emit('detection_control', {
    action: 'start' | 'stop' | 'process_frame'
});
```

### **Detection Results API Variable Mapping:**

#### **Backend Response Structure:**
```json
{
    "success": true,
    "results": [
        {
            "id": 123,
            "timestamp": "2025-08-24T10:15:25Z",
            "vehicle_detected_image_path": "captured_images/vehicle_detected_20250824_101525_123.jpg",
            "plate_image_path": "captured_images/plate_detected_20250824_101525_123.jpg",
            "vehicles_count": 2,
            "plates_count": 1,
            "processing_time_ms": 45.2,
            "ocr_results": [
                {
                    "text": "ABC123",
                    "confidence": 0.95,
                    "language": "en"
                }
            ]
        }
    ],
    "count": 1
}
```

#### **Frontend Variable Mapping:**
- `data.results[i].id` → Detection result ID
- `data.results[i].timestamp` → Detection timestamp
- `data.results[i].vehicle_detected_image_path` → Vehicle detection image path
- `data.results[i].plate_image_path` → License plate detection image path
- `data.results[i].vehicles_count` → Number of vehicles detected
- `data.results[i].plates_count` → Number of plates detected
- `data.results[i].processing_time_ms` → Processing time in milliseconds
- `data.results[i].ocr_results` → OCR results array

#### **Image Path Structure:**
- **Vehicle Detection Image**: `captured_images/vehicle_detected_YYYYMMDD_HHMMSS_microseconds.jpg`
- **Plate Detection Image**: `captured_images/plate_detected_YYYYMMDD_HHMMSS_microseconds.jpg`
- **Original Image**: `captured_images/detection_YYYYMMDD_HHMMSS_microseconds.jpg`
- **Cropped Plates**: `captured_images/plate_YYYYMMDD_HHMMSS_microseconds_N.jpg`

### **Error Handling for Detection APIs**

#### **Frontend Error Handling:**
```javascript
// Standard error response mapping
if (!data.success) {
    const error = data.error;
    const timestamp = data.timestamp;
    
    // Display error to user
    AICameraUtils.showToast(error, 'error');
    console.error('Detection API error:', error);
}
```

#### **Backend Error Response:**
```python
# Standard error response structure
return jsonify({
    'success': False,
    'error': str(e),
    'timestamp': datetime.now().isoformat()
}), 500
```

## Variable Conflict Prevention Guide

### Layer-Specific Naming Standards

#### 1. Backend (Python) - `snake_case`

```python
# ✅ Correct
camera_status = {
    'initialized': True,
    'streaming': True,
    'frame_count': 1234,
    'average_fps': 29.5,
    'auto_start_enabled': True
}

detection_processor_status = {
    'models_loaded': True,
    'vehicle_model_available': True,
    'lp_detection_model_available': True
}

# ❌ Incorrect
cameraStatus = {...}  # camelCase in Python
CameraStatus = {...}  # PascalCase for variables
camera-status = {...}  # kebab-case in Python
```

#### 2. Frontend (JavaScript) - `camelCase`

```javascript
// ✅ Correct
const cameraStatus = {
    initialized: true,
    streaming: true,
    frameCount: 1234,
    averageFps: 29.5,
    autoStartEnabled: true
};

const detectionProcessorStatus = {
    modelsLoaded: true,
    vehicleModelAvailable: true,
    lpDetectionModelAvailable: true
};

// ❌ Incorrect
const camera_status = {...};  // snake_case in JavaScript
const CameraStatus = {...};   // PascalCase for variables
const camera-status = {...};  // kebab-case in JavaScript
```

#### 3. HTML Elements - `kebab-case`

```html
<!-- ✅ Correct -->
<span id="main-camera-model">Loading...</span>
<span id="feature-camera-resolution">Loading...</span>
<div class="status-online">Online</div>
<button id="camera-start-btn">Start</button>

<!-- ❌ Incorrect -->
<span id="mainCameraModel">Loading...</span>  <!-- camelCase -->
<span id="main_camera_model">Loading...</span>  <!-- snake_case -->
<div class="statusOnline">Online</div>  <!-- camelCase -->
```

#### 4. API Endpoints - `snake_case`

```
✅ Correct:
GET /camera/status
POST /detection/start
GET /health/system
GET /health/logs
GET /health/status
GET /health/system-info

❌ Incorrect:
GET /camera/getStatus
POST /detection/startDetection
GET /health/getSystemHealth
```

#### 5. WebSocket Events - `snake_case`

```javascript
// ✅ Correct
socket.emit('camera_status_request', {});
socket.on('camera_status_update', callback);
socket.emit('detection_control', {command: 'start'});
socket.emit('health_status_request', {});

// ❌ Incorrect
socket.emit('cameraStatusRequest', {});  // camelCase
socket.on('camera-status-update', callback);  // kebab-case
```

### Common Conflict Scenarios

#### 1. Duplicate HTML Element IDs

**Problem:**
```html
<!-- System Information section -->
<span id="main-camera-model">Loading...</span>

<!-- Features section -->  
<span id="main-camera-model">Loading...</span>  <!-- ❌ Duplicate ID -->
```

**Solution:**
```html
<!-- System Information section -->
<span id="main-camera-model">Loading...</span>

<!-- Features section -->
<span id="feature-camera-model">Loading...</span>  <!-- ✅ Unique ID -->
```

#### 2. Inconsistent Variable Naming Across Layers

**Problem:**
```python
# Backend
camera_status = {'frame_count': 1234}

# Frontend expects camelCase but receives snake_case
const frameCount = status.frameCount;  // ❌ undefined
```

**Solution:**
```python
# Backend - Keep snake_case
camera_status = {'frame_count': 1234}

# Frontend - Access with original structure
const frameCount = status.frame_count;  // ✅ Works
// OR convert if needed
const frameCount = status.frameCount || status.frame_count;
```

#### 3. WebSocket Event Name Mismatches

**Problem:**
```javascript
// Client sends camelCase
socket.emit('cameraStatusRequest', {});

// Server expects snake_case
@socketio.on('camera_status_request')  // ❌ Mismatch
```

**Solution:**
```javascript
// Client uses snake_case
socket.emit('camera_status_request', {});  // ✅ Matches server

// Server handles snake_case
@socketio.on('camera_status_request')  // ✅ Matches client
```

#### 4. CSS Class Naming Conflicts

**Problem:**
```css
/* Bootstrap uses kebab-case */
.btn-primary { ... }

/* Custom classes use camelCase */
.statusOnline { ... }  /* ❌ Inconsistent */
```

**Solution:**
```css
/* All classes use kebab-case */
.btn-primary { ... }
.status-online { ... }  /* ✅ Consistent */
```

### Prevention Strategies

#### 1. Code Review Checklist

**Backend (Python):**
- [ ] All variables use `snake_case`
- [ ] API responses follow `variable_management.md` format
- [ ] WebSocket events use `snake_case` naming
- [ ] Database columns use `snake_case`
- [ ] No camelCase or kebab-case in Python code

**Frontend (JavaScript):**
- [ ] All variables use `camelCase`
- [ ] API data accessed with original structure
- [ ] WebSocket events use `snake_case` (server compatibility)
- [ ] No snake_case variables in JavaScript
- [ ] Consistent property access patterns

**HTML Templates:**
- [ ] All element IDs use `kebab-case`
- [ ] No duplicate IDs in same page
- [ ] CSS classes use `kebab-case`
- [ ] Semantic and descriptive naming
- [ ] Section prefixes for organization

#### 2. HTML Element ID Mapping

```javascript
// ✅ Correct - Unique IDs for different sections
const ELEMENT_IDS = {
    // Main System Information section
    MAIN_CAMERA_MODEL: 'main-camera-model',
    MAIN_CAMERA_RESOLUTION: 'main-camera-resolution',
    MAIN_CAMERA_FPS: 'main-camera-fps',
    
    // Features section (different data, different IDs)
    FEATURE_CAMERA_MODEL: 'feature-camera-model',
    FEATURE_CAMERA_RESOLUTION: 'feature-camera-resolution',
    FEATURE_CAMERA_FPS: 'feature-camera-fps',
    
    // Status indicators
    MAIN_CAMERA_STATUS: 'main-camera-status',
    MAIN_CAMERA_DETAIL_STATUS: 'main-camera-detail-status',
    MAIN_CAMERA_FEATURE_STATUS: 'main-camera-feature-status'
};

// ❌ Wrong - Duplicate IDs cause conflicts
// Both sections using same IDs:
// 'main-camera-model' appears twice → only first gets updated
```

#### 3. Backend → Frontend Data Flow

```python
# Backend (Python) - snake_case
api_response = {
    "success": True,
    "status": {
        "camera_handler": {
            "current_config": {
                "main": {
                    "size": [1280, 720]
                },
                "controls": {
                    "FrameDurationLimits": [33333, 33333]
                }
            },
            "camera_properties": {
                "Model": "imx708"
            }
        }
    }
}
```

```javascript
// Frontend (JavaScript) - Access with camelCase conversion
function updateCameraStatus(status) {
    // Direct access (structure preserved)
    const resolution = status.camera_handler.current_config.main.size;
    const model = status.camera_handler.camera_properties.Model;
    const frameDuration = status.camera_handler.current_config.controls.FrameDurationLimits[0];
    
    // Convert to display format
    const resolutionText = `${resolution[0]}x${resolution[1]}`;
    const fpsText = `${Math.round(1000000 / frameDuration)} FPS`;
    
    // Update DOM elements
    document.getElementById('main-camera-resolution').textContent = resolutionText;
    document.getElementById('main-camera-fps').textContent = fpsText;
    document.getElementById('main-camera-model').textContent = model;
}
```

### Testing & Validation

#### 1. Validation Scripts

**Backend Validation:**
```python
#!/usr/bin/env python3
# validate_backend_naming.py

import re
import json

def validate_api_responses():
    """Validate all API responses use snake_case"""
    errors = []
    
    # Test camera status endpoint
    with camera_bp.test_client() as client:
        response = client.get('/camera/status')
        data = json.loads(response.data)
        
        if 'frameCount' in str(data):
            errors.append("Found camelCase in camera status API")
        
        if 'frame_count' not in str(data):
            errors.append("Missing snake_case variables in camera status API")
    
    return errors

if __name__ == "__main__":
    errors = validate_api_responses()
    if errors:
        print("❌ Validation failed:")
        for error in errors:
            print(f"  - {error}")
        exit(1)
    else:
        print("✅ Backend naming validation passed")
```

**Frontend Validation:**
```javascript
// validate_frontend_naming.js

function validateJavaScriptNaming() {
    const errors = [];
    
    // Check for snake_case in JavaScript (should be camelCase)
    const jsFiles = ['dashboard.js', 'camera.js', 'detection.js'];
    
    jsFiles.forEach(file => {
        const content = fs.readFileSync(`/path/to/${file}`, 'utf8');
        
        // Look for snake_case variable declarations
        const snakeCasePattern = /(?:const|let|var)\s+[a-z]+_[a-z]/g;
        const matches = content.match(snakeCasePattern);
        
        if (matches) {
            errors.push(`Found snake_case variables in ${file}: ${matches.join(', ')}`);
        }
    });
    
    return errors;
}

function validateElementIds() {
    const errors = [];
    const htmlFiles = glob.sync('edge/src/web/templates/**/*.html');
    const allIds = [];
    
    htmlFiles.forEach(file => {
        const content = fs.readFileSync(file, 'utf8');
        const idMatches = content.match(/id="([^"]+)"/g);
        
        if (idMatches) {
            idMatches.forEach(match => {
                const id = match.match(/id="([^"]+)"/)[1];
                
                // Check for camelCase (should be kebab-case)
                if (/[a-z][A-Z]/.test(id)) {
                    errors.push(`CamelCase ID found in ${file}: ${id}`);
                }
                
                // Check for duplicates
                if (allIds.includes(id)) {
                    errors.push(`Duplicate ID found: ${id}`);
                } else {
                    allIds.push(id);
                }
            });
        }
    });
    
    return errors;
}

// Run validations
const jsErrors = validateJavaScriptNaming();
const htmlErrors = validateElementIds();

if (jsErrors.length > 0 || htmlErrors.length > 0) {
    console.log("❌ Frontend validation failed:");
    [...jsErrors, ...htmlErrors].forEach(error => console.log(`  - ${error}`));
    process.exit(1);
} else {
    console.log("✅ Frontend naming validation passed");
}
```

#### 2. Pre-deployment Checklist

**API Endpoints:**
- [ ] All endpoints return consistent response format
- [ ] Variable names follow snake_case convention
- [ ] No camelCase in API responses
- [ ] Timestamp format is ISO 8601
- [ ] Error responses include error_code

**Frontend Integration:**
- [ ] JavaScript variables use camelCase
- [ ] API data accessed correctly
- [ ] WebSocket events work bidirectionally
- [ ] No undefined variable errors
- [ ] DOM elements update correctly

**HTML Templates:**
- [ ] No duplicate element IDs
- [ ] CSS classes use kebab-case
- [ ] Element IDs are descriptive
- [ ] Bootstrap compatibility maintained
- [ ] Cross-browser compatibility tested

### Variable Naming Quick Reference

| Context | Convention | Example | ✅ / ❌ |
|---------|------------|---------|---------|
| Python Variables | snake_case | `camera_status` | ✅ |
| Python Variables | camelCase | `cameraStatus` | ❌ |
| JavaScript Variables | camelCase | `cameraStatus` | ✅ |
| JavaScript Variables | snake_case | `camera_status` | ❌ |
| HTML Element IDs | kebab-case | `main-camera-status` | ✅ |
| HTML Element IDs | camelCase | `mainCameraStatus` | ❌ |
| CSS Classes | kebab-case | `status-online` | ✅ |
| CSS Classes | camelCase | `statusOnline` | ❌ |
| API Endpoints | snake_case | `/camera/status` | ✅ |
| API Endpoints | camelCase | `/camera/getStatus` | ❌ |
| WebSocket Events | snake_case | `camera_status_update` | ✅ |
| WebSocket Events | camelCase | `cameraStatusUpdate` | ❌ |

### Common Data Paths

| Data Type | Backend Path | Frontend Access | Display Element |
|-----------|--------------|-----------------|-----------------|
| **Camera Model** | `status.camera_handler.camera_properties.Model` | `status.camera_handler.camera_properties.Model` | `main-camera-model` |
| **Resolution** | `status.camera_handler.current_config.main.size` | `status.camera_handler.current_config.main.size` | `main-camera-resolution` |
| **FPS** | `status.camera_handler.current_config.controls.FrameDurationLimits[0]` | `Math.round(1000000 / status.camera_handler.current_config.controls.FrameDurationLimits[0])` | `main-camera-fps` |
| **Camera Status** | `status.streaming` | `status.streaming` | `main-camera-status` |
| **Frame Count** | `status.frame_count` | `status.frame_count` | N/A |
| **Uptime** | `status.uptime` | `AICameraUtils.formatDuration(status.uptime)` | `main-system-uptime` |

### WebSocket Event Reference

| Event Type | Client → Server | Server → Client | Data Structure |
|------------|-----------------|-----------------|----------------|
| **Camera Status** | `camera_status_request` | `camera_status_update` | Same as API response |
| **Camera Control** | `camera_control` | `camera_control_response` | `{command, success, message}` |
| **Detection Status** | `detection_status_request` | `detection_status_update` | Same as API response |
| **Detection Control** | `detection_control` | `detection_control_response` | `{command, success, message}` |
| **Health Status** | `health_status_request` | `health_status_update` | Same as API response |
| **Health Logs** | `health_logs_request` | `health_logs_update` | Same as API response |
| **Health Monitor Control** | `health_monitor_start/stop` | `health_monitor_response` | `{success, message}` |
| **Health Check** | `health_check_run` | `health_check_response` | Same as API response |
| **Health Room** | `join_health_room/leave_health_room` | `health_room_joined/left` | `{success, message}` |

### Health System Variable Mapping (Updated v2.0.0)

#### Health API Response Structure

**Backend (Python) - Health Service Response:**
```python
health_response = {
    "success": True,
    "data": {
        "overall_status": "healthy",  # snake_case
        "components": {
            "camera": {
                "status": "healthy",
                "message": "Camera initialized and streaming",
                "last_check": "2025-09-02T22:41:08.439079",
                "execution_time_ms": 6.42
            },
            "detection": {
                "status": "unhealthy", 
                "message": "Insufficient models loaded: 0/2 required"
            }
        },
        "system": {
            "cpu": {
                "usage_percent": 68.9,
                "count": 4,
                "temperature_c": 55.1
            },
            "memory": {
                "usage_percent": 42.9,
                "total_gb": 8.0,
                "available_gb": 4.6
            }
        }
    },
    "timestamp": "2025-09-02T22:41:18.385453"
}
```

**Frontend (JavaScript) - Variable Mapping:**
```javascript
// ✅ Correct - Consistent mapping
const healthData = response.data;
const overallStatus = healthData.overall_status;  // snake_case from backend
const cameraComponent = healthData.components.camera;
const cpuUsage = healthData.system.cpu.usage_percent;

// Dashboard display variables (camelCase for DOM)
const statusElements = {
    overallStatusIndicator: document.getElementById('overall-status'),
    cameraStatusText: document.getElementById('camera-status-text'),
    cpuUsageDisplay: document.getElementById('cpu-usage-display')
};
```

#### Component Name Mapping

Health components use standardized names across the system:

| Component | Backend Key | Frontend Display | API Endpoint |
|-----------|-------------|------------------|--------------|
| Camera System | `camera` | Camera Status | `/camera/status` |
| Detection Models | `detection` | AI Models | `/detection/status` |
| Database | `database` | Database | Internal check |
| System Resources | `system` | System Info | `/health/system-info` |
| Storage | `storage` | Storage | Internal check |
| Network | `network` | Network | Internal check |

### Automated Validation

#### ESLint Rules (JavaScript):
```javascript
// .eslintrc.js
module.exports = {
    rules: {
        'camelcase': ['error', { properties: 'always' }],
        'id-match': ['error', '^[a-z][a-zA-Z0-9]*$', { 
            properties: true,
            onlyDeclarations: false
        }]
    }
};
```

#### Python Linting (pylint/flake8):
```python
# .pylintrc
[MESSAGES CONTROL]
enable = invalid-name

[BASIC]
variable-rgx = ^[a-z_][a-z0-9_]{2,30}$
```

#### HTML Validation Script:
```bash
#!/bin/bash
# check_duplicate_ids.sh
echo "Checking for duplicate HTML IDs..."
grep -r 'id="' edge/src/web/templates/ | \
  sed 's/.*id="\([^"]*\)".*/\1/' | \
  sort | uniq -d
```

### Error Prevention Checklist

**Before Code Commit:**
- [ ] Run naming validation scripts
- [ ] Check for duplicate HTML IDs
- [ ] Verify API response structure
- [ ] Test WebSocket events
- [ ] Validate CSS class names
- [ ] Check cross-browser compatibility

**Before Deployment:**
- [ ] Integration tests pass
- [ ] Frontend can access all API data
- [ ] WebSocket communication works
- [ ] No console errors
- [ ] All UI elements update correctly

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
- [ ] Follow detection API variable mapping standards
- [ ] Implement accessibility attributes (title, aria-label) for UI elements
- [ ] Use optimized CSS animations with transform properties
- [ ] Apply proper cache-control headers without deprecated directives
- [ ] Follow layer-specific naming conventions
- [ ] Prevent duplicate HTML element IDs
- [ ] Ensure WebSocket event name consistency

### Code Review Compliance:
- [ ] No direct camera access violations
- [ ] Proper variable naming
- [ ] Error handling implemented
- [ ] Performance considerations
- [ ] Test coverage adequate
- [ ] Documentation complete
- [ ] Detection API responses follow standard format
- [ ] Health monitor status variables properly mapped
- [ ] Server connection status priority implemented correctly
- [ ] Manual capture system variables documented
- [ ] CSS performance optimizations applied
- [ ] Accessibility compliance verified
- [ ] No variable naming conflicts across layers
- [ ] Unique HTML element IDs throughout application
- [ ] Consistent WebSocket event naming
