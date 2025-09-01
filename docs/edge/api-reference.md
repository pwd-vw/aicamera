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

#### GET /health/
Basic health status endpoint that serves both dashboard UI and API requests.

**Browser Request:** Returns HTML dashboard  
**API Request:** Returns JSON health data (when Accept: application/json header is present)

**API Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "components": {
      "camera": {
        "status": "healthy",
        "message": "Camera initialized and streaming",
        "last_check": "2025-08-24T22:41:08.439079",
        "execution_time_ms": 6.42
      },
      "database": {
        "status": "healthy",
        "message": "Database connection active",
        "last_check": "2025-08-24T22:41:18.385453",
        "execution_time_ms": 0.07
      },
      "detection": {
        "status": "unhealthy",
        "message": "Insufficient models loaded: 0/2 required",
        "last_check": "2025-08-24T22:41:08.950181",
        "execution_time_ms": 0.11
      },
      "system": {
        "status": "healthy",
        "message": "System resources OK: CPU 68.9%, RAM 42.9%, CPU temp: 55.1°C",
        "last_check": "2025-08-24T22:41:08.947494",
        "execution_time_ms": 503.76
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
    },
    "last_check": "2025-08-24T22:41:18.385453"
  },
  "timestamp": "2025-08-24T22:41:18.385453"
}
```

#### GET /health/system
Comprehensive system health information with detailed component status.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_status": "healthy",
    "components": {
      "camera": {
  "status": "healthy",
        "message": "Camera initialized and streaming",
        "last_check": "2025-08-24T22:41:08.439079",
        "execution_time_ms": 6.42
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
  "timestamp": "2025-08-24T22:41:18.385453"
}
```

#### GET /health/logs
System logs with filtering and pagination support.

**Query Parameters:**
- `limit` (int, optional): Number of log entries to return (default: 50)
- `page` (int, optional): Page number for pagination (default: 1)
- `level` (string, optional): Log level filter (DEBUG, INFO, WARNING, ERROR)

