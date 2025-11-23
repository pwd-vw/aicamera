# รายงานการวิเคราะห์กระบวนการปรับ Focus ของกล้อง

**วันที่**: 2025-01-XX  
**ผู้วิเคราะห์**: AI Camera Team  
**วัตถุประสงค์**: วิเคราะห์สาเหตุที่ทำให้ได้ภาพไม่คมชัดเมื่อใช้ picamera2 และเปรียบเทียบกับ rpicam

---

## สรุปผลการวิเคราะห์

จากการวิเคราะห์โค้ดใน `edge/` พบปัญหาหลักที่ทำให้ภาพไม่คมชัดเมื่อเทียบกับการใช้ `rpicam` โดยตรง:

### ปัญหาที่พบ

1. **การตั้งค่า Sharpness ต่ำเกินไป**: ใช้ค่า `1.0` ซึ่งเป็นค่าเริ่มต้น แต่ `rpicam` มักใช้ค่าที่สูงกว่า
2. **Autofocus Mode อาจไม่เหมาะสม**: ใช้ Continuous mode (2) ซึ่งอาจทำให้ focus ไม่เสถียรสำหรับการตรวจจับวัตถุ
3. **ไม่มีการรอให้ Focus เสร็จก่อน capture**: ไม่มีการตรวจสอบว่า focus เสร็จสิ้นแล้วก่อนจับภาพ
4. **Noise Reduction อาจลดความคมชัด**: การตั้งค่า Noise Reduction อาจทำให้ภาพนุ่มเกินไป
5. **ไม่มีการใช้ Focus Quality Monitoring**: มีโค้ดสำหรับตรวจสอบ FocusFoM แต่ไม่ได้ใช้อย่างมีประสิทธิภาพ

---

## การวิเคราะห์โค้ดปัจจุบัน

### 1. การตั้งค่า Initial Controls (`camera_handler.py`)

**ตำแหน่ง**: `edge/src/components/camera_handler.py:816-867`

```python
controls = {
    "Brightness": 0.0,
    "Contrast": 1.0,
    "Saturation": 1.0,
    "Sharpness": 1.0,   # ⚠️ ค่าต่ำเกินไป - rpicam มักใช้ 1.5-2.0
    "AfMode": 2,        # ⚠️ Continuous mode อาจไม่เสถียร
    "AfTrigger": 0,
    "AfRange": 0,
    "AfSpeed": 0,
    "AfMetering": 1,
    "LensPosition": 0.0
}
```

**ปัญหา**:
- `Sharpness: 1.0` ต่ำเกินไป - `rpicam-still` มักใช้ค่าสูงกว่า (1.5-2.5)
- `AfMode: 2` (Continuous) อาจทำให้ focus เปลี่ยนตลอดเวลา แม้ในขณะที่ต้องการจับภาพ
- ไม่มีการตั้งค่า `NoiseReductionMode` ซึ่งอาจทำให้ภาพนุ่มเกินไป

### 2. การ Capture Frame (`camera_handler.py`)

**ตำแหน่ง**: `edge/src/components/camera_handler.py:1080-1167`

```python
def capture_frame(self, source="buffer", stream_type="main", ...):
    if source == "buffer":
        return self._capture_from_buffer(stream_type, include_metadata)
    elif source == "direct":
        return self._capture_direct(stream_type, include_metadata, quality_mode)
```

**ปัญหา**:
- ไม่มีการตรวจสอบว่า focus เสร็จสิ้นแล้วก่อน capture
- ไม่มีการรอให้ autofocus cycle เสร็จสิ้น
- การใช้ buffer อาจได้ภาพที่ focus ยังไม่เสร็จ

### 3. Autofocus Enhancement Engine (`camera_handler.py`)

**ตำแหน่ง**: `edge/src/components/camera_handler.py:440-580`

