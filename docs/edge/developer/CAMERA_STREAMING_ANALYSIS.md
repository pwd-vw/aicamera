# การวิเคราะห์ระบบ Camera และ Video Streaming

## สรุปภาพรวม

ระบบ Camera ทำงานผ่านหลายชั้น (layers):
1. **CameraHandler** - จัดการ hardware camera (Picamera2)
2. **CameraManager** - จัดการ lifecycle และ configuration
3. **VideoStreamingService** - จัดการ video streaming สำหรับ web
4. **Camera Blueprint** - HTTP endpoints สำหรับ video feed
5. **Frontend Dashboard** - แสดงผล video streaming

---

## 1. การบริหารจัดการ Image Frame

### 1.1 Frame Buffer System

**CameraHandler** ใช้ frame buffer system:

```python
# camera_handler.py:537-543
_frame_buffer_lock = threading.RLock()
_main_frame_buffer = None  # Main stream (RGB888)
_lores_frame_buffer = None  # Lores stream (RGB888)
_metadata_buffer = {}
_capture_thread = None
_capture_running = False
_capture_interval = 0.033  # 30 FPS
```

**การทำงาน:**
- Background thread (`_frame_capture_loop`) capture frames อย่างต่อเนื่อง
- เก็บ frames ใน buffer (main และ lores)
- Thread-safe access ผ่าน `_frame_buffer_lock`

### 1.2 Frame Capture Methods

**CameraHandler.capture_frame()** รองรับ 2 modes:

1. **Buffer Mode** (`source="buffer"`):
   - อ่านจาก frame buffer (เร็ว, thread-safe)
   - ใช้สำหรับ detection pipeline และ streaming

2. **Direct Mode** (`source="direct"`):
   - Capture ตรงจาก camera (ช้ากว่า, แต่คุณภาพสูง)
   - ใช้สำหรับ manual capture

### 1.3 Dual Stream Configuration

```python
# camera_handler.py:685-694
main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}  # 1280x720
lores_config = {"size": LORES_RESOLUTION, "format": "RGB888"}  # 1280x720
```

**ปัจจุบัน:**
- Main stream: 1280x720 RGB888 (สำหรับ detection)
- Lores stream: 1280x720 RGB888 (สำหรับ streaming)

**หมายเหตุ:** ทั้งสอง stream ใช้ resolution เดียวกัน (1280x720) ซึ่งอาจไม่จำเป็น

---

## 2. การส่งภาพเข้า Detection Pipeline

### 2.1 Detection Manager Process

```python
# detection_manager.py:272-311
def process_frame_from_camera(self, camera_manager):
    # ดึง frame จาก camera buffer
    frame = camera_manager.camera_handler.capture_frame(
        source="buffer", 
        stream_type="main", 
        include_metadata=False
    )
    # ส่งต่อไปยัง detection pipeline
    return self.process_frame(frame)
```

**การทำงาน:**
1. DetectionManager เรียก `camera_manager.capture_frame()`
2. CameraManager เรียก `camera_handler.capture_frame(source="buffer", stream_type="main")`
3. CameraHandler อ่านจาก `_main_frame_buffer`
4. ส่ง frame ไปยัง DetectionProcessor

### 2.2 Detection Interval

```python
# detection_manager.py:490-521
def _detection_loop(self):
    while self.is_running:
        camera_manager = get_service('camera_manager')
        if camera_manager and self._is_camera_ready(camera_manager):
            result = self.process_frame_from_camera(camera_manager)
        time.sleep(self.detection_interval)  # Default: 30.0 seconds
```

**ปัญหาที่พบ:**
- `DETECTION_INTERVAL = 30.0` วินาที (นานเกินไป)
- ไม่ได้ใช้ tracking/deduplication ใน main pipeline

---

## 3. Camera Streaming Architecture

### 3.1 Video Streaming Service

**VideoStreamingService** ทำงานใน background thread:

