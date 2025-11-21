# Picamera2 Configuration Guide สำหรับ IMX708 (Camera Module 3)

## ภาพรวม

เอกสารนี้อธิบายวิธีการ configure `picamera2` library สำหรับ **Raspberry Pi Camera Module 3** ที่ใช้เซ็นเซอร์ **IMX708**

## 1. การเริ่มต้นใช้งาน (Basic Initialization)

### 1.1 สร้าง Camera Instance

```python
from picamera2 import Picamera2

# สร้าง camera instance
picam2 = Picamera2()
```

**หมายเหตุ**: Picamera2 จะตรวจจับกล้องที่เชื่อมต่ออัตโนมัติ (Camera Module 3 = IMX708)

### 1.2 ตรวจสอบ Camera Properties

```python
# ดูข้อมูลเซ็นเซอร์
camera_properties = picam2.camera_properties
print(f"Camera Model: {camera_properties['Model']}")  # จะแสดง "imx708"

# ดู sensor modes ที่รองรับ
sensor_modes = picam2.sensor_modes
print(f"Available sensor modes: {len(sensor_modes)}")
for i, mode in enumerate(sensor_modes):
    print(f"Mode {i}: {mode}")
```

**ตัวอย่าง Output สำหรับ IMX708**:
```python
{
    'Model': 'imx708',
    'PixelArrayActiveAreas': [[0, 0, 4608, 2592]],
    'ScalerCropMaximum': [0, 0, 4608, 2592],
    # ... properties อื่นๆ
}
```

## 2. การ Configure Camera (Configuration)

### 2.1 Video Configuration (แนะนำสำหรับ Video Streaming)

```python
from edge.src.core.config import MAIN_RESOLUTION, LORES_RESOLUTION

# Main stream configuration (สำหรับ Detection)
main_config = {
    "size": MAIN_RESOLUTION,  # ตัวอย่าง: (1280, 720)
    "format": "RGB888"        # RGB color format
}

# Lores stream configuration (สำหรับ Web Preview/Streaming)
lores_config = {
    "size": LORES_RESOLUTION,  # ตัวอย่าง: (640, 640)
    "format": "RGB888"         # RGB color format
}

# สร้าง video configuration
config = picam2.create_video_configuration(
    main=main_config,
    lores=lores_config
)

# Apply configuration
picam2.configure(config)
```

### 2.2 Still Configuration (สำหรับการถ่ายภาพคุณภาพสูง)

```python
# Still configuration สำหรับ IMX708
still_config = {
    "size": (4608, 2592),  # Native resolution ของ IMX708
    "format": "RGB888"
}

config = picam2.create_still_configuration(
    main=still_config
)

picam2.configure(config)
```

### 2.3 Preview Configuration (สำหรับ Preview เท่านั้น)

```python
# Preview configuration
preview_config = picam2.create_preview_configuration(
    main={"size": (1280, 720)}
)

picam2.configure(preview_config)
```

## 3. Camera Controls (การควบคุมกล้อง)

### 3.1 Basic Quality Controls

```python
controls = {
    "Brightness": 0.0,      # -1.0 ถึง 1.0
    "Contrast": 1.0,        # 0.0 ถึง 2.0
    "Saturation": 1.0,      # 0.0 ถึง 2.0
    "Sharpness": 1.0,       # 0.0 ถึง 4.0
}

picam2.set_controls(controls)
```

### 3.2 Auto Exposure และ Auto White Balance

```python
from libcamera import controls as lc_controls

controls = {
    "AeEnable": True,                    # Auto Exposure
    "AwbEnable": True,                   # Auto White Balance
    "AwbMode": lc_controls.AwbModeEnum.Auto,
    "AeConstraintMode": lc_controls.AeConstraintModeEnum.Normal,
}

picam2.set_controls(controls)
```

### 3.3 Autofocus Controls (สำคัญสำหรับ Camera Module 3)

```python
from libcamera import controls as lc_controls

# Mode 0: Manual focus
# Mode 1: Auto (single-shot when triggered)
# Mode 2: Continuous autofocus

# Continuous Autofocus (แนะนำสำหรับ Video)
controls = {
    "AfMode": 2,              # Continuous autofocus
    "AfRange": 0,             # Full range
    "AfSpeed": 0,             # Normal speed (0) หรือ Fast (1)
    "AfMetering": 1,          # Center-weighted metering
}

# Auto Mode (single-shot)
controls = {
    "AfMode": 1,              # Auto mode
    "AfTrigger": 0,           # Start trigger (0=Start, 1=Cancel)
    "AfRange": 0,             # Full range
    "AfSpeed": 0,             # Normal speed
    "AfMetering": 1,          # Center-weighted
}

# Manual Focus
controls = {
    "AfMode": 0,              # Manual mode
    "LensPosition": 0.3,      # 0.0 ถึง 1.0 (focus distance)
}

picam2.set_controls(controls)
```

