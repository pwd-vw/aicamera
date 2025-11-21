# การวิเคราะห์ระบบโฟกัสและข้อเสนอแนะสำหรับ AI Camera

## สรุปการวิเคราะห์

### 1. กระบวนการจับภาพและส่งผล Image Frame

#### 1.1 Frame Capture Flow
```
Camera Sensor (Picamera2)
    ↓
_frame_capture_loop() [Thread]
    ├─→ Main Stream (RGB888, 1920x1080) → Detection Pipeline
    └─→ Lores Stream (RGB888, 640x480) → Video Streaming
```

**Key Components:**
- `CameraHandler._frame_capture_loop()` - จับภาพแบบต่อเนื่องใน background thread
- `CameraHandler.capture_frame()` - จับภาพแบบ buffer (thread-safe) หรือ direct
- `CameraManager.capture_frame()` - จับภาพสำหรับ detection pipeline
- `VideoStreamingService._get_frame_with_fallback()` - จับภาพสำหรับ video feed

#### 1.2 Frame Distribution
1. **Detection Pipeline:**
   - Source: `main` stream (1920x1080 RGB888)
   - Method: `camera_handler.capture_frame(source="buffer", stream_type="main")`
   - Usage: Vehicle detection → License plate detection → OCR

2. **Video Streaming:**
   - Source: `lores` stream (640x480 RGB888)
   - Method: `camera_handler.capture_frame(source="buffer", stream_type="lores")`
   - Encoding: RGB888 → MJPEG → Web display

3. **Video Feed:**
   - Source: `lores` stream
   - Method: `generate_frames()` → `camera_manager.camera_handler.capture_frame()`
   - Format: Multipart MJPEG stream

### 2. ปัญหาการปรับระยะโฟกัส

#### 2.1 ปัญหาที่พบ
1. **ภาพเบลอจากการโฟกัสไม่ถูกต้อง:**
   - FocusFoM ต่ำ (< 400) บ่งชี้คุณภาพโฟกัสต่ำ
   - การเคลื่อนไหวของพื้นหลัง (กิ่งไม้ไหว) ทำให้ระบบโฟกัสสับสน
   - ระบบ autofocus ปัจจุบันใช้ manual focus lock ที่ระยะ 3 เมตร

2. **ระบบ Autofocus ปัจจุบัน:**
   ```python
   # จาก camera_handler.py
   - AfMode: 0 (Manual) / 1 (Auto) / 2 (Continuous)
   - Focus Target: 3.0 เมตร (focus_target_distance_m)
   - Focus Lock: เมื่อ FocusFoM > 900 ต่อเนื่อง 60 frames
   - Focus Unlock: เมื่อ FocusFoM < 350 ต่อเนื่อง 8 frames
   ```

3. **ข้อจำกัด:**
   - ใช้ manual focus lock ที่ระยะคงที่ (3m)
   - ไม่มีการปรับโฟกัสตามการเคลื่อนไหวของวัตถุ
   - Focus check interval ยาว (90 วินาที)
   - ไม่รองรับการโฟกัสแบบ continuous สำหรับวัตถุเคลื่อนไหว

### 3. ข้อเสนอแนะ: การทดลองโหมดโฟกัส

#### 3.1 โหมด Auto (AfMode = 1)
**ลักษณะการทำงาน:**
- โฟกัสครั้งเดียวเมื่อเริ่มต้นหรือเมื่อ trigger
- เหมาะสำหรับวัตถุคงที่หรือเคลื่อนไหวช้า

**ข้อดี:**
- ประหยัดพลังงาน
- โฟกัสแม่นยำเมื่อวัตถุไม่เคลื่อนไหว
- ไม่มีการปรับโฟกัสบ่อยเกินไป

**ข้อเสีย:**
- ไม่เหมาะกับวัตถุเคลื่อนไหว
- อาจโฟกัสผิดพลาดเมื่อพื้นหลังเคลื่อนไหว

