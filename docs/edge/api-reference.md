# AI Camera Edge System - API Reference

**Version:** 2.0.0  
**Last Updated:** 2025-08-23  
**Author:** AI Camera Team  
**Category:** API Documentation  
**Status:** Active

## Overview

API Reference สำหรับ AI Camera Edge System ครอบคลุม REST API endpoints และ WebSocket interfaces

## Base URL

- **Development:** `http://localhost:5000`
- **Production:** `http://localhost` (via Nginx reverse proxy)

## Authentication

API ใช้ Tailscale authentication โดยอัตโนมัติ

## Architecture Overview

The edge system follows a modular architecture with the following components:

- **Core Services**: Camera Manager, Detection Manager, Health Service, Storage Service, WebSocket Sender
- **Components**: Camera Handler, Detection Processor, Health Monitor, Storage Monitor
- **Web Interface**: Flask Blueprints for each service
- **Dependency Injection**: Centralized service management
- **Auto-Startup**: Sequential service initialization with configurable delays

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
  "timestamp": "2025-08-23T10:30:00Z"
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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

## REST API Endpoints

### Health Check

#### GET /health
ตรวจสอบสถานะของระบบ

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "service": "aicamera_lpr",
  "version": "2.0.0",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### Camera Control

#### GET /camera/status
ตรวจสอบสถานะกล้อง

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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /camera/start
เริ่มการทำงานกล้อง

