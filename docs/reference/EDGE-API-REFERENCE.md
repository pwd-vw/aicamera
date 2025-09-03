# AI Camera Edge System - Complete API Reference

**Version:** 2.0.0  
**Last Updated:** 2025-09-02  
**Author:** AI Camera Team  
**Category:** Complete API Documentation  
**Status:** Active

## Overview

Complete API Reference สำหรับ AI Camera Edge System v2.0 รวมรวมข้อมูล REST API endpoints, WebSocket interfaces, และ data structures ที่ใช้งานจริงในโปรเจกต์

## Base URL

- **Development:** `http://localhost:5000`
- **Production:** `http://aicamera1` (via Nginx reverse proxy)

## Authentication

API ใช้ Tailscale authentication โดยอัตโนมัติ

## Architecture Overview

The edge system follows a modular architecture with the following components:

- **Core Services**: Camera Manager, Detection Manager, Health Service, Storage Service, WebSocket Sender
- **Components**: Camera Handler, Detection Processor, Health Monitor, Storage Monitor
- **Web Interface**: Flask Blueprints for each service
- **Dependency Injection**: Centralized service management
- **Auto-Startup**: Sequential service initialization with configurable delays

### Singleton Camera Access Architecture

**🚨 CRITICAL**: The camera system uses a singleton pattern to prevent multiple concurrent access to Picamera2, which does not support multiple processes accessing the camera simultaneously.

#### Camera Access Pattern:
- **CameraHandler**: Singleton low-level camera operations (Picamera2 interface)
- **CameraManager**: High-level camera service management (accesses CameraHandler)
- **Frame Buffer System**: Single capture thread provides frames and metadata to all consumers
- **Other Components**: Access camera data ONLY through CameraManager, never directly to CameraHandler

#### Frame Buffer System:
- **Single Capture Thread**: Continuously captures main and lores frames + metadata
- **Thread-Safe Buffers**: Shared memory for frames and metadata
- **Multiple Consumers**: Detection Manager, Video Streaming, Health Monitor read from buffers
- **No Direct Access**: Components use `get_main_frame()`, `get_lores_frame()`, `get_cached_metadata()`

#### Component Access Rules:
- ✅ **Detection Manager**: Uses `camera_manager.capture_frame()` for main stream
- ✅ **Video Streaming**: Uses `camera_manager.capture_lores_frame()` for web interface
- ✅ **Health Monitor**: Gets status from `camera_manager.get_status()`
- ✅ **Metadata Access**: Uses `camera_manager.get_status()` for camera metadata
- ❌ **Direct Camera Access**: Never call `picam2.capture_request()` directly
- ❌ **Multiple Processes**: Never access CameraHandler from multiple processes

## Response Format Standards

### Standard Response Structure
All API responses follow this consistent format:

