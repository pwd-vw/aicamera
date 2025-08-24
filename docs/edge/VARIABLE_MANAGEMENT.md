# AI Camera v2.0 - Variable Management Standards

**Version:** 2.0.0  
**Last Updated:** 2025-08-24  
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

#### **Backend Service Intervals (Optimized):**
```python
# Reduced frequency for non-essential services
HEALTH_CHECK_INTERVAL = 7200      # 2 hours (was 1 hour)
SENDER_INTERVAL = 300.0           # 5 minutes (was 1 minute)
HEALTH_SENDER_INTERVAL = 1800.0   # 30 minutes (was 5 minutes)
STORAGE_MONITOR_INTERVAL = 1800   # 30 minutes (was 5 minutes)
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

### Code Review Compliance:
- [ ] No direct camera access violations
- [ ] Proper variable naming
- [ ] Error handling implemented
- [ ] Performance considerations
- [ ] Test coverage adequate
- [ ] Documentation complete
- [ ] Detection API responses follow standard format