```python
# video_streaming.py:341-394
def _streaming_worker(self):
    while not self.stop_event.is_set():
        # Get frame with fallback
        frame, source = self._get_frame_with_fallback()
        
        if frame is not None:
            # Process frame (already MJPEG bytes)
            processed_frame = self._process_frame_with_fallback(frame, source)
            
            if processed_frame:
                # Add to queue (maxsize=1)
                while not self.frame_queue.empty():
                    self.frame_queue.get_nowait()  # Clear old frames
                self.frame_queue.put_nowait(processed_frame)
        
        # Sleep to maintain target FPS
        time.sleep(1.0 / self.fps)  # Default: 30 FPS
```

**การทำงาน:**
1. Worker thread ดึง frame จาก camera (lores stream)
2. Process frame (encode เป็น MJPEG ถ้าจำเป็น)
3. เก็บใน queue (maxsize=1 - ลบ frame เก่าก่อนใส่ใหม่)
4. Sleep เพื่อควบคุม FPS

### 3.2 Frame Source Priority

```python
# video_streaming.py:129-228
def _get_frame_with_fallback(self):
    # 1. Primary: Camera manager (lores stream)
    frame = camera_manager.camera_handler.capture_frame(
        source="buffer", stream_type="lores", include_metadata=False
    )
    
    # 2. Secondary: Cached frame
    if self.last_successful_frame:
        return self.last_successful_frame, "cached_frame"
    
    # 3. Tertiary: Fallback frame
    return self.fallback_frame, "fallback_frame"
```

**Fallback Mechanisms:**
- Hardware-encoded frames (H.264/MJPEG) - ถ้ามี
- RGB888 array → Software MJPEG encoding
- Cached frame (frame ล่าสุดที่สำเร็จ)
- Fallback frame (placeholder)

### 3.3 Video Feed Endpoint

```python
# camera.py:1022-1094
@camera_bp.route('/video_feed')
def video_feed():
    video_streaming = get_service('video_streaming')
    return Response(
        _generate_frames_from_service_improved(video_streaming),
        mimetype='multipart/x-mixed-replace; boundary=frame',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',  # Disable nginx buffering
            ...
        }
    )
```

**การทำงาน:**
1. Flask endpoint `/camera/video_feed`
2. Generator function `_generate_frames_from_service_improved()`
3. ดึง frame จาก `video_streaming.get_frame()`
4. Format เป็น multipart MJPEG stream
5. Yield กลับไปยัง client

### 3.4 Frontend Display

```html
<!-- dashboard.html:534 -->
<img id="video-feed" src="/camera/video_feed" class="video-feed-compact" alt="Camera Feed">
```

**การทำงาน:**
- Browser request `/camera/video_feed`
- Flask ส่ง multipart MJPEG stream
- Browser แสดงผลภาพแบบ real-time

---

## 4. วิเคราะห์สาเหตุ Video Streaming ไม่ Smooth

### 4.1 ปัญหาที่พบ

1. **ภาพกระตุก (Stuttering)**
2. **Delay/Latency สูง**
3. **Frame drops**

### 4.2 สาเหตุที่วิเคราะห์ได้

#### 4.2.1 Resolution สูงเกินไป

**สถานะปัจจุบัน:**
```python
# config.py:85-86
MAIN_RESOLUTION = (1280, 720)  # Main stream
LORES_RESOLUTION = (1280, 720)  # Lores stream (สำหรับ streaming)
```

**ปัญหา:**
- Lores stream ใช้ 1280x720 (เหมือน main stream)
- ไม่ได้ลด resolution สำหรับ streaming
- ต้อง encode MJPEG จาก RGB888 array (software encoding)
- ใช้ CPU สูง → กระตุก

**การคำนวณ:**
- 1280x720 RGB888 = 2.76 MB per frame
- 30 FPS = 82.8 MB/s (uncompressed)
- MJPEG encoding ใช้ CPU ~20-30% บน Raspberry Pi 5
- Network bandwidth: ~2-5 Mbps (compressed)

#### 4.2.2 Software Encoding Overhead

**สถานะปัจจุบัน:**
```python
# video_streaming.py:165-193
# Convert RGB888 array to MJPEG bytes (software encoding)
frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Color conversion
_, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 85])
mjpeg_bytes = buffer.tobytes()
```

