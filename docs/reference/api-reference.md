# AI Camera Edge System - API Reference

**Version:** 2.0.0  
**Last Updated:** 2025-08-23  
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
    "is_running": boolean,
    "model_loaded": boolean,
    "current_fps": number,
    "total_detections": number,
    "last_detection": string,
    "processing_time": number,
    "error_count": number,
    "config": {...}
  },
  "timestamp": "2025-08-20T08:51:30Z"
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
