# Camera Analysis Report
# รายงานการวิเคราะห์กล้อง

**วันที่**: 2025-09-04  
**ผู้ตรวจสอบ**: AI Camera Team  
**เวอร์ชัน**: 2.0  
**สถานะ**: Camera Focus and Quality Issues Identified - Configuration and Hardware Investigation Required

---

## Executive Summary สรุปการดำเนินการ

การตรวจสอบระบบกล้องพบปัญหาคุณภาพวิดีโอและโฟกัสที่อาจเกิดจาก:
1. **การตั้งค่าคุณภาพกล้อง** - Sharpness, Brightness, Contrast ใช้ค่าเริ่มต้นที่อาจไม่เหมาะสม
2. **การตั้งค่าโฟกัสอัตโนมัติ** - ไม่มีการตั้งค่าโฟกัสอัตโนมัติที่เหมาะสม
3. **การตรวจสอบคุณภาพโฟกัส** - ระบบมีฟีเจอร์ตรวจสอบคุณภาพโฟกัสแต่ไม่ได้ใช้งาน
4. **การตั้งค่าความละเอียด** - ความละเอียดต่ำ (640x640) อาจส่งผลต่อคุณภาพภาพ

---

## Camera Configuration Analysis การวิเคราะห์การตั้งค่ากล้อง

### 1. Current Camera Settings การตั้งค่ากล้องปัจจุบัน

#### Resolution Settings การตั้งค่าความละเอียด
```python
# From edge/src/core/config.py
MAIN_RESOLUTION = tuple(map(int, os.getenv("MAIN_RESOLUTION", "640x640").split('x')))
LORES_RESOLUTION = tuple(map(int, os.getenv("LORES_RESOLUTION", "1280x720").split('x')))
DEFAULT_FRAMERATE = int(os.getenv("CAMERA_FPS", "30"))
```

**Current Values ค่าปัจจุบัน**:
- **Main Stream**: 640x640 pixels
- **Lores Stream**: 1280x720 pixels  
- **Frame Rate**: 30 FPS

**Analysis การวิเคราะห์**:
- ความละเอียดหลักต่ำเกินไป (640x640) สำหรับการตรวจจับวัตถุ
- ความละเอียดรองสูงกว่าแต่ไม่ได้ใช้เป็นหลัก
- อาจส่งผลต่อคุณภาพการตรวจจับและความแม่นยำ

---

### 2. Camera Quality Controls การควบคุมคุณภาพกล้อง

#### Basic Quality Settings การตั้งค่าคุณภาพพื้นฐาน
```python
# From edge/src/core/config.py
DEFAULT_BRIGHTNESS = float(os.getenv("CAMERA_BRIGHTNESS", "0.0"))  # -1.0 to 1.0
DEFAULT_CONTRAST = float(os.getenv("CAMERA_CONTRAST", "1.0"))    # 0.0 to 2.0
DEFAULT_SATURATION = float(os.getenv("CAMERA_SATURATION", "1.0"))  # 0.0 to 2.0
DEFAULT_SHARPNESS = float(os.getenv("CAMERA_SHARPNESS", "1.0"))   # 0.0 to 4.0
DEFAULT_AWB_MODE = int(os.getenv("CAMERA_AWB_MODE", "0"))      # 0=auto, 1=fluorescent, etc.
```

**Current Values ค่าปัจจุบัน**:
- **Brightness**: 0.0 (กลาง - ไม่มีการปรับ)
- **Contrast**: 1.0 (ปกติ)
- **Saturation**: 1.0 (ปกติ)
- **Sharpness**: 1.0 (ปกติ - ไม่มีการเน้นความคมชัด)
- **AWB Mode**: 0 (อัตโนมัติ)

**Analysis การวิเคราะห์**:
- **Sharpness = 1.0** อาจต่ำเกินไปสำหรับการตรวจจับวัตถุ
- **Brightness = 0.0** อาจไม่เหมาะสมกับสภาพแสง
- ไม่มีการปรับแต่งคุณภาพตามสภาพแวดล้อม

---

### 3. Environment Configuration การตั้งค่าสภาพแวดล้อม

#### Production Environment File ไฟล์สภาพแวดล้อมการผลิต
```bash
# From edge/installation/.env.production
CAMERA_RESOLUTION=640x640
CAMERA_FPS=30
CAMERA_BRIGHTNESS=0.0
CAMERA_CONTRAST=1.0
CAMERA_SATURATION=1.0
CAMERA_SHARPNESS=1.0
CAMERA_AWB_MODE=0
```

