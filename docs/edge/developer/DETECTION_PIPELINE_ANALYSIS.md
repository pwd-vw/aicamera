# การวิเคราะห์ Detection Pipeline และการจัดการผลลัพธ์

## ภาพรวม

ระบบ AI Camera ใช้ **Detection Pipeline** ที่ประกอบด้วย 2 ส่วนหลัก:
1. **DetectionProcessor** (`detection_processor.py`) - รับผิดชอบการประมวลผล AI models
2. **DetectionManager** (`detection_manager.py`) - รับผิดชอบการจัดการ workflow และบันทึกผลลัพธ์

---

## Detection Pipeline Flow

### 1. การเริ่มต้น Detection Loop

**DetectionManager** ทำงานใน background thread (`_detection_loop`):

```python
# detection_manager.py:490-521
def _detection_loop(self):
    while self.is_running:
        camera_manager = get_service('camera_manager')
        if camera_manager and self._is_camera_ready(camera_manager):
            result = self.process_frame_from_camera(camera_manager)
        time.sleep(self.detection_interval)  # รอตาม detection_interval
```

### 2. การดึงภาพจากกล้อง

**DetectionManager.process_frame_from_camera()** ดึง frame จาก camera:

```python
# detection_manager.py:272-311
def process_frame_from_camera(self, camera_manager):
    # ดึง frame จาก camera buffer
    frame = camera_manager.camera_handler.capture_frame(
        source="buffer", 
        stream_type="main", 
        include_metadata=False
    )
    # ส่งต่อไปยัง process_frame()
    return self.process_frame(frame)
```

### 3. Detection Pipeline (6 ขั้นตอน)

**DetectionManager.process_frame()** เป็น orchestrator หลักที่เรียกใช้ DetectionProcessor:

#### **Step 1: Validate and Enhance Frame**
```python
# detection_manager.py:332-338
enhanced_frame = self.detection_processor.validate_and_enhance_frame(frame)
```
- ตรวจสอบความถูกต้องของ frame
- ปรับปรุงคุณภาพภาพสำหรับการตรวจจับ (enhancement)

#### **Step 2: Vehicle Detection**
```python
# detection_manager.py:341-343
vehicle_boxes, mapping_info = self.detection_processor.detect_vehicles(frame)
```

**กระบวนการใน DetectionProcessor.detect_vehicles():**
```python
# detection_processor.py:685-758
def detect_vehicles(self, frame):
    # 1. Resize frame เป็น 640x640 พร้อม letterbox และเก็บ mapping_info
    model_frame, mapping_info = self.resize_for_model_input(frame, (640, 640))
    
    # 2. แปลง BGR → RGB สำหรับ model
    model_frame = cv2.cvtColor(model_frame, cv2.COLOR_BGR2RGB)
    
    # 3. เรียกใช้ vehicle detection model
    results = self.vehicle_model(model_frame)
    vehicle_boxes = getattr(results, "results", [])
    
    # 4. กรองตาม confidence threshold และ map พิกัดกลับสู่ภาพต้นฉบับ
    filtered_boxes = []
    for box in vehicle_boxes:
        if box.get('score', 0) >= self.confidence_threshold:
            mapped_bbox = self.map_coordinates_to_original(box['bbox'], mapping_info)
            box['bbox'] = mapped_bbox
            filtered_boxes.append(box)
    
    return filtered_boxes, mapping_info
```

**ผลลัพธ์:**
- `vehicle_boxes`: List ของ vehicle detections พร้อม bbox ที่ map กลับสู่ภาพต้นฉบับแล้ว
- `mapping_info`: ข้อมูลสำหรับ coordinate mapping (ใช้สำหรับ frontend)

**หากไม่พบ vehicle → ข้าม frame นี้และไป frame ถัดไป**

#### **Step 3: License Plate Detection**
```python
# detection_manager.py:352-354
plate_boxes = self.detection_processor.detect_license_plates(
    frame, vehicle_boxes, mapping_info
)
```