**Response:**
```json
{
  "success": true,
  "message": "Camera started successfully",
  "status": {
    "initialized": true,
    "streaming": true
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /camera/stop
หยุดการทำงานกล้อง

**Response:**
```json
{
  "success": true,
  "message": "Camera stopped successfully",
  "status": {
    "initialized": true,
    "streaming": false
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /camera/restart
รีสตาร์ทกล้อง

**Response:**
```json
{
  "success": true,
  "message": "Camera restarted successfully",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /camera/config
รับการตั้งค่ากล้องปัจจุบัน

**Response:**
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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /camera/config
อัปเดตการตั้งค่ากล้อง

**Request Body:**
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

**Response:**
```json
{
  "success": true,
  "message": "Camera configuration updated successfully",
  "config": {
    "resolution": [1920, 1080],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto"
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /camera/capture
ถ่ายภาพ

**Response:**
```json
{
  "success": true,
  "message": "Image captured successfully",
  "data": {
    "filename": "capture_20250820_103000.jpg",
    "filepath": "/home/camuser/aicamera/edge/captured_images/capture_20250820_103000.jpg",
    "timestamp": "2025-08-20T10:30:00Z",
    "size": [1280, 720]
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /camera/video_feed
สตรีมวิดีโอ (MJPEG)

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

#### GET /camera/video_feed_lores
สตรีมวิดีโอความละเอียดต่ำ (MJPEG)

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

#### GET /camera/test
ทดสอบการทำงานของกล้อง

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
    "uptime": 3600.5,
    "timestamp": "2025-08-23T10:30:00Z"
  }
}
```

#### GET /camera/video_test
ทดสอบการทำงานของ video feed

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
    "video_feed_lores_url": "/camera/video_feed_lores",
    "timestamp": "2025-08-23T10:30:00Z"
  }
}
```

#### GET /camera/metadata
หน้าแสดง metadata ของกล้อง

**Response:** HTML page with camera metadata viewer

#### GET /camera/debug_metadata
ข้อมูล debug metadata ของกล้อง

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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /camera/api/metadata
API endpoint สำหรับ metadata ของกล้อง

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
    "last_frame_time": "2025-08-23T10:30:00Z"
  },
  "available_modes": [...],
  "sensor_modes_count": 4,
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### AI Processing

#### GET /detection/status
ตรวจสอบสถานะการตรวจจับ

**Response:**
```json
{
  "success": true,
  "status": {
    "service_running": true,
    "detection_active": true,
    "detection_processor_status": {
      "models_loaded": true,
      "vehicle_model_available": true,
      "lp_detection_model_available": true,
      "lp_ocr_model_available": true,
      "easyocr_available": true,
      "detection_resolution": [640, 640],
      "confidence_threshold": 0.8,
      "plate_confidence_threshold": 0.6,
      "processing_stats": {
        "total_processed": 156,
        "vehicles_detected": 89,
        "plates_detected": 67,
        "successful_ocr": 45,
        "last_detection": "2025-08-20T10:25:30.123456"
      },
      "last_update": "2025-08-20T10:30:00Z"
    },
    "detection_interval": 0.1,
    "auto_start": true,
    "statistics": {
      "total_detections": 156,
      "processing_time_avg": 0.045,
      "failed_detections": 3,
      "last_detection": "2025-08-20T10:25:30.123456"
    },
    "queue_size": 0,
    "thread_alive": true,
    "last_update": "2025-08-20T10:30:00Z"
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /detection/start
เริ่มการตรวจจับ

**Response:**
```json
{
  "success": true,
  "message": "Detection started successfully",
  "status": {
    "service_running": true,
    "detection_active": true
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /detection/stop
หยุดการตรวจจับ

**Response:**
```json
{
  "success": true,
  "message": "Detection stopped successfully",
  "status": {
    "service_running": true,
    "detection_active": false
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /detection/results
รับผลการตรวจจับ

**Query Parameters:**
- `limit` (optional): จำนวนผลลัพธ์ (default: 50, max: 100)
- `offset` (optional): เริ่มจากตำแหน่ง (default: 0)

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": 1,
        "timestamp": "2025-08-20T10:25:30.123456",
        "detections": [
          {
            "type": "vehicle",
            "confidence": 0.95,
            "bbox": [100, 150, 300, 250],
            "license_plate": {
              "text": "ABC-1234",
              "confidence": 0.87,
              "bbox": [150, 200, 250, 230]
            }
          }
        ],
        "image_path": "/home/camuser/aicamera/edge/captured_images/detection_20250820_102530.jpg"
      }
    ],
    "total_count": 156,
    "limit": 50,
    "offset": 0
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /detection/configure
ตั้งค่าการตรวจจับ

**Request Body:**
```json
{
  "detection_interval": 0.1,
  "confidence_threshold": 0.8,
  "plate_confidence_threshold": 0.6,
  "save_images": true,
  "save_to_database": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Detection configuration updated successfully",
  "config": {
    "detection_interval": 0.1,
    "confidence_threshold": 0.8,
    "plate_confidence_threshold": 0.6,
    "save_images": true,
    "save_to_database": true
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### System Health

#### GET /health/system
รับสถานะสุขภาพระบบ

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
        "last_check": "2025-08-20T10:30:00Z"
      },
      "detection": {
        "status": "healthy",
        "models_loaded": true,
        "easyocr_available": true,
        "detection_active": true,
        "service_running": true,
        "thread_alive": true,
        "auto_start": true,
        "last_check": "2025-08-20T10:30:00Z"
      },
      "database": {
        "status": "healthy",
        "connected": true,
        "database_path": "/home/camuser/aicamera/edge/db/lpr_data.db",
        "last_check": "2025-08-20T10:30:00Z"
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
        "last_check": "2025-08-20T10:30:00Z"
      }
    },
    "system": {
      "cpu_count": 4,
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
      "uptime": 86400
    },
    "last_check": "2025-08-20T10:30:00Z"
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /health/logs
รับ system logs

**Query Parameters:**
- `level` (optional): log level (PASS, FAIL, WARNING)
- `page` (optional): หน้า (default: 1)
- `limit` (optional): จำนวน log entries (default: 50, max: 100)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-08-20T10:30:00Z",
        "component": "Camera",
        "status": "PASS",
        "message": "Camera working normally",
        "details": "{}"
      }
    ],
    "total_count": 1500,
    "level_filter": "PASS",
    "page": 1,
    "limit": 50
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### Storage Management

#### GET /storage/status
รับสถานะการจัดเก็บข้อมูล

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
      "newest_file": "2025-08-20T10:00:00Z"
    },
    "file_counts": {
      "sent_files": 890,
      "unsent_files": 344,
      "total_files": 1234
    },
    "cleanup_stats": {
      "files_deleted": 45,
      "space_freed_gb": 2.3,
      "last_cleanup": "2025-08-20T09:00:00Z"
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
      "last_cleanup": "2025-08-20T09:00:00Z",
      "needs_cleanup": false
    }
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### POST /storage/cleanup
ทำการลบไฟล์เก่า

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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### WebSocket Sender

#### GET /websocket-sender/status
รับสถานะ WebSocket sender

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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /websocket-sender/logs
รับ WebSocket sender logs

**Query Parameters:**
- `page` (optional): หน้า (default: 1)
- `limit` (optional): จำนวน records (default: 50)
- `filter` (optional): กรองตาม action type

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-08-20T10:30:00Z",
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
  "timestamp": "2025-08-23T10:30:00Z"
}
```

## WebSocket API

### Connection

**URL:** `ws://localhost:5000/camera` (Camera namespace)

### Camera Events

#### camera_connected
Event sent when client connects to camera namespace

**Data:**
```json
{
  "success": true,
  "message": "Connected to camera service",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### camera_status_update
Event sent in response to camera_status_request

**Data:**
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
    "config": {
      "main": {
        "size": [1280, 720],
        "format": "RGB888"
      },
      "controls": {
        "FrameDurationLimits": [33333, 33333]
      }
    }
  },
  "config": {
    "resolution": [1280, 720],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto"
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### camera_control_response
Event sent in response to camera_control commands

**Data:**
```json
{
  "success": true,
  "message": "Camera started successfully",
  "command": "start",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### camera_config_response
Event sent in response to camera_config_update

**Data:**
```json
{
  "success": true,
  "message": "Configuration updated successfully",
  "timestamp": "2025-08-23T10:30:00Z"
}
```

### Client Events

#### camera_status_request
Request camera status update

**Data:**
```json
{}
```

#### camera_control
Send camera control command

**Data:**
```json
{
  "command": "start|stop|restart|capture"
}
```

#### camera_config_update
Update camera configuration

**Data:**
```json
{
  "config": {
    "resolution": [1280, 720],
    "framerate": 30,
    "brightness": 0.0,
    "contrast": 1.0,
    "saturation": 1.0,
    "awb_mode": "auto"
  }
}
```

### General WebSocket Events

#### camera_frame
ส่งข้อมูล frame จากกล้อง

**Data:**
```json
{
  "event": "camera_frame",
  "data": {
    "frame_id": 12345,
    "timestamp": "2025-08-23T10:30:00Z",
    "image_data": "base64_encoded_image",
    "detections": [
      {
        "bbox": [100, 100, 200, 200],
        "confidence": 0.95,
        "class": "person"
      }
    ]
  }
}
```

#### system_status
ส่งสถานะระบบ

**Data:**
```json
{
  "event": "system_status",
  "data": {
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
    "camera_status": "active",
    "ai_status": "ready"
  }
}
```

#### error
ส่งข้อผิดพลาด

**Data:**
```json
{
  "event": "error",
  "data": {
    "error_code": "CAMERA_ERROR",
    "message": "Camera device not found",
    "timestamp": "2025-08-20T10:30:00Z"
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| `CAMERA_NOT_INITIALIZED` | ข้อผิดพลาดเกี่ยวกับกล้อง |
| `CAMERA_NOT_STREAMING` | ข้อผิดพลาดเกี่ยวกับกล้อง |
| `AI_MODEL_ERROR` | ข้อผิดพลาดเกี่ยวกับ AI model |
| `NETWORK_ERROR` | ข้อผิดพลาดเกี่ยวกับเครือข่าย |
| `SYSTEM_ERROR` | ข้อผิดพลาดระบบ |
| `VALIDATION_ERROR` | ข้อผิดพลาดการตรวจสอบข้อมูล |
| `OPERATION_FAILED` | การดำเนินการล้มเหลว |
| `SERVICE_UNAVAILABLE` | บริการไม่พร้อมใช้งาน |

## Rate Limiting

- **REST API:** 100 requests/minute
- **WebSocket:** ไม่จำกัด

## Configuration Values

### Camera Configuration
```json
{
  "DEFAULT_RESOLUTION": [640, 640],
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

### Storage Configuration
```json
{
  "STORAGE_MONITOR_ENABLED": true,
  "STORAGE_MONITOR_INTERVAL": 300,
  "STORAGE_MIN_FREE_SPACE_GB": 10.0,
  "STORAGE_RETENTION_DAYS": 7,
  "STORAGE_BATCH_SIZE": 100,
  "STORAGE_FOLDER_PATH": "/home/camuser/aicamera/edge/captured_images"
}
```

### WebSocket Configuration
```json
{
  "WEBSOCKET_SENDER_ENABLED": true,
  "WEBSOCKET_CONNECTION_TIMEOUT": 30.0,
  "WEBSOCKET_RETRY_INTERVAL": 60.0,
  "WEBSOCKET_MAX_RETRIES": 5,
  "SENDER_INTERVAL": 60.0,
  "HEALTH_SENDER_INTERVAL": 300.0
}
```

## Examples

### Python Client Example

```python
import requests
import websocket
import json

# REST API Example
def get_system_status():
    response = requests.get('http://localhost/health/system')
    return response.json()

def process_image(image_data):
    payload = {
        'image_data': image_data,
        'confidence_threshold': 0.8
    }
    response = requests.post('http://localhost/detection/configure', json=payload)
    return response.json()

# WebSocket Example
def on_message(ws, message):
    data = json.loads(message)
    if data['event'] == 'camera_frame':
        print(f"Received frame {data['data']['frame_id']}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    print("WebSocket connection opened")

# Connect to WebSocket
ws = websocket.WebSocketApp(
    "ws://localhost:5000",
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close
)
ws.run_forever()
```

### JavaScript Client Example

```javascript
// REST API Example
async function getSystemStatus() {
    const response = await fetch('http://localhost/health/system');
    return await response.json();
}

async function processImage(imageData) {
    const payload = {
        image_data: imageData,
        confidence_threshold: 0.8
    };
    
    const response = await fetch('http://localhost/detection/configure', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    });
    
    return await response.json();
}

// WebSocket Example
const ws = new WebSocket('ws://localhost:5000');

ws.onopen = function(event) {
    console.log('WebSocket connection opened');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.event === 'camera_frame') {
        console.log(`Received frame ${data.data.frame_id}`);
        // Process frame data
    } else if (data.event === 'system_status') {
        console.log('System status:', data.data);
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};

ws.onclose = function(event) {
    console.log('WebSocket connection closed');
};
```

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [WebSocket Documentation](https://websockets.readthedocs.io/)
- [REST API Best Practices](https://restfulapi.net/)

---

**Note:** เอกสารนี้จะได้รับการอัปเดตเมื่อมีการเปลี่ยนแปลงใน API specification