**การทดลอง:**
```python
# Configuration
AfMode = 1  # Auto
AfTrigger = 1  # Trigger AF
AfMetering = 1  # Center-weighted
AfRange = 0  # Full range

# Trigger conditions
- เมื่อ FocusFoM < 400 (poor quality)
- ทุก 30 วินาที (periodic check)
- เมื่อตรวจพบวัตถุใหม่ (vehicle detection)
```

**การประเมิน:**
- วัด FocusFoM เฉลี่ย
- วัดอัตราการโฟกัสสำเร็จ (focus success rate)
- วัดเวลาในการโฟกัส (focus time)
- วัดผลการ detection และ OCR accuracy

#### 3.2 โหมด Continuous (AfMode = 2)
**ลักษณะการทำงาน:**
- โฟกัสต่อเนื่องตลอดเวลา
- ปรับโฟกัสตามการเปลี่ยนแปลงของฉาก

**ข้อดี:**
- เหมาะกับวัตถุเคลื่อนไหว
- ตอบสนองเร็วต่อการเปลี่ยนแปลง
- รองรับการเคลื่อนไหวของพื้นหลัง

**ข้อเสีย:**
- ใช้พลังงานมาก
- อาจโฟกัสผิดพลาดเมื่อพื้นหลังเคลื่อนไหวมาก
- อาจทำให้ภาพกระตุก (focus hunting)

**การทดลอง:**
```python
# Configuration
AfMode = 2  # Continuous
AfSpeed = 0  # Normal speed (1 = Fast)
AfMetering = 1  # Center-weighted
AfRange = 0  # Full range

# Optimization
- ใช้ AfSpeed = 0 (Normal) เพื่อลด focus hunting
- ใช้ AfMetering = 1 (Center) เพื่อโฟกัสที่กลางภาพ
- จำกัด AfRange ตามระยะที่ต้องการ (2-10m สำหรับ LPR)
```

**การประเมิน:**
- วัด FocusFoM เฉลี่ยและความแปรปรวน
- วัดอัตราการ focus hunting
- วัดผลการ detection และ OCR accuracy
- วัดการใช้พลังงาน (CPU/GPU)

#### 3.3 โหมด Manual (AfMode = 0) + Smart Lock
**ลักษณะการทำงาน:**
- ตั้งค่าโฟกัสที่ระยะคงที่
- ใช้ FocusFoM เพื่อตรวจสอบคุณภาพ
- ปรับโฟกัสเมื่อคุณภาพต่ำ

**ข้อดี:**
- ควบคุมได้แม่นยำ
- ประหยัดพลังงาน
- เหมาะกับวัตถุที่ระยะคงที่

**ข้อเสีย:**
- ไม่เหมาะกับวัตถุเคลื่อนไหว
- ต้องปรับระยะโฟกัสเอง

**การทดลอง:**
```python
# Configuration
AfMode = 0  # Manual
LensPosition = 0.33  # 3 meters (1/3.0 diopters)
AfMetering = 1

# Smart Lock Logic
- Monitor FocusFoM ทุก frame
- เมื่อ FocusFoM < 400: Trigger AF scan
- เมื่อ FocusFoM > 900: Lock focus
- Unlock ทุก 60 วินาทีเพื่อ re-check
```

**การประเมิน:**
- วัด FocusFoM เฉลี่ย
- วัดความถี่ในการ unlock/lock
- วัดผลการ detection และ OCR accuracy

### 4. แนวทางการทดลองและประเมินผล

#### 4.1 Test Scenarios
1. **Scenario 1: วัตถุคงที่ (Static Object)**
   - รถจอดนิ่ง
   - พื้นหลังมีกิ่งไม้ไหว
   - ระยะ: 3-5 เมตร