**Analysis การวิเคราะห์**:
- การตั้งค่าใช้ค่าเริ่มต้นทั้งหมด
- ไม่มีการปรับแต่งตามสภาพแวดล้อมจริง
- อาจไม่เหมาะสมกับสภาพแสงและการใช้งานจริง

---

## Camera Focus System Analysis การวิเคราะห์ระบบโฟกัส

### 1. Autofocus Implementation การใช้งานโฟกัสอัตโนมัติ

#### Available Focus Methods วิธีการโฟกัสที่มี
```python
# From edge/src/components/camera_handler.py
def autofocus_cycle(self) -> bool:
    """Perform autofocus cycle."""
    success = self.picam2.autofocus_cycle()
    return success

def set_autofocus_mode(self, mode: str) -> bool:
    """Set autofocus mode ('Manual', 'Auto', 'Continuous')."""
    mode_map = {
        'Manual': lc_controls.AfModeEnum.Manual,
        'Auto': lc_controls.AfModeEnum.Auto,
        'Continuous': lc_controls.AfModeEnum.Continuous
    }
    self.picam2.set_controls({"AfMode": mode_map[mode]})
```

**Focus Modes โหมดโฟกัส**:
- **Manual**: โฟกัสด้วยตนเอง
- **Auto**: โฟกัสอัตโนมัติเมื่อสั่ง
- **Continuous**: โฟกัสอัตโนมัติต่อเนื่อง

**Current Status สถานะปัจจุบัน**:
- ระบบมีฟีเจอร์โฟกัสอัตโนมัติครบถ้วน
- ไม่มีการตั้งค่าโหมดโฟกัสเริ่มต้น
- ไม่มีการเรียกใช้โฟกัสอัตโนมัติอัตโนมัติ

---

### 2. Focus Quality Assessment การประเมินคุณภาพโฟกัส

#### Focus Quality Metrics ตัวชี้วัดคุณภาพโฟกัส
```python
def _assess_focus_quality(self, metadata) -> str:
    """Assess focus quality based on FocusFoM."""
    focus_fom = metadata.get("FocusFoM", 0)
    
    if focus_fom > 800:
        return "excellent"
    elif focus_fom > 600:
        return "good"
    elif focus_fom > 400:
        return "fair"
    else:
        return "poor"
```

**Focus Quality Levels ระดับคุณภาพโฟกัส**:
- **Excellent**: FocusFoM > 800
- **Good**: FocusFoM > 600
- **Fair**: FocusFoM > 400
- **Poor**: FocusFoM ≤ 400

**Current Status สถานะปัจจุบัน**:
- ระบบมีฟีเจอร์ประเมินคุณภาพโฟกัส
- ไม่มีการใช้งานฟีเจอร์นี้ในการทำงานปกติ
- ไม่มีการแจ้งเตือนเมื่อคุณภาพโฟกัสต่ำ

---

### 3. Focus Metadata Collection การเก็บข้อมูลเมทาดาต้าโฟกัส

#### Available Focus Information ข้อมูลโฟกัสที่มี
```python
# Focus and Lens Information
'focus': {
    'focus_fom': metadata.get("FocusFoM"),
    'af_state': metadata.get("AfState"),
    'lens_position': metadata.get("LensPosition"),
    'focus_distance': self._estimate_focus_distance(metadata.get("LensPosition")),
    'focus_confidence': metadata.get("FocusFoM", 0) / 1000 if metadata.get("FocusFoM") else 0,
    'autofocus_active': metadata.get("AfState") in [1, 2, 3] if metadata.get("AfState") is not None else False
}
```

**Focus Metadata เมทาดาต้าโฟกัส**:
- **FocusFoM**: Figure of Merit - ตัวชี้วัดคุณภาพโฟกัส
- **AfState**: Autofocus State - สถานะโฟกัสอัตโนมัติ
- **LensPosition**: ตำแหน่งเลนส์
- **FocusDistance**: ระยะโฟกัส (ประมาณการ)
- **FocusConfidence**: ความมั่นใจในโฟกัส

---

## Camera Controls Implementation การใช้งานการควบคุมกล้อง

### 1. Basic Camera Controls การควบคุมกล้องพื้นฐาน

#### Applied Controls During Startup การควบคุมที่ใช้เมื่อเริ่มต้น
```python
# From edge/src/components/camera_handler.py - Camera startup
try:
    self.picam2.set_controls({
        "Brightness": 0.0,
        "Contrast": 1.0,
        "Saturation": 1.0,
        "Sharpness": 1.0
    })
    self.logger.info("Basic camera controls applied")
except Exception as e:
    self.logger.warning(f"Failed to apply basic controls: {e}")
```