### 3.4 Exposure Control (Manual)

```python
# Manual exposure control
controls = {
    "ExposureTime": 16666,      # microseconds (16.666ms = 60fps)
    "AnalogueGain": 1.0,        # Analog gain
    "FrameDurationLimits": (33333, 33333),  # Min, Max frame duration (us)
}

picam2.set_controls(controls)
```

### 3.5 Low Light Optimization (สำหรับ IMX708)

```python
# Optimization สำหรับสภาพแสงต่ำ
controls = {
    "NoiseReductionMode": lc_controls.draft.NoiseReductionModeEnum.HighQuality,
    "ExposureTime": 50000,      # เพิ่ม exposure time
    "AnalogueGain": 2.0,        # เพิ่ม gain
    "Brightness": 0.1,          # เพิ่ม brightness เล็กน้อย
}

picam2.set_controls(controls)
```

## 4. Configuration ใน Codebase (ตัวอย่างจากโปรเจค)

### 4.1 Camera Handler Initialization

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
def initialize_camera(self) -> bool:
    """Initialize camera with IMX708 configuration"""
    
    from picamera2 import Picamera2
    
    # Create camera instance
    self.picam2 = Picamera2()
    
    # Get camera properties (IMX708 info)
    self.camera_properties = self.picam2.camera_properties
    self.sensor_modes = self.picam2.sensor_modes
    
    # Configure dual stream
    main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}
    lores_config = {"size": LORES_RESOLUTION, "format": "RGB888"}
    
    config = self.picam2.create_video_configuration(
        main=main_config,
        lores=lores_config
    )
    
    # Apply configuration
    self.picam2.configure(config)
    
    # Apply initial controls
    self._apply_initial_controls()
    
    return True
```

### 4.2 Initial Controls Application

```python
def _apply_initial_controls(self):
    """Apply initial camera controls for IMX708"""
    
    controls = {
        "Brightness": 0.0,
        "Contrast": 1.0,
        "Saturation": 1.0,
        "Sharpness": 1.0,
        "AwbMode": 0,           # Auto white balance
        "AeEnable": True,       # Auto exposure
        "AwbEnable": True,      # Auto white balance
    }
    
    # Autofocus setup
    if DEFAULT_AUTOFOCUS_ENABLED:
        controls["AfMode"] = DEFAULT_AUTOFOCUS_MODE  # 0=Manual, 1=Auto, 2=Continuous
        controls["AfRange"] = 0      # Full range
        controls["AfSpeed"] = 0      # Normal speed
        controls["AfMetering"] = 1   # Center-weighted
    
    # Try libcamera controls
    try:
        from libcamera import controls as lc_controls
        controls["AwbMode"] = lc_controls.AwbModeEnum.Auto
        controls["AeConstraintMode"] = lc_controls.AeConstraintModeEnum.Normal
    except ImportError:
        pass
    
    self.picam2.set_controls(controls)
```

## 5. Environment Variables Configuration

### 5.1 Resolution Configuration

**ไฟล์**: `.env.production`

```bash
# Main stream resolution (สำหรับ Detection)
MAIN_RESOLUTION=1280x720

# Lores stream resolution (สำหรับ Web Preview)
LORES_RESOLUTION=640x640

# Camera FPS
CAMERA_FPS=15
```

### 5.2 Focus Configuration

```bash
# Autofocus mode: 0=Manual, 1=Auto, 2=Continuous
DEFAULT_AUTOFOCUS_MODE=2

# Enable/Disable autofocus
DEFAULT_AUTOFOCUS_ENABLED=true
```

### 5.3 Quality Controls

```bash
# Brightness (-1.0 to 1.0)
CAMERA_BRIGHTNESS=0.0

# Contrast (0.0 to 2.0)
CAMERA_CONTRAST=1.0

# Saturation (0.0 to 2.0)
CAMERA_SATURATION=1.0

# Sharpness (0.0 to 4.0)
CAMERA_SHARPNESS=1.0

# Auto White Balance Mode (0=Auto, 1=Fluorescent, etc.)
CAMERA_AWB_MODE=0
```

## 6. Sensor Modes สำหรับ IMX708

### 6.1 ตรวจสอบ Sensor Modes

```python
sensor_modes = picam2.sensor_modes

for i, mode in enumerate(sensor_modes):
    print(f"Mode {i}:")
    print(f"  Size: {mode['size']}")
    print(f"  Bit depth: {mode.get('bit_depth', 'N/A')}")
    print(f"  Unpacked format: {mode.get('unpacked', 'N/A')}")
    print(f"  Packed format: {mode.get('packed', 'N/A')}")