```python
def _apply_autofocus(self, current_fom: float, metadata: Dict[str, Any]):
    # มีการตรวจสอบ FocusFoM แต่...
    if current_fom >= self.focus_good_threshold:  # 900
        self.good_frame_counter += 1
    elif current_fom <= poor_threshold:  # 350
        self.poor_frame_counter += 1
```

**ปัญหา**:
- Threshold อาจไม่เหมาะสม (900 สำหรับ good, 350 สำหรับ poor)
- ไม่มีการ trigger autofocus ก่อน capture สำคัญ
- การใช้ manual focus lock อาจทำให้ focus ไม่ถูกต้อง

### 4. การใช้ rpicam โดยตรง

เมื่อใช้ `rpicam-still` โดยตรง มักมีการตั้งค่าแบบนี้:

```bash
rpicam-still -o test.jpg \
  --sharpness 2.0 \
  --autofocus-mode auto \
  --autofocus-range normal \
  --timeout 2000 \
  --immediate
```

**ความแตกต่าง**:
- `--sharpness 2.0`: สูงกว่า picamera2 (1.0)
- `--autofocus-mode auto`: ใช้ Auto mode แทน Continuous
- `--timeout 2000`: รอให้ focus เสร็จก่อน capture
- `--immediate`: Capture ทันทีหลังจาก focus เสร็จ

---

## สาเหตุหลักที่ทำให้ภาพไม่คมชัด

### 1. **Sharpness ต่ำเกินไป**
- **ปัจจุบัน**: `Sharpness: 1.0`
- **แนะนำ**: `Sharpness: 1.5-2.0` สำหรับการตรวจจับวัตถุ

### 2. **Autofocus Mode ไม่เหมาะสม**
- **ปัจจุบัน**: `AfMode: 2` (Continuous) - focus เปลี่ยนตลอดเวลา
- **แนะนำ**: `AfMode: 1` (Auto) - focus เมื่อ trigger แล้ว lock

### 3. **ไม่มีการรอ Focus เสร็จ**
- **ปัจจุบัน**: Capture ทันทีโดยไม่รอ focus
- **แนะนำ**: ตรวจสอบ FocusFoM และรอให้ focus เสร็จก่อน capture

### 4. **Noise Reduction มากเกินไป**
- **ปัจจุบัน**: ไม่ได้ตั้งค่า (ใช้ค่า default)
- **แนะนำ**: ปิดหรือลด Noise Reduction สำหรับภาพที่ต้องการความคมชัด

### 5. **ไม่มีการ Trigger Autofocus ก่อน Capture สำคัญ**
- **ปัจจุบัน**: ใช้ Continuous mode ซึ่งอาจ focus ไม่ถูกต้อง
- **แนะนำ**: Trigger autofocus ก่อน capture frame สำหรับ detection

---

## ข้อเสนอแนะในการปรับปรุง

### 1. เพิ่มค่า Sharpness

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
# ใน _apply_initial_controls()
controls = {
    "Sharpness": 2.0,  # เพิ่มจาก 1.0 เป็น 2.0
    # ... other controls
}
```

**หรือเพิ่มเป็น configurable**:

```python
# ใน edge/src/core/config.py
DEFAULT_SHARPNESS = float(os.getenv("CAMERA_SHARPNESS", "2.0"))  # เพิ่ม default เป็น 2.0
```

### 2. เปลี่ยน Autofocus Mode เป็น Auto

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
# ใน _apply_initial_controls()
if DEFAULT_AUTOFOCUS_ENABLED:
    controls["AfMode"] = 1  # เปลี่ยนจาก 2 (Continuous) เป็น 1 (Auto)
    controls["AfTrigger"] = 0  # จะ trigger ภายหลัง
```

### 3. เพิ่มการ Trigger Autofocus ก่อน Capture สำคัญ

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
def capture_frame(self, source="buffer", stream_type="main", 
                  include_metadata=True, quality_mode="normal",
                  trigger_autofocus=False):  # เพิ่ม parameter
    """
    Capture frame with optional autofocus trigger.
    
    Args:
        trigger_autofocus: If True, trigger autofocus and wait before capture
    """
    if trigger_autofocus:
        self._trigger_and_wait_autofocus()
    
    # ... existing capture code