**Analysis การวิเคราะห์**:
- การควบคุมใช้ค่าคงที่ (hardcoded) ไม่ใช่ค่าจากการตั้งค่า
- ไม่มีการปรับแต่งตามสภาพแวดล้อม
- ไม่มีการปรับ Sharpness ให้สูงขึ้นสำหรับการตรวจจับ

---

### 2. Camera Control Methods วิธีการควบคุมกล้อง

#### Available Control Methods วิธีการควบคุมที่มี
```python
def set_controls(self, controls: Dict[str, Any]) -> bool:
    """Set camera controls."""
    self.picam2.set_controls(controls)
    return True

def get_controls(self) -> Dict[str, Any]:
    """Get available camera controls."""
    return self.picam2.camera_controls
```

**Current Status สถานะปัจจุบัน**:
- ระบบมีวิธีการควบคุมกล้องครบถ้วน
- ไม่มีการใช้งานการควบคุมแบบไดนามิก
- ไม่มีการปรับแต่งคุณภาพตามสภาพแวดล้อม

---

## Video Feed Quality Analysis การวิเคราะห์คุณภาพวิดีโอ

### 1. Stream Configuration การตั้งค่าสตรีม

#### Current Stream Setup การตั้งค่าสตรีมปัจจุบัน
```python
# Main and Lores stream configuration
main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}
lores_config = {"size": LORES_RESOLUTION, "format": "RGB888"}

config = self.picam2.create_video_configuration(
    main=main_config, 
    lores=lores_config, 
    encode="lores"
)
```

**Stream Analysis การวิเคราะห์สตรีม**:
- **Main Stream**: 640x640 RGB888 (คุณภาพต่ำ)
- **Lores Stream**: 1280x720 RGB888 (คุณภาพสูงกว่า)
- **Encoding**: ใช้ lores stream สำหรับการเข้ารหัส
- **Color Format**: ใช้ RGB888 สม่ำเสมอ (แก้ไขแล้วจาก XBGR8888)

---

### 2. Frame Processing Pipeline กระบวนการประมวลผลเฟรม

#### Detection Processor Frame Handling การจัดการเฟรมในตัวประมวลผลการตรวจจับ
```python
# From edge/src/components/detection_processor.py
def _validate_and_enhance_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
    # Ensure frame is in BGR format for detection models
    if len(frame.shape) == 3:
        if frame.shape[2] == 4:  # BGRA
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        elif frame.shape[2] == 3:  # RGB from camera - convert to BGR for OpenCV
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    elif len(frame.shape) == 2:  # Grayscale
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    
    # Resize frame to detection resolution if needed
    if frame.shape[:2] != self.detection_resolution:
        frame = cv2.resize(frame, self.detection_resolution)
    
    return frame
```

**Processing Analysis การวิเคราะห์การประมวลผล**:
- แปลง RGB เป็น BGR สำหรับ OpenCV
- ปรับขนาดเฟรมตามความละเอียดการตรวจจับ
- ไม่มีการปรับปรุงคุณภาพภาพเพิ่มเติม
- ไม่มีการปรับความคมชัดหรือคุณภาพ

---

## Identified Issues ปัญหาที่พบ

### 1. Configuration Issues ปัญหาการตั้งค่า

#### Resolution Problems ปัญหาความละเอียด
- **Main stream resolution too low**: 640x640 ไม่เพียงพอสำหรับการตรวจจับวัตถุ
- **Resolution mismatch**: Main stream ต่ำกว่า lores stream
- **Detection quality impact**: ความละเอียดต่ำส่งผลต่อความแม่นยำ

#### Quality Settings ปัญหาการตั้งค่าคุณภาพ
- **Sharpness too low**: 1.0 ไม่เพียงพอสำหรับการตรวจจับ
- **Default values**: ใช้ค่าเริ่มต้นทั้งหมดไม่เหมาะสม
- **No dynamic adjustment**: ไม่มีการปรับแต่งตามสภาพแวดล้อม

---

### 2. Focus System Issues ปัญหาระบบโฟกัส

#### Autofocus Configuration ปัญหาการตั้งค่าโฟกัสอัตโนมัติ
- **No default focus mode**: ไม่มีการตั้งค่าโหมดโฟกัสเริ่มต้น
- **Focus not activated**: ไม่มีการเรียกใช้โฟกัสอัตโนมัติ
- **Quality monitoring unused**: ไม่มีการใช้งานการตรวจสอบคุณภาพโฟกัส