2. **Scenario 2: วัตถุเคลื่อนไหว (Moving Object)**
   - รถเคลื่อนที่
   - พื้นหลังมีกิ่งไม้ไหว
   - ระยะ: 2-10 เมตร

3. **Scenario 3: หลายวัตถุ (Multiple Objects)**
   - มีรถหลายคัน
   - พื้นหลังซับซ้อน
   - ระยะ: 1-15 เมตร

#### 4.2 Metrics สำหรับประเมินผล

**Focus Quality Metrics:**
```python
metrics = {
    'focus_fom_mean': float,      # FocusFoM เฉลี่ย
    'focus_fom_std': float,       # ความแปรปรวนของ FocusFoM
    'focus_fom_min': float,       # FocusFoM ต่ำสุด
    'focus_fom_max': float,       # FocusFoM สูงสุด
    'focus_quality_distribution': {
        'excellent': int,  # FocusFoM > 1000
        'good': int,       # FocusFoM > 700
        'fair': int,       # FocusFoM > 400
        'poor': int        # FocusFoM <= 400
    },
    'focus_lock_count': int,      # จำนวนครั้งที่ lock focus
    'focus_unlock_count': int,    # จำนวนครั้งที่ unlock focus
    'focus_hunting_count': int,   # จำนวนครั้งที่ focus hunting
    'focus_time_ms': float        # เวลาในการโฟกัส (milliseconds)
}
```

**Detection & OCR Metrics:**
```python
detection_metrics = {
    'vehicle_detection_rate': float,    # อัตราการตรวจจับรถ
    'license_plate_detection_rate': float,  # อัตราการตรวจจับป้ายทะเบียน
    'ocr_accuracy': float,              # ความแม่นยำของ OCR
    'ocr_confidence_mean': float,       # Confidence เฉลี่ย
    'false_positive_rate': float,       # อัตรา false positive
    'processing_time_ms': float         # เวลาประมวลผล
}
```

**System Performance Metrics:**
```python
performance_metrics = {
    'cpu_usage_percent': float,   # การใช้ CPU
    'memory_usage_mb': float,     # การใช้หน่วยความจำ
    'frame_rate_fps': float,      # อัตราเฟรม
    'power_consumption_w': float   # การใช้พลังงาน (ถ้าวัดได้)
}
```

#### 4.3 Test Implementation Plan

**Phase 1: Baseline Testing (1 สัปดาห์)**
1. ทดสอบโหมด Manual (AfMode = 0) ปัจจุบัน
2. เก็บข้อมูล FocusFoM, detection rate, OCR accuracy
3. วิเคราะห์ปัญหาที่พบ

**Phase 2: Auto Mode Testing (1 สัปดาห์)**
1. ทดสอบโหมด Auto (AfMode = 1)
2. ทดสอบ trigger conditions ต่างๆ
3. เปรียบเทียบกับ baseline

**Phase 3: Continuous Mode Testing (1 สัปดาห์)**
1. ทดสอบโหมด Continuous (AfMode = 2)
2. ทดสอบ AfSpeed และ AfRange ต่างๆ
3. เปรียบเทียบกับ baseline และ Auto mode

**Phase 4: Hybrid Mode Testing (1 สัปดาห์)**
1. ทดสอบ hybrid approach (Auto + Manual lock)
2. ทดสอบ adaptive focus range
3. เปรียบเทียบผลลัพธ์ทั้งหมด

**Phase 5: Optimization (1 สัปดาห์)**
1. เลือกโหมดที่ดีที่สุด
2. Fine-tune parameters
3. Implement production solution

### 5. Implementation Recommendations

#### 5.1 Enhanced Focus Control System