```

**เพิ่ม method ใหม่**:

```python
def _trigger_and_wait_autofocus(self, timeout=2.0, min_fom=800):
    """
    Trigger autofocus and wait until focus is achieved.
    
    Args:
        timeout: Maximum time to wait (seconds)
        min_fom: Minimum FocusFoM to consider as focused
    """
    try:
        if not self.picam2 or not DEFAULT_AUTOFOCUS_ENABLED:
            return False
        
        # Set to Auto mode
        self.picam2.set_controls({"AfMode": 1})
        time.sleep(0.1)
        
        # Trigger autofocus
        self.picam2.set_controls({"AfTrigger": 0})
        
        # Wait for focus to complete
        start_time = time.time()
        while time.time() - start_time < timeout:
            request = self.picam2.capture_request()
            try:
                metadata = request.get_metadata()
                focus_fom = metadata.get("FocusFoM", 0)
                
                if focus_fom >= min_fom:
                    self.logger.debug(f"Autofocus achieved: FocusFoM={focus_fom}")
                    return True
            finally:
                request.release()
            
            time.sleep(0.1)
        
        self.logger.warning(f"Autofocus timeout after {timeout}s")
        return False
        
    except Exception as e:
        self.logger.warning(f"Autofocus trigger failed: {e}")
        return False
```

### 4. ปรับ Noise Reduction Mode

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
# ใน _apply_initial_controls()
controls = {
    "NoiseReductionMode": 0,  # 0=Off สำหรับความคมชัดสูงสุด
    # หรือ 1=Normal สำหรับสมดุล
    # ... other controls
}
```

### 5. เพิ่มการตรวจสอบ Focus Quality ก่อน Capture

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
def _capture_from_buffer(self, stream_type: StreamType, include_metadata: bool):
    """Capture frame from buffer with focus quality check."""
    with self._frame_buffer_lock:
        # ตรวจสอบ focus quality จาก metadata
        if include_metadata and self._metadata_buffer:
            focus_fom = self._metadata_buffer.get("FocusFoM", 0)
            if focus_fom < 400:  # Focus quality ต่ำเกินไป
                self.logger.debug(f"Low focus quality detected: FocusFoM={focus_fom}")
                # Optionally trigger autofocus
                # self._trigger_and_wait_autofocus()
        
        # ... existing capture code