**ปัญหา:**
- ไม่มี hardware encoder สำหรับ lores stream
- ต้องใช้ software encoding (cv2.imencode)
- ใช้ CPU สูง → กระทบ detection pipeline

**Hardware Encoder:**
```python
# camera_handler.py:708-713
if MJPEGEncoder._hw_encoder_available:
    self.mjpeg_encoder = MJPEGEncoder(bitrate=2000000, quality=85)
    self.mjpeg_output = CircularOutput(size=10)
    self.mjpeg_encoder.output = self.mjpeg_output
```

**หมายเหตุ:** Hardware encoder มี แต่ไม่ได้ใช้สำหรับ lores stream ใน streaming service

#### 4.2.3 Frame Queue Bottleneck

**สถานะปัจจุบัน:**
```python
# video_streaming.py:68
self.frame_queue = queue.Queue(maxsize=1)  # Single frame buffer
```

**ปัญหา:**
- Queue size = 1 (เล็กเกินไป)
- ถ้า client ช้า → frame ถูก drop
- ไม่มี buffering → กระตุกเมื่อ network ช้า

#### 4.2.4 Detection Pipeline Interference

**การวิเคราะห์:**
- Detection pipeline ใช้ `stream_type="main"` (1280x720)
- Video streaming ใช้ `stream_type="lores"` (1280x720)
- **ไม่มีการแชร์ buffer โดยตรง**

**แต่:**
- ทั้งสองใช้ camera resource เดียวกัน
- Frame capture thread ต้อง capture ทั้ง main และ lores
- CPU/Memory competition → กระทบทั้งสอง

**การตรวจสอบ:**
```python
# camera_handler.py:859-956
def _frame_capture_loop(self):
    while self._capture_running:
        request = self.picam2.capture_request()
        main_frame = request.make_array("main")  # 1280x720
        lores_frame = request.make_array("lores")  # 1280x720 (เหมือน main!)
        metadata = request.get_metadata()
        
        with self._frame_buffer_lock:
            self._main_frame_buffer = main_frame
            self._lores_frame_buffer = lores_frame
```

**สรุป:** Detection pipeline **ไม่ได้ทำให้ streaming กระตุกโดยตรง** แต่:
- ใช้ CPU/Memory ร่วมกัน
- Frame capture thread ต้องทำงานหนัก (capture 2 streams)
- ถ้า detection ใช้ CPU สูง → กระทบ frame capture rate

#### 4.2.5 Network Latency

**สถานะปัจจุบัน:**
```python
# camera.py:1097-1168
def _generate_frames_from_service_improved(video_streaming):
    while True:
        frame_data = video_streaming.get_frame()  # No timeout
        # Format และ yield frame
        yield frame_data
        # No sleep - FPS controlled by worker thread
```

**ปัญหา:**
- ไม่มีการควบคุม frame rate ใน generator
- ถ้า network ช้า → frames สะสม → delay
- ไม่มี adaptive quality

#### 4.2.6 Browser Rendering

**Frontend:**
```html
<img src="/camera/video_feed" class="video-feed-compact">
```

**ปัญหา:**
- Browser อาจ buffer frames
- ไม่มีการใช้ WebSocket สำหรับ lower latency
- Multipart MJPEG มี overhead สูง

---

## 5. ข้อเสนอแนะในการปรับปรุง

### 5.1 ลด Resolution สำหรับ Streaming (สำคัญมาก!)

**แนวทางที่ 1: แยก Resolution**

```python
# config.py
MAIN_RESOLUTION = (1280, 720)  # สำหรับ detection (คงเดิม)
LORES_RESOLUTION = (640, 480)  # สำหรับ streaming (ลดลง)
```

**ผลลัพธ์:**
- ลด data size: 1280x720 → 640x480 = **75% reduction**
- ลด encoding time: ~4x เร็วขึ้น
- ลด network bandwidth: ~4x น้อยลง
- **Streaming จะ smooth ขึ้นมาก**