**Response:**
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2025-08-24 22:41:08",
        "level": "INFO",
        "message": "Health Check - Camera: PASS - Camera initialized and streaming",
        "service": "aicamera_lpr"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 125,
      "has_next": true,
      "has_prev": false
    }
  },
  "timestamp": "2025-08-24T22:41:18.385453"
}
```

#### GET /health/status
Basic health status information.

**Response:**
```json
{
  "success": true,
  "status": {
    "initialized": true,
    "last_check": "2025-08-24T18:26:40.208073",
    "monitoring": false
  },
  "timestamp": "2025-08-24T18:31:36.202441"
}
```

#### GET /health/system-info
System information and specifications.

**Response:**
```json
{
  "success": true,
  "data": {
    "hostname": "aicamera1",
    "platform": "Linux",
    "architecture": "aarch64",
    "python_version": "3.11.2",
    "system_uptime_hours": 24.5,
    "service_uptime_minutes": 15.2
  },
  "timestamp": "2025-08-24T22:41:18.385453"
}
```

### Camera Control

#### Camera Architecture Overview

The camera system uses a **Singleton pattern** with **thread-safe access control**:

- **CameraHandler**: Low-level camera operations using Picamera2 (Singleton)
- **CameraManager**: High-level camera service management
- **Frame Buffer System**: Single capture thread provides frames to all consumers
- **Auto-Start System**: Configurable automatic camera initialization and streaming

#### Camera Initialization Process

1. **Hardware Detection**: Check for camera devices (`/dev/video0`, `/dev/media0`)
2. **Software Check**: Verify libcamera and Picamera2 availability
3. **Camera Configuration**: Create video configuration with main and lores streams
4. **Camera Start**: Begin streaming and start frame capture thread
5. **Auto-Start**: Optional automatic initialization based on configuration

#### Camera Status States

| State | initialized | streaming | Description |
|-------|-------------|-----------|-------------|
| **Offline** | `false` | `false` | Camera not initialized or hardware unavailable |
| **Ready** | `true` | `false` | Camera configured but not streaming |
| **Online** | `true` | `true` | Camera streaming and capturing frames |
| **Fallback** | `true` | `false` | Camera handler ready but hardware not available |

#### Frame Capture System

The camera system uses a **thread-safe frame buffer system** with concurrent access:

- **Single Capture Thread**: Continuously captures frames from both main and lores streams
- **Frame Buffers**: Thread-safe buffers for main frame, lores frame, and metadata
- **Concurrent Access**: Multiple consumers can access frames simultaneously
- **Performance Tracking**: Frame count and FPS statistics

#### Auto-Start System

The camera system supports configurable auto-start functionality:

**Configuration:**
- `AUTO_START_CAMERA`: Enable/disable automatic camera initialization
- `AUTO_START_STREAMING`: Enable/disable automatic streaming after initialization
- `STARTUP_DELAY`: Delay before auto-start (seconds)

**Auto-Start Process:**
1. **Normal Mode**: Camera hardware available
   - Initialize camera handler
   - Start camera streaming
   - Begin frame capture

2. **Fallback Mode**: Camera hardware not available
   - Initialize camera handler in fallback mode
   - Monitor camera availability
   - Auto-connect when hardware becomes available

#### Error Handling and Recovery

**Camera Availability Check:**
- Hardware detection (`/dev/video0`, `/dev/media0`)
- Software availability (libcamera, Picamera2)
- Resource conflict resolution

**Resource Management:**
- Singleton pattern prevents multiple camera instances
- Thread-safe access control
- Automatic resource cleanup on errors

**Recovery Mechanisms:**
- Automatic retry on connection failures
- Hardware reset on resource conflicts
- Fallback mode when hardware unavailable

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
สตรีมวิดีโอความละเอียดต่ำ (MJPEG) จาก lores stream

**Process:**
1. Check camera streaming status
2. Get frames from lores stream buffer
3. Encode frames to JPEG format
4. Stream via multipart/x-mixed-replace

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

#### GET /camera/api/experimental_metadata
API endpoint สำหรับ comprehensive experimental metadata ของกล้อง

**Response:**
```json
{
  "success": true,
  "experimental_metadata": {
    "timing": {
      "frame_timestamp": 1234567890,
      "sensor_timestamp": 1234567890,
      "request_timestamp": 1234567890,
      "frame_duration": 33333,
      "exposure_time": 10000,
      "timestamp_ns": 1234567890,
      "timestamp_ms": 1234.567,
      "capture_latency": 5.2
    },
    "exposure": {
      "exposure_time": 10000,
      "exposure_time_ms": 10.0,
      "analogue_gain": 2.0,
      "digital_gain": 1.0,
      "total_gain": 2.0,
      "gain_db": 6.02,
      "exposure_index": 20.0
    },
    "color": {
      "awb_gains": [1.2, 0.8],
      "colour_gains": [1.2, 1.0, 0.8],
      "color_temperature": 5500.0,
      "red_gain": 1.2,
      "blue_gain": 0.8,
      "green_gain": 1.0,
      "wb_ratio": 1.5
    },
    "focus": {
      "focus_fom": 750,
      "af_state": 2,
      "lens_position": 500,
      "focus_distance": 2.0,
      "focus_confidence": 0.75,
      "autofocus_active": true
    },
    "sensor": {
      "sensor_id": "imx708",
      "sensor_mode": 0,
      "sensor_timestamp": 1234567890,
      "sensor_line_length": 3840,
      "sensor_frame_length": 720,
      "sensor_exposure_time": 10000
    },
    "quality": {
      "sharpness": 1.0,
      "contrast": 1.0,
      "brightness": 0.0,
      "saturation": 1.0,
      "noise_reduction": "Fast",
      "dynamic_range": 10.5,
      "signal_to_noise": 25.3
    },
    "performance": {
      "frame_count": 1234,
      "average_fps": 29.5,
      "buffer_ready": true,
      "main_frame_available": true,
      "lores_frame_available": true,
      "capture_thread_active": true,
      "buffer_latency": 2.1
    },
    "camera_properties": {
      "model": "imx708",
      "location": 2,
      "rotation": 0,
      "pixel_array_size": [4608, 2592],
      "unit_cell_size": [1.4, 1.4],
      "color_filter_arrangement": 0
    },
    "configuration": {
      "resolution": [1280, 720],
      "format": "RGB888",
      "framerate": 30.0,
      "buffer_count": 4,
      "use_case": "video",
      "transform": "identity",
      "colour_space": "Rec709"
    },
    "experimental": {
      "lighting_condition": "normal",
      "motion_detected": false,
      "image_stability": 0.95,
      "exposure_adequacy": "adequate",
      "focus_quality": "good",
      "noise_level": "low",
      "dynamic_range_utilization": 75.5
    },
    "raw_metadata": {...},
    "metadata_info": {
      "collection_time": 1692800000.0,
      "collection_method": "comprehensive_experimental",
      "version": "2.0",
      "source": "camera_handler"
    }
  },
  "timestamp": "2025-08-23T10:30:00Z"
}
```

#### GET /camera/api/metadata_summary
API endpoint สำหรับ metadata summary สำหรับ experimental efficiency

**Response:**
```json
{
  "success": true,
  "metadata_summary": {
    "camera_status": {
      "initialized": true,
      "streaming": true,
      "frame_count": 1234,
      "average_fps": 29.5
    },
    "image_quality": {
      "exposure_adequacy": "adequate",
      "focus_quality": "good",
      "lighting_condition": "normal",
      "noise_level": "low",
      "dynamic_range_utilization": 75.5
    },
    "performance_metrics": {
      "buffer_ready": true,
      "buffer_latency_ms": 2.1,
      "capture_thread_active": true,
      "actual_framerate": 30.0
    },
    "camera_settings": {
      "resolution": [1280, 720],
      "exposure_time_ms": 10.0,
      "total_gain": 2.0,
      "color_temperature": 5500.0,
      "focus_distance": 2.0
    },
    "experimental_indicators": {
      "image_stability": 0.95,
      "signal_to_noise_db": 25.3,
      "dynamic_range_stops": 10.5,
      "focus_confidence": 0.75
    }
  },
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
      "easyocr_available": false,
      "detection_resolution": [640, 640],
      "confidence_threshold": 0.7,
      "plate_confidence_threshold": 0.5,
      "processing_stats": {
        "total_processed": 6023,
        "vehicles_detected": 512,
        "plates_detected": 0,
        "successful_ocr": 0,
        "last_detection": null
      },
      "last_update": "2025-08-24T18:20:35.601865"
    },
    "detection_interval": 0.1,
    "auto_start": true,
    "statistics": {
      "total_frames_processed": 6023,
      "total_vehicles_detected": 512,
      "total_plates_detected": 0,
      "successful_ocr": 0,
      "failed_detections": 512,
      "processing_time_avg": 0,
      "last_detection": null,
      "started_at": "2025-08-24T18:08:03.714003"
    },
    "queue_size": 0,
    "thread_alive": true,
    "last_update": "2025-08-24T18:20:35.601884"
  },
  "timestamp": "2025-08-24T18:20:35.601904"
}
```

### Get Detection Status
**GET** `/detection/status`

Returns current detection service status including model availability and processing statistics.

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
      "easyocr_available": false,
      "detection_resolution": [640, 640],
      "confidence_threshold": 0.7,
      "plate_confidence_threshold": 0.5,
      "processing_stats": {
        "total_processed": 6023,
        "vehicles_detected": 512,
        "plates_detected": 0,
        "successful_ocr": 0,
        "last_detection": null
      },
      "last_update": "2025-08-24T18:20:35.601865"
    },
    "detection_interval": 0.1,
    "auto_start": true,
    "statistics": {
      "total_frames_processed": 6023,
      "total_vehicles_detected": 512,
      "total_plates_detected": 0,
      "successful_ocr": 0,
      "failed_detections": 512,
      "processing_time_avg": 0,
      "last_detection": null,
      "started_at": "2025-08-24T18:08:03.714003"
    },
    "queue_size": 0,
    "thread_alive": true,
    "last_update": "2025-08-24T18:20:35.601884"
  },
  "timestamp": "2025-08-24T18:20:35.601904"
}
```