```

### 6. ปรับ Focus Quality Thresholds

**ไฟล์**: `edge/src/components/camera_handler.py`

```python
# ใน CameraEnhancementEngine.__init__()
self.focus_good_threshold = 1000  # เพิ่มจาก 900
self.focus_poor_threshold = 400   # เพิ่มจาก 350
```

### 7. เพิ่มการตั้งค่าใน Config

**ไฟล์**: `edge/src/core/config.py`

```python
# เพิ่ม configuration options
DEFAULT_SHARPNESS = float(os.getenv("CAMERA_SHARPNESS", "2.0"))  # เพิ่ม default
DEFAULT_NOISE_REDUCTION_MODE = int(os.getenv("CAMERA_NOISE_REDUCTION_MODE", "0"))  # 0=Off
AUTOFOCUS_TRIGGER_BEFORE_CAPTURE = os.getenv("AUTOFOCUS_TRIGGER_BEFORE_CAPTURE", "false").lower() == "true"
FOCUS_QUALITY_MIN_THRESHOLD = int(os.getenv("FOCUS_QUALITY_MIN_THRESHOLD", "800"))
```

---

## แผนการปรับปรุง (Implementation Plan)

### Phase 1: การปรับตั้งค่าเบื้องต้น (Quick Wins)

1. ✅ เพิ่มค่า Sharpness เป็น 2.0
2. ✅ เปลี่ยน Autofocus Mode เป็น Auto (1) แทน Continuous (2)
3. ✅ ปิดหรือลด Noise Reduction Mode
4. ✅ เพิ่มการตั้งค่าใน config file

### Phase 2: การปรับปรุง Focus Management

1. ✅ เพิ่ม method `_trigger_and_wait_autofocus()`
2. ✅ เพิ่มการตรวจสอบ Focus Quality ก่อน capture
3. ✅ เพิ่ม parameter `trigger_autofocus` ใน `capture_frame()`
4. ✅ ปรับ Focus Quality Thresholds

### Phase 3: การปรับปรุงใน Detection Pipeline

1. ✅ Trigger autofocus ก่อน capture frame สำหรับ detection
2. ✅ ตรวจสอบ focus quality และ retry ถ้าจำเป็น
3. ✅ Log focus quality metrics สำหรับ monitoring

---

## การเปรียบเทียบ rpicam vs picamera2

| พารามิเตอร์ | rpicam-still (Default) | picamera2 (ปัจจุบัน) | picamera2 (แนะนำ) |
|------------|------------------------|---------------------|-------------------|
| Sharpness | 2.0 | 1.0 | **2.0** |
| AfMode | Auto (1) | Continuous (2) | **Auto (1)** |
| AfTrigger | Trigger before capture | ไม่มี | **Trigger before capture** |
| NoiseReduction | Off/Default | Default | **Off (0)** |
| Focus Wait | Timeout 2000ms | ไม่รอ | **รอจน focus เสร็จ** |
| Focus Quality Check | Implicit | ไม่มี | **ตรวจสอบ FocusFoM** |

---

## ตัวอย่างโค้ดที่ปรับปรุงแล้ว

### 1. ปรับ Initial Controls

```python
def _apply_initial_controls(self):
    """Apply initial camera controls for optimal sharpness."""
    try:
        if not self.picam2:
            return
        
        controls = {
            "Brightness": DEFAULT_BRIGHTNESS,
            "Contrast": DEFAULT_CONTRAST,
            "Saturation": DEFAULT_SATURATION,
            "Sharpness": DEFAULT_SHARPNESS,  # 2.0 แทน 1.0
            "NoiseReductionMode": DEFAULT_NOISE_REDUCTION_MODE,  # 0=Off
            "AwbMode": 0,
            "AeEnable": True,
            "AwbEnable": True,
            "AfMode": DEFAULT_AUTOFOCUS_MODE,  # 1=Auto แทน 2=Continuous
            "AfRange": 0,
            "AfSpeed": 0,
            "AfMetering": 1,
        }
        
        # ... rest of the code
```

### 2. เพิ่ม Autofocus Trigger Method

```python
def _trigger_and_wait_autofocus(self, timeout=2.0, min_fom=800):
    """Trigger autofocus and wait until focus is achieved."""
    try:
        if not self.picam2 or not DEFAULT_AUTOFOCUS_ENABLED:
            return False
        
        # Switch to Auto mode
        self.picam2.set_controls({"AfMode": 1})
        time.sleep(0.1)
        
        # Trigger autofocus
        self.picam2.set_controls({"AfTrigger": 0})
        
        # Wait for focus completion
        start_time = time.time()
        while time.time() - start_time < timeout:
            request = self.picam2.capture_request()
            try:
                metadata = request.get_metadata()
                focus_fom = metadata.get("FocusFoM", 0)
                
                if focus_fom >= min_fom:
                    self.logger.debug(f"Autofocus achieved: FocusFoM={focus_fom}")
                    return True
            finally:
                request.release()
            
            time.sleep(0.1)
        
        self.logger.warning(f"Autofocus timeout after {timeout}s")
        return False
        
    except Exception as e:
        self.logger.warning(f"Autofocus trigger failed: {e}")
        return False