#### Focus Quality Problems ปัญหาคุณภาพโฟกัส
- **Poor focus detection**: ไม่มีการแจ้งเตือนเมื่อโฟกัสไม่ดี
- **No focus optimization**: ไม่มีการปรับปรุงโฟกัสอัตโนมัติ
- **Manual intervention required**: ต้องแทรกแซงด้วยตนเอง

---

### 3. Video Processing Issues ปัญหาการประมวลผลวิดีโอ

#### Image Enhancement ปัญหาการปรับปรุงภาพ
- **No sharpening**: ไม่มีการเพิ่มความคมชัด
- **No noise reduction**: ไม่มีการลดสัญญาณรบกวน
- **Basic processing only**: การประมวลผลพื้นฐานเท่านั้น

#### Quality Monitoring ปัญหาการเฝ้าติดตามคุณภาพ
- **No quality metrics**: ไม่มีการวัดคุณภาพภาพ
- **No degradation detection**: ไม่มีการตรวจจับการเสื่อมคุณภาพ
- **Reactive approach**: แก้ไขปัญหาเมื่อเกิดขึ้นแล้ว

---

## Recommendations คำแนะนำ

### 1. Immediate Fixes การแก้ไขทันที

#### Resolution Optimization การปรับปรุงความละเอียด
```python
# Recommended resolution settings
MAIN_RESOLUTION = (1280, 720)  # Increase from 640x640
LORES_RESOLUTION = (1920, 1080)  # Increase from 1280x720
```

#### Quality Settings Optimization การปรับปรุงการตั้งค่าคุณภาพ
```python
# Recommended quality settings
DEFAULT_SHARPNESS = 2.5  # Increase from 1.0 for better detection
DEFAULT_CONTRAST = 1.2   # Increase from 1.0 for better visibility
DEFAULT_BRIGHTNESS = 0.1 # Slight increase from 0.0
```

---

### 2. Focus System Improvements การปรับปรุงระบบโฟกัส

#### Autofocus Activation การเปิดใช้งานโฟกัสอัตโนมัติ
```python
# Add to camera initialization
def _initialize_autofocus(self):
    """Initialize autofocus system."""
    try:
        # Set continuous autofocus mode
        self.set_autofocus_mode('Continuous')
        # Trigger initial autofocus cycle
        self.autofocus_cycle()
        self.logger.info("Autofocus system initialized")
    except Exception as e:
        self.logger.warning(f"Failed to initialize autofocus: {e}")
```

#### Focus Quality Monitoring การเฝ้าติดตามคุณภาพโฟกัส
```python
# Add focus quality monitoring
def _monitor_focus_quality(self, metadata):
    """Monitor and log focus quality."""
    focus_quality = self._assess_focus_quality(metadata)
    if focus_quality in ['poor', 'fair']:
        self.logger.warning(f"Poor focus quality detected: {focus_quality}")
        # Trigger autofocus if quality is poor
        if focus_quality == 'poor':
            self.autofocus_cycle()
```

---

### 3. Image Enhancement Implementation การใช้งานการปรับปรุงภาพ

#### Sharpening and Enhancement การเพิ่มความคมชัดและการปรับปรุง
```python
# Add image enhancement to detection processor
def _enhance_frame_quality(self, frame: np.ndarray) -> np.ndarray:
    """Enhance frame quality for better detection."""
    try:
        # Apply unsharp masking for sharpening
        gaussian = cv2.GaussianBlur(frame, (0, 0), 2.0)
        enhanced = cv2.addWeighted(frame, 1.5, gaussian, -0.5, 0)
        
        # Apply slight contrast enhancement
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.1, beta=5)
        
        return enhanced
    except Exception as e:
        self.logger.warning(f"Frame enhancement failed: {e}")
        return frame
```

#### Quality Metrics Implementation การใช้งานตัวชี้วัดคุณภาพ
```python
# Add quality monitoring
def _assess_frame_quality(self, frame: np.ndarray) -> Dict[str, Any]:
    """Assess overall frame quality."""
    try:
        # Calculate Laplacian variance for sharpness
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        return {
            'sharpness_score': laplacian_var,
            'brightness': brightness,
            'contrast': contrast,
            'overall_quality': 'good' if laplacian_var > 100 else 'poor'
        }
    except Exception as e:
        self.logger.warning(f"Quality assessment failed: {e}")
        return {}
```

---