### Detection Processor Status Fields

The `detection_processor_status` object contains detailed information about the AI models and processing:

- **`models_loaded`** (boolean): Overall model loading status
- **`vehicle_model_available`** (boolean): Vehicle detection model availability
- **`lp_detection_model_available`** (boolean): License plate detection model availability  
- **`lp_ocr_model_available`** (boolean): License plate OCR model availability
- **`easyocr_available`** (boolean): EasyOCR initialization status
- **`detection_resolution`** (array): Model input resolution [width, height]
- **`confidence_threshold`** (float): Vehicle detection confidence threshold
- **`plate_confidence_threshold`** (float): License plate detection confidence threshold
- **`processing_stats`** (object): Real-time processing statistics
- **`last_update`** (string): ISO timestamp of last status update

### Health Monitoring Integration

The detection status endpoint is used by the health monitoring system to verify model availability:

- **Health Check**: Monitors `vehicle_model_available` and `lp_detection_model_available`
- **Status Validation**: Ensures both essential models are loaded before marking as healthy
- **Fallback Mechanism**: Uses direct degirum model loading if API is unavailable
- **Real-time Monitoring**: Continuous health checks every 2 hours

## Health Monitoring System

The health monitoring system provides comprehensive system status monitoring with the following features:

- **Automatic Health Checks**: Runs every 2 hours (configurable via `HEALTH_CHECK_INTERVAL`)
- **Component Monitoring**: Camera, Detection Models, Database, Storage, CPU/RAM, Network
- **Background Monitoring**: Continuous monitoring thread with result caching
- **WebSocket Integration**: Real-time health status updates (when WebSocket is enabled)
- **Database Logging**: Health check results stored in database for historical analysis

### Removed Endpoints (v2.0.0)

The following endpoints were removed as they were unused:
- ~~POST /health/monitor/start~~ (Removed - monitoring is automatic)
- ~~POST /health/monitor/stop~~ (Removed - monitoring is automatic)  
- ~~POST /health/check/run~~ (Removed - use GET /health/system instead)

### Health Check Components

