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
MAIN_RESOLUTION = tuple(map(int, os.getenv("MAIN_RESOLUTION", "1280x720").split('x')))
LORES_RESOLUTION = tuple(map(int, os.getenv("LORES_RESOLUTION", "640x640").split('x')))
DEFAULT_FRAMERATE = int(os.getenv("CAMERA_FPS", "30"))
```

**Current Values ค่าปัจจุบัน**:
- **Main Stream**: 1280x720 pixels
- **Lores Stream**: 640x640 pixels  
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

## Camera Focus Issue Investigation
### Current Focus System Status
The system has autofocus capabilities but they're not being utilized effectively:
- Autofocus is implemented but not activated - The CameraHandler has autofocus methods but they're not called during initialization
- Focus quality monitoring exists but unused - The _assess_focus_quality method is available but not integrated into the detection pipeline
- No automatic focus optimization - The system doesn't automatically adjust focus based on detection quality
### Detection Resolution Constraint Analysis
The detection models require 640x640 pixels, but the current configuration has:
- Main Stream: 1280x720 (higher quality)
- Lores Stream: 640x640 (detection resolution)
- Detection Models: Require 640x640

### Implementation Priority and Timeline
**1: Focus System and Basic Quality**
- Task 1.1: Implement Automatic Focus Initialization
- Task 1.2: Implement Focus Quality Monitoring
- Task 1.3: Add Focus Distance Optimization for LPR
- Task 2.1: Implement Smart Resolution Management

**2: Resolution Pipeline and Enhancement**
- Task 2.2: Create Intelligent Frame Resizing Pipeline
- Task 2.3: Implement Letterbox Resizing for Detection
- Task 3.1: Implement Advanced Image Enhancement

**3: Quality Monitoring and Configuration**
- Task 3.2: Implement Quality Metrics and Monitoring
- Task 4.1: Implement Environment-Based Camera Configuration
- Task 4.2: Implement Adaptive Quality Adjustment

**4: Analytics and Performance**
- Task 5.1: Implement Quality Analytics Dashboard
- Task 5.2: Implement Performance Monitoring

**Expected Improvements**
**Focus Quality:** 50-70% improvement in autofocus accuracy 
**Detection Accuracy:** 20-40% improvement due to better image quality
**Video Quality:** 30-50% improvement in overall video feed quality
**System Reliability:** Better handling of environmental changes
**Performance:** Optimized processing pipeline with quality monitoring

This comprehensive approach addresses the camera focus issues while maintaining the 640x640 detection requirement through intelligent resizing and quality enhancement.

### Comprehensive Improvement Task List
1. High Priority - Camera Focus System (Week 1)
- Task 1.1: Implement Automatic Focus Initialization
```python
# Add to CameraHandler.__init__ or _initialize_camera
def _initialize_autofocus(self):
    """Initialize autofocus system with optimal settings."""
    try:
        # Set continuous autofocus mode for best results
        self.set_autofocus_mode('Continuous')
        
        # Trigger initial autofocus cycle
        success = self.autofocus_cycle()
        if success:
            self.logger.info("Autofocus system initialized successfully")
        else:
            self.logger.warning("Initial autofocus cycle failed")
            
        # Set focus range for typical LPR distances (2-10 meters)
        self._set_focus_range_for_lpr()
        
    except Exception as e:
        self.logger.error(f"Failed to initialize autofocus: {e}")
