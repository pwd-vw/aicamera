# AI Camera Edge System - API Reference

**Version:** 2.0.0  
**Last Updated:** 2025-08-24  
**Author:** AI Camera Team  
**Category:** API Documentation  
**Status:** Active

## System Optimization Notice

**🚀 OPTIMIZED FOR CORE COMPONENTS PRIORITY**

This system has been optimized to prioritize core camera and detection functionality while reducing resource usage for non-essential services:

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

### **Resource Usage Reduction**
- **CPU Usage**: Significantly reduced background processing
- **Memory Usage**: Optimized polling frequencies
- **Network Traffic**: Reduced non-essential communication
- **System Stability**: Enhanced with prioritized core components

## Overview

API Reference สำหรับ AI Camera Edge System v1.3.9 ครอบคลุม REST API endpoints, WebSocket interfaces, และ data structures สำหรับ development และ UI design รวมถึง checkpoint vehicle tracking system

## Base URL

- **Development:** `http://localhost`
- **Production:** `http://aicamera1` (via Tailscale)

## Authentication

API ใช้ Tailscale authentication โดยอัตโนมัติ

## Performance Optimization

### **Resource Management Strategy**

The system implements a **Core Components Priority** strategy to ensure optimal performance:

#### **High Priority Components (Full Resources)**
```python
# Core camera and detection services maintain full performance
DETECTION_INTERVAL = 0.1  # 10 FPS detection processing
CAMERA_FPS = 30          # 30 FPS video streaming
VIDEO_STREAMING_QUALITY = "high"  # Full quality video
```

#### **Optimized Non-Essential Services**
```python
# Reduced frequency for background services
HEALTH_CHECK_INTERVAL = 7200      # 2 hours (was 1 hour)
SENDER_INTERVAL = 300.0           # 5 minutes (was 1 minute)
HEALTH_SENDER_INTERVAL = 1800.0   # 30 minutes (was 5 minutes)
STORAGE_MONITOR_INTERVAL = 1800   # 30 minutes (was 5 minutes)
```

#### **UI Optimization**
```javascript
// Reduced polling frequency for UI components
statusUpdateThrottle: 30000,      // 30 seconds (was 5 seconds)
videoRefreshCooldown: 15000,      // 15 seconds (was 5 seconds)
dashboardUpdates: 60000,          // 60 seconds (was 10 seconds)
```

### **Performance Monitoring**

#### **CPU Usage Optimization**
- **Before**: 46.6% CPU (high background load)
- **After**: Significantly reduced CPU usage
- **Core components**: Maintained full performance
- **Background services**: Minimal resource impact

#### **Memory Usage Optimization**
- **Before**: 3.4GB memory usage
- **After**: Reduced memory usage
- **Polling frequency**: Optimized for resource efficiency
- **UI updates**: Reduced frequency for better performance

## System Architecture
```
v1_3/src/web/blueprints/
├── main.py              # Main dashboard (/)
├── camera.py            # Camera control (/camera/*)
├── detection.py         # Detection control (/detection/*)
├── detection_results.py # Results viewing (/detection_results/*)
├── health.py            # Health monitoring (/health/*)
├── streaming.py         # Video streaming (/streaming/*)
└── experiments.py       # Experiments (optional)
```

### Service Dependencies
```
Dependency Container:
├── camera_manager       # Camera operations
├── detection_manager    # AI detection
├── database_manager     # Data storage
├── health_service       # System health
├── video_streaming      # Video streaming
└── experiment_service   # Experiments (optional)
```

## REST API Endpoints

### Main Dashboard

#### GET /
Main dashboard page

**Template Variables:**
- `camera_status` (object) - Camera service status and metadata
- `title` (string) - Page title

**Response:** HTML page

#### WebSocket: main_status_request
Request system status

**Response Event:** `main_status_update`
```json
{
  "status": "ok",
  "camera": {...},
  "message": "System status retrieved successfully"
}
```

### Camera APIs