The health monitoring system performs comprehensive checks on the following components:

1. **Camera System**: Camera initialization and streaming status
2. **Detection Models**: AI model availability and loading status via `/detection/status` API
3. **Database**: Database connectivity and operations
4. **EasyOCR**: OCR engine initialization and language support
5. **Network Connectivity**: Internet connectivity and DNS resolution
6. **Storage Management**: Disk space availability and file operations

**Note**: Detailed health check results are logged to the system journal and can be viewed using:
```bash
journalctl -u aicamera_lpr.service | grep -i "health check"
```

### Detection Models Health Check

The detection models health check specifically validates:

- **Vehicle Detection Model**: Ensures vehicle detection model is loaded and available
- **License Plate Detection Model**: Ensures license plate detection model is loaded and available
- **API Integration**: Uses `/detection/status` endpoint for real-time status
- **Fallback Mechanism**: Direct degirum model loading if API unavailable
- **Status Reporting**: Detailed logging of model availability and errors

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

## Detection API Endpoints

### Get All Detection Results
**GET** `/detection/results`

Returns all detection results from the database.

**Response:**
```json
{
  "success": true,
    "results": [
      {
        "id": 1,
      "timestamp": "2025-08-22 16:57:25",
      "vehicles_count": 1,
      "plates_count": 2,
      "original_image_path": "captured_images/detection_20250824_101530_123.jpg",
      "vehicle_detected_image_path": "captured_images/vehicle_detected_20250824_101530_123.jpg",
      "plate_image_path": "captured_images/plate_detected_20250824_101530_123.jpg",
      "cropped_plates_paths": [
        "captured_images/plate_20250824_101530_123_0.jpg",
        "captured_images/plate_20250824_101530_123_1.jpg"
      ],
      "ocr_results": [
        {
          "text": "ABC-123",
            "confidence": 0.95,
          "language": "en"
        }
      ],
      "processing_time_ms": 150.5,
      "created_at": "2025-08-22 16:57:25"
    }
  ],
  "count": 1,
  "timestamp": "2025-08-24T10:15:30.123Z"
}
```

### Get Detection Result by ID
**GET** `/detection/results/{id}`

Returns a specific detection result by ID.

**Parameters:**
- `id` (integer): Detection result ID

**Response:**
```json
{
  "success": true,
  "result": {
    "id": 1,
    "timestamp": "2025-08-22 16:57:25",
    "vehicles_count": 1,
    "plates_count": 2,
    "original_image_path": "captured_images/detection_20250824_101530_123.jpg",
    "vehicle_detected_image_path": "captured_images/vehicle_detected_20250824_101530_123.jpg",
    "plate_image_path": "captured_images/plate_detected_20250824_101530_123.jpg",
    "cropped_plates_paths": [
      "captured_images/plate_20250824_101530_123_0.jpg",
      "captured_images/plate_20250824_101530_123_1.jpg"
    ],
    "ocr_results": [
      {
        "text": "ABC-123",
        "confidence": 0.95,
        "language": "en",
        "method": "hailo"
      }
    ],
    "processing_time_ms": 150.5,
    "created_at": "2025-08-22 16:57:25"
  },
  "timestamp": "2025-08-24T10:15:30.123Z"
}
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Detection result with ID 999 not found"
}
```

### Image Storage Pipeline

The detection system stores 4 types of images for each detection:

1. **Original Image** (`original_image_path`)
   - **Content**: Raw captured image frame
   - **Filename**: `detection_{timestamp}.jpg`
   - **Purpose**: Reference to the original captured image

2. **Vehicle Detection Image** (`vehicle_detected_image_path`)
   - **Content**: Original image + green vehicle bounding boxes + confidence scores
   - **Filename**: `vehicle_detected_{timestamp}.jpg`
   - **Purpose**: Shows vehicle detection results with annotations

3. **Plate Detection Image** (`plate_image_path`)
   - **Content**: Original image + blue plate bounding boxes + OCR text + confidence scores
   - **Filename**: `plate_detected_{timestamp}.jpg`
   - **Purpose**: Shows license plate detection and OCR results

4. **Cropped Plates** (`cropped_plates_paths`)
   - **Content**: Individual cropped license plate images
   - **Filename**: `plate_{timestamp}_{index}.jpg`
   - **Purpose**: Extracted license plate images for detailed analysis

### Image Path Examples

```json
{
  "original_image_path": "captured_images/detection_20250824_101530_123.jpg",
  "vehicle_detected_image_path": "captured_images/vehicle_detected_20250824_101530_123.jpg",
  "plate_image_path": "captured_images/plate_detected_20250824_101530_123.jpg",
  "cropped_plates_paths": [
    "captured_images/plate_20250824_101530_123_0.jpg",
    "captured_images/plate_20250824_101530_123_1.jpg"
  ]
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
