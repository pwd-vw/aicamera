# โมดูลตรวจจับ (Detection Module) – AI Camera v2.0

เวอร์ชัน: 2.0.0  
ปรับปรุงล่าสุด: 2025-01-09  
ผู้เขียน: AI Camera Team  
หมวดหมู่: Technical Analysis  
สถานะ: Active

## 1) วัตถุประสงค์ (Objectives)

โมดูลตรวจจับมีเป้าหมายเพื่อสร้างระบบตรวจจับยานพาหนะและอ่านป้ายทะเบียนแบบครบวงจร ตั้งแต่การรับภาพจากกล้องไปจนถึงการแสดงผลบนแดชบอร์ด ด้วยความแม่นยำสูงและประสิทธิภาพที่ดี

### เป้าหมายหลัก:
- รับภาพจากกล้องแบบเรียลไทม์ (1280x720 main, 640x640 lores)
- ตรวจจับยานพาหนะด้วย AI model แบบแม่นยำ
- ตรวจจับป้ายทะเบียนในยานพาหนะที่พบ
- อ่านข้อความป้ายทะเบียนด้วย OCR (Hailo + EasyOCR)
- จัดเก็บผลลัพธ์ลงฐานข้อมูลและไฟล์ภาพ
- แสดงผลบนแดชบอร์ดแบบ interactive
- แสดงภาพต้นฉบับพร้อม bounding boxes และ labels

## 2) สถาปัตยกรรมและ Pipeline (Architecture & Pipeline)

```
Camera Frame Acquisition → Vehicle Detection → LP Detection → OCR Processing → Storage → Dashboard Display
         ↓                       ↓                ↓              ↓            ↓            ↓
    Main/Lores Stream      AI Model Inference   Plate Region   Text Recognition   DB + Images   Canvas Rendering
```

### 2.1 โครงสร้างโมดูล (Module Structure)
```
Detection Module Architecture
├── Detection Processor (AI Inference)
│   ├── Vehicle Detection Model
│   ├── License Plate Detection Model
│   ├── OCR Models (Hailo + EasyOCR)
│   └── Processing Pipeline
├── Detection Manager (Orchestration)
│   ├── Frame Processing
│   ├── Result Aggregation
│   ├── Image Storage
│   └── Database Operations
├── Detection Blueprint (Web API)
│   ├── Status Endpoints
│   ├── Results Endpoints
│   └── Statistics Endpoints
├── Dashboard JavaScript (Frontend)
│   ├── Real-time Updates
│   ├── Data Visualization
│   └── Canvas Rendering
└── Detection Template (UI)
    ├── Service Status
    ├── Statistics Display
    └── Results Visualization
```

## 3) อัลกอริทึมและขั้นตอนการทำงาน (Algorithm & Procedure)

### 3.1 ขั้นตอนการประมวลผลหลัก (Main Processing Steps)

#### **ขั้นตอนที่ 1: การรับภาพจากกล้อง (Camera Frame Acquisition)**
```python
# รับภาพจากกล้องผ่าน Camera Manager
def process_frame_from_camera(self):
    # ใช้ main resolution (1280x720) สำหรับ detection
    frame = camera_manager.capture_main_frame()
    
    if frame is None:
        return None  # กล้องไม่พร้อมหรือ buffer ไม่พร้อม
    
    # แปลงเป็น RGB format สำหรับ AI model
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return frame_rgb
```

#### **ขั้นตอนที่ 2: การตรวจจับยานพาหนะ (Vehicle Detection)**
```python
def detect_vehicles(self, frame):
    """
    ตรวจจับยานพาหนะในภาพ
    Returns: List[Dict] - รายการยานพาหนะที่พบ
    """
    # Preprocessing: ปรับขนาดเป็น 640x640
    resized_frame = cv2.resize(frame, (640, 640))
    
    # AI Model Inference
    results = self.vehicle_model(resized_frame)
    
    # Post-processing: กรองผลลัพธ์ตาม confidence
    vehicle_detections = []
    for detection in results:
        if detection.confidence > self.confidence_threshold:
            vehicle_detections.append({
                'bbox': detection.bbox.tolist(),  # [x1, y1, x2, y2]
                'score': float(detection.confidence),
                'label': detection.label,
                'class_id': int(detection.class_id)
            })
    
    return vehicle_detections
```