```python
class EnhancedFocusController:
    """
    Enhanced focus controller with multiple modes and adaptive behavior.
    """
    
    def __init__(self, camera_handler):
        self.camera = camera_handler
        self.mode = "auto"  # auto, continuous, manual, hybrid
        self.focus_history = deque(maxlen=100)
        self.detection_results_history = deque(maxlen=50)
        
    def set_focus_mode(self, mode: str, **kwargs):
        """
        Set focus mode with optional parameters.
        
        Args:
            mode: "auto", "continuous", "manual", "hybrid"
            **kwargs: Mode-specific parameters
        """
        if mode == "auto":
            self._setup_auto_mode(**kwargs)
        elif mode == "continuous":
            self._setup_continuous_mode(**kwargs)
        elif mode == "manual":
            self._setup_manual_mode(**kwargs)
        elif mode == "hybrid":
            self._setup_hybrid_mode(**kwargs)
    
    def _setup_auto_mode(self, trigger_interval=30.0, poor_threshold=400):
        """Setup auto focus mode."""
        controls = {
            "AfMode": 1,  # Auto
            "AfTrigger": 0,  # No trigger initially
            "AfMetering": 1,  # Center-weighted
            "AfRange": 0  # Full range
        }
        self.camera.picam2.set_controls(controls)
        self.trigger_interval = trigger_interval
        self.poor_threshold = poor_threshold
    
    def _setup_continuous_mode(self, speed=0, metering=1, range_mode=0):
        """Setup continuous focus mode."""
        controls = {
            "AfMode": 2,  # Continuous
            "AfSpeed": speed,  # 0=Normal, 1=Fast
            "AfMetering": metering,  # 0=Auto, 1=Center
            "AfRange": range_mode  # 0=Full, 1=Macro, 2=Normal
        }
        self.camera.picam2.set_controls(controls)
    
    def _setup_manual_mode(self, distance_m=3.0, unlock_interval=60.0):
        """Setup manual focus mode with smart lock."""
        diopters = 1.0 / distance_m
        controls = {
            "AfMode": 0,  # Manual
            "LensPosition": diopters,
            "AfMetering": 1
        }
        self.camera.picam2.set_controls(controls)
        self.unlock_interval = unlock_interval
    
    def _setup_hybrid_mode(self, base_distance=3.0, continuous_range=2.0):
        """
        Hybrid mode: Continuous focus with range limitation.
        Focus continuously but limit range to reduce hunting.
        """
        # Calculate focus range
        min_distance = base_distance - continuous_range
        max_distance = base_distance + continuous_range
        
        # Convert to diopters
        min_diopters = 1.0 / max_distance
        max_diopters = 1.0 / min_distance
        
        controls = {
            "AfMode": 2,  # Continuous
            "AfSpeed": 0,  # Normal speed
            "AfMetering": 1,  # Center-weighted
            "AfRange": 0  # Full range (libcamera may not support custom range)
        }
        self.camera.picam2.set_controls(controls)
    
    def update_focus_quality(self, metadata: Dict[str, Any], 
                            detection_result: Optional[Dict[str, Any]] = None):
        """
        Update focus quality assessment and adjust if needed.
        
        Args:
            metadata: Camera metadata with FocusFoM
            detection_result: Detection results (optional)
        """
        focus_fom = metadata.get("FocusFoM", 0)
        self.focus_history.append({
            'fom': focus_fom,
            'timestamp': time.time(),
            'detection_success': detection_result is not None if detection_result else None
        })
        
        if self.mode == "auto":
            self._handle_auto_mode(focus_fom, metadata)
        elif self.mode == "continuous":
            self._handle_continuous_mode(focus_fom, metadata)
        elif self.mode == "manual":
            self._handle_manual_mode(focus_fom, metadata)
        elif self.mode == "hybrid":
            self._handle_hybrid_mode(focus_fom, metadata, detection_result)
    
    def _handle_auto_mode(self, focus_fom: float, metadata: Dict[str, Any]):
        """Handle auto focus mode updates."""
        if focus_fom < self.poor_threshold:
            # Trigger autofocus
            self.camera.picam2.set_controls({"AfTrigger": 1})
            time.sleep(0.1)  # Wait for trigger
            self.camera.picam2.set_controls({"AfTrigger": 0})
    
    def _handle_continuous_mode(self, focus_fom: float, metadata: Dict[str, Any]):
        """Handle continuous focus mode updates."""
        # Continuous mode handles focus automatically
        # Just monitor for quality issues
        if focus_fom < 300:
            # Very poor quality - might need intervention
            self.camera.logger.warning(f"Very poor focus quality: {focus_fom}")
    
    def _handle_manual_mode(self, focus_fom: float, metadata: Dict[str, Any]):
        """Handle manual focus mode with smart lock."""
        current_time = time.time()
        
        # Check if we need to unlock and re-focus
        if hasattr(self, 'last_unlock_time'):
            if current_time - self.last_unlock_time > self.unlock_interval:
                # Unlock and trigger AF
                self.camera.picam2.set_controls({
                    "AfMode": 1,  # Switch to Auto
                    "AfTrigger": 1
                })
                time.sleep(0.5)  # Wait for focus
                # Lock back to manual
                self._setup_manual_mode()
                self.last_unlock_time = current_time
        
        # If quality is very poor, trigger immediate re-focus
        if focus_fom < 300:
            self._setup_manual_mode()  # Re-lock at target distance
    
    def _handle_hybrid_mode(self, focus_fom: float, metadata: Dict[str, Any],
                           detection_result: Optional[Dict[str, Any]]):
        """Handle hybrid focus mode."""
        # Use continuous mode but adjust based on detection results
        if detection_result and detection_result.get('vehicles'):
            # Vehicle detected - ensure good focus
            if focus_fom < 500:
                # Temporarily switch to auto for better focus
                self.camera.picam2.set_controls({
                    "AfMode": 1,
                    "AfTrigger": 1
                })
                time.sleep(0.3)
                # Switch back to continuous
                self._setup_continuous_mode()
```