#### GET /camera/
Camera dashboard page

**Template Variables:**
- `camera_status` (object) - Camera service status

**Response:** HTML page

#### GET /camera/status
Camera service status

**Response:**
```json
{
  "success": true,
  "camera_status": {
    "is_running": boolean,
    "camera_handler": {
      "camera_properties": {...},
      "current_config": {...},
      "configuration": {...},
      "sensor_modes": [...],
      "sensor_modes_count": number
    },
    "metadata": {...},
    "frame_count": number,
    "average_fps": number,
    "timestamp": string
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /camera/start
Start camera service

**Response:**
```json
{
  "success": true,
  "message": "Camera started successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /camera/stop
Stop camera service

**Response:**
```json
{
  "success": true,
  "message": "Camera stopped successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /camera/restart
Restart camera service

**Response:**
```json
{
  "success": true,
  "message": "Camera restarted successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET/POST /camera/config
Camera configuration management

**GET Response:**
```json
{
  "success": true,
  "config": {
  "resolution": "1920x1080",
  "fps": 30,
    "exposure": "auto",
    "white_balance": "auto"
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /camera/capture
Capture image

**Response:**
```json
{
  "success": true,
  "image_path": "captured_images/image_20250820_085130.png",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET /camera/metadata
Camera metadata viewer

**Response:** HTML page

#### GET /camera/api/metadata
Camera metadata API

**Response:**
```json
{
  "success": true,
  "camera_status": {...},
  "camera_properties": {...},
  "current_config": {...},
  "camera_controls": {...},
  "frame_metadata": {...},
  "frame_statistics": {
    "frame_count": number,
    "average_fps": number,
    "last_frame_time": string
  },
  "available_modes": [...],
  "sensor_modes_count": number,
  "timestamp": "2025-08-20T08:51:30Z"
}
```

### Detection APIs

#### GET /detection/
Detection dashboard page

**Template Variables:**
- `detection_status` (object) - Detection service status and statistics
- `stats` (object) - Detection statistics from database
- `title` (string) - Page title

**Response:** HTML page

#### GET /detection/status
Detection service status

**Response:**
```json
{
  "success": true,
  "detection_status": {
    "service_running": boolean,
    "detection_processor_status": {
      "models_loaded": boolean,
      "vehicle_model_available": boolean,
      "lp_detection_model_available": boolean,
      "lp_ocr_model_available": boolean,
      "easyocr_available": boolean,
      "confidence_threshold": number,
      "detection_resolution": [number, number]
    },
    "detection_interval": number,
    "auto_start": boolean
  },
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### POST /detection/start
Start detection service

**Response:**
```json
{
  "success": true,
  "message": "Detection service started successfully",
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### POST /detection/stop
Stop detection service

**Response:**
```json
{
  "success": true,
  "message": "Detection service stopped successfully",
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### POST /detection/process_frame
Process single frame for detection

**Response:**
```json
{
  "success": true,
  "detection_result": {
    "vehicles_detected": number,
    "plates_detected": number,
    "processing_time_ms": number,
    "confidence_scores": [...]
  },
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### GET/POST /detection/config
Detection configuration management

**GET Response:**
```json
{
  "success": true,
  "config": {
    "detection_interval": number,
    "vehicle_confidence": number,
    "plate_confidence": number,
    "detection_resolution": [number, number]
  },
  "timestamp": "2025-08-24T10:02:28Z"
}
```

**POST Request:**
```json
{
  "detection_interval": 0.1,
  "vehicle_confidence": 0.5,
  "plate_confidence": 0.3,
  "detection_resolution": [640, 640]
}
```

#### GET /detection/statistics
Detection statistics

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_frames_processed": number,
    "total_vehicles_detected": number,
    "total_plates_detected": number,
    "successful_ocr": number,
    "detection_rate_percent": number,
    "avg_processing_time_ms": number
  },
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### GET /detection/results
All detection results

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": number,
      "timestamp": string,
      "image_path": string,
      "vehicles_detected": number,
      "plates_detected": number,
      "confidence_scores": [...],
      "processing_time_ms": number
    }
  ],
  "count": number,
  "timestamp": "2025-08-24T10:02:28Z"
}
```

#### POST /detection/start
Start detection service

**Response:**
```json
{
  "success": true,
  "message": "Detection service started successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /detection/stop
Stop detection service

**Response:**
```json
{
  "success": true,
  "message": "Detection service stopped successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET/POST /detection/config
Detection configuration

**GET Response:**
```json
{
  "success": true,
  "config": {
    "detection_interval": 0.1,
    "vehicle_confidence": 0.5,
    "plate_confidence": 0.3,
    "detection_resolution": "640x640"
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET /detection/statistics
Detection statistics

**Response:**
```json
{
  "success": true,
  "stats": {
    "total_detections": number,
    "total_vehicles": number,
    "total_plates": number,
    "avg_processing_time_ms": number,
    "last_detection": string
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

### Detection Results APIs

#### GET /detection_results/
Results dashboard page

**Template Variables:**
- `stats` (object) - Detection statistics from database

**Response:** HTML page

#### GET /detection_results/api/results
Paginated results with filters

**Query Parameters:**
- `page` (int, default: 1) - Page number
- `per_page` (int, default: 20, max: 100) - Results per page
- `search` (string) - Search term for OCR/plate text
- `sort_by` (string, default: "created_at") - Column to sort by
- `sort_order` (string, default: "desc") - Sort order (asc/desc)
- `date_from` (string, YYYY-MM-DD) - Start date filter
- `date_to` (string, YYYY-MM-DD) - End date filter
- `has_vehicles` (boolean) - Filter by vehicle presence
- `has_plates` (boolean) - Filter by license plate presence

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": number,
      "timestamp": string,
      "created_at": string,
      "vehicles_count": number,
      "plates_count": number,
      "processing_time_ms": number,
      "ocr_results": [...],
      "vehicle_detections": [...],
      "plate_detections": [...],
      "annotated_image_path": string,
      "cropped_plates_paths": [...]
    }
  ],
  "pagination": {
    "page": number,
    "per_page": number,
    "total": number,
    "pages": number,
    "has_prev": boolean,
    "has_next": boolean
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET /detection_results/api/results/{id}
Single result detail

**Response:**
```json
{
  "success": true,
  "result": {
    "id": number,
    "timestamp": string,
    "created_at": string,
    "vehicles_count": number,
    "plates_count": number,
    "processing_time_ms": number,
    "ocr_results": [
      {
        "text": string,
        "confidence": number,
        "language": string
      }
    ],
    "vehicle_detections": [...],
    "plate_detections": [...],
    "annotated_image_path": string,
    "cropped_plates_paths": [...]
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET /detection_results/api/export
Export results (CSV/JSON)

**Query Parameters:**
- `format` (string, default: "csv") - Export format (csv/json)
- Same filters as `/api/results`

**Response:** File download

#### GET /detection_results/images/{filename}
Serve captured images

**Response:** Image file

### Health APIs

#### GET /health/
Health dashboard page

**Response:** HTML page

#### GET /health/system
System health status

**Response:**
```json
{
  "success": true,
  "health_data": {
    "system_health": {
      "overall_status": string,
      "checks": {...},
      "last_check": string
    },
    "services": {...},
    "resources": {...},
    "timestamp": string
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### GET /health/logs
Health check logs with pagination

**Query Parameters:**
- `level` (string) - Log level filter (PASS/FAIL/WARNING)
- `page` (int, default: 1) - Page number
- `limit` (int, default: 50, max: 100) - Log entries per page

**Response:**
```json
{
  "success": true,
  "logs": [...],
  "pagination": {...},
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /health/check
Run health check

**Response:**
```json
{
  "success": true,
  "check_result": {
    "overall_status": string,
    "checks": {...},
    "timestamp": string
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

### Streaming APIs

#### GET /streaming/
Streaming dashboard page

**Response:** HTML page

#### GET /streaming/status
Streaming service status

**Response:**
```json
{
  "success": true,
  "status": {
    "is_streaming": boolean,
    "stream_url": string,
    "fps": number,
    "resolution": string
  },
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /streaming/start
Start video streaming

**Response:**
```json
{
  "success": true,
  "message": "Streaming started successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

#### POST /streaming/stop
Stop video streaming

**Response:**
```json
{
  "success": true,
  "message": "Streaming stopped successfully",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

## WebSocket Events

### Client → Server Events

#### main_status_request
Request system status

**Data:** None

### Server → Client Events

#### main_status_update
System status update

**Data:**
```json
{
  "status": "ok",
  "camera": {...},
  "message": "System status retrieved successfully"
}
```

#### camera_status_update
Camera status update

**Data:** `camera_status` object

#### detection_status_update
Detection status update

**Data:** `detection_status` object

#### health_status_update
Health status update

**Data:** `health_data` object

## Data Structures

### Camera Status Object
```json
{
  "is_running": boolean,
  "camera_handler": {
    "camera_properties": {...},
    "current_config": {...},
    "configuration": {...},
    "sensor_modes": [...],
    "sensor_modes_count": number
  },
  "metadata": {...},
  "frame_count": number,
  "average_fps": number,
  "timestamp": string
}
```

### Detection Status Object
```json
{
  "is_running": boolean,
  "model_loaded": boolean,
  "current_fps": number,
  "total_detections": number,
  "last_detection": string,
  "processing_time": number,
  "error_count": number,
  "config": {...}
}
```

### Detection Result Object
```json
{
  "id": number,
  "timestamp": string,
  "created_at": string,
  "vehicles_count": number,
  "plates_count": number,
  "processing_time_ms": number,
  "ocr_results": [
    {
      "text": string,
      "confidence": number,
      "language": string
    }
  ],
  "vehicle_detections": [...],
  "plate_detections": [...],
  "annotated_image_path": string,
  "cropped_plates_paths": [...]
}
```

### Health Data Object
```json
{
  "system_health": {
    "overall_status": string,
    "checks": {...},
    "last_check": string
  },
  "services": {...},
  "resources": {...},
  "timestamp": string
}
```

## Template Variables Mapping

| Variable | Type | Description | Available In | Backend Source |
|----------|------|-------------|--------------|----------------|
| `camera_status` | object | Camera service status and metadata | Main, Camera | `camera_manager.get_status()` |
| `detection_status` | object | Detection service status and statistics | Detection | `detection_manager.get_status()` |
| `stats` | object | Detection statistics from database | Detection, Results | `database_manager.get_detection_statistics()` |
| `title` | string | Page title | All pages | Hardcoded in blueprints |

## Detection Dashboard API Reference Extraction Overview

### **Data Flow Architecture**

```
Detection Manager → Detection Blueprint → Dashboard JS → HTML Elements
     ↓                    ↓                    ↓              ↓
  Raw Data           API Response        JS Variables    UI Display
```

### **1. Detection Manager Output (Backend Service)**

#### **DetectionManager.get_status() Output:**
```python
# edge/src/services/detection_manager.py
{
    "service_running": True,
    "detection_processor_status": {
        "models_loaded": True,
        "vehicle_model_available": True,
        "lp_detection_model_available": True,
        "lp_ocr_model_available": True,
        "easyocr_available": True,
        "confidence_threshold": 0.7,
        "detection_resolution": [640, 640]
    },
    "detection_interval": 0.1,
    "auto_start": True,
    "total_frames_processed": 1250,
    "total_vehicles_detected": 45,
    "total_plates_detected": 23,
    "successful_ocr": 18,
    "detection_rate_percent": 85.2,
    "avg_processing_time_ms": 45.3
}
```

#### **DetectionManager.get_statistics() Output:**
```python
# edge/src/services/detection_manager.py
{
    "total_frames_processed": 1250,
    "total_vehicles_detected": 45,
    "total_plates_detected": 23,
    "successful_ocr": 18,
    "detection_rate_percent": 85.2,
    "avg_processing_time_ms": 45.3,
    "last_detection_time": "2025-08-24T10:15:30Z",
    "current_fps": 10.0,
    "error_count": 2,
    "success_rate_percent": 98.4
}
```

### **2. Detection Blueprint Output (API Endpoints)**

#### **GET /detection/status Response:**
```json
{
    "success": true,
    "detection_status": {
        "service_running": true,
        "detection_processor_status": {
            "models_loaded": true,
            "vehicle_model_available": true,
            "lp_detection_model_available": true,
            "lp_ocr_model_available": true,
            "easyocr_available": true,
            "confidence_threshold": 0.7,
            "detection_resolution": [640, 640]
        },
        "detection_interval": 0.1,
        "auto_start": true
    },
    "timestamp": "2025-08-24T10:15:30Z"
}
```

#### **GET /detection/statistics Response:**
```json
{
    "success": true,
    "statistics": {
        "total_frames_processed": 1250,
        "total_vehicles_detected": 45,
        "total_plates_detected": 23,
        "successful_ocr": 18,
        "detection_rate_percent": 85.2,
        "avg_processing_time_ms": 45.3
    },
    "timestamp": "2025-08-24T10:15:30Z"
}
```

#### **GET /detection/config Response:**
```json
{
    "success": true,
    "config": {
        "detection_interval": 0.1,
        "vehicle_confidence": 0.7,
        "plate_confidence": 0.5,
        "detection_resolution": [640, 640]
    },
    "timestamp": "2025-08-24T10:15:30Z"
}
```

#### **GET /detection/results Response:**
```json
{
    "success": true,
    "results": [
        {
            "id": 123,
            "timestamp": "2025-08-24T10:15:25Z",
            "image_path": "captured_images/detection_20250824_101525_123.jpg",
            "vehicles_detected": 2,
            "plates_detected": 1,
            "confidence_scores": [0.85, 0.92],
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
    "count": 1,
    "timestamp": "2025-08-24T10:15:30Z"
}
```

### **3. Dashboard JavaScript Output (Frontend Processing)**

#### **Detection Status Variables (detection.js):**
```javascript
// edge/src/web/static/js/detection.js
const detectionStatus = {
    serviceRunning: true,
    processorStatus: {
        modelsLoaded: true,
        vehicleModelAvailable: true,
        lpDetectionModelAvailable: true,
        lpOcrModelAvailable: true,
        easyocrAvailable: true,
        confidenceThreshold: 0.7,
        detectionResolution: [640, 640]
    },
    detectionInterval: 0.1,
    autoStart: true
};

const detectionStatistics = {
    totalFramesProcessed: 1250,
    totalVehiclesDetected: 45,
    totalPlatesDetected: 23,
    successfulOcr: 18,
    detectionRatePercent: 85.2,
    avgProcessingTimeMs: 45.3
};

const detectionConfig = {
    detectionInterval: 0.1,
    vehicleConfidence: 0.7,
    plateConfidence: 0.5,
    detectionResolution: [640, 640]
};

const recentResults = [
    {
        id: 123,
        timestamp: "2025-08-24T10:15:25Z",
        imagePath: "captured_images/detection_20250824_101525_123.jpg",
        vehiclesDetected: 2,
        platesDetected: 1,
        confidenceScores: [0.85, 0.92],
        processingTimeMs: 45.2,
        ocrResults: [
            {
                text: "ABC123",
                confidence: 0.95,
                language: "en"
            }
        ]
    }
];
```

#### **JavaScript Processing Functions:**
```javascript
// edge/src/web/static/js/detection.js
function updateDetectionStatus(status) {
    // Update service status
    const serviceRunning = status.service_running;
    document.getElementById('service-status').textContent = 
        serviceRunning ? 'Running' : 'Stopped';
    
    // Update models status
    const processorStatus = status.detection_processor_status;
    const modelsLoaded = processorStatus.models_loaded;
    document.getElementById('models-status').textContent = 
        modelsLoaded ? 'Loaded' : 'Not Loaded';
    
    // Update detection interval
    const interval = status.detection_interval;
    document.getElementById('detection-interval').textContent = 
        `${interval}s`;
}

function updateStatistics(stats) {
    document.getElementById('frames-processed').textContent = 
        stats.total_frames_processed;
    document.getElementById('vehicles-detected').textContent = 
        stats.total_vehicles_detected;
    document.getElementById('plates-detected').textContent = 
        stats.total_plates_detected;
    document.getElementById('successful-ocr').textContent = 
        stats.successful_ocr;
    document.getElementById('detection-rate').textContent = 
        `${stats.detection_rate_percent}%`;
    document.getElementById('avg-processing-time').textContent = 
        `${stats.avg_processing_time_ms}ms`;
}

function updateConfigForm(config) {
    document.getElementById('detection-interval').value = 
        config.detection_interval;
    document.getElementById('vehicle-confidence').value = 
        config.vehicle_confidence;
    document.getElementById('plate-confidence').value = 
        config.plate_confidence;
}

function displayRecentResults(results) {
    const resultsContainer = document.getElementById('recent-results');
    resultsContainer.innerHTML = '';
    
    results.forEach(result => {
        const resultElement = createResultElement(result);
        resultsContainer.appendChild(resultElement);
    });
}
```

### **4. HTML Elements and IDs (UI Display)**

#### **Detection Dashboard HTML Structure:**
```html
<!-- edge/src/web/templates/detection/dashboard.html -->
<div class="detection-dashboard">
    <!-- Service Status Section -->
    <div class="card status-card">
        <div class="card-header">
            <h5>Detection Service Status</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-6">
                    <strong>Service Status:</strong>
                    <span id="service-status" class="badge bg-success">Running</span>
                </div>
                <div class="col-md-6">
                    <strong>Models Status:</strong>
                    <span id="models-status" class="badge bg-success">Loaded</span>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-6">
                    <strong>Detection Interval:</strong>
                    <span id="detection-interval">0.1s</span>
                </div>
                <div class="col-md-6">
                    <strong>Auto Start:</strong>
                    <span id="auto-start">Enabled</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Statistics Section -->
    <div class="card">
        <div class="card-header">
            <h5>Detection Statistics</h5>
        </div>
        <div class="card-body">
            <div class="row">
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Frames Processed:</strong>
                        <span id="frames-processed">1250</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Vehicles Detected:</strong>
                        <span id="vehicles-detected">45</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Plates Detected:</strong>
                        <span id="plates-detected">23</span>
                    </div>
                </div>
            </div>
            <div class="row mt-2">
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Successful OCR:</strong>
                        <span id="successful-ocr">18</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Detection Rate:</strong>
                        <span id="detection-rate">85.2%</span>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-item">
                        <strong>Avg Processing Time:</strong>
                        <span id="avg-processing-time">45.3ms</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Configuration Section -->
    <div class="card">
        <div class="card-header">
            <h5>Detection Configuration</h5>
        </div>
        <div class="card-body">
            <form id="detection-config-form">
                <div class="row">
                    <div class="col-md-3">
                        <label for="detection-interval">Detection Interval (s):</label>
                        <input type="number" id="detection-interval" 
                               class="form-control" step="0.1" min="0.1" max="10.0">
                    </div>
                    <div class="col-md-3">
                        <label for="vehicle-confidence">Vehicle Confidence:</label>
                        <input type="number" id="vehicle-confidence" 
                               class="form-control" step="0.1" min="0.1" max="1.0">
                    </div>
                    <div class="col-md-3">
                        <label for="plate-confidence">Plate Confidence:</label>
                        <input type="number" id="plate-confidence" 
                               class="form-control" step="0.1" min="0.1" max="1.0">
                    </div>
                    <div class="col-md-3">
                        <button type="submit" class="btn btn-primary">Update Config</button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Recent Results Section -->
    <div class="card">
        <div class="card-header">
            <h5>Recent Detection Results</h5>
        </div>
        <div class="card-body">
            <div id="recent-results">
                <!-- Results will be dynamically populated -->
            </div>
        </div>
    </div>
</div>
```

### **5. JSON Extraction Data Dictionary**

#### **Complete Data Flow Mapping:**

| **Component** | **Data Source** | **Key Fields** | **HTML ID** | **JavaScript Variable** |
|---------------|-----------------|----------------|-------------|-------------------------|
| **Service Status** | `detection_status.service_running` | `service_running` | `#service-status` | `detectionStatus.serviceRunning` |
| **Models Status** | `detection_status.detection_processor_status.models_loaded` | `models_loaded` | `#models-status` | `detectionStatus.processorStatus.modelsLoaded` |
| **Detection Interval** | `detection_status.detection_interval` | `detection_interval` | `#detection-interval` | `detectionStatus.detectionInterval` |
| **Auto Start** | `detection_status.auto_start` | `auto_start` | `#auto-start` | `detectionStatus.autoStart` |
| **Frames Processed** | `statistics.total_frames_processed` | `total_frames_processed` | `#frames-processed` | `detectionStatistics.totalFramesProcessed` |
| **Vehicles Detected** | `statistics.total_vehicles_detected` | `total_vehicles_detected` | `#vehicles-detected` | `detectionStatistics.totalVehiclesDetected` |
| **Plates Detected** | `statistics.total_plates_detected` | `total_plates_detected` | `#plates-detected` | `detectionStatistics.totalPlatesDetected` |
| **Successful OCR** | `statistics.successful_ocr` | `successful_ocr` | `#successful-ocr` | `detectionStatistics.successfulOcr` |
| **Detection Rate** | `statistics.detection_rate_percent` | `detection_rate_percent` | `#detection-rate` | `detectionStatistics.detectionRatePercent` |
| **Avg Processing Time** | `statistics.avg_processing_time_ms` | `avg_processing_time_ms` | `#avg-processing-time` | `detectionStatistics.avgProcessingTimeMs` |
| **Config Interval** | `config.detection_interval` | `detection_interval` | `#detection-interval` | `detectionConfig.detectionInterval` |
| **Config Vehicle Confidence** | `config.vehicle_confidence` | `vehicle_confidence` | `#vehicle-confidence` | `detectionConfig.vehicleConfidence` |
| **Config Plate Confidence** | `config.plate_confidence` | `plate_confidence` | `#plate-confidence` | `detectionConfig.plateConfidence` |
| **Recent Results** | `results[]` | `id, timestamp, image_path, vehicles_detected, plates_detected` | `#recent-results` | `recentResults[]` |

#### **Data Transformation Rules:**

```javascript
// Backend to Frontend Transformation
const transformDetectionStatus = (apiResponse) => {
    return {
        serviceRunning: apiResponse.detection_status.service_running,
        processorStatus: {
            modelsLoaded: apiResponse.detection_status.detection_processor_status.models_loaded,
            vehicleModelAvailable: apiResponse.detection_status.detection_processor_status.vehicle_model_available,
            lpDetectionModelAvailable: apiResponse.detection_status.detection_processor_status.lp_detection_model_available,
            lpOcrModelAvailable: apiResponse.detection_status.detection_processor_status.lp_ocr_model_available,
            easyocrAvailable: apiResponse.detection_status.detection_processor_status.easyocr_available,
            confidenceThreshold: apiResponse.detection_status.detection_processor_status.confidence_threshold,
            detectionResolution: apiResponse.detection_status.detection_processor_status.detection_resolution
        },
        detectionInterval: apiResponse.detection_status.detection_interval,
        autoStart: apiResponse.detection_status.auto_start
    };
};

const transformStatistics = (apiResponse) => {
    return {
        totalFramesProcessed: apiResponse.statistics.total_frames_processed,
        totalVehiclesDetected: apiResponse.statistics.total_vehicles_detected,
        totalPlatesDetected: apiResponse.statistics.total_plates_detected,
        successfulOcr: apiResponse.statistics.successful_ocr,
        detectionRatePercent: apiResponse.statistics.detection_rate_percent,
        avgProcessingTimeMs: apiResponse.statistics.avg_processing_time_ms
    };
};

const transformConfig = (apiResponse) => {
    return {
        detectionInterval: apiResponse.config.detection_interval,
        vehicleConfidence: apiResponse.config.vehicle_confidence,
        plateConfidence: apiResponse.config.plate_confidence,
        detectionResolution: apiResponse.config.detection_resolution
    };
};
```

#### **Error Handling Data Flow:**

```javascript
// Error Response Structure
const errorResponse = {
    success: false,
    error: "Detection manager not available",
    timestamp: "2025-08-24T10:15:30Z"
};

// Error Display Mapping
const displayError = (errorData) => {
    const errorMessage = errorData.error;
    const timestamp = errorData.timestamp;
    
    // Display in UI
    document.getElementById('error-message').textContent = errorMessage;
    document.getElementById('error-timestamp').textContent = timestamp;
    
    // Log to console
    console.error('Detection API Error:', errorMessage, timestamp);
};
```
| `results` | array | Detection results for display | Results | `database_manager.get_detection_results_paginated()` |
| `pagination` | object | Pagination information | Results | Calculated in blueprints |

## Main Dashboard Status Variables

Key status variables สำหรับ main dashboard display:

- `camera_status.is_running` - Camera service status
- `camera_status.average_fps` - Current FPS
- `camera_status.frame_count` - Total frames processed
- `camera_status.camera_handler.current_config` - Current camera settings
- `detection_status.is_running` - Detection service status
- `detection_status.total_detections` - Total detections made
- `detection_status.current_fps` - Detection FPS
- `stats.total_detections` - Database statistics
- `stats.total_vehicles` - Total vehicles detected
- `stats.total_plates` - Total plates detected
- `health_data.system_health.overall_status` - System health status

## Development Guidelines

### Import Patterns
- ใช้ **absolute imports** จาก `v1_3.src.*`
- ตัวอย่าง: `from v1_3.src.core.dependency_container import get_service`

### Service Access
- เข้าถึง services ผ่าน `get_service('service_name')` จาก dependency container
- ตัวอย่าง: `camera_manager = get_service('camera_manager')`

### API Response Standards
- ทุก response ต้องมี `timestamp` และ `success` fields
- Error responses ต้องมี `error` field พร้อม descriptive message
- ใช้ consistent JSON structure

### Template Variables
- Pass variables explicitly เพื่อ avoid undefined errors
- ใช้ proper error handling ใน blueprints
- ตรวจสอบ service availability ก่อนใช้งาน

### WebSocket Communication
- ใช้ room-based communication สำหรับ real-time updates
- Handle connection errors gracefully
- ใช้ consistent event naming

### Database Operations
- ใช้ `database_manager` service สำหรับ database operations
- ใช้ proper error handling และ logging
- ตรวจสอบ database connection status

### Image Serving
- ใช้ Flask routes สำหรับ image serving (security และ flexibility)
- ตรวจสอบ file existence ก่อน serving
- ใช้ proper content-type headers

## Error Handling

### Common Error Responses
```json
{
  "success": false,
  "error": "Service not available",
  "timestamp": "2025-08-20T08:51:30Z"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Version History

- **v1.3.8** (2025-08-20) - Updated API reference with comprehensive endpoint mapping
- **v1.3.7** - Added detection results APIs and image serving
- **v1.3.6** - Enhanced health monitoring APIs
- **v1.3.5** - Added streaming APIs
- **v1.3.4** - Improved camera metadata APIs
- **v1.3.3** - Initial API structure