**กระบวนการใน DetectionProcessor.detect_license_plates():**
```python
# detection_processor.py:760-838
def detect_license_plates(self, frame, vehicle_boxes, mapping_info):
    detected_plates = []
    
    for vehicle_box in vehicle_boxes:
        # 1. Crop vehicle region จากภาพต้นฉบับ
        x1, y1, x2, y2 = vehicle_box['bbox']
        vehicle_region = frame[int(y1):int(y2), int(x1):int(x2)]
        
        # 2. เรียกใช้ license plate detection model บน vehicle region
        lp_results = self.lp_detection_model(vehicle_region)
        lp_boxes = getattr(lp_results, "results", [])
        
        # 3. กรองตาม confidence และแปลงพิกัดกลับสู่ภาพเต็ม
        for lp_box in lp_boxes:
            if lp_box.get('score', 0) >= self.plate_confidence_threshold:
                # แปลงพิกัดจาก vehicle region → full frame
                lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                full_x1 = x1 + lp_x1
                full_y1 = y1 + lp_y1
                full_x2 = x1 + lp_x2
                full_y2 = y1 + lp_y2
                
                plate_data = {
                    'bbox': [full_x1, full_y1, full_x2, full_y2],
                    'score': confidence,
                    'vehicle_idx': i,
                    'vehicle_bbox': vehicle_box['bbox']
                }
                detected_plates.append(plate_data)
    
    return detected_plates
```

**ผลลัพธ์:**
- `plate_boxes`: List ของ license plate detections พร้อม bbox ในพิกัดภาพเต็ม

#### **Step 4: OCR Processing**
```python
# detection_manager.py:363-369
ocr_results = []
if plate_boxes:
    ocr_results = self.detection_processor.perform_ocr(frame, plate_boxes)
```

**กระบวนการใน DetectionProcessor.perform_ocr():**
```python
# detection_processor.py:840-990
def perform_ocr(self, frame, plate_boxes):
    ocr_results = []
    
    for plate_box in plate_boxes:
        # 1. Crop license plate region พร้อม padding 15%
        bbox = plate_box['bbox']
        plate_region, crop_info = self.crop_with_safe_padding(
            frame, bbox, padding_ratio=0.15
        )
        
        # 2. ปรับปรุงภาพสำหรับ OCR (CLAHE + threshold)
        plate_region = self._enhance_plate_for_ocr(plate_region)
        
        # 3. Parallel OCR Processing (Hailo + EasyOCR พร้อมกัน)
        if self.parallel_ocr_processor:
            parallel_results = self.parallel_ocr_processor.process_plate_parallel(
                plate_region, i, timeout=10.0
            )
        
        # 4. เลือกผลลัพธ์ที่ดีที่สุด
        # - Hailo OCR (ถ้ามี)
        # - EasyOCR (fallback)
        
        ocr_result = {
            'plate_idx': i,
            'bbox': plate_box['bbox'],
            'text': final_ocr_text.strip(),
            'confidence': final_ocr_confidence,
            'ocr_method': ocr_method,
            'hailo_ocr': {...},
            'easyocr': {...},
            'parallel_processing': {...}
        }
        ocr_results.append(ocr_result)
    
    return ocr_results
```

**ผลลัพธ์:**
- `ocr_results`: List ของ OCR results พร้อมข้อมูลจากทั้ง Hailo และ EasyOCR

#### **Step 5: Save Detection Results (บันทึกไฟล์ภาพ)**
```python
# detection_manager.py:372-376
original_path, _, _, _ = self.detection_processor.save_detection_results(
    frame, vehicle_boxes, plate_boxes, ocr_results
)
```