**การคำนวณ:**
- 640x480 RGB888 = 0.92 MB per frame
- 30 FPS = 27.6 MB/s (uncompressed)
- MJPEG encoding: ~5-10% CPU (แทน 20-30%)
- Network: ~0.5-1.5 Mbps (compressed)

**Implementation:**
```python
# camera_handler.py:685-694
main_config = {"size": MAIN_RESOLUTION, "format": "RGB888"}  # 1280x720
lores_config = {"size": (640, 480), "format": "RGB888"}  # 640x480 (ลดลง)
```

**ข้อควรระวัง:**
- ต้อง reconfigure camera (stop → configure → start)
- Frontend อาจต้องปรับ CSS สำหรับ aspect ratio

### 5.2 ใช้ Hardware Encoder (ถ้ามี)

**แนวทาง:**
```python
# video_streaming.py:147-164
# ใช้ hardware-encoded frame ถ้ามี
if hasattr(self, 'mjpeg_output') and not self.mjpeg_output.empty():
    lores_frame = self.mjpeg_output.get_frame()  # Hardware-encoded MJPEG
    return lores_frame, "camera_lores_mjpeg"
```

**ผลลัพธ์:**
- ไม่ต้องใช้ CPU สำหรับ encoding
- Latency ต่ำกว่า
- Smooth streaming

### 5.3 เพิ่ม Frame Queue Size

**แนวทาง:**
```python
# video_streaming.py:68
self.frame_queue = queue.Queue(maxsize=3)  # เพิ่มจาก 1 → 3
```

**ผลลัพธ์:**
- Buffer 3 frames → ลด frame drops
- Smooth streaming เมื่อ network ช้า

**ข้อควรระวัง:**
- เพิ่ม memory usage
- อาจเพิ่ม latency (old frames)

### 5.4 ปรับ FPS สำหรับ Streaming

**แนวทาง:**
```python
# video_streaming.py:64
self.fps = 15  # ลดจาก 30 → 15 FPS
```

**ผลลัพธ์:**
- ลด CPU usage: ~50%
- ลด network bandwidth: ~50%
- ยัง smooth สำหรับ monitoring

### 5.5 ปรับ JPEG Quality

**แนวทาง:**
```python
# video_streaming.py:185
_, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 70])  # ลดจาก 85 → 70
```

**ผลลัพธ์:**
- ลด file size: ~30-40%
- ลด encoding time: ~10-15%
- คุณภาพยังดีพอสำหรับ monitoring

### 5.6 ใช้ WebSocket แทน Multipart MJPEG

**แนวทาง:**
- ใช้ WebSocket สำหรับ real-time streaming
- ส่ง base64-encoded frames
- Lower latency, better control

**ข้อเสีย:**
- ต้องแก้ frontend
- ใช้ memory มากขึ้น

### 5.7 แยก Thread Priority

**แนวทาง:**
```python
# video_streaming.py:299-303
self.streaming_thread = threading.Thread(
    target=self._streaming_worker,
    daemon=True,
    name="VideoStreamingWorker"
)
# Set higher priority (if supported)
if hasattr(threading, 'set_priority'):
    threading.set_priority(self.streaming_thread, 'high')
```

**ผลลัพธ์:**
- Streaming thread ได้ CPU priority สูงกว่า
- Smooth streaming แม้ detection ทำงาน

---

## 6. แนวทางแก้ไขที่แนะนำ (เรียงตามความสำคัญ)

### Priority 1: Critical (ทำทันที)

1. **ลด LORES_RESOLUTION เป็น 640x480**
   - Impact: สูงมาก
   - Effort: ต่ำ
   - Risk: ต่ำ

2. **ปรับ FPS เป็น 15**
   - Impact: สูง
   - Effort: ต่ำ
   - Risk: ต่ำ

3. **ปรับ JPEG Quality เป็น 70**
   - Impact: ปานกลาง
   - Effort: ต่ำ
   - Risk: ต่ำ

### Priority 2: Important (ทำในระยะสั้น)

4. **เพิ่ม Frame Queue Size เป็น 3**
   - Impact: ปานกลาง
   - Effort: ต่ำ
   - Risk: ต่ำ

