# โมดูลกล้อง (Camera Module) – AI Camera v2.0

เวอร์ชัน: 2.0  
ปรับปรุงล่าสุด: 2025-01-09  
ผู้เขียน: AI Camera Team

## 1) วัตถุประสงค์ (Objectives)

โมดูลกล้องมีเป้าหมายเพื่อจัดการกล้อง Picamera2 แบบครบวงจร ให้บริการสตรีมวิดีโอ จัดเก็บข้อมูล metadata และรองรับการตรวจจับวัตถุ ด้วยสถาปัตยกรรมแบบ modular ที่มีประสิทธิภาพสูง

### เป้าหมายหลัก:
- จัดการกล้อง Picamera2 แบบ thread-safe และมีประสิทธิภาพ
- รองรับ dual stream ตามค่าจาก config (main สำหรับงานตรวจจับ, lores สำหรับพรีวิวเว็บ)
- จัดเก็บและแสดง metadata ของกล้องแบบครบถ้วน (11 หมวดหมู่)
- รองรับการสตรีมวิดีโอแบบ MJPEG ผ่าน HTTP (Socket.IO เป็นตัวเลือก และปิดเป็นค่าเริ่มต้น)
- ผนวกรวมกับระบบตรวจจับ (Detection) และ Health Monitor
- ลดการใช้ CPU ด้วยการแคช metadata ที่ความถี่ ~60 Hz (และอัปเดตเมื่อมีเหตุการณ์สำคัญ)

## 2) สถาปัตยกรรมและองค์ประกอบ (Architecture & Components)

```
Camera Module Architecture
├── Camera Handler (Component)
│   ├── _initialize_camera_internal()
│   ├── _start_camera_internal()
│   ├── get_main_frame()
│   ├── get_lores_frame()
│   ├── get_metadata() [11 categories]
│   └── safe_camera_operation() [thread-safe wrapper]
├── Camera Manager (Service)
│   ├── capture_main_frame()
│   ├── capture_lores_frame()
│   ├── get_status()
│   ├── _update_metadata() [event-based]
│   └── lifecycle management
├── Video Streaming Service
│   ├── generate_frames()
│   └── WebSocket streaming
└── Camera Blueprint (Web Interface)
    ├── /camera/ (dashboard)
    ├── /camera/metadata (metadata viewer)
    ├── /camera/status (API)
    └── /camera/test (service test)
```

### การกำหนดค่า Resolution:
- ขับเคลื่อนด้วย environment variables ใน `/edge/installation/.env.production`
- **Main Stream**: ใช้สำหรับ Detection (RGB888) ค่าเริ่มต้น 1280x720
- **Lores Stream**: ใช้สำหรับ Web Preview/Streaming (เข้ารหัสเป็น MJPEG ไบต์หรือเข้ารหัสซอฟต์แวร์) ค่าเริ่มต้น 1280x720

## 3) อัลกอริทึมและขั้นตอนการทำงาน (Algorithm & Procedure)

### 3.1 Camera Initialization Sequence
```
1. Load configuration from .env.production
   ├── MAIN_RESOLUTION=1280x720
   └── LORES_RESOLUTION=640x640

2. Initialize Picamera2
   ├── Configure main stream (RGB888)
   ├── Configure lores stream (RGB888)  # เตรียมสำหรับเข้ารหัส MJPEG
   └── Set camera controls (ปรับค่า AF/AWB/AE และคุณภาพพื้นฐาน)

3. Start streaming
   ├── Begin frame capture (worker คุม FPS เดียว)
   ├── Enable hardware MJPEG encoder (ถ้ามี) หรือใช้เส้นทางซอฟต์แวร์
   ├── Cache metadata ทุก ~1 วินาที
   └── Enable frame access

4. Register with services
   ├── Video streaming service
   ├── Detection manager (lores frames)
   └── Health monitor
```