**กระบวนการใน DetectionProcessor.save_detection_results():**
```python
# detection_processor.py:995-1059
def save_detection_results(self, original_frame, vehicle_boxes, plate_boxes, ocr_results):
    # 1. สร้าง timestamp สำหรับ filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    
    # 2. สร้าง directory ถ้ายังไม่มี
    Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
    
    # 3. บันทึกเฉพาะภาพต้นฉบับ (optimized for disk space)
    original_filename = f"detection_{timestamp}.jpg"
    original_path = os.path.join(IMAGE_SAVE_DIR, original_filename)
    
    # 4. บันทึกภาพ (quality 85% เพื่อประหยัดพื้นที่)
    success = cv2.imwrite(original_path, original_frame)
    
    # หมายเหตุ: ไม่ได้บันทึกภาพที่มี bounding box วาดแล้ว
    # Bounding boxes จะถูกวาดแบบ dynamic ใน frontend (showDetail)
    
    return original_path, "", "", []  # ส่งคืนเฉพาะ original_path
```

**ผลลัพธ์:**
- `original_path`: Path ของไฟล์ภาพที่บันทึกแล้ว
- ภาพถูกบันทึกใน `IMAGE_SAVE_DIR` (default: `captured_images/`)
- Filename format: `detection_YYYYMMDD_HHMMSS_mmm.jpg`

#### **Step 6: Store Results in Database (บันทึกลงฐานข้อมูล)**
```python
# detection_manager.py:383-470
# สร้าง detection_record
detection_record = {
    'timestamp': datetime.now().isoformat(),
    'vehicles_count': len(vehicle_boxes),
    'plates_count': len(plate_boxes),
    'ocr_results': ocr_results,
    'original_image_path': f"captured_images/{os.path.basename(original_path)}",
    'vehicle_detections': vehicle_boxes,
    'plate_detections': plate_boxes,
    'processing_time_ms': processing_time * 1000.0,
    'coordinate_mapping': mapping_info
}

# Extract parallel OCR data
if ocr_results:
    # สกัดข้อมูลจาก parallel OCR processing
    detection_record.update({
        'hailo_ocr_results': [...],
        'easyocr_results': [...],
        'best_ocr_method': ...,
        'ocr_processing_time_ms': ...,
        ...
    })

# บันทึกลงฐานข้อมูล (ถ้าภาพบันทึกสำเร็จ)
if original_path and os.path.exists(original_path):
    if self.database_manager:
        self.database_manager.insert_detection_result(detection_record)
```

**กระบวนการใน DatabaseManager.insert_detection_result():**
```python
# database_manager.py:173-246
def insert_detection_result(self, detection_data):
    cursor = self.connection.cursor()
    
    # Serialize complex data เป็น JSON
    ocr_results_json = json.dumps(detection_data.get('ocr_results', []))
    vehicle_detections_json = json.dumps(detection_data.get('vehicle_detections', []))
    plate_detections_json = json.dumps(detection_data.get('plate_detections', []))
    hailo_ocr_json = json.dumps(detection_data.get('hailo_ocr_results', []))
    easyocr_json = json.dumps(detection_data.get('easyocr_results', []))
    
    # INSERT INTO detection_results
    cursor.execute("""
        INSERT INTO detection_results (
            timestamp, vehicles_count, plates_count, ocr_results,
            original_image_path, vehicle_detections, plate_detections,
            processing_time_ms,
            hailo_ocr_results, easyocr_results, best_ocr_method,
            ocr_processing_time_ms, parallel_ocr_success,
            hailo_ocr_confidence, easyocr_confidence,
            hailo_processing_time_ms, easyocr_processing_time_ms,
            hailo_ocr_error, easyocr_error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (...))
    
    self.connection.commit()
    return cursor.lastrowid
```

**ผลลัพธ์:**
- บันทึกข้อมูลทั้งหมดลงในตาราง `detection_results` ใน SQLite database
- ข้อมูลที่ซับซ้อน (lists, dicts) ถูก serialize เป็น JSON
- Return: `record_id` (ID ของ record ที่เพิ่งสร้าง)