5. **ใช้ Hardware Encoder (ถ้ามี)**
   - Impact: สูง
   - Effort: ปานกลาง
   - Risk: ปานกลาง

### Priority 3: Long-term (ทำในระยะยาว)

6. **WebSocket Streaming**
   - Impact: สูง
   - Effort: สูง
   - Risk: ปานกลาง

7. **Adaptive Quality**
   - Impact: ปานกลาง
   - Effort: สูง
   - Risk: ต่ำ

---

## 7. Implementation Example

### 7.1 แก้ไข Configuration

```python
# edge/src/core/config.py
MAIN_RESOLUTION = tuple(map(int, os.getenv("MAIN_RESOLUTION", "1280x720").split('x')))
LORES_RESOLUTION = tuple(map(int, os.getenv("LORES_RESOLUTION", "640x480").split('x')))  # เปลี่ยนจาก 1280x720
```

### 7.2 แก้ไข Video Streaming Service

```python
# edge/src/services/video_streaming.py
# Line 63-65
self.width, self.height = LORES_RESOLUTION  # จะได้ 640x480
self.fps = 15  # ลดจาก 30 → 15
self.quality = 70  # ลดจาก 80 → 70

# Line 68
self.frame_queue = queue.Queue(maxsize=3)  # เพิ่มจาก 1 → 3

# Line 185
_, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 70])  # ลดจาก 85 → 70
```

### 7.3 Reconfigure Camera

```python
# ต้อง restart camera เพื่อใช้ resolution ใหม่
camera_manager.reconfigure_camera_safely({
    'lores': {'size': (640, 480), 'format': 'RGB888'}
})
```

---

## 8. Expected Results

### Before Optimization
- Resolution: 1280x720
- FPS: 30
- Quality: 85
- CPU Usage: 20-30%
- Network: 2-5 Mbps
- **Streaming: กระตุก, delay สูง**

### After Optimization
- Resolution: 640x480
- FPS: 15
- Quality: 70
- CPU Usage: 5-10%
- Network: 0.5-1.5 Mbps
- **Streaming: Smooth, near real-time**

---

## 9. Testing Checklist

- [ ] ทดสอบ streaming ที่ resolution 640x480
- [ ] ตรวจสอบ CPU usage (ควรลดลง ~50%)
- [ ] ตรวจสอบ network bandwidth (ควรลดลง ~70%)
- [ ] ตรวจสอบ latency (ควรลดลง ~30-50%)
- [ ] ตรวจสอบคุณภาพภาพ (ยังดีพอสำหรับ monitoring)
- [ ] ตรวจสอบ detection pipeline (ไม่กระทบ)

---

## 10. สรุป

### สาเหตุหลักของ Streaming ไม่ Smooth

1. **Resolution สูงเกินไป** (1280x720 สำหรับ streaming)
2. **Software Encoding Overhead** (ใช้ CPU สูง)
3. **Frame Queue ขนาดเล็ก** (maxsize=1)
4. **FPS สูงเกินไป** (30 FPS)
5. **JPEG Quality สูงเกินไป** (85)

### Detection Pipeline Impact

**Detection pipeline ไม่ได้ทำให้ streaming กระตุกโดยตรง** แต่:
- ใช้ CPU/Memory ร่วมกัน
- Frame capture thread ต้องทำงานหนัก
- ถ้า detection ใช้ CPU สูง → กระทบ frame capture rate

### แนวทางแก้ไขที่แนะนำ

1. **ลด LORES_RESOLUTION เป็น 640x480** (สำคัญที่สุด!)
2. **ปรับ FPS เป็น 15**
3. **ปรับ JPEG Quality เป็น 70**
4. **เพิ่ม Frame Queue Size เป็น 3**
5. **ใช้ Hardware Encoder (ถ้ามี)**

**ผลลัพธ์ที่คาดหวัง:**
- Streaming จะ smooth ขึ้นมาก
- CPU usage ลดลง ~50-70%
- Network bandwidth ลดลง ~70%
- Latency ลดลง ~30-50%
- **Near real-time streaming**