#### **ขั้นตอนที่ 3: การตรวจจับป้ายทะเบียน (License Plate Detection)**
```python
def detect_license_plates(self, frame, vehicle_boxes):
    """
    ตรวจจับป้ายทะเบียนในยานพาหนะที่พบ
    Returns: List[Dict] - รายการป้ายทะเบียนที่พบ
    """
    plate_detections = []
    
    for vehicle in vehicle_boxes:
        # Crop ยานพาหนะจากภาพ
        x1, y1, x2, y2 = vehicle['bbox']
        vehicle_roi = frame[y1:y2, x1:x2]
        
        # ตรวจจับป้ายทะเบียนใน ROI
        plate_results = self.lp_detection_model(vehicle_roi)
        
        for plate in plate_results:
            if plate.confidence > self.plate_confidence_threshold:
                # แปลง coordinates กลับไปยังภาพต้นฉบับ
                plate_bbox = self._convert_roi_to_global(plate.bbox, vehicle['bbox'])
                plate_detections.append({
                    'bbox': plate_bbox,
                    'score': float(plate.confidence),
                    'label': 'license_plate',
                    'class_id': 1,
                    'vehicle_idx': vehicle_boxes.index(vehicle)
                })
    
    return plate_detections
```

#### **ขั้นตอนที่ 4: การอ่านข้อความป้ายทะเบียน (OCR Processing)**
```python
def perform_ocr(self, frame, plate_boxes):
    """
    อ่านข้อความป้ายทะเบียนด้วย OCR แบบ parallel
    Returns: List[Dict] - ผลลัพธ์ OCR
    """
    ocr_results = []
    
    for plate in plate_boxes:
        # Crop ป้ายทะเบียน
        x1, y1, x2, y2 = plate['bbox']
        plate_image = frame[y1:y2, x1:x2]
        
        # Parallel OCR processing
        hailo_result = self._hailo_ocr(plate_image)
        easyocr_result = self._easyocr_ocr(plate_image)
        
        # เลือกผลลัพธ์ที่ดีที่สุด
        best_result = self._select_best_ocr(hailo_result, easyocr_result)
        
        ocr_results.append({
            'text': best_result['text'],
            'confidence': best_result['confidence'],
            'plate_idx': plate_boxes.index(plate),
            'ocr_method': best_result['method'],
            'hailo_ocr': hailo_result,
            'easyocr': easyocr_result,
            'parallel_processing': {
                'parallel_success': True,
                'processing_time': max(hailo_result['time'], easyocr_result['time']),
                'selection_reason': best_result['reason']
            }
        })
    
    return ocr_results
```

### 3.2 การประมวลผลแบบ Parallel (Parallel Processing)

```python
def _parallel_ocr_processing(self, plate_image):
    """
    ประมวลผล OCR แบบ parallel เพื่อเพิ่มประสิทธิภาพ
    """
    import threading
    import time
    
    hailo_result = {'success': False, 'text': '', 'confidence': 0.0, 'time': 0}
    easyocr_result = {'success': False, 'text': '', 'confidence': 0.0, 'time': 0}
    
    def hailo_thread():
        start_time = time.time()
        try:
            result = self.hailo_ocr.readtext(plate_image)
            if result:
                hailo_result.update({
                    'success': True,
                    'text': result[0][1],
                    'confidence': result[0][2]
                })
        except Exception as e:
            hailo_result['error'] = str(e)
        finally:
            hailo_result['time'] = time.time() - start_time
    
    def easyocr_thread():
        start_time = time.time()
        try:
            result = self.easyocr.readtext(plate_image)
            if result:
                easyocr_result.update({
                    'success': True,
                    'text': result[0][1],
                    'confidence': result[0][2]
                })
        except Exception as e:
            easyocr_result['error'] = str(e)
        finally:
            easyocr_result['time'] = time.time() - start_time
    
    # เริ่ม threads พร้อมกัน
    t1 = threading.Thread(target=hailo_thread)
    t2 = threading.Thread(target=easyocr_thread)
    
    t1.start()
    t2.start()
    
    # รอให้เสร็จทั้งคู่
    t1.join()
    t2.join()
    
    return hailo_result, easyocr_result
```

## 4) การจัดเก็บข้อมูลและภาพ (Data & Image Storage)

### 4.1 โครงสร้างการจัดเก็บภาพ (Image Storage Structure)