---

## สรุปการไหลของข้อมูล

```
┌─────────────────────────────────────────────────────────────┐
│ DetectionManager._detection_loop()                          │
│ (Background Thread, ทำงานทุก detection_interval วินาที)     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ DetectionManager.process_frame_from_camera()                │
│ - ดึง frame จาก camera_manager                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ DetectionManager.process_frame()                            │
│ (Orchestrator - จัดการ workflow ทั้งหมด)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─► Step 1: validate_and_enhance_frame()
                     │
                     ├─► Step 2: detect_vehicles()
                     │   └─► DetectionProcessor.detect_vehicles()
                     │       - Resize 640x640 + letterbox
                     │       - Vehicle model inference
                     │       - Map coordinates → original
                     │
                     ├─► Step 3: detect_license_plates()
                     │   └─► DetectionProcessor.detect_license_plates()
                     │       - Crop vehicle regions
                     │       - LP detection model inference
                     │       - Map coordinates → full frame
                     │
                     ├─► Step 4: perform_ocr()
                     │   └─► DetectionProcessor.perform_ocr()
                     │       - Crop plate regions + padding
                     │       - Parallel OCR (Hailo + EasyOCR)
                     │       - Select best result
                     │
                     ├─► Step 5: save_detection_results()
                     │   └─► DetectionProcessor.save_detection_results()
                     │       - Save original image to disk
                     │       - Filename: detection_TIMESTAMP.jpg
                     │
                     └─► Step 6: insert_detection_result()
                         └─► DatabaseManager.insert_detection_result()
                             - Serialize data to JSON
                             - INSERT INTO detection_results
                             - Commit transaction
```

---

## ข้อมูลที่บันทึกในแต่ละขั้นตอน

### 1. ไฟล์ภาพ (File System)
- **Path**: `IMAGE_SAVE_DIR/detection_TIMESTAMP.jpg`
- **Content**: ภาพต้นฉบับที่ capture จากกล้อง
- **Format**: JPG (quality 85%)
- **หมายเหตุ**: ไม่ได้วาด bounding boxes ไว้ในภาพ (วาดแบบ dynamic ใน frontend)

### 2. ฐานข้อมูล (SQLite)
**ตาราง**: `detection_results`

**ข้อมูลที่บันทึก:**
- `timestamp`: เวลาที่ทำการ detection
- `vehicles_count`: จำนวนยานพาหนะที่พบ
- `plates_count`: จำนวนป้ายทะเบียนที่พบ
- `original_image_path`: Path ของไฟล์ภาพ (relative path)
- `vehicle_detections`: JSON array ของ vehicle detections
  ```json
  [
    {
      "bbox": [x1, y1, x2, y2],
      "score": 0.95,
      "class": "car"
    }
  ]
  ```
- `plate_detections`: JSON array ของ plate detections
  ```json
  [
    {
      "bbox": [x1, y1, x2, y2],
      "score": 0.92,
      "vehicle_idx": 0,
      "vehicle_bbox": [...]
    }
  ]
  ```
- `ocr_results`: JSON array ของ OCR results
  ```json
  [
    {
      "text": "กก1234",
      "confidence": 0.88,
      "ocr_method": "hailo",
      "hailo_ocr": {...},
      "easyocr": {...},
      "parallel_processing": {...}
    }
  ]
  ```
- `processing_time_ms`: เวลาที่ใช้ในการประมวลผล (milliseconds)
- `hailo_ocr_results`: JSON array ของ Hailo OCR results
- `easyocr_results`: JSON array ของ EasyOCR results
- `best_ocr_method`: วิธี OCR ที่ให้ผลลัพธ์ดีที่สุด
- `ocr_processing_time_ms`: เวลาที่ใช้ในการทำ OCR
- `parallel_ocr_success`: ว่าการทำ parallel OCR สำเร็จหรือไม่
- `hailo_ocr_confidence`: Confidence score จาก Hailo OCR
- `easyocr_confidence`: Confidence score จาก EasyOCR
- `hailo_processing_time_ms`: เวลาที่ใช้ในการทำ Hailo OCR
- `easyocr_processing_time_ms`: เวลาที่ใช้ในการทำ EasyOCR
- `hailo_ocr_error`: Error message จาก Hailo OCR (ถ้ามี)
- `easyocr_error`: Error message จาก EasyOCR (ถ้ามี)