### 3.2 Metadata Collection Algorithm
```python
def collect_metadata_event_based():
    """Event-based metadata collection (CPU efficient)"""
    metadata = {}
    
    # 1. Camera Properties (hardware info)
    metadata['camera_properties'] = get_camera_properties()
    
    # 2. Available Sensor Modes
    metadata['available_modes'] = get_sensor_modes()
    
    # 3. Current Configuration
    metadata['current_config'] = get_current_config()
    
    # 4-11. Additional categories...
    # Only update on: initialization, config changes, manual refresh
    
    return metadata
```

### 3.3 Frame Capture Procedure
```
Main (สำหรับ Detection):
Camera Handler → get_main_frame() [RGB888 array] → Detection Processor → AI Analysis

Lores (สำหรับ Preview/Streaming):
Camera Handler → get_lores_frame() [MJPEG bytes หรือ RGB888→JPEG] → Video Streaming → Dashboard Display
```

### 3.4 Thread Safety Implementation
```python
@safe_camera_operation
def camera_operation():
    """All camera operations wrapped with unified locking"""
    with self._lock:
        # Critical camera operations
        pass
```

## 4) API สำหรับนักพัฒนา (Developer API Reference)

### 4.1 REST Endpoints

```http
GET /camera/                    # แดshboard กล้อง
GET /camera/status              # สถานะกล้องปัจจุบัน
GET /camera/metadata            # metadata viewer (UI)
GET /camera/test               # ทดสอบ service availability
POST /camera/start             # เริ่มกล้อง
POST /camera/stop              # หยุดกล้อง
```

**ตัวอย่าง Response จาก `/camera/status`:**
```json
{
  "success": true,
  "status": {
    "initialized": true,
    "streaming": true,
    "uptime": 1234.56,
    "resolution": [1280, 720],
    "metadata": {
      "camera_properties": {
        "Model": "imx708",
        "PixelArrayActiveAreas": [[0, 0, 4608, 2592]],
        "ScalerCropMaximum": [0, 0, 4608, 2592]
      },
      "available_modes": [
        {
          "size": [4608, 2592],
          "bit_depth": 10,
          "unpacked": "BGGR10_CSI2P"
        }
      ],
      "current_config": {
        "main": {
          "size": [1280, 720],
          "format": "RGB888"
        },
        "lores": {
          "size": [640, 640],
          "format": "XBGR8888"
        }
      },
      "metadata_timestamp": 1704789123.456
    }
  }
}
```

### 4.2 WebSocket Events
(ตัวเลือก — ปิดเป็นค่าเริ่มต้น ขณะนี้แดชบอร์ดใช้ HTTP + MJPEG เป็นหลัก)

**Client → Server:**
```javascript
socket.emit('camera_status_request');           // ขอสถานะกล้อง
socket.emit('camera_metadata_request');         // ขอ metadata
socket.emit('join_camera_room');               // เข้าร่วม camera room
socket.emit('leave_camera_room');              // ออกจาก camera room
```

**Server → Client:**
```javascript
socket.on('camera_status_update', (status) => {
    // อัปเดตสถานะกล้อง
    console.log('Camera status:', status);
});

socket.on('camera_frame_update', (frame_data) => {
    // เฟรมวิดีโอใหม่
    updateVideoDisplay(frame_data);
});

socket.on('camera_metadata_update', (metadata) => {
    // อัปเดต metadata
    updateMetadataDisplay(metadata);
});
```

### 4.3 Service API (Internal)

```python
# Camera Manager Service
camera_manager = get_service('camera_manager')

# Frame capture
main_frame = camera_manager.capture_main_frame()      # 1280x720
lores_frame = camera_manager.capture_lores_frame()    # 640x640

# Status and metadata
status = camera_manager.get_status()
metadata = camera_manager.last_metadata

# Control operations
camera_manager.start_camera()
camera_manager.stop_camera()
```

## 5) ข้อมูล Metadata ครบถ้วน (Complete Metadata Reference)

### 5.1 หมวดหมู่ Metadata ทั้ง 11 ประเภท