```

### 6.2 เลือก Sensor Mode (ถ้าต้องการ)

```python
# ใช้ sensor mode เฉพาะ (ถ้ามีหลาย mode)
config = picam2.create_video_configuration(
    main={"size": (1280, 720)},
    sensor={"output_size": (4608, 2592)}  # Native IMX708 resolution
)

picam2.configure(config)
```

## 7. Best Practices สำหรับ IMX708

### 7.1 Dual Stream Setup

- **Main Stream**: ใช้ resolution สูง (1280x720 หรือสูงกว่า) สำหรับ Detection
- **Lores Stream**: ใช้ resolution ต่ำกว่า (640x640) สำหรับ Preview/Streaming
- ใช้ format **RGB888** สำหรับทั้งสอง stream

### 7.2 Autofocus Strategy

- **Video Streaming**: ใช้ **Continuous (Mode 2)** สำหรับการปรับโฟกัสอัตโนมัติ
- **Detection**: ใช้ **Auto (Mode 1)** กับ trigger เมื่อคุณภาพภาพลดลง
- **Fixed Distance**: ใช้ **Manual (Mode 0)** พร้อม LensPosition

### 7.3 Performance Optimization

```python
# ใช้ hardware encoder ถ้ามี
from picamera2.encoders import MJPEGEncoder, H264Encoder

if MJPEGEncoder._hw_encoder_available:
    encoder = MJPEGEncoder(bitrate=2000000, quality=85)
    # ใช้ encoder สำหรับ lores stream
```

### 7.4 Low Light Handling

```python
# สำหรับสภาพแสงต่ำ
controls = {
    "ExposureTime": 50000,       # เพิ่ม exposure
    "AnalogueGain": 2.0,         # เพิ่ม gain
    "NoiseReductionMode": lc_controls.draft.NoiseReductionModeEnum.HighQuality,
}
```

## 8. Troubleshooting

### 8.1 Camera ไม่พบ

```python
# ตรวจสอบ camera availability
camera_status = check_camera_availability()
print(camera_status)

# ตรวจสอบ hardware
import os
print(os.path.exists('/dev/video0'))
```

### 8.2 Configuration Errors

```python
# ตรวจสอบ camera properties
print(picam2.camera_properties)

# ตรวจสอบ sensor modes
print(picam2.sensor_modes)

# ตรวจสอบ current config
print(picam2.camera_configuration())
```

### 8.3 Autofocus Issues

- ตรวจสอบว่า `AfMode` ถูกต้อง (0, 1, หรือ 2)
- สำหรับ Auto mode ต้อง trigger ด้วย `AfTrigger: 0`
- ตรวจสอบ `DEFAULT_AUTOFOCUS_ENABLED` ใน config

## 9. ตัวอย่างการใช้งานเต็มรูปแบบ

```python
#!/usr/bin/env python3
"""Complete example: IMX708 Configuration"""

from picamera2 import Picamera2
from libcamera import controls as lc_controls
import time

# 1. Initialize camera
picam2 = Picamera2()

# 2. Check camera model
print(f"Camera Model: {picam2.camera_properties['Model']}")  # imx708

# 3. Configure dual stream
main_config = {"size": (1280, 720), "format": "RGB888"}
lores_config = {"size": (640, 640), "format": "RGB888"}

config = picam2.create_video_configuration(
    main=main_config,
    lores=lores_config
)

picam2.configure(config)

# 4. Apply controls
controls = {
    "Brightness": 0.0,
    "Contrast": 1.0,
    "Saturation": 1.0,
    "Sharpness": 1.0,
    "AeEnable": True,
    "AwbEnable": True,
    "AwbMode": lc_controls.AwbModeEnum.Auto,
    "AfMode": 2,  # Continuous autofocus
    "AfRange": 0,
    "AfSpeed": 0,
    "AfMetering": 1,
}

picam2.set_controls(controls)

# 5. Start camera
picam2.start()

# 6. Capture frames
try:
    for i in range(10):
        request = picam2.capture_request()
        main_array = request.make_array("main")
        lores_array = request.make_array("lores")
        request.release()
        print(f"Captured frame {i}: main={main_array.shape}, lores={lores_array.shape}")
        time.sleep(0.1)
finally:
    # 7. Stop camera
    picam2.stop()
```

## 10. อ้างอิง

- [Picamera2 GitHub Repository](https://github.com/raspberrypi/picamera2)
- [Libcamera Documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- Camera Module 3 Specifications: IMX708 sensor, 12MP (4608x2592)

---

**หมายเหตุ**: 
- IMX708 เป็นเซ็นเซอร์ที่ใช้ใน **Raspberry Pi Camera Module 3**
- Picamera2 จะตรวจจับกล้องอัตโนมัติ ไม่ต้องระบุ sensor model โดยตรง
- การ configuration จะผ่าน `create_video_configuration()` หรือ `create_still_configuration()`
- Controls จะถูกกำหนดผ่าน `set_controls()` dictionary