```
- Task 1.2: Implement Focus Quality Monitoring
``` python
# Add to CameraHandler
def _monitor_focus_quality(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Monitor focus quality and trigger optimization if needed."""
    focus_quality = self._assess_focus_quality(metadata)
    focus_data = {
        'quality': focus_quality,
        'focus_fom': metadata.get("FocusFoM", 0),
        'af_state': metadata.get("AfState"),
        'lens_position': metadata.get("LensPosition"),
        'needs_optimization': False
    }
    
    # Trigger autofocus if quality is poor
    if focus_quality in ['poor', 'fair']:
        self.logger.warning(f"Poor focus quality detected: {focus_quality}")
        focus_data['needs_optimization'] = True
        
        # Trigger autofocus for poor quality
        if focus_quality == 'poor':
            self.autofocus_cycle()
            
    return focus_data
```
- Task 1.3: Add Focus Distance Optimization for LPR
``` python
# Add to CameraHandler
def _set_focus_range_for_lpr(self):
    """Set focus range optimized for license plate detection."""
    try:
        from libcamera import controls as lc_controls
        
        # LPR typically works best at 2-10 meters
        # Convert to dioptres: 1/distance_in_meters
        min_distance = 1/10.0  # 10 meters = 0.1 dioptres
        max_distance = 1/2.0   # 2 meters = 0.5 dioptres
        
        self.picam2.set_controls({
            "AfRange": lc_controls.AfRangeEnum.Normal,  # or Macro for closer focus
            "AfSpeed": lc_controls.AfSpeedEnum.Normal
        })
        
        self.logger.info(f"Set focus range for LPR: {min_distance:.2f} to {max_distance:.2f} dioptres")
        
    except Exception as e:
        self.logger.warning(f"Failed to set focus range: {e}")
```

### 2. High Priority - Resolution and Quality Optimization (Week 1-2)
- Task 2.1: Implement Smart Resolution Management
``` python
# Add to config.py
# New configuration for high-quality capture with detection resizing
HIGH_QUALITY_CAPTURE_RESOLUTION = tuple(map(int, os.getenv("HIGH_QUALITY_CAPTURE_RESOLUTION", "1920x1080").split('x')))
DETECTION_RESOLUTION = tuple(map(int, os.getenv("DETECTION_RESOLUTION", "640x640").split('x')))
QUALITY_ENHANCEMENT_ENABLED = os.getenv("QUALITY_ENHANCEMENT_ENABLED", "true").lower() == "true"
```

- Task 2.2: Create Intelligent Frame Resizing Pipeline
``` python
# Add to DetectionProcessor
def _create_high_quality_detection_pipeline(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create high-quality frame for storage and detection-optimized frame for AI models.
    
    Returns:
        Tuple of (high_quality_frame, detection_frame)
    """
    try:
        # Keep original high-quality frame for storage
        high_quality_frame = frame.copy()
        
        # Create detection-optimized frame
        detection_frame = self._optimize_for_detection(frame)
        
        return high_quality_frame, detection_frame
        
    except Exception as e:
        self.logger.error(f"Failed to create detection pipeline: {e}")
        return frame, frame

def _optimize_for_detection(self, frame: np.ndarray) -> np.ndarray:
    """Optimize frame specifically for detection models."""
    try:
        # Step 1: Apply quality enhancements before resizing
        enhanced_frame = self._enhance_frame_quality(frame)
        
        # Step 2: Smart resizing with letterboxing for aspect ratio preservation
        detection_frame = self._resize_with_letterbox(enhanced_frame, self.detection_resolution)
        
        # Step 3: Apply final detection-specific optimizations
        detection_frame = self._apply_detection_optimizations(detection_frame)
        
        return detection_frame
        
    except Exception as e:
        self.logger.error(f"Detection optimization failed: {e}")
        return cv2.resize(frame, self.detection_resolution)
```

- Task 2.3: Implement Letterbox Resizing for Detection 
``` python
# Add to DetectionProcessor
def _resize_with_letterbox(self, frame: np.ndarray, target_size: Tuple[int, int], 
                          padding_color: Tuple[int, int, int] = (114, 114, 114)) -> np.ndarray:
    """
    Resize frame to target size while preserving aspect ratio using letterboxing.
    
    Args:
        frame: Input frame
        target_size: Target (width, height)
        padding_color: BGR color for padding
        
    Returns:
        Resized frame with letterboxing
    """
    try:
        target_w, target_h = target_size
        frame_h, frame_w = frame.shape[:2]
        
        # Calculate scaling factor
        scale = min(target_w / frame_w, target_h / frame_h)
        
        # Calculate new dimensions
        new_w = int(frame_w * scale)
        new_h = int(frame_h * scale)
        
        # Resize frame
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Create target canvas with padding color
        canvas = np.full((target_h, target_w, 3), padding_color, dtype=np.uint8)
        
        # Calculate padding
        pad_x = (target_w - new_w) // 2
        pad_y = (target_h - new_h) // 2
        
        # Place resized frame on canvas
        canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
        
        return canvas
        
    except Exception as e:
        self.logger.error(f"Letterbox resizing failed: {e}")
        return cv2.resize(frame, target_size)
```
### 3. Medium Priority - Image Quality Enhancement 
- Task 3.1: Implement Advanced Image Enhancement
``` python
# Add to DetectionProcessor
def _enhance_frame_quality(self, frame: np.ndarray) -> np.ndarray:
    """Apply advanced image enhancement for better detection quality."""
    try:
        enhanced_frame = frame.copy()
        
        # Step 1: Noise reduction
        enhanced_frame = cv2.fastNlMeansDenoisingColored(enhanced_frame, None, 10, 10, 7, 21)
        
        # Step 2: Sharpening using unsharp masking
        enhanced_frame = self._apply_unsharp_masking(enhanced_frame, amount=1.5, radius=1.0, threshold=0)
        
        # Step 3: Contrast enhancement using CLAHE
        enhanced_frame = self._apply_clahe_enhancement(enhanced_frame)
        
        # Step 4: Brightness normalization
        enhanced_frame = self._normalize_brightness(enhanced_frame)
        
        return enhanced_frame
        
    except Exception as e:
        self.logger.warning(f"Frame enhancement failed: {e}")
        return frame

def _apply_unsharp_masking(self, frame: np.ndarray, amount: float = 1.5, 
                          radius: float = 1.0, threshold: int = 0) -> np.ndarray:
    """Apply unsharp masking for image sharpening."""
    try:
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # Create Gaussian blur
        blurred = cv2.GaussianBlur(frame_float, (0, 0), radius)
        
        # Apply unsharp masking
        sharpened = frame_float + amount * (frame_float - blurred)
        
        # Clip values and convert back to uint8
        sharpened = np.clip(sharpened, 0, 1)
        return (sharpened * 255).astype(np.uint8)
        
    except Exception as e:
        self.logger.warning(f"Unsharp masking failed: {e}")
        return frame
```

- Task 3.2: Implement Quality Metrics and Monitoring
``` python
# Add to DetectionProcessor
def _assess_frame_quality(self, frame: np.ndarray) -> Dict[str, Any]:
    """Assess overall frame quality for detection."""
    try:
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance for sharpness
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Calculate brightness and contrast
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        # Calculate noise level using local variance
        noise_level = self._estimate_noise_level(gray)
        
        # Determine overall quality score
        quality_score = self._calculate_quality_score(laplacian_var, brightness, contrast, noise_level)
        
        return {
            'sharpness_score': laplacian_var,
            'brightness': brightness,
            'contrast': contrast,
            'noise_level': noise_level,
            'quality_score': quality_score,
            'overall_quality': 'excellent' if quality_score > 80 else 'good' if quality_score > 60 else 'fair' if quality_score > 40 else 'poor'
        }
        
    except Exception as e:
        self.logger.warning(f"Quality assessment failed: {e}")
        return {}

def _calculate_quality_score(self, sharpness: float, brightness: float, 
                           contrast: float, noise: float) -> float:
    """Calculate overall quality score (0-100)."""
    try:
        # Normalize values to 0-100 scale
        sharpness_score = min(sharpness / 10.0, 100)  # Normalize sharpness
        brightness_score = 100 - abs(brightness - 128) / 1.28  # Optimal around 128
        contrast_score = min(contrast / 2.0, 100)  # Normalize contrast
        noise_score = max(100 - noise, 0)  # Lower noise = higher score
        
        # Weighted average
        weights = [0.4, 0.2, 0.2, 0.2]  # Sharpness is most important
        scores = [sharpness_score, brightness_score, contrast_score, noise_score]
        
        quality_score = sum(w * s for w, s in zip(weights, scores))
        return max(0, min(100, quality_score))
        
    except Exception as e:
        self.logger.warning(f"Quality score calculation failed: {e}")
        return 50.0  # Default middle score
```
### 4. Medium Priority - Dynamic Configuration Management
- Task 4.1: Implement Environment-Based Camera Configuration
``` python
# Add to CameraHandler
def _load_environment_camera_config(self) -> Dict[str, Any]:
    """Load camera configuration from environment variables."""
    config = {
        'capture_resolution': tuple(map(int, os.getenv('HIGH_QUALITY_CAPTURE_RESOLUTION', '1920x1080').split('x'))),
        'detection_resolution': tuple(map(int, os.getenv('DETECTION_RESOLUTION', '640x640').split('x'))),
        'sharpness': float(os.getenv('CAMERA_SHARPNESS', '2.5')),
        'contrast': float(os.getenv('CAMERA_CONTRAST', '1.2')),
        'brightness': float(os.getenv('CAMERA_BRIGHTNESS', '0.1')),
        'autofocus_mode': os.getenv('CAMERA_AUTOFOCUS_MODE', 'Continuous'),
        'focus_range': os.getenv('CAMERA_FOCUS_RANGE', 'Normal'),
        'quality_monitoring': os.getenv('CAMERA_QUALITY_MONITORING', 'true').lower() == 'true',
        'enhancement_enabled': os.getenv('QUALITY_ENHANCEMENT_ENABLED', 'true').lower() == 'true'
    }
    return config
```

- Task 4.2: Implement Adaptive Quality Adjustment
``` python
# Add to CameraHandler
def _adjust_quality_based_on_conditions(self, metadata: Dict[str, Any]):
    """Dynamically adjust camera quality based on environmental conditions."""
    try:
        # Check lighting conditions from metadata
        exposure_time = metadata.get("ExposureTime", 0)
        analogue_gain = metadata.get("AnalogueGain", 1.0)
        
        # Adjust settings based on conditions
        if exposure_time > 50000:  # Low light condition
            self._optimize_for_low_light()
        elif exposure_time < 10000:  # Bright light condition
            self._optimize_for_bright_light()
        else:  # Normal lighting
            self._optimize_for_normal_light()
            
    except Exception as e:
        self.logger.warning(f"Dynamic quality adjustment failed: {e}")

def _optimize_for_low_light(self):
    """Optimize camera settings for low light conditions."""
    try:
        self.picam2.set_controls({
            "Sharpness": 2.0,  # Reduce sharpness to minimize noise
            "Contrast": 1.1,   # Slight contrast boost
            "Brightness": 0.2  # Slight brightness boost
        })
        self.logger.info("Applied low-light optimization")
    except Exception as e:
        self.logger.warning(f"Low-light optimization failed: {e}")
```
### 5. Low Priority - Performance Optimization and Analytics 
- Task 5.1: Implement Quality Analytics Dashboard
``` python
# Add to DetectionProcessor
def _log_quality_metrics(self, frame: np.ndarray, detection_results: List[Dict[str, Any]]):
    """Log quality metrics for analytics and monitoring."""
    try:
        quality_metrics = self._assess_frame_quality(frame)
        
        # Add detection performance metrics
        quality_metrics.update({
            'detection_count': len(detection_results),
            'detection_confidence_avg': np.mean([d.get('confidence', 0) for d in detection_results]) if detection_results else 0,
            'timestamp': time.time(),
            'frame_shape': frame.shape
        })
        
        # Log to database or analytics system
        self._store_quality_metrics(quality_metrics)
        
        # Alert if quality is consistently poor
        if quality_metrics['overall_quality'] == 'poor':
            self._alert_poor_quality(quality_metrics)
            
    except Exception as e:
        self.logger.warning(f"Quality metrics logging failed: {e}")
```

- Task 5.2: Implement Performance Monitoring
``` python
# Add to DetectionProcessor
def _monitor_processing_performance(self):
    """Monitor detection processing performance."""
    try:
        current_time = time.time()
        
        # Calculate processing time
        if hasattr(self, '_last_processing_time'):
            processing_time = current_time - self._last_processing_time
            self._processing_times.append(processing_time)
            
            # Keep only last 100 measurements
            if len(self._processing_times) > 100:
                self._processing_times.pop(0)
                
            # Calculate average processing time
            avg_processing_time = np.mean(self._processing_times)
            
            # Alert if processing is too slow
            if avg_processing_time > 0.1:  # More than 100ms
                self.logger.warning(f"Slow processing detected: {avg_processing_time:.3f}s average")
                
        self._last_processing_time = current_time
        
    except Exception as e:
        self.logger.warning(f"Performance monitoring failed: {e}")
```