| หมวด | คำอธิบาย | ตัวอย่างข้อมูล |
|------|----------|----------------|
| `camera_properties` | ข้อมูลฮาร์ดแวร์กล้อง | Model, PixelArrayActiveAreas |
| `available_modes` | โหมดเซ็นเซอร์ที่รองรับ | Size, bit_depth, format |
| `current_config` | การตั้งค่าปัจจุบัน | Main/lores stream config |
| `camera_controls` | ตัวควบคุมกล้อง | Exposure, gain, focus |
| `frame_metadata` | ข้อมูลเฟรมแบบเรียลไทม์ | Timestamp, duration |
| `camera_status` | สถานะการทำงาน | Initialized, streaming |
| `frame_statistics` | สถิติการประมวลผล | Frame count, FPS |
| `configuration_details` | รายละเอียดการตั้งค่า | Stream details |
| `streams` | ข้อมูลสตรีม | Size, format, stride |
| `camera_config` | การตั้งค่าอุปกรณ์ | Sensor model, ISP |
| `metadata_timestamp` | เวลาที่เก็บข้อมูล | Unix timestamp |

### 5.2 ตัวอย่าง Metadata แบบละเอียด

```json
{
  "camera_properties": {
    "Model": "imx708",
    "PixelArrayActiveAreas": [[0, 0, 4608, 2592]],
    "ScalerCropMaximum": [0, 0, 4608, 2592],
    "SensorBlackLevels": [4096, 4096, 4096, 4096],
    "AeEnable": true,
    "AfEnable": true,
    "AwbEnable": true
  },
  "current_config": {
    "main": {
      "size": [1280, 720],
      "format": "RGB888",
      "stride": 3840,
      "frame_size": 2764800
    },
    "lores": {
      "size": [640, 640],
      "format": "XBGR8888",
      "stride": 2560,
      "frame_size": 1638400
    }
  },
  "camera_controls": {
    "FrameDurationLimits": [33333, 33333],
    "SensorExposureTime": 16666,
    "SensorAnalogueGain": 1.0,
    "ColourGains": [1.0, 1.0]
  }
}
```

## 6) การปรับแต่งประสิทธิภาพ (Performance Optimization)

### 6.1 Metadata Updates (Cache + Event)
```python
# แคชเมทาดาทาที่ความถี่ ~60 Hz และอัปเดตเมื่อมีเหตุการณ์สำคัญ
def _should_update_metadata(event_type):
    return event_type in ['camera_init', 'config_change', 'manual_refresh']

def update_metadata_loop():
    last = 0
    while running:
        now = time.time()
        if now - last >= 60.0 or _should_update_metadata(pending_event()):
            self._update_metadata()
            last = now
```

### 6.2 Thread-Safe Operations
```python
# Unified locking mechanism
@safe_camera_operation
def critical_camera_function(self):
    # Thread-safe camera operations
    pass
```

### 6.3 Memory Management
- JSON serializable metadata
- Structured storage by category
- Timestamp tracking for freshness
- Graceful error handling

## 7) การแก้ไขปัญหา (Debugging & Troubleshooting)

### 7.1 ปัญหาที่พบบ่อย

**1. Camera Initialization Failed**
```bash
# ตรวจสอบฮาร์ดแวร์
ls /dev/video*
lsmod | grep camera

# ทดสอบ Picamera2
python3 -c "from picamera2 import Picamera2; print('Camera OK')"
```

**2. Metadata Viewer 500 Error**
```bash
# ตรวจสอบ service availability
curl http://localhost/camera/test

# ตรวจสอบ dependency injection
python3 -c "
from src.core.dependency_container import get_service
camera_manager = get_service('camera_manager')
print(f'Camera manager: {camera_manager}')
"
```

**3. Resolution Configuration Issues**
```bash
# ตรวจสอบ .env.production
grep -E "MAIN_RESOLUTION|LORES_RESOLUTION" /home/camuser/aicamera/edge/installation/.env.production

# Expected output:
# MAIN_RESOLUTION=1280x720
# LORES_RESOLUTION=640x640
```

### 7.2 คำสั่งวินิจฉัยระบบ