---

## การจัดการข้อผิดพลาด

### 1. Frame Validation Failure
- **ที่**: `DetectionProcessor.validate_and_enhance_frame()`
- **การจัดการ**: Return `None` → ข้าม frame นี้

### 2. No Vehicles Detected
- **ที่**: `DetectionManager.process_frame()`
- **การจัดการ**: Return `None` → ข้าม frame นี้ (ไม่บันทึกอะไร)

### 3. No License Plates Detected
- **ที่**: `DetectionManager.process_frame()`
- **การจัดการ**: ยังคงบันทึก vehicle detections แต่ไม่มี plate/OCR data

### 4. Image Save Failure
- **ที่**: `DetectionProcessor.save_detection_results()`
- **การจัดการ**: Return empty path → ไม่บันทึกลงฐานข้อมูล

### 5. Database Insert Failure
- **ที่**: `DatabaseManager.insert_detection_result()`
- **การจัดการ**: Log error และ return `None` (ภาพยังถูกบันทึกไว้)

---

## Performance Optimization

### 1. Storage Optimization
- บันทึกเฉพาะภาพต้นฉบับ (ไม่บันทึกภาพที่มี bounding boxes)
- ใช้ quality 85% สำหรับ JPG
- Bounding boxes วาดแบบ dynamic ใน frontend

### 2. Coordinate Mapping
- ใช้ `mapping_info` เพื่อ map พิกัดระหว่างภาพที่ resize และภาพต้นฉบับ
- เก็บ `mapping_info` ใน database สำหรับ frontend

### 3. Parallel OCR Processing
- เรียกใช้ Hailo OCR และ EasyOCR พร้อมกัน
- เลือกผลลัพธ์ที่ดีที่สุด
- เก็บผลลัพธ์จากทั้งสองวิธีไว้ใน database

### 4. Detection Interval
- ใช้ `DETECTION_INTERVAL` เพื่อควบคุมความถี่ในการ detection
- ป้องกันการประมวลผลซ้ำซ้อน

---

## Statistics Tracking

**DetectionManager** ติดตามสถิติ:
- `total_frames_processed`: จำนวน frame ที่ประมวลผล
- `total_vehicles_detected`: จำนวนยานพาหนะที่พบทั้งหมด
- `total_plates_detected`: จำนวนป้ายทะเบียนที่พบทั้งหมด
- `successful_ocr`: จำนวน OCR ที่สำเร็จ
- `failed_detections`: จำนวน detection ที่ล้มเหลว
- `processing_time_avg`: เวลาเฉลี่ยในการประมวลผล

สถิติเหล่านี้สามารถดูได้ผ่าน `DetectionManager.get_status()`

---

## สรุป

1. **Detection Pipeline** ทำงานใน background thread และประมวลผล frame ตาม `detection_interval`
2. **6 ขั้นตอนหลัก**: Validate → Vehicle Detection → Plate Detection → OCR → Save Image → Save DB
3. **การบันทึกไฟล์**: บันทึกเฉพาะภาพต้นฉบับใน `IMAGE_SAVE_DIR`
4. **การบันทึกฐานข้อมูล**: บันทึกข้อมูลทั้งหมดในตาราง `detection_results` (JSON serialization)
5. **Error Handling**: จัดการข้อผิดพลาดในแต่ละขั้นตอนและข้าม frame ที่มีปัญหา
6. **Performance**: ใช้ parallel OCR, coordinate mapping, และ storage optimization