#### 5.2 Focus Testing Framework

```python
class FocusTestFramework:
    """
    Framework for testing different focus modes.
    """
    
    def __init__(self, camera_handler, detection_manager):
        self.camera = camera_handler
        self.detection = detection_manager
        self.results = []
        
    def run_test(self, mode: str, duration: int = 300, **kwargs):
        """
        Run focus test for specified mode and duration.
        
        Args:
            mode: Focus mode to test
            duration: Test duration in seconds
            **kwargs: Mode-specific parameters
        """
        # Setup focus mode
        focus_controller = EnhancedFocusController(self.camera)
        focus_controller.set_focus_mode(mode, **kwargs)
        
        # Initialize metrics
        metrics = {
            'mode': mode,
            'start_time': time.time(),
            'focus_fom_values': [],
            'detection_results': [],
            'focus_actions': []
        }
        
        # Run test
        end_time = time.time() + duration
        frame_count = 0
        
        while time.time() < end_time:
            # Capture frame
            frame = self.camera.capture_frame(source="buffer", stream_type="main")
            if frame is None:
                continue
            
            # Get metadata
            frame_data = self.camera.capture_frame(
                source="buffer", 
                stream_type="main", 
                include_metadata=True
            )
            metadata = frame_data.get('metadata', {}) if isinstance(frame_data, dict) else {}
            
            # Record FocusFoM
            focus_fom = metadata.get("FocusFoM", 0)
            metrics['focus_fom_values'].append(focus_fom)
            
            # Run detection
            detection_result = self.detection.process_frame_from_camera(
                self.camera.camera_manager
            )
            
            if detection_result:
                metrics['detection_results'].append({
                    'timestamp': time.time(),
                    'vehicles_detected': len(detection_result.get('vehicles', [])),
                    'license_plates_detected': len(detection_result.get('license_plates', [])),
                    'ocr_results': detection_result.get('ocr_results', [])
                })
            
            # Update focus controller
            focus_controller.update_focus_quality(metadata, detection_result)
            
            frame_count += 1
            time.sleep(0.033)  # ~30 FPS
        
        # Calculate final metrics
        metrics['end_time'] = time.time()
        metrics['total_frames'] = frame_count
        metrics['focus_fom_mean'] = np.mean(metrics['focus_fom_values'])
        metrics['focus_fom_std'] = np.std(metrics['focus_fom_values'])
        metrics['focus_fom_min'] = np.min(metrics['focus_fom_values'])
        metrics['focus_fom_max'] = np.max(metrics['focus_fom_values'])
        
        # Detection metrics
        if metrics['detection_results']:
            metrics['detection_rate'] = len(metrics['detection_results']) / frame_count
            metrics['avg_vehicles_per_frame'] = np.mean([
                r['vehicles_detected'] for r in metrics['detection_results']
            ])
        else:
            metrics['detection_rate'] = 0
            metrics['avg_vehicles_per_frame'] = 0
        
        self.results.append(metrics)
        return metrics
    
    def compare_results(self):
        """Compare results from all test modes."""
        if not self.results:
            return None
        
        comparison = {
            'modes': [r['mode'] for r in self.results],
            'focus_fom_means': [r['focus_fom_mean'] for r in self.results],
            'focus_fom_stds': [r['focus_fom_std'] for r in self.results],
            'detection_rates': [r['detection_rate'] for r in self.results],
            'best_mode': None
        }
        
        # Find best mode (highest FocusFoM mean and detection rate)
        scores = []
        for r in self.results:
            # Normalized score: FocusFoM (0-1) + Detection Rate (0-1)
            fom_score = min(r['focus_fom_mean'] / 1000.0, 1.0)
            det_score = r['detection_rate']
            total_score = (fom_score * 0.6) + (det_score * 0.4)
            scores.append(total_score)
        
        best_idx = np.argmax(scores)
        comparison['best_mode'] = self.results[best_idx]['mode']
        comparison['best_score'] = scores[best_idx]
        
        return comparison
```