```json
{
  "success": true/false,
  "message": "descriptive message",
  "status": {...},     // for status data
  "data": {...},       // for response data
  "error": "error message",  // for error responses
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### WebSocket Event Standards
All WebSocket events follow the same response format:

```json
{
  "success": true/false,
  "message": "descriptive message",
  "status": {...},     // for status data
  "config": {...},     // for configuration data
  "error": "error message",  // for error responses
  "timestamp": "2025-09-02T10:30:00Z"
}
```

## REST API Endpoints

### Main Dashboard

#### GET /
Main dashboard with comprehensive system status monitoring and control.

**Features:**
- Real-time status indicators for all system components
- Toggle show/hide functionality for System Information and Development Reference sections
- Health monitor status with detailed explanations
- Server connection status with priority-based display
- Accessibility-compliant UI with proper ARIA labels

**Status Indicators:**
- **Health Monitor Status:**
  - Online (Green): "ตรวจสอบทุก 60 วินาที"
  - Warning/Offline: Specific reasons (Camera not initialized, AI models not loaded, Database disconnected, System resources critical)
- **Server Connection Status Priority:**
  - Connected (Green) - Highest priority
  - Offline Mode (Yellow) - Medium priority
  - Disconnected (Yellow) - Medium priority  
  - Not Running (Red) - Lowest priority

**Template Variables:**
- `camera_status` (object) - Camera service status and metadata
- `title` (string) - Page title

**Response:** HTML page

### Camera Management APIs

#### GET /camera/
Camera dashboard page with video feed and controls.

**Template Variables:**
- `camera_status` (object) - Camera service status

**Response:** HTML page

#### GET /camera/status
Get current camera status and metadata.

**Response:**
```json
{
  "success": true,
  "status": {
    "initialized": true,
    "streaming": true,
    "frame_count": 1234,
    "average_fps": 29.5,
    "uptime": 3600.5,
    "auto_start_enabled": true,
    "auto_streaming_enabled": true,
    "config": {
      "buffer_count": 4,
      "colour_space": "RGB888",
      "controls": {
        "FrameDurationLimits": [33333, 33333],
        "NoiseReductionMode": "Fast"
      },
      "main": {
        "format": "RGB888",
        "framesize": 2764800,
        "preserve_ar": true,
        "size": [1280, 720],
        "stride": 3840
      }
    },
    "camera_handler": {
      "initialized": true,
      "streaming": true,
      "frame_count": 1234,
      "average_fps": 29.5,
      "recording": false,
      "sensor_modes_count": 4,
      "current_config": {
        "main": {
          "size": [1280, 720],
          "format": "RGB888"
        },
        "controls": {
          "FrameDurationLimits": [33333, 33333]
        }
      },
      "camera_properties": {
        "Model": "imx708",
        "Location": 2,
        "ColorFilterArrangement": 0,
        "PixelArraySize": [4608, 2592]
      }
    }
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /camera/start
Start camera service.

**Response:**
```json
{
  "success": true,
  "message": "Camera started successfully",
  "status": {
    "initialized": true,
    "streaming": true
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /camera/stop
Stop camera service.

**Response:**
```json
{
  "success": true,
  "message": "Camera stopped successfully",
  "status": {
    "initialized": true,
    "streaming": false
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /camera/restart
Restart camera service.

**Response:**
```json
{
  "success": true,
  "message": "Camera restarted successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET/POST /camera/config
Camera configuration management.

**GET Response:**
```json
{
  "success": true,
  "config": {
    "resolution": [1280, 720],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

**POST Request:**
```json
{
  "resolution": [1920, 1080],
  "framerate": 30,
  "brightness": 0.0,
  "contrast": 1.0,
  "saturation": 1.0,
  "awb_mode": "auto"
}
```

#### POST /camera/capture
Manual image capture (Added 2025-09-02).

**Response:**
```json
{
  "success": true,
  "message": "Image captured successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

**Features:**
- Saves to `/edge/manual_capture/` directory
- Filename format: `manual_capture_YYYYMMDD_HHMMSS.jpg`
- Real-time UI feedback with loading states

#### GET /camera/health
Camera health check endpoint.

**Response:**
```json
{
  "success": true,
  "health": {
    "camera_initialized": true,
    "camera_streaming": true,
    "frame_buffer_ready": true
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/video_feed
MJPEG video stream from main camera.

**Response:** `multipart/x-mixed-replace` stream
```
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
Content-Type: image/jpeg

[JPEG image data]
--frame
...
```

#### GET /camera/ml_frame
Get single frame for ML processing.

**Response:**
```json
{
  "success": true,
  "frame_data": "base64_encoded_image",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/debug
Camera debug information.

**Response:**
```json
{
  "success": true,
  "debug_info": {
    "camera_available": true,
    "hardware_status": "OK",
    "software_status": "OK"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/metadata
Camera metadata viewer page.

**Response:** HTML page

#### GET /camera/debug_metadata
Debug camera metadata.

**Response:**
```json
{
  "success": true,
  "debug_info": {
    "camera_properties": {...},
    "current_config": {...},
    "camera_status": {...},
    "manager_status": {...}
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/api/metadata
Camera metadata API.

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
    "frame_count": 1234,
    "average_fps": 29.5,
    "last_frame_time": "2025-09-02T10:30:00Z"
  },
  "available_modes": [...],
  "sensor_modes_count": 4,
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/api/experimental_metadata
Comprehensive experimental metadata.

**Response:**
```json
{
  "success": true,
  "experimental_metadata": {
    "timing": {...},
    "exposure": {...},
    "color": {...},
    "focus": {...},
    "sensor": {...},
    "quality": {...},
    "performance": {...},
    "camera_properties": {...},
    "configuration": {...},
    "experimental": {...},
    "raw_metadata": {...}
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/api/metadata_summary
Metadata summary for efficiency.

**Response:**
```json
{
  "success": true,
  "metadata_summary": {
    "camera_status": {...},
    "image_quality": {...},
    "performance_metrics": {...},
    "camera_settings": {...},
    "experimental_indicators": {...}
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/test
Test camera functionality.

**Response:**
```json
{
  "success": true,
  "test_results": {
    "handler_initialized": true,
    "handler_streaming": true,
    "manager_initialized": true,
    "manager_streaming": true,
    "auto_start_enabled": true,
    "uptime": 3600.5
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/video_test
Test video feed functionality.

**Response:**
```json
{
  "success": true,
  "video_test_results": {
    "camera_initialized": true,
    "camera_streaming": true,
    "frame_capture_success": true,
    "frame_shape": [720, 1280, 3],
    "frame_error": null,
    "video_feed_url": "/camera/video_feed",
    "video_feed_lores_url": "/camera/video_feed_lores"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/video_streaming_status
Video streaming status.

**Response:**
```json
{
  "success": true,
  "streaming_status": {
    "active": true,
    "connected_clients": 2,
    "fps": 30
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /camera/video_streaming_reset
Reset video streaming.

**Response:**
```json
{
  "success": true,
  "message": "Video streaming reset successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/browser_connections
Get browser connection information.

**Response:**
```json
{
  "success": true,
  "connections": [...],
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /camera/browser_connections/clear
Clear browser connection tracking.

**Response:**
```json
{
  "success": true,
  "message": "Browser connections cleared",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/video_feed/health
Video feed health check.

**Response:**
```json
{
  "success": true,
  "health": {
    "feed_active": true,
    "frame_rate": 30
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /camera/video_feed/debug
Video feed debug information.

**Response:**
```json
{
  "success": true,
  "debug_info": {
    "stream_active": true,
    "client_count": 2
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Detection Management APIs

#### GET /detection/
Detection dashboard page.

**Template Variables:**
- `detection_status` (object) - Detection service status and statistics
- `stats` (object) - Detection statistics from database
- `title` (string) - Page title

**Response:** HTML page

#### GET /detection/status
Get detection service status.

**Response:**
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
      "plate_confidence_threshold": 0.5,
      "detection_resolution": [640, 640]
    },
    "detection_interval": 0.1,
    "auto_start": true,
    "statistics": {
      "total_frames_processed": 6023,
      "total_vehicles_detected": 512,
      "total_plates_detected": 260,
      "successful_ocr": 180,
      "failed_detections": 512,
      "processing_time_avg": 0.045,
      "last_detection": "2025-09-02T18:20:30.123456",
      "started_at": "2025-09-02T18:08:03.714003"
    },
    "queue_size": 0,
    "thread_alive": true,
    "last_update": "2025-09-02T18:20:35.601884"
  },
  "timestamp": "2025-09-02T18:20:35.601904"
}
```

Notes:
- `statistics.processing_time_avg` is seconds; frontend derives `avg_processing_time_ms = processing_time_avg * 1000` when `avg_processing_time_ms` is not provided.
- WebSocket `detection_status_update` emits the status object directly (not wrapped in `{ detection_status: ... }`).

#### POST /detection/start
Start detection service.

**Response:**
```json
{
  "success": true,
  "message": "Detection started successfully",
  "status": {
    "service_running": true,
    "detection_active": true
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /detection/stop
Stop detection service.

**Response:**
```json
{
  "success": true,
  "message": "Detection stopped successfully",
  "status": {
    "service_running": true,
    "detection_active": false
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /detection/process_frame
Process single frame for detection.

**Response:**
```json
{
  "success": true,
  "detection_result": {
    "vehicles_detected": 2,
    "plates_detected": 1,
    "processing_time_ms": 45.2,
    "confidence_scores": [0.85, 0.92]
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET/POST /detection/config
Detection configuration management.

**GET Response:**
```json
{
  "success": true,
  "config": {
    "detection_interval": 0.1,
    "vehicle_confidence": 0.7,
    "plate_confidence": 0.5,
    "detection_resolution": [640, 640]
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

**POST Request:**
```json
{
  "detection_interval": 0.1,
  "vehicle_confidence": 0.8,
  "plate_confidence": 0.6,
  "detection_resolution": [640, 640]
}
```

#### GET /detection/statistics
Detection statistics.

**Response:**
```json
{
  "success": true,
  "statistics": {
    "total_detections": 120,
    "total_vehicles": 45,
    "total_plates": 23,
    "successful_ocr": 18,
    "avg_processing_time_ms": 45.3,
    "last_detection": "2025-09-02T10:25:00Z",
    "plate_detection_rate_percent": 51.11,
    "ocr_success_rate_percent": 78.26
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

หมายเหตุ:
- `plate_detection_rate_percent` = (total_plates / total_vehicles) × 100
- `ocr_success_rate_percent` = (successful_ocr / total_plates) × 100

#### GET /detection/results
Get all detection results (ข้อมูลล่าสุดจากฐานข้อมูล)

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "id": 123,
      "timestamp": "2025-09-02T10:15:25Z",
      "vehicles_count": 2,
      "plates_count": 1,
      "original_image_path": "captured_images/detection_20250902_101525_123.jpg",
      "vehicle_detected_image_path": "",
      "plate_image_path": "",
      "cropped_plates_paths": [],
      "ocr_results": [
        {
          "text": "ABC123",
          "confidence": 0.95,
          "language": "en",
          "method": "hailo"
        }
      ],
      "processing_time_ms": 45.2,
      "created_at": "2025-09-02T10:15:25Z"
    }
  ],
  "count": 1,
  "timestamp": "2025-09-02T10:15:30Z"
}
```

#### GET /detection/results/{id}
Get specific detection result by ID.

**Parameters:**
- `id` (integer): Detection result ID

**Response:**
```json
{
  "success": true,
  "result": {
    "id": 123,
    "timestamp": "2025-09-02T10:15:25Z",
    "vehicles_count": 2,
    "plates_count": 1,
    "original_image_path": "captured_images/detection_20250902_101525_123.jpg",
    "vehicle_detected_image_path": "",
    "plate_image_path": "",
    "cropped_plates_paths": [],
    "ocr_results": [...],
    "processing_time_ms": 45.2,
    "created_at": "2025-09-02T10:15:25Z"
  },
  "timestamp": "2025-09-02T10:15:30Z"
}
```

#### GET /detection/models/status
Detection models status.

**Response:**
```json
{
  "success": true,
  "models_status": {
    "vehicle_model_loaded": true,
    "plate_detection_model_loaded": true,
    "plate_ocr_model_loaded": true,
    "easyocr_loaded": true
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /detection/update-config
Update detection configuration.

**Request:**
```json
{
  "detection_interval": 0.1,
  "confidence_threshold": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Health Monitoring APIs

#### GET /health/
Health dashboard page (serves both HTML and JSON based on Accept header).

**Browser Request:** Returns HTML dashboard  
**API Request:** Returns JSON health data (when Accept: application/json header is present)

**Response:** HTML page or JSON data

#### GET /health/system
Comprehensive system health status.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "components": {
      "camera": {
        "status": "healthy",
        "initialized": true,
        "streaming": true,
        "frame_count": 1234,
        "average_fps": 29.5,
        "uptime": 3600,
        "auto_start_enabled": true,
        "last_check": "2025-09-02T10:30:00Z"
      },
      "detection": {
        "status": "healthy",
        "models_loaded": true,
        "easyocr_available": true,
        "detection_active": true,
        "service_running": true,
        "thread_alive": true,
        "auto_start": true,
        "last_check": "2025-09-02T10:30:00Z"
      },
      "database": {
        "status": "healthy",
        "connected": true,
        "database_path": "/home/camuser/aicamera/edge/db/lpr_data.db",
        "last_check": "2025-09-02T10:30:00Z"
      },
      "system": {
        "status": "healthy",
        "cpu_usage": 25.5,
        "memory_usage": {
          "used": 6.2,
          "total": 15.84,
          "percentage": 39.1
        },
        "disk_usage": {
          "used": 20.64,
          "total": 57.44,
          "percentage": 35.9
        },
        "uptime": 86400,
        "last_check": "2025-09-02T10:30:00Z"
      }
    },
    "system": {
      "cpu_info": {
        "architecture": "aarch64",
        "processor": "Unknown",
        "model": "Raspberry Pi 5 Model B Rev 1.0",
        "cores": 4,
        "frequency": "2400 MHz",
        "usage_percent": 25.5
      },
      "cpu_usage": 25.5,
      "cpu_count": 4,
      "memory_usage": {
        "used": 6.2,
        "total": 15.84,
        "percentage": 39.1
      },
      "disk_usage": {
        "used": 20.64,
        "total": 57.44,
        "percentage": 35.9
      },
      "uptime": 86400,
      "os_info": {
        "name": "Linux",
        "distribution": "Debian GNU/Linux 12 (bookworm)",
        "kernel_version": "6.12.34+rpt-rpi-2712",
        "architecture": "aarch64"
      },
      "ai_accelerator_info": {
        "device_architecture": "HAILO8",
        "firmware_version": "4.18.0",
        "board_name": "Hailo-8",
        "status": "Available"
      }
    },
    "error_details": null,
    "last_check": "2025-09-02T10:30:00Z"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /health/logs
Health check logs with pagination.

**Query Parameters:**
- `level` (string, optional): Log level filter (PASS, FAIL, WARNING)
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Number of log entries per page (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-09-02T10:30:00Z",
        "level": "PASS",
        "module": "Camera",
        "message": "Camera working normally",
        "details": "{}"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 30,
      "total_count": 1500,
      "per_page": 50,
      "has_next": true,
      "has_prev": false
    },
    "level_filter": "PASS"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /health/system-info
System information without running health checks.

**Response:**
```json
{
  "success": true,
  "data": {
    "system": {
      "cpu_info": {...},
      "memory_usage": {...},
      "disk_usage": {...},
      "uptime": 86400,
      "os_info": {...},
      "ai_accelerator_info": {...}
    }
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /health/status
Health service status.

**Response:**
```json
{
  "success": true,
  "status": {
    "initialized": true,
    "monitoring": false,
    "last_check": "2025-09-02T10:30:00Z"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Storage Management APIs

#### GET /storage/
Storage dashboard page.

**Response:** HTML page

#### GET /storage/status
Storage management status.

**Response:**
```json
{
  "success": true,
  "data": {
    "disk_usage": {
      "total_gb": 57.44,
      "used_gb": 20.64,
      "free_gb": 36.80,
      "used_percent": 35.9
    },
    "folder_stats": {
      "total_files": 1234,
      "total_size_gb": 15.6,
      "oldest_file": "2025-08-13T10:00:00Z",
      "newest_file": "2025-09-02T10:00:00Z"
    },
    "file_counts": {
      "sent_files": 890,
      "unsent_files": 344,
      "total_files": 1234
    },
    "cleanup_stats": {
      "files_deleted": 45,
      "space_freed_gb": 2.3,
      "last_cleanup": "2025-09-02T09:00:00Z"
    },
    "configuration": {
      "folder_path": "/home/camuser/aicamera/edge/captured_images",
      "min_free_space_gb": 10.0,
      "retention_days": 7,
      "batch_size": 100,
      "monitor_interval": 300
    },
    "status": {
      "running": true,
      "last_cleanup": "2025-09-02T09:00:00Z",
      "needs_cleanup": false
    }
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /storage/analytics
Storage analytics data.

**Response:**
```json
{
  "success": true,
  "analytics": {
    "daily_stats": [...],
    "weekly_trends": [...],
    "storage_efficiency": 85.2
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /storage/alerts
Storage alerts.

**Response:**
```json
{
  "success": true,
  "alerts": [
    {
      "type": "warning",
      "message": "Low disk space",
      "timestamp": "2025-09-02T10:30:00Z"
    }
  ],
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /storage/cleanup
Manual storage cleanup.

**Response:**
```json
{
  "success": true,
  "message": "Storage cleanup completed successfully",
  "data": {
    "files_deleted": 45,
    "space_freed_gb": 2.3,
    "sent_files_deleted": 30,
    "unsent_files_deleted": 15,
    "errors": 0,
    "duration_ms": 1500
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET/POST /storage/config
Storage configuration management.

**GET Response:**
```json
{
  "success": true,
  "config": {
    "min_free_space_gb": 10.0,
    "retention_days": 7,
    "monitor_interval": 300
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /storage/monitor/start
Start storage monitoring.

**Response:**
```json
{
  "success": true,
  "message": "Storage monitoring started",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /storage/monitor/stop
Stop storage monitoring.

**Response:**
```json
{
  "success": true,
  "message": "Storage monitoring stopped",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /storage/alerts/clear
Clear storage alerts.

**Response:**
```json
{
  "success": true,
  "message": "Storage alerts cleared",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### WebSocket Sender APIs

#### GET /websocket-sender/
WebSocket sender dashboard page.

**Response:** HTML page

#### GET /websocket-sender/status
WebSocket sender status.

**Response:**
```json
{
  "success": true,
  "status": {
    "enabled": true,
    "running": true,
    "connected": false,
    "server_url": null,
    "server_type": "unknown",
    "offline_mode": true,
    "aicamera_id": "1",
    "checkpoint_id": "1",
    "retry_count": 0,
    "total_detections_sent": 0,
    "total_health_sent": 0,
    "last_detection_check": null,
    "last_health_check": null,
    "detection_thread_alive": true,
    "health_thread_alive": true
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /websocket-sender/logs
WebSocket sender logs.

**Query Parameters:**
- `page` (int, optional): Page number (default: 1)
- `limit` (int, optional): Number of records (default: 50)
- `filter` (string, optional): Filter by action type

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-09-02T10:30:00Z",
        "action": "send_detection",
        "status": "offline",
        "message": "Processing 5 detection records locally (offline mode)",
        "data_type": "detection_results",
        "record_count": 5,
        "aicamera_id": "1",
        "checkpoint_id": "1"
      }
    ],
    "total_count": 150,
    "page": 1,
    "limit": 50
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /websocket-sender/start
Start WebSocket sender service.

**Response:**
```json
{
  "success": true,
  "message": "WebSocket sender started successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /websocket-sender/stop
Stop WebSocket sender service.

**Response:**
```json
{
  "success": true,
  "message": "WebSocket sender stopped successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /websocket-sender/connection-test
Test WebSocket connection.

**Response:**
```json
{
  "success": true,
  "test_result": {
    "connection_successful": false,
    "error": "Connection timeout"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /websocket-sender/clear-logs
Clear WebSocket sender logs.

**Response:**
```json
{
  "success": true,
  "message": "Logs cleared successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Streaming APIs

#### GET /streaming/
Streaming dashboard page.

**Response:** HTML page

#### GET /streaming/status
Streaming service status.

**Response:**
```json
{
  "success": true,
  "status": {
    "is_streaming": true,
    "stream_url": "/camera/video_feed",
    "fps": 30,
    "resolution": "1280x720"
  },
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /streaming/start
Start video streaming.

**Response:**
```json
{
  "success": true,
  "message": "Streaming started successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### POST /streaming/stop
Stop video streaming.

**Response:**
```json
{
  "success": true,
  "message": "Streaming stopped successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Experiments APIs (Optional)

#### GET /experiments/
Experiments dashboard page.

**Response:** HTML page

#### GET/POST /experiments/new
Create new experiment.

**Response:** HTML page or JSON data

#### GET /experiments/run/{experiment_id}
Run specific experiment.

**Response:** HTML page

#### POST /experiments/api/run_step/{experiment_id}
Run experiment step.

**Response:**
```json
{
  "success": true,
  "result": {...},
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /experiments/results/{experiment_id}
Get experiment results.

**Response:** HTML page

#### GET /experiments/api/experiments
Get all experiments.

**Response:**
```json
{
  "success": true,
  "experiments": [...],
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /experiments/api/experiment/{experiment_id}
Get specific experiment.

**Response:**
```json
{
  "success": true,
  "experiment": {...},
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### GET /experiments/api/summary/{experiment_id}
Get experiment summary.

**Response:**
```json
{
  "success": true,
  "summary": {...},
  "timestamp": "2025-09-02T10:30:00Z"
}
```

## WebSocket Events

### Connection
```javascript
// Connect to WebSocket
const socket = io();

// Connection events
socket.on('connect', function() {
    console.log('Connected to WebSocket server');
});

socket.on('disconnect', function() {
    console.log('Disconnected from WebSocket server');
});
```

### Camera Events

#### Client to Server
```javascript
// Request camera status
socket.emit('camera_status_request', {});

// Camera control
socket.emit('camera_control', {
    command: 'start' // 'start', 'stop', 'restart', 'capture'
});

// Configuration update
socket.emit('camera_config_update', {
    config: {
        resolution: [1920, 1080],
        framerate: 30,
        brightness: 0.0
    }
});
```

#### Server to Client
```javascript
// Camera status updates
socket.on('camera_status_update', function(status) {
    console.log('Camera status:', status);
});

// Camera control response
socket.on('camera_control_response', function(response) {
    console.log('Camera control result:', response);
});

// Configuration response
socket.on('camera_config_response', function(response) {
    console.log('Configuration update result:', response);
});
```

### Detection Events

#### Client to Server
```javascript
// Detection control
socket.emit('detection_control', {
    command: 'start' // 'start', 'stop'
});

// Request detection status
socket.emit('detection_status_request', {});
```

#### Server to Client
```javascript
// Detection status updates (status object is emitted directly)
socket.on('detection_status_update', function(status) {
    console.log('Detection status:', status);
});

// Detection results (real-time)
socket.on('detection_result', function(result) {
    console.log('New detection result:', result);
});
```

### Health Events

#### Client to Server
```javascript
// Request health status
socket.emit('health_status_request', {});

// Request health logs
socket.emit('health_logs_request', {
    level: 'PASS',
    page: 1,
    limit: 50
});

// Start health monitoring
socket.emit('health_monitor_start', {
    interval: 60
});

// Stop health monitoring
socket.emit('health_monitor_stop', {});

// Run health check
socket.emit('health_check_run', {});

// Join health monitoring room
socket.emit('join_health_room', {});

// Leave health monitoring room
socket.emit('leave_health_room', {});
```

#### Server to Client
```javascript
// Health status updates
socket.on('health_status_update', function(health) {
    console.log('Health status:', health);
});

// Health logs updates
socket.on('health_logs_update', function(logs) {
    console.log('Health logs:', logs);
});

// Health monitor response
socket.on('health_monitor_response', function(response) {
    console.log('Health monitor response:', response);
});

// Health check response
socket.on('health_check_response', function(response) {
    console.log('Health check response:', response);
});

// Health room joined
socket.on('health_room_joined', function(response) {
    console.log('Joined health room:', response);
});

// Health room left
socket.on('health_room_left', function(response) {
    console.log('Left health room:', response);
});
```

## UI Dashboard Enhancements (Added 2025-09-02)

### Toggle Functionality
The main dashboard includes toggle show/hide functionality for content sections:

#### Toggle Controls:
- **System Info**: Toggle System Information section
- **Development Reference**: Toggle Development Reference section  
- **Show All**: Show all sections
- **Hide All**: Hide all sections

#### JavaScript Variables:
```javascript
// Toggle state management
let systemInfoVisible = true;
let developmentRefVisible = true;

// Toggle elements mapping
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
```

### Health Monitor Status Display
Enhanced health monitor status with detailed explanations:

#### Status Messages:
- **Online (Green)**: "ตรวจสอบทุก 60 วินาที"
- **Warning/Offline**: Specific reasons based on component status

#### Status Detail Messages:
```javascript
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

### Server Connection Status Priority
Enhanced server connection status with 4-tier priority system:

#### Priority Levels:
1. **Connected** (Green) - Highest priority
2. **Offline Mode** (Yellow) - Medium priority
3. **Disconnected** (Yellow) - Medium priority  
4. **Not Running** (Red) - Lowest priority

#### JavaScript Implementation:
```javascript
const connectionStatusPriority = {
    'connected': {
        className: 'status-indicator status-online',
        text: 'Connected',
        priority: 1
    },
    'offline_mode': {
        className: 'status-indicator status-warning', 
        text: 'Offline Mode',
        priority: 2
    },
    'disconnected': {
        className: 'status-indicator status-warning',
        text: 'Disconnected', 
        priority: 3
    },
    'not_running': {
        className: 'status-indicator status-offline',
        text: 'Not Running',
        priority: 4
    }
};
```

### Data Sending Status
Data sending status with condition-based mapping:

#### Status Levels:
1. **Active** (Green): `status.running && (status.total_detections_sent > 0 || status.total_health_sent > 0)`
2. **Ready** (Yellow): `status.running` but no data sent
3. **Inactive** (Red): `status.running = false`

### Accessibility Enhancements
All UI elements include proper accessibility attributes:

#### Accessibility Attributes:
```html
<button title="Toggle System Information content visibility"
        aria-label="Toggle System Information content visibility"
        aria-expanded="true"
        aria-controls="system-info-content">
```

## Performance Optimizations (Updated 2025-09-02)

### Cache-Control Headers
Optimized cache-control headers for better performance:

```python
# Optimized headers
{
    'Cache-Control': 'no-cache'  # Simplified from complex directives
    # Removed deprecated 'Pragma': 'no-cache'
    # Removed conflicting 'Expires': '0'
}
```

### CSS Performance
Optimized animations using transform instead of left property:

```css
/* GPU-accelerated animations */
@keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

@keyframes loading {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Button hover effects */
.btn::before {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
```

### Browser Compatibility
Added vendor prefixes for cross-browser support:

```css
/* Safari support */
-webkit-backdrop-filter: blur(5px);
backdrop-filter: blur(5px);

-webkit-user-select: none;
user-select: none;

text-align: match-parent;
text-align: -webkit-match-parent;
```

## Manual Capture System (เพิ่มเมื่อ 2025-09-02)

### ความสามารถในการ Capture แบบ Manual
ระบบบันทึกภาพแบบ Manual ถูกเชื่อมต่อกับหน้า Camera Dashboard:

#### Endpoint: POST /camera/capture
**คุณสมบัติ:**
- บันทึกไฟล์ภาพลงในโฟลเดอร์ `/edge/manual_capture/`
- ชื่อไฟล์รูปแบบ `manual_capture_YYYYMMDD_HHMMSS.jpg`
- มีสถานะแจ้งเตือนและโหลดดิ้งใน UI แบบเรียลไทม์
- แสดงข้อความผลลัพธ์สำเร็จ/ล้มเหลวให้ผู้ใช้ทราบ

#### Response:
```json
{
  "success": true,
  "message": "Image captured successfully",
  "timestamp": "2025-09-02T10:30:00Z"
}
```

#### Frontend Integration:
```javascript
function captureImage() {
    // Show loading state
    // HTTP POST request to /camera/capture
    // Display success/error message
    // Provide user guidance
}
```

## Data Structures

### Camera Status Object
```json
{
  "initialized": true,
  "streaming": true,
  "frame_count": 1234,
  "average_fps": 29.5,
  "uptime": 3600.5,
  "auto_start_enabled": true,
  "camera_handler": {
    "camera_properties": {...},
    "current_config": {...},
    "configuration": {...},
    "sensor_modes": [...],
    "sensor_modes_count": 4
  },
  "metadata": {...},
  "timestamp": "2025-09-02T10:30:00Z"
}
```

### Detection Status Object
```json
{
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
  "auto_start": true,
  "statistics": {
    "total_frames_processed": 0,
    "total_vehicles_detected": 0,
    "total_plates_detected": 0,
    "successful_ocr": 0,
    "failed_detections": 0,
    "processing_time_avg": 0.0,
    "last_detection": null,
    "started_at": "2025-09-02T18:08:03.714003"
  },
  "queue_size": 0,
  "thread_alive": true,
  "last_update": "2025-09-02T18:20:35.601884"
}
```

### Health Data Object
```json
{
  "overall_status": "healthy",
  "components": {
    "camera": {
      "status": "healthy",
      "initialized": true,
      "streaming": true,
      "last_check": "2025-09-02T10:30:00Z"
    },
    "detection": {
      "status": "healthy",
      "models_loaded": true,
      "detection_active": true,
      "last_check": "2025-09-02T10:30:00Z"
    },
    "database": {
      "status": "healthy",
      "connected": true,
      "last_check": "2025-09-02T10:30:00Z"
    },
    "system": {
      "status": "healthy",
      "cpu_usage": 25.5,
      "memory_usage": {...},
      "disk_usage": {...},
      "last_check": "2025-09-02T10:30:00Z"
    }
  },
  "system": {...},
  "error_details": null,
  "last_check": "2025-09-02T10:30:00Z"
}
```

### Detection Result Object
```json
{
  "id": 123,
  "timestamp": "2025-09-02T10:15:25Z",
  "vehicles_count": 2,
  "plates_count": 1,
  "original_image_path": "captured_images/detection_20250902_101525_123.jpg",
  "vehicle_detected_image_path": "captured_images/vehicle_detected_20250902_101525_123.jpg",
  "plate_image_path": "captured_images/plate_detected_20250902_101525_123.jpg",
  "cropped_plates_paths": [
    "captured_images/plate_20250902_101525_123_0.jpg"
  ],
  "ocr_results": [
    {
      "text": "ABC123",
      "confidence": 0.95,
      "language": "en",
      "method": "hailo"
    }
  ],
  "processing_time_ms": 45.2,
  "created_at": "2025-09-02T10:15:25Z"
}
```

## Variable Naming Conventions

| Layer | Convention | Example |
|-------|------------|---------|
| **Backend (Python)** | `snake_case` | `camera_status`, `frame_count`, `average_fps` |
| **Frontend (JavaScript)** | `camelCase` | `cameraStatus`, `frameCount`, `averageFps` |
| **API Endpoints** | `snake_case` | `/camera/status`, `/detection/start` |
| **HTML Element IDs** | `kebab-case` | `main-camera-status`, `feature-camera-model` |

## Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `CAMERA_NOT_INITIALIZED` | Camera not initialized | 500 |
| `CAMERA_NOT_STREAMING` | Camera not streaming | 500 |
| `CAMERA_BUSY` | Camera is busy with another operation | 409 |
| `CONFIGURATION_FAILED` | Configuration update failed | 400 |
| `DETECTION_NOT_AVAILABLE` | AI detection service not available | 503 |
| `MODEL_NOT_LOADED` | AI models not loaded | 503 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `INVALID_PARAMETER` | Invalid parameter provided | 400 |
| `SERVICE_UNAVAILABLE` | Service temporarily unavailable | 503 |
| `OPERATION_FAILED` | Generic operation failure | 500 |

## Rate Limiting

| Endpoint Category | Limit | Window |
|-------------------|-------|---------|
| Camera Control | 10 requests | 1 minute |
| Status Requests | 60 requests | 1 minute |
| Configuration Updates | 5 requests | 1 minute |
| Detection Control | 10 requests | 1 minute |

## Configuration Values

### Camera Configuration
```json
{
  "DEFAULT_RESOLUTION": [1280, 720],
  "DEFAULT_FRAMERATE": 30,
  "DEFAULT_BRIGHTNESS": 0.0,
  "DEFAULT_CONTRAST": 1.0,
  "DEFAULT_SATURATION": 1.0,
  "DEFAULT_SHARPNESS": 1.0,
  "DEFAULT_AWB_MODE": 0
}
```

### Detection Configuration
```json
{
  "DETECTION_INTERVAL": 0.1,
  "CONFIDENCE_THRESHOLD": 0.8,
  "PLATE_CONFIDENCE_THRESHOLD": 0.6,
  "VEHICLE_DETECTION_MODEL": "yolov8n_relu6_car--640x640_quant_hailort_hailo8_1",
  "LICENSE_PLATE_DETECTION_MODEL": "yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1",
  "LICENSE_PLATE_OCR_MODEL": "yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1",
  "OCR_MODEL": "easyOCR_raw_image",
  "EASYOCR_LANGUAGES": ["en", "th"]
}
```

### Auto-Startup Configuration
```json
{
  "AUTO_START_CAMERA": true,
  "AUTO_START_STREAMING": true,
  "AUTO_START_DETECTION": true,
  "AUTO_START_HEALTH_MONITOR": true,
  "AUTO_START_WEBSOCKET_SENDER": true,
  "AUTO_START_STORAGE_MONITOR": true,
  "STARTUP_DELAY": 5.0,
  "HEALTH_MONITOR_STARTUP_DELAY": 5.0,
  "WEBSOCKET_SENDER_STARTUP_DELAY": 5.0,
  "STORAGE_MONITOR_STARTUP_DELAY": 5.0
}
```

## Development Guidelines

### Import Patterns
- ใช้ **absolute imports** จาก `edge.src.*`
- ตัวอย่าง: `from edge.src.core.dependency_container import get_service`

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

## Testing & Development

### API Testing with curl
```bash
# Health check
curl -X GET http://aicamera1/health

# Camera status
curl -X GET http://aicamera1/camera/status

# Start camera
curl -X POST http://aicamera1/camera/start

# Manual capture
curl -X POST http://aicamera1/camera/capture

# Detection status
curl -X GET http://aicamera1/detection/status

# Get detection results
curl -X GET "http://aicamera1/detection/results?limit=10"

# Storage status
curl -X GET http://aicamera1/storage/status

# WebSocket sender status
curl -X GET http://aicamera1/websocket-sender/status
```

### WebSocket Testing with JavaScript
```javascript
// Test WebSocket connection
const socket = io('http://aicamera1');

socket.on('connect', () => {
    console.log('Connected');
    
    // Test camera status request
    socket.emit('camera_status_request', {});
    
    // Test health status request
    socket.emit('health_status_request', {});
});

socket.on('camera_status_update', (status) => {
    console.log('Camera status:', status);
});

socket.on('health_status_update', (health) => {
    console.log('Health status:', health);
});
```

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

## Changelog

### Version 2.0.0 (September 2025)
- ✅ Merged multiple API documentation sources
- ✅ Added UI Dashboard enhancements documentation
- ✅ Added toggle functionality for content sections
- ✅ Enhanced health monitor status display
- ✅ Added server connection status priority system
- ✅ Added manual capture system documentation
- ✅ Added accessibility enhancements
- ✅ Added performance optimizations
- ✅ Added cache-control header optimizations
- ✅ Added CSS performance improvements
- ✅ Updated to reflect actual project implementation
- ✅ Added comprehensive WebSocket events documentation
- ✅ Added complete endpoint mapping from actual blueprints

### Version 1.3 (August 2025)
- ✅ Added comprehensive variable naming conventions
- ✅ Updated WebSocket event documentation
- ✅ Added detailed response schemas
- ✅ Improved error handling documentation
- ✅ Added rate limiting information
- ✅ Enhanced detection API endpoints
- ✅ Added system health monitoring APIs
- ✅ Improved camera configuration validation
- ✅ Added modular service architecture support
- ✅ Added auto-startup configuration for all services
- ✅ Added storage management APIs
- ✅ Added WebSocket sender offline mode support
- ✅ Updated configuration management with environment variables

---

**Note:** This documentation reflects the current implementation as of September 3, 2025. All endpoints and data structures have been validated against the actual project code in `/edge/src/web/blueprints/`.

## Quality Metrics System (Added 2025-09-03)

### Overview
The Quality Metrics system provides real-time performance indicators for the AI detection pipeline, displaying dynamic progress bars with intelligent color coding based on performance thresholds.

### Quality Metrics Endpoints

#### GET /detection/status - Quality Metrics
**Response includes quality metrics:**
```json
{
    "success": true,
    "detection_status": {
        # ... existing fields ...
        "detection_accuracy": 8.5,           # Percentage based on vehicle detections vs total frames
        "ocr_accuracy": 69.2,                # Percentage based on successful OCR vs total plates
        "system_reliability": 91.5,          # Percentage based on service uptime and error rate
        # ... other fields ...
    }
}
```

### Quality Metrics Calculation

#### Backend Calculation (DetectionManager)
```python
def _calculate_quality_metrics(self) -> Dict[str, float]:
    """
    Calculate quality metrics from detection statistics.
    
    Returns:
        Dict[str, float]: Quality metrics for frontend progress bars
    """
    stats = self.detection_stats
    
    # Detection Accuracy: Based on successful vehicle detections vs total frames
    total_frames = stats['total_frames_processed']
    if total_frames > 0:
        detection_accuracy = (stats['total_vehicles_detected'] / total_frames) * 100
    else:
        detection_accuracy = 0.0
    
    # OCR Accuracy: Based on successful OCR vs total plates detected
    total_plates = stats['total_plates_detected']
    if total_plates > 0:
        ocr_accuracy = (stats['successful_ocr'] / total_plates) * 100
    else:
        ocr_accuracy = 0.0
    
    # System Reliability: Based on service uptime and error rate
    if total_frames > 0:
        error_rate = (stats['failed_detections'] / total_frames) * 100
        system_reliability = max(0, 100 - error_rate)  # Higher is better
    else:
        system_reliability = 100.0  # No errors if no frames processed
    
    return {
        'detection_accuracy': round(detection_accuracy, 1),
        'ocr_accuracy': round(ocr_accuracy, 1),
        'system_reliability': round(system_reliability, 1)
    }
```

### Frontend Quality Metrics Display

#### Dynamic Color Logic
**Detection Accuracy:**
- **≥80%**: 🟢 `bg-success` (Green) - Excellent
- **≥60%**: 🟡 `bg-warning` (Yellow) - Good  
- **≥40%**: 🔵 `bg-info` (Blue) - Fair
- **<40%**: 🔴 `bg-danger` (Red) - Poor

**OCR Accuracy:**
- **≥90%**: 🟢 `bg-success` (Green) - Excellent
- **≥75%**: 🟡 `bg-warning` (Yellow) - Good
- **≥50%**: 🔵 `bg-info` (Blue) - Fair
- **<50%**: 🔴 `bg-danger` (Red) - Poor

**System Reliability:**
- **≥95%**: 🟢 `bg-success` (Green) - Excellent
- **≥85%**: 🟡 `bg-warning` (Yellow) - Good
- **≥70%**: 🔵 `bg-info` (Blue) - Fair
- **<70%**: 🔴 `bg-danger` (Red) - Poor

#### Frontend Implementation
```javascript
/**
 * Update quality progress bar with dynamic colors and percentage display
 */
updateQualityProgressBar: function(barId, valueId, percentage, metricType) {
    const barElement = document.getElementById(barId);
    const valueElement = document.getElementById(valueId);
    
    if (barElement && valueElement) {
        // Update progress bar width and percentage value
        barElement.style.width = percentage + '%';
        barElement.setAttribute('aria-valuenow', percentage);
        valueElement.textContent = percentage + '%';
        
        // Set dynamic colors based on metric type and performance
        let barColor = '';
        let textColor = '';
        
        // Apply color logic based on metricType and percentage
        // ... color logic implementation ...
        
        // Apply colors
        barElement.className = `progress-bar ${barColor}`;
        valueElement.className = `h5 fw-bold ${textColor}`;
    }
}
```

### Quality Metrics Integration

#### Detection Dashboard
- **Progress Bars**: Real-time quality metrics with dynamic colors
- **Percentage Display**: Clear percentage values below each progress bar
- **Smart Color Coding**: Colors that make sense with performance statistics
- **Responsive Design**: Adapts to different screen sizes

#### Health Dashboard Integration
- **Component Status**: Enhanced status mapping for all components
- **Camera Information**: Model display with uptime information
- **Database Status**: Connection and path information
- **AI Detection Status**: Model loading and service status
- **System Information**: OS, CPU, and AI accelerator details

### Performance Benefits
- **Real-time Monitoring**: Live updates of system performance
- **Visual Feedback**: Immediate understanding of system health
- **Proactive Maintenance**: Early detection of performance issues
- **User Experience**: Clear, intuitive interface for system monitoring