```
edge/captured_images/
├── detection_{timestamp}_{id}.jpg           # ภาพต้นฉบับ (Original)
├── vehicle_detected_{timestamp}_{id}.jpg    # ภาพพร้อม vehicle bounding boxes
├── plate_detected_{timestamp}_{id}.jpg      # ภาพพร้อม plate bounding boxes + OCR
├── plate_{timestamp}_{id}_0.jpg            # ป้ายทะเบียนที่ crop แล้ว (Plate 1)
└── plate_{timestamp}_{id}_1.jpg            # ป้ายทะเบียนที่ crop แล้ว (Plate 2)
```

### 4.2 การบันทึกลงฐานข้อมูล (Database Storage)

```sql
-- ตาราง detection_results
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    vehicles_count INTEGER DEFAULT 0,
    plates_count INTEGER DEFAULT 0,
    ocr_results TEXT,                        -- JSON string ของ OCR results
    original_image_path TEXT,                 -- ภาพต้นฉบับ
    vehicle_detected_image_path TEXT,         -- ภาพพร้อม vehicle boxes
    plate_image_path TEXT,                    -- ภาพพร้อม plate boxes
    cropped_plates_paths TEXT,                -- JSON array ของ cropped plates
    vehicle_detections TEXT,                  -- JSON string ของ vehicle detections
    plate_detections TEXT,                    -- JSON string ของ plate detections
    processing_time_ms REAL,                  -- เวลาประมวลผล
    hailo_ocr_results TEXT,                   -- ผลลัพธ์ Hailo OCR
    easyocr_results TEXT,                     -- ผลลัพธ์ EasyOCR
    best_ocr_method TEXT,                     -- วิธี OCR ที่ดีที่สุด
    ocr_processing_time_ms REAL,              -- เวลา OCR
    parallel_ocr_success BOOLEAN,             -- ความสำเร็จของ parallel OCR
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.3 การสร้างภาพพร้อม Annotations

```python
def create_annotated_images(self, frame, vehicle_detections, plate_detections, ocr_results):
    """
    สร้างภาพพร้อม bounding boxes และ labels
    """
    # สร้างภาพ vehicle detection
    vehicle_image = frame.copy()
    for i, vehicle in enumerate(vehicle_detections):
        x1, y1, x2, y2 = vehicle['bbox']
        cv2.rectangle(vehicle_image, (x1, y1), (x2, y2), (0, 123, 255), 2)  # สีน้ำเงิน
        
        # เพิ่ม label
        label = f"Vehicle {i+1}: {vehicle['label']} ({vehicle['score']:.2f})"
        cv2.putText(vehicle_image, label, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 123, 255), 2)
    
    # สร้างภาพ plate detection
    plate_image = frame.copy()
    for i, plate in enumerate(plate_detections):
        x1, y1, x2, y2 = plate['bbox']
        cv2.rectangle(plate_image, (x1, y1), (x2, y2), (0, 255, 0), 2)  # สีเขียว
        
        # เพิ่ม OCR text
        ocr_text = ocr_results[i]['text'] if i < len(ocr_results) else "No OCR"
        label = f"Plate {i+1}: {ocr_text}"
        cv2.putText(plate_image, label, (x1, y1-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    return vehicle_image, plate_image
```

## 5) API และการเชื่อมต่อ (API & Integration)

### 5.1 REST Endpoints

```http
# สถานะ Detection Service
GET /detection/status
Response: {
    "success": true,
    "detection_status": {
        "service_running": true,
        "models_loaded": true,
        "detection_interval": 0.1,
        "auto_start": true
    }
}

# สถิติการตรวจจับ
GET /detection/statistics
Response: {
    "success": true,
    "statistics": {
        "total_frames_processed": 1250,
        "total_vehicles_detected": 45,
        "total_plates_detected": 23,
        "successful_ocr": 18,
        "detection_rate_percent": 85.2
    }
}

# ผลลัพธ์ล่าสุด
GET /detection/results/recent?limit=10
Response: {
    "success": true,
    "results": [
        {
            "id": 123,
            "timestamp": "2025-08-24T10:15:25Z",
            "vehicles_detected": 2,
            "plates_detected": 1,
            "ocr_results": [{"text": "ABC123", "confidence": 0.95}],
            "processing_time_ms": 45.2
        }
    ]
}

# ผลลัพธ์เฉพาะ ID
GET /detection/results/{id}
Response: {
    "success": true,
    "result": {
        "id": 123,
        "timestamp": "2025-08-24T10:15:25Z",
        "vehicle_detections": [...],
        "plate_detections": [...],
        "ocr_results": [...],
        "image_paths": {...}
    }
}
```

### 5.2 WebSocket Events

```javascript
// Client → Server
socket.emit('detection_status_request');        // ขอสถานะ detection
socket.emit('detection_results_request');       // ขอผลลัพธ์ล่าสุด
socket.emit('join_detection_room');            // เข้าร่วม detection room

// Server → Client
socket.on('detection_status_update', (status) => {
    // อัปเดตสถานะ detection service
    updateDetectionStatus(status);
});

socket.on('detection_result_update', (result) => {
    // ผลลัพธ์การตรวจจับใหม่
    addNewDetectionResult(result);
});

socket.on('detection_statistics_update', (stats) => {
    // อัปเดตสถิติ
    updateDetectionStatistics(stats);
});
```

## 6) แดชบอร์ดและการแสดงผล (Dashboard & Visualization)

### 6.1 โครงสร้างแดชบอร์ด (Dashboard Structure)

```html
<!-- Detection Dashboard Template -->
<div class="detection-dashboard">
    <!-- Service Status -->
    <div class="status-section">
        <h4>Detection Service Status</h4>
        <div id="service-status" class="badge bg-success">Running</div>
        <div id="models-status" class="badge bg-success">Models Loaded</div>
    </div>
    
    <!-- Statistics -->
    <div class="statistics-section">
        <h4>Detection Statistics</h4>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">Frames Processed:</span>
                <span id="frames-processed">1250</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Vehicles Detected:</span>
                <span id="vehicles-detected">45</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Plates Detected:</span>
                <span id="plates-detected">23</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Successful OCR:</span>
                <span id="successful-ocr">18</span>
            </div>
        </div>
    </div>
    
    <!-- Recent Results -->
    <div class="results-section">
        <h4>Recent Detection Results</h4>
        <div id="recent-results">
            <!-- Dynamic content loaded via JavaScript -->
        </div>
    </div>
</div>
```

### 6.2 การแสดงผลแบบ Canvas (Canvas Rendering)

#### **การสร้าง Canvas Elements**
```javascript
function createDetectionCanvas(imageUrl, boxes, ocrResults, type) {
    const canvasId = `canvas-${type}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const canvas = document.createElement('canvas');
    canvas.id = canvasId;
    canvas.className = 'img-fluid rounded';
    canvas.style.cssText = 'max-height: 200px; object-fit: contain; cursor: pointer;';
    
    // Click handler สำหรับเปิด modal
    canvas.onclick = () => DetectionManager.openImageModal(imageUrl, `${type} Visualization`);
    
    // เพิ่มลงใน DOM
    const container = document.getElementById(`${type}-visualization-container`);
    container.appendChild(canvas);
    
    // โหลดภาพและวาด bounding boxes
    loadImageAndDrawBoxes(canvas, imageUrl, boxes, ocrResults, type);
}
```

#### **การวาด Bounding Boxes**
```javascript
function drawBoundingBoxes(canvas, img, boxes, ocrResults, type) {
    const ctx = canvas.getContext('2d');
    
    // ตั้งขนาด canvas ให้ตรงกับภาพ
    canvas.width = img.width;
    canvas.height = img.height;
    
    // วาดภาพต้นฉบับ
    ctx.drawImage(img, 0, 0);
    
    // วาด bounding boxes
    boxes.forEach((box, index) => {
        let x, y, width, height;
        
        // รองรับหลายรูปแบบ bbox
        if (box.bbox && Array.isArray(box.bbox)) {
            // รูปแบบ: bbox: [x1, y1, x2, y2] ✅
            x = box.bbox[0];
            y = box.bbox[1];
            width = box.bbox[2] - x;
            height = box.bbox[3] - y;
        } else if (box.x !== undefined && box.y !== undefined) {
            // รูปแบบ: {x, y, width, height} ✅
            x = box.x;
            y = box.y;
            width = box.width || 0;
            height = box.height || 0;
        } else if (box.x1 !== undefined && box.y1 !== undefined) {
            // รูปแบบ: {x1, y1, x2, y2} ✅
            x = box.x1;
            y = box.y1;
            width = (box.x2 || 0) - x;
            height = (box.y2 || 0) - y;
        } else {
            // Fallback ✅
            x = 0; y = 0; width = 0; height = 0;
        }
        
        // เลือกสีตามประเภท
        const color = type === 'vehicle' ? '#007bff' : '#28a745';
        const label = type === 'vehicle' ? `Vehicle ${index + 1}` : `Plate ${index + 1}`;
        
        // วาด rectangle
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, width, height);
        
        // วาด label background
        const textWidth = ctx.measureText(label).width;
        ctx.fillStyle = color;
        ctx.fillRect(x, y - 20, textWidth + 10, 20);
        
        // วาด label text
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.fillText(label, x + 5, y - 5);
        
        // เพิ่ม confidence score ถ้ามี
        if (box.score !== undefined) {
            const scoreText = `${(box.score * 100).toFixed(1)}%`;
            ctx.fillStyle = color;
            ctx.fillRect(x + width - 50, y, 50, 20);
            ctx.fillStyle = 'white';
            ctx.fillText(scoreText, x + width - 45, y + 15);
        }
        
        // เพิ่ม OCR text สำหรับ plates
        if (type === 'plate' && ocr_results[index]) {
            const ocrText = ocr_results[index].text;
            ctx.fillStyle = '#28a745';
            ctx.fillRect(x, y + height, textWidth + 10, 20);
            ctx.fillStyle = 'white';
            ctx.fillText(ocrText, x + 5, y + height + 15);
        }
    });
}
```

### 6.3 การแสดงผลแบบ Modal (Modal Display)

```javascript
function openImageModal(imageUrl, title) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('modalTitle');
    
    modalTitle.textContent = title;
    modalImage.src = imageUrl;
    
    // แสดง modal
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}
```

## 7) การแก้ไขปัญหาและการ Debug (Troubleshooting & Debug)

### 7.1 ปัญหาที่พบบ่อยและวิธีแก้

#### **ปัญหา 1: Canvas ไม่แสดงภาพ**
```javascript
// ตรวจสอบ console logs
console.log('Canvas rendering debug:', {
    canvasId: canvas.id,
    imageUrl: imageUrl,
    boxes: boxes,
    type: type
});

// ตรวจสอบ image loading
img.onload = function() {
    console.log('Image loaded successfully:', img.width, 'x', img.height);
};

img.onerror = function() {
    console.error('Image failed to load:', imageUrl);
};
```

#### **ปัญหา 2: Bounding Boxes ไม่ตรงตำแหน่ง**
```javascript
// ตรวจสอบ bbox format
console.log('Bbox data:', boxes);

// ตรวจสอบ coordinate conversion
console.log('Canvas dimensions:', canvas.width, 'x', canvas.height);
console.log('Image dimensions:', img.width, 'x', img.height);
```

#### **ปัญหา 3: OCR ไม่ทำงาน**
```bash
# ตรวจสอบ service status
curl http://localhost/detection/status

# ตรวจสอบ model loading
curl http://localhost/detection/config

# ตรวจสอบ logs
journalctl -u aicamera_lpr.service -n 100 | grep -i ocr
```

### 7.2 คำสั่งวินิจฉัยระบบ

```bash
# ตรวจสอบ Detection Service
curl -s http://localhost/detection/status | python3 -m json.tool

# ดูสถิติการตรวจจับ
curl -s http://localhost/detection/statistics | python3 -m json.tool

# ทดสอบผลลัพธ์ล่าสุด
curl -s "http://localhost/detection/results/recent?limit=5" | python3 -m json.tool

# ตรวจสอบภาพที่จัดเก็บ
ls -la /home/camuser/aicamera/edge/captured_images/ | head -10

# ตรวจสอบฐานข้อมูล
sqlite3 /home/camuser/aicamera/edge/database.db "SELECT COUNT(*) FROM detection_results;"
```

## 8) การปรับแต่งประสิทธิภาพ (Performance Optimization)

### 8.1 การปรับแต่ง AI Models

```python
# การตั้งค่า confidence thresholds
class DetectionProcessor:
    def __init__(self):
        self.confidence_threshold = 0.7        # Vehicle detection
        self.plate_confidence_threshold = 0.5  # Plate detection
        self.ocr_confidence_threshold = 0.8    # OCR validation
```

### 8.2 การปรับแต่งการประมวลผล

```python
# การตั้งค่า detection interval
class DetectionManager:
    def __init__(self):
        self.detection_interval = 0.1  # 10 FPS
        self.max_queue_size = 100      # จำกัด queue size
        self.batch_processing = True    # ประมวลผลแบบ batch
```

### 8.3 การจัดการ Memory

```python
# การทำความสะอาด memory
def cleanup_old_images(self, max_age_hours=24):
    """ลบภาพเก่าที่เกินอายุที่กำหนด"""
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    for filename in os.listdir(self.image_save_dir):
        filepath = os.path.join(self.image_save_dir, filename)
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > max_age_seconds:
                os.remove(filepath)
                print(f"Removed old image: {filename}")
```

## 9) การติดตั้งและการตั้งค่า (Installation & Configuration)

### 9.1 Environment Variables

```bash
# /edge/installation/.env.production
# Detection Configuration
DETECTION_INTERVAL=0.1
VEHICLE_CONFIDENCE_THRESHOLD=0.7
PLATE_CONFIDENCE_THRESHOLD=0.5
OCR_CONFIDENCE_THRESHOLD=0.8

# Model Paths
VEHICLE_MODEL_PATH=models/vehicle_detection.onnx
PLATE_MODEL_PATH=models/plate_detection.onnx

# Image Storage
IMAGE_SAVE_DIR=captured_images
MAX_IMAGE_AGE_HOURS=24
```

### 9.2 การตั้งค่า Models

```python
# การโหลด AI Models
def load_models(self):
    """โหลด AI models สำหรับ detection และ OCR"""
    try:
        # Vehicle detection model
        self.vehicle_model = onnxruntime.InferenceSession(
            self.vehicle_model_path,
            providers=['CPUExecutionProvider']
        )
        
        # License plate detection model
        self.lp_detection_model = onnxruntime.InferenceSession(
            self.lp_detection_model_path,
            providers=['CPUExecutionProvider']
        )
        
        # EasyOCR
        self.easyocr = easyocr.Reader(['en'])
        
        return True
    except Exception as e:
        print(f"Error loading models: {e}")
        return False
```

## 10) การทดสอบและการตรวจสอบ (Testing & Validation)

### 10.1 Unit Tests

```python
def test_vehicle_detection():
    """ทดสอบการตรวจจับยานพาหนะ"""
    processor = DetectionProcessor()
    
    # สร้าง test image
    test_image = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
    
    # ทดสอบ detection
    results = processor.detect_vehicles(test_image)
    
    # ตรวจสอบผลลัพธ์
    assert isinstance(results, list)
    assert all(isinstance(r, dict) for r in results)
    assert all('bbox' in r for r in results)
```

### 10.2 Integration Tests

```python
def test_detection_pipeline():
    """ทดสอบ pipeline การตรวจจับแบบครบวงจร"""
    manager = DetectionManager()
    
    # ทดสอบการประมวลผลภาพ
    test_frame = np.random.randint(0, 255, (720, 1280, 3), dtype=np.uint8)
    result = manager.process_frame(test_frame)
    
    # ตรวจสอบผลลัพธ์
    if result:
        assert 'timestamp' in result
        assert 'vehicles_count' in result
        assert 'plates_count' in result
        assert 'ocr_results' in result
```

### 10.3 Performance Tests

```bash
# ทดสอบ performance
python3 -m pytest tests/test_detection_performance.py -v

# ทดสอบ memory usage
python3 -m memory_profiler tests/test_memory_usage.py

# ทดสอบ throughput
python3 tests/benchmark_detection.py
```

---

## 📋 **สรุป**

โมดูลตรวจจับของ AI Camera v2.0 เป็นระบบที่ครบครันสำหรับการตรวจจับยานพาหนะและอ่านป้ายทะเบียน ตั้งแต่การรับภาพจากกล้องไปจนถึงการแสดงผลบนแดชบอร์ด ด้วยการประมวลผลแบบ parallel และการจัดการข้อมูลที่มีประสิทธิภาพ

### **จุดเด่น:**
- ✅ **Pipeline ครบครัน**: Camera → Detection → OCR → Storage → Dashboard
- ✅ **การประมวลผลแบบ Parallel**: Hailo + EasyOCR พร้อมกัน
- ✅ **Canvas Rendering**: แสดงผลแบบ interactive พร้อม bounding boxes
- ✅ **การจัดการข้อมูล**: จัดเก็บครบถ้วนทั้งภาพและ metadata
- ✅ **Real-time Updates**: อัปเดตแบบเรียลไทม์ผ่าน WebSocket
- ✅ **Error Handling**: จัดการข้อผิดพลาดอย่างครอบคลุม

### **การใช้งาน:**
1. **สำหรับนักพัฒนา**: ใช้ API endpoints และ WebSocket events
2. **สำหรับผู้ใช้**: เข้าถึงผ่านแดชบอร์ด web interface
3. **สำหรับระบบ**: ทำงานแบบ auto-startup ผ่าน systemd

เอกสารนี้เป็นคู่มือครบถ้วนสำหรับการพัฒนา บำรุงรักษา และใช้งานโมดูลตรวจจับของระบบ AI Camera v2.0