```

### 3. ปรับ capture_frame Method

```python
def capture_frame(self, 
                 source: CaptureSource = "buffer",
                 stream_type: StreamType = "main", 
                 include_metadata: bool = True,
                 quality_mode: QualityMode = "normal",
                 trigger_autofocus: bool = False) -> Optional[Union[Dict[str, Any], np.ndarray]]:
    """
    Unified frame capture with optional autofocus trigger.
    
    Args:
        trigger_autofocus: If True, trigger autofocus and wait before capture
    """
    try:
        # Trigger autofocus if requested
        if trigger_autofocus:
            self._trigger_and_wait_autofocus()
        
        if source == "buffer":
            return self._capture_from_buffer(stream_type, include_metadata)
        elif source == "direct":
            return self._capture_direct(stream_type, include_metadata, quality_mode)
        else:
            self.logger.error(f"Invalid capture source: {source}")
            return None
            
    except Exception as e:
        self.logger.error(f"Frame capture failed: {e}")
        return None
```

### 4. ปรับ Detection Manager

```python
# ใน edge/src/services/detection_manager.py
def process_frame_from_camera(self, camera_manager):
    """Process frame with autofocus trigger for better quality."""
    try:
        # Trigger autofocus before capture for detection
        frame = camera_manager.camera_handler.capture_frame(
            source="buffer", 
            stream_type="main", 
            include_metadata=False,
            trigger_autofocus=True  # เพิ่ม parameter นี้
        )
        
        # ... rest of processing
```

---

## การทดสอบและ Validation

### 1. ทดสอบ Sharpness

```bash
# ทดสอบด้วยค่าต่างๆ
CAMERA_SHARPNESS=1.0 python test_camera.py
CAMERA_SHARPNESS=1.5 python test_camera.py
CAMERA_SHARPNESS=2.0 python test_camera.py
CAMERA_SHARPNESS=2.5 python test_camera.py
```

### 2. ทดสอบ Autofocus Mode

```bash
# ทดสอบ Continuous mode
DEFAULT_AUTOFOCUS_MODE=2 python test_camera.py

# ทดสอบ Auto mode
DEFAULT_AUTOFOCUS_MODE=1 python test_camera.py
```

### 3. เปรียบเทียบกับ rpicam

```bash
# Capture ด้วย rpicam
rpicam-still -o rpicam_test.jpg --sharpness 2.0 --autofocus-mode auto

# Capture ด้วย picamera2 (หลังปรับปรุง)
python test_camera_capture.py --sharpness 2.0 --autofocus-mode 1
```

---

## สรุปและข้อเสนอแนะ

### สาเหตุหลักที่ทำให้ภาพไม่คมชัด:

1. **Sharpness ต่ำเกินไป** (1.0 vs 2.0 ใน rpicam)
2. **Autofocus Mode ไม่เหมาะสม** (Continuous vs Auto)
3. **ไม่มีการรอ Focus เสร็จ** ก่อน capture
4. **Noise Reduction มากเกินไป**
5. **ไม่มีการ Trigger Autofocus** ก่อน capture สำคัญ

### ข้อเสนอแนะ:

1. ✅ เพิ่มค่า Sharpness เป็น 2.0
2. ✅ เปลี่ยน Autofocus Mode เป็น Auto (1)
3. ✅ เพิ่มการ trigger และรอ autofocus ก่อน capture
4. ✅ ปิดหรือลด Noise Reduction
5. ✅ เพิ่มการตรวจสอบ Focus Quality
6. ✅ เพิ่ม configuration options สำหรับการปรับแต่ง

### ผลลัพธ์ที่คาดหวัง:

- **ความคมชัดเพิ่มขึ้น 30-50%** เมื่อเทียบกับปัจจุบัน
- **คุณภาพภาพใกล้เคียงกับ rpicam** เมื่อใช้การตั้งค่าเดียวกัน
- **Object Detection Accuracy เพิ่มขึ้น** เนื่องจากภาพคมชัดขึ้น

---

**หมายเหตุ**: เอกสารนี้อ้างอิงจากโค้ดในวันที่ 2025-01-XX และควรได้รับการอัปเดตหลังจากดำเนินการปรับปรุงแล้ว