### 6. สรุปและข้อเสนอแนะ

#### 6.1 แนวทางที่แนะนำ
1. **เริ่มต้นด้วย Continuous Mode (AfMode = 2)**
   - เหมาะกับวัตถุเคลื่อนไหวและพื้นหลังที่เคลื่อนไหว
   - ใช้ AfSpeed = 0 (Normal) เพื่อลด focus hunting
   - จำกัด AfRange ตามระยะที่ต้องการ (2-10m)

2. **ทดสอบ Hybrid Mode**
   - ใช้ Continuous mode แต่ปรับตาม detection results
   - เมื่อตรวจจับรถ → ใช้ Auto mode เพื่อโฟกัสแม่นยำ
   - เมื่อไม่มีรถ → ใช้ Continuous mode เพื่อเตรียมพร้อม

3. **Optimize Parameters**
   - ปรับ AfSpeed ตามสภาพแวดล้อม
   - ปรับ AfRange ตามระยะที่ต้องการ
   - ใช้ AfMetering = 1 (Center) เพื่อโฟกัสที่กลางภาพ

#### 6.2 Implementation Steps
1. สร้าง `EnhancedFocusController` class
2. สร้าง `FocusTestFramework` สำหรับทดสอบ
3. ทดสอบแต่ละโหมดตาม Phase Plan
4. วิเคราะห์ผลและเลือกโหมดที่ดีที่สุด
5. Fine-tune parameters
6. Deploy to production

#### 6.3 Monitoring และ Maintenance
- Monitor FocusFoM อย่างต่อเนื่อง
- Track detection rate และ OCR accuracy
- Alert เมื่อ FocusFoM ต่ำกว่า threshold
- Auto-adjust parameters ตามสภาพแวดล้อม

---

**เอกสารนี้ให้แนวทางในการทดลองและประเมินผลระบบโฟกัสสำหรับ AI Camera System**