```bash
# ตรวจสอบสถานะกล้อง
curl -s http://localhost/camera/status | python3 -m json.tool

# ดู metadata แบบละเอียด
curl -s http://localhost/camera/status | jq '.status.metadata'

# ทดสอบ WebSocket connection
wscat -c ws://localhost/socket.io/

# ตรวจสอบ systemd service
systemctl status aicamera_lpr.service
journalctl -u aicamera_lpr.service -n 50
```

## 8) การผนวกรวมกับโมดูลอื่น (Integration)

### 8.1 Detection Module Integration
```python
# Detection ใช้ lores stream (640x640)
frame = camera_manager.capture_lores_frame()
detection_result = detection_processor.process_frame(frame)
```

### 8.2 Health Monitor Integration
```python
# Health monitor ตรวจสอบสถานะกล้อง
camera_status = camera_manager.get_status()
health_check = {
    'camera_initialized': camera_status.get('initialized', False),
    'camera_streaming': camera_status.get('streaming', False)
}
```

### 8.3 Video Streaming Integration
```python
# Video streaming ใช้ main stream (1280x720)
def generate_frames():
    while True:
        frame = camera_manager.capture_main_frame()
        yield encode_frame(frame)
```

## 9) การตั้งค่าและที่เก็บไฟล์ (Configuration & Storage)

### 9.1 Environment Variables
```bash
# /edge/installation/.env.production (ตัวอย่างค่าเริ่มต้น)
MAIN_RESOLUTION=1280x720        # สำหรับ Detection (main)
LORES_RESOLUTION=1280x720       # สำหรับ Web Preview (lores)
CAMERA_FPS=30
IMAGE_SAVE_DIR=captured_images  # สำหรับเก็บภาพ/บันทึก
```

### 9.2 File Structure
```
edge/
├── src/
│   ├── components/
│   │   └── camera_handler.py      # Low-level camera operations
│   ├── services/
│   │   ├── camera_manager.py      # High-level camera management
│   │   └── video_streaming.py     # Video streaming service
│   └── web/
│       ├── blueprints/camera.py   # Camera web routes
│       ├── static/js/camera.js    # Frontend JavaScript
│       └── templates/camera/      # Camera templates
└── captured_images/               # Image storage directory
```

## 10) แนวทางการพัฒนา (Development Guidelines)

### 10.1 การเพิ่ม Metadata ใหม่
```python
def get_metadata(self):
    metadata = {
        # Existing categories...
        'new_category': self._extract_new_metadata()
    }
    return metadata
```

### 10.2 การปรับแต่ง Resolution
```python
# ใน config.py
MAIN_RESOLUTION = tuple(map(int, os.getenv("MAIN_RESOLUTION", "1280x720").split('x')))
LORES_RESOLUTION = tuple(map(int, os.getenv("LORES_RESOLUTION", "640x640").split('x')))
```

### 10.3 การทดสอบ
```python
# Unit testing
def test_camera_initialization():
    camera_manager = get_service('camera_manager')
    status = camera_manager.get_status()
    assert status['initialized'] == True

# Integration testing (ขนาดขึ้นกับ config)
def test_dual_stream():
    main_frame = camera_manager.capture_main_frame()
    lores = camera_manager.capture_lores_frame()
    # main เป็นอาร์เรย์ RGB888 (ตรวจจับ)
    assert hasattr(main_frame, 'shape')
    # lores อาจเป็น bytes (MJPEG) หรืออาร์เรย์หากไม่มีฮาร์ดแวร์เอนโค้ด
    assert (isinstance(lores, bytes) or hasattr(lores, 'shape'))
```

---

เอกสารนี้เป็นคู่มือสำหรับนักพัฒนาในการทำงานกับโมดูลกล้องของระบบ AI Camera v2.0 ครอบคลุมตั้งแต่การตั้งค่าเบื้องต้นไปจนถึงการแก้ไขปัญหาขั้นสูง เพื่อให้สามารถพัฒนาและบำรุงรักษาระบบได้อย่างมีประสิทธิภาพ