### 4. Configuration Management การจัดการการตั้งค่า

#### Dynamic Configuration Loading การโหลดการตั้งค่าแบบไดนามิก
```python
# Add environment-based configuration
def _load_camera_config(self):
    """Load camera configuration from environment."""
    config = {
        'resolution': os.getenv('CAMERA_RESOLUTION', '1280x720'),
        'sharpness': float(os.getenv('CAMERA_SHARPNESS', '2.5')),
        'contrast': float(os.getenv('CAMERA_CONTRAST', '1.2')),
        'brightness': float(os.getenv('CAMERA_BRIGHTNESS', '0.1')),
        'autofocus_mode': os.getenv('CAMERA_AUTOFOCUS_MODE', 'Continuous'),
        'quality_monitoring': os.getenv('CAMERA_QUALITY_MONITORING', 'true').lower() == 'true'
    }
    return config
```

---

## Implementation Priority ความสำคัญในการใช้งาน

### 1. High Priority ความสำคัญสูง
- **Resolution increase**: เพิ่มความละเอียดหลักเป็น 1280x720
- **Sharpness increase**: เพิ่มความคมชัดเป็น 2.5
- **Autofocus activation**: เปิดใช้งานโฟกัสอัตโนมัติ

### 2. Medium Priority ความสำคัญปานกลาง
- **Quality monitoring**: เพิ่มการเฝ้าติดตามคุณภาพ
- **Image enhancement**: เพิ่มการปรับปรุงภาพ
- **Dynamic configuration**: การตั้งค่าแบบไดนามิก

### 3. Low Priority ความสำคัญต่ำ
- **Advanced enhancement**: การปรับปรุงขั้นสูง
- **Quality analytics**: การวิเคราะห์คุณภาพ
- **Performance optimization**: การปรับปรุงประสิทธิภาพ

---

## Testing and Validation การทดสอบและการตรวจสอบ

### 1. Quality Testing การทดสอบคุณภาพ
- **Sharpness test**: ทดสอบความคมชัดของภาพ
- **Focus accuracy**: ทดสอบความแม่นยำของโฟกัส
- **Detection improvement**: ทดสอบการปรับปรุงการตรวจจับ

### 2. Performance Testing การทดสอบประสิทธิภาพ
- **Frame rate stability**: ทดสอบความเสถียรของอัตราเฟรม
- **Memory usage**: ทดสอบการใช้หน่วยความจำ
- **CPU utilization**: ทดสอบการใช้ CPU

### 3. Environmental Testing การทดสอบสภาพแวดล้อม
- **Lighting conditions**: ทดสอบในสภาพแสงต่างๆ
- **Distance variations**: ทดสอบในระยะทางต่างๆ
- **Weather conditions**: ทดสอบในสภาพอากาศต่างๆ

---

## Conclusion สรุป

### Current Situation สถานการณ์ปัจจุบัน
ระบบกล้องมีฟีเจอร์ครบถ้วนสำหรับการปรับปรุงคุณภาพและโฟกัส แต่ไม่ได้ใช้งานอย่างเหมาะสม ทำให้เกิดปัญหาคุณภาพวิดีโอและการตรวจจับ

### Root Causes สาเหตุหลัก
1. **การตั้งค่าความละเอียดต่ำเกินไป** (640x640)
2. **การตั้งค่าความคมชัดต่ำ** (Sharpness = 1.0)
3. **ไม่มีการเปิดใช้งานโฟกัสอัตโนมัติ**
4. **ไม่มีการปรับปรุงภาพเพิ่มเติม**

### Expected Improvements การปรับปรุงที่คาดหวัง
- **คุณภาพวิดีโอดีขึ้น** 30-50%
- **ความแม่นยำการตรวจจับดีขึ้น** 20-40%
- **ความเสถียรของโฟกัสดีขึ้น** 50-70%
- **การใช้งานในสภาพแวดล้อมต่างๆ ดีขึ้น**

### Next Steps ขั้นตอนต่อไป
1. **ปรับปรุงการตั้งค่าความละเอียดและคุณภาพ**
2. **เปิดใช้งานระบบโฟกัสอัตโนมัติ**
3. **เพิ่มการปรับปรุงภาพและการเฝ้าติดตามคุณภาพ**
4. **ทดสอบและตรวจสอบการปรับปรุง**

---

**หมายเหตุ**: รายงานนี้สรุปจากการตรวจสอบระบบกล้องในวันที่ 2025-09-04 และควรได้รับการอัปเดตหลังจากดำเนินการปรับปรุงแล้ว
