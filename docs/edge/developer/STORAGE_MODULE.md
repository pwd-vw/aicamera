# โมดูลจัดการพื้นที่จัดเก็บ (Storage Manager Module) – AI Camera v2.0

เวอร์ชัน: 2.0.0  
ปรับปรุงล่าสุด: 2025-01-09  
ผู้เขียน: AI Camera Team  
หมวดหมู่: Technical Analysis  
สถานะ: Active

## 1) วัตถุประสงค์ (Objectives)

โมดูลจัดการพื้นที่จัดเก็บมีเป้าหมายเพื่อจัดการพื้นที่ดิสก์สำหรับการจัดเก็บภาพการตรวจจับแบบหมุนเวียน (Rotation Storage) โดยอัตโนมัติ เพื่อให้ระบบทำงานได้อย่างต่อเนื่องและมีประสิทธิภาพ

### เป้าหมายหลัก:
- **จัดการพื้นที่ดิสก์อัตโนมัติ**: ตรวจสอบและรักษาพื้นที่ว่างให้เพียงพอ
- **การจัดเก็บแบบหมุนเวียน**: ลบภาพเก่าตามนโยบาย retention
- **ป้องกันการล้นพื้นที่**: หลีกเลี่ยงปัญหา disk full
- **การจัดการแบบ Batch**: ประมวลผลไฟล์เป็นชุดเพื่อประสิทธิภาพ
- **การติดตามและรายงาน**: บันทึกการทำงานและสร้างรายงาน

## 2) สถาปัตยกรรมและ Pipeline (Architecture & Pipeline)

### 2.1 โครงสร้างโมดูล (Module Structure)
```
Storage Manager Module Architecture
├── Storage Service (Core Logic)
│   ├── Disk Space Monitoring
│   ├── File Rotation Management
│   ├── Batch Processing
│   └── Retention Policy
├── Storage Manager (Orchestration)
│   ├── Space Check Scheduler
│   ├── File Cleanup Orchestrator
│   ├── Performance Monitoring
│   └── Report Generator
├── Storage Blueprint (Web API)
│   ├── Storage Status
│   ├── Cleanup Operations
│   └── Configuration Management
├── Dashboard JavaScript (Frontend)
│   ├── Real-time Monitoring
│   ├── Storage Analytics
│   └── Manual Operations
└── Storage Template (UI)
    ├── Storage Dashboard
    ├── Configuration Forms
    └── Reports Viewer
```

### 2.2 การทำงานของ Pipeline
```
Disk Space Check → Threshold Evaluation → File Selection → Batch Processing → Cleanup → Report
      ↓                    ↓                ↓              ↓              ↓         ↓
   Monitor Space      Compare with      Find Old Files   Process in     Remove    Log Results
   Usage Stats        Min Free Space    by Age/Type      Batches        Files     & Metrics
```

## 3) อัลกอริทึมและขั้นตอนการทำงาน (Algorithm & Procedure)

### 3.1 อัลกอริทึมหลัก (Main Algorithm)

```python
def manage_image_folder(folder_path, min_free_space_gb, retention_days, batch_size):
    """
    อัลกอริทึมหลักสำหรับจัดการโฟลเดอร์ภาพ
    Args:
        folder_path: เส้นทางโฟลเดอร์ภาพ
        min_free_space_gb: พื้นที่ว่างขั้นต่ำ (GB)
        retention_days: จำนวนวันเก็บภาพ
        batch_size: ขนาด batch สำหรับการลบ
    """
    import os, time, shutil
    from datetime import datetime, timedelta

    # ขั้นตอนที่ 1: ตรวจสอบพื้นที่ว่าง
    def get_free_space_gb(path):
        total, used, free = shutil.disk_usage(path)
        return free / (1024 ** 3)

    # ขั้นตอนที่ 2: ประเมินความต้องการพื้นที่
    current_free_space = get_free_space_gb(folder_path)
    
    if current_free_space < min_free_space_gb:
        # ขั้นตอนที่ 3: คำนวณ retention limit
        now = time.time()
        retention_limit = now - (retention_days * 86400)  # 86400 = 24*60*60

        # ขั้นตอนที่ 4: รวบรวมไฟล์ที่เก่ากว่า retention
        image_files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if f.lower().endswith(('.jpg', '.png', '.jpeg')) and
               os.path.getmtime(os.path.join(folder_path, f)) < retention_limit
        ]

        # ขั้นตอนที่ 5: เรียงลำดับตามเวลา (เก่า → ใหม่)
        image_files.sort(key=lambda x: os.path.getmtime(x))

        # ขั้นตอนที่ 6: ประมวลผลแบบ batch
        files_to_delete = image_files[:batch_size]
        
        for file in files_to_delete:
            try:
                os.remove(file)
                print(f"Deleted: {file}")
            except OSError as e:
                print(f"Error deleting {file}: {e}")

        print(f"Deleted {len(files_to_delete)} files to free up space.")
        return len(files_to_delete)
    else:
        print("Disk space is sufficient. No action needed.")
        return 0
```

### 3.2 ขั้นตอนการทำงานแบบละเอียด (Detailed Procedure)

#### **ขั้นตอนที่ 1: การตรวจสอบพื้นที่ดิสก์**
```python
def check_disk_space(self, path):
    """ตรวจสอบพื้นที่ดิสก์และสร้างรายงาน"""
    try:
        total, used, free = shutil.disk_usage(path)
        
        space_info = {
            'total_gb': total / (1024 ** 3),
            'used_gb': used / (1024 ** 3),
            'free_gb': free / (1024 ** 3),
            'usage_percent': (used / total) * 100,
            'free_percent': (free / total) * 100
        }
        
        # ตรวจสอบสถานะพื้นที่
        if space_info['free_gb'] < self.min_free_space_gb:
            space_info['status'] = 'critical'
            space_info['action_required'] = True
        elif space_info['free_gb'] < self.min_free_space_gb * 1.5:
            space_info['status'] = 'warning'
            space_info['action_required'] = False
        else:
            space_info['status'] = 'healthy'
            space_info['action_required'] = False
        
        return space_info
        
    except Exception as e:
        self.logger.error(f"Error checking disk space: {e}")
        return None
```

#### **ขั้นตอนที่ 2: การเลือกไฟล์สำหรับการลบ**
```python
def select_files_for_deletion(self, folder_path, retention_days, file_types=None):
    """เลือกไฟล์ที่เหมาะสมสำหรับการลบ"""
    if file_types is None:
        file_types = ['.jpg', '.png', '.jpeg', '.bmp']
    
    now = time.time()
    retention_limit = now - (retention_days * 86400)
    
    candidate_files = []
    
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        
        # ตรวจสอบว่าเป็นไฟล์ภาพหรือไม่
        if not any(filename.lower().endswith(ext) for ext in file_types):
            continue
            
        # ตรวจสอบว่าเป็นไฟล์จริงหรือไม่
        if not os.path.isfile(file_path):
            continue
            
        # ตรวจสอบอายุไฟล์
        file_age = os.path.getmtime(file_path)
        if file_age < retention_limit:
            candidate_files.append({
                'path': file_path,
                'filename': filename,
                'age_days': (now - file_age) / 86400,
                'size_bytes': os.path.getsize(file_path),
                'size_mb': os.path.getsize(file_path) / (1024 * 1024)
            })
    
    # เรียงลำดับตามอายุ (เก่า → ใหม่)
    candidate_files.sort(key=lambda x: x['age_days'], reverse=True)
    
    return candidate_files
```

#### **ขั้นตอนที่ 3: การประมวลผลแบบ Batch**
```python
def process_batch_deletion(self, files_to_delete, batch_size=100):
    """ประมวลผลการลบไฟล์แบบ batch"""
    total_files = len(files_to_delete)
    processed_files = 0
    deleted_files = 0
    errors = []
    
    # แบ่งเป็น batches
    for i in range(0, total_files, batch_size):
        batch = files_to_delete[i:i + batch_size]
        
        for file_info in batch:
            try:
                # ลบไฟล์
                os.remove(file_info['path'])
                deleted_files += 1
                
                # บันทึก log
                self.logger.info(f"Deleted file: {file_info['filename']} "
                               f"(Age: {file_info['age_days']:.1f} days, "
                               f"Size: {file_info['size_mb']:.2f} MB)")
                
            except OSError as e:
                error_msg = f"Error deleting {file_info['filename']}: {e}"
                self.logger.error(error_msg)
                errors.append({
                    'file': file_info['filename'],
                    'error': str(e)
                })
            
            processed_files += 1
            
            # อัปเดต progress
            if processed_files % 10 == 0:
                progress = (processed_files / total_files) * 100
                self.logger.info(f"Progress: {progress:.1f}% ({processed_files}/{total_files})")
    
    return {
        'total_files': total_files,
        'processed_files': processed_files,
        'deleted_files': deleted_files,
        'errors': errors,
        'success_rate': (deleted_files / total_files) * 100 if total_files > 0 else 0
    }
```

### 3.3 นโยบายการเก็บรักษา (Retention Policy)

```python
class RetentionPolicy:
    """นโยบายการเก็บรักษาไฟล์"""
    
    def __init__(self):
        self.policies = {
            'detection_images': {
                'retention_days': 7,
                'priority': 'high',
                'file_types': ['.jpg', '.png', '.jpeg'],
                'min_size_mb': 0.1
            },
            'experiment_images': {
                'retention_days': 30,
                'priority': 'medium',
                'file_types': ['.jpg', '.png', '.jpeg', '.bmp'],
                'min_size_mb': 0.05
            },
            'debug_images': {
                'retention_days': 3,
                'priority': 'low',
                'file_types': ['.jpg', '.png', '.log'],
                'min_size_mb': 0.01
            }
        }
    
    def get_retention_days(self, file_category):
        """ดึงจำนวนวันเก็บรักษาตามประเภทไฟล์"""
        return self.policies.get(file_category, {}).get('retention_days', 7)
    
    def should_delete_file(self, file_info, category):
        """ตัดสินใจว่าควรลบไฟล์หรือไม่"""
        policy = self.policies.get(category, {})
        
        # ตรวจสอบอายุ
        if file_info['age_days'] > policy['retention_days']:
            return True
            
        # ตรวจสอบขนาดไฟล์
        if file_info['size_mb'] < policy['min_size_mb']:
            return True
            
        return False
```

## 4) การตั้งค่าและการกำหนดค่า (Configuration & Settings)

### 4.1 Environment Variables

```bash
# /edge/installation/.env.production
# Storage Manager Configuration
STORAGE_MANAGER_ENABLED=true
STORAGE_CHECK_INTERVAL=300          # ตรวจสอบทุก 5 นาที
MIN_FREE_SPACE_GB=10               # พื้นที่ว่างขั้นต่ำ 10 GB
DEFAULT_RETENTION_DAYS=7           # เก็บภาพ 7 วัน
BATCH_SIZE=100                     # ลบทีละ 100 ไฟล์
MAX_DELETION_PER_CYCLE=1000        # ลบสูงสุด 1000 ไฟล์ต่อรอบ
ENABLE_COMPRESSION=true            # เปิดการบีบอัดภาพเก่า
COMPRESSION_QUALITY=85             # คุณภาพการบีบอัด 85%
```

### 4.2 การตั้งค่าแบบ Dynamic

```python
class StorageConfig:
    """การตั้งค่าแบบ dynamic สำหรับ Storage Manager"""
    
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """โหลดการตั้งค่าจาก environment variables"""
        self.enabled = os.getenv('STORAGE_MANAGER_ENABLED', 'true').lower() == 'true'
        self.check_interval = int(os.getenv('STORAGE_CHECK_INTERVAL', 300))
        self.min_free_space_gb = float(os.getenv('MIN_FREE_SPACE_GB', 10))
        self.default_retention_days = int(os.getenv('DEFAULT_RETENTION_DAYS', 7))
        self.batch_size = int(os.getenv('BATCH_SIZE', 100))
        self.max_deletion_per_cycle = int(os.getenv('MAX_DELETION_PER_CYCLE', 1000))
        self.enable_compression = os.getenv('ENABLE_COMPRESSION', 'true').lower() == 'true'
        self.compression_quality = int(os.getenv('COMPRESSION_QUALITY', 85))
    
    def update_config(self, **kwargs):
        """อัปเดตการตั้งค่าแบบ dynamic"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                self.logger.info(f"Updated {key} to {value}")
    
    def get_config_summary(self):
        """ดึงสรุปการตั้งค่า"""
        return {
            'enabled': self.enabled,
            'check_interval_seconds': self.check_interval,
            'min_free_space_gb': self.min_free_space_gb,
            'default_retention_days': self.default_retention_days,
            'batch_size': self.batch_size,
            'max_deletion_per_cycle': self.max_deletion_per_cycle,
            'enable_compression': self.enable_compression,
            'compression_quality': self.compression_quality
        }
```

## 5) API และการเชื่อมต่อ (API & Integration)

### 5.1 REST Endpoints

```http
# สถานะพื้นที่จัดเก็บ
GET /storage/status
Response: {
    "success": true,
    "storage_status": {
        "total_gb": 500.0,
        "used_gb": 350.0,
        "free_gb": 150.0,
        "usage_percent": 70.0,
        "status": "healthy",
        "action_required": false
    }
}

# ข้อมูลโฟลเดอร์ภาพ
GET /storage/images/info
Response: {
    "success": true,
    "folder_info": {
        "path": "/home/camuser/aicamera/edge/captured_images",
        "total_files": 1250,
        "total_size_gb": 2.5,
        "oldest_file_days": 8.5,
        "newest_file_days": 0.1
    }
}

# รายการไฟล์เก่า
GET /storage/images/old?limit=50
Response: {
    "success": true,
    "old_files": [
        {
            "filename": "detection_20250101_120000_001.jpg",
            "age_days": 8.5,
            "size_mb": 0.85,
            "path": "/home/camuser/aicamera/edge/captured_images/detection_20250101_120000_001.jpg"
        }
    ]
}

# เริ่มการทำความสะอาด
POST /storage/cleanup/start
Content-Type: application/json
{
    "retention_days": 7,
    "batch_size": 100,
    "max_files": 500
}

# สถานะการทำความสะอาด
GET /storage/cleanup/status
Response: {
    "success": true,
    "cleanup_status": {
        "running": true,
        "progress_percent": 45.5,
        "files_processed": 455,
        "files_deleted": 450,
        "errors": 5,
        "start_time": "2025-01-09T15:30:00Z"
    }
}

# หยุดการทำความสะอาด
POST /storage/cleanup/stop

# รายงานการทำความสะอาด
GET /storage/cleanup/reports?days=7
Response: {
    "success": true,
    "reports": [
        {
            "date": "2025-01-09",
            "files_deleted": 150,
            "space_freed_gb": 0.75,
            "errors": 2,
            "duration_seconds": 45
        }
    ]
}
```

### 5.2 WebSocket Events

```javascript
// Client → Server
socket.emit('storage_status_request');           // ขอสถานะพื้นที่จัดเก็บ
socket.emit('storage_cleanup_start', config);   // เริ่มการทำความสะอาด
socket.emit('storage_cleanup_stop');            // หยุดการทำความสะอาด
socket.emit('join_storage_room');               // เข้าร่วม storage room

// Server → Client
socket.on('storage_status_update', (status) => {
    // อัปเดตสถานะพื้นที่จัดเก็บ
    updateStorageStatus(status);
});

socket.on('cleanup_progress', (progress) => {
    // อัปเดตความคืบหน้าการทำความสะอาด
    updateCleanupProgress(progress);
});

socket.on('cleanup_complete', (summary) => {
    // การทำความสะอาดเสร็จสิ้น
    showCleanupComplete(summary);
});

socket.on('storage_warning', (warning) => {
    // แจ้งเตือนพื้นที่จัดเก็บ
    showStorageWarning(warning);
});
```

## 6) แดชบอร์ดและการแสดงผล (Dashboard & Visualization)

### 6.1 โครงสร้างแดชบอร์ด

```html
<!-- Storage Dashboard -->
<div class="storage-dashboard">
    <!-- Storage Status -->
    <div class="storage-status">
        <h4>สถานะพื้นที่จัดเก็บ</h4>
        <div class="storage-metrics">
            <div class="metric-item">
                <span class="metric-label">พื้นที่ทั้งหมด:</span>
                <span id="total-space">500.0 GB</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">พื้นที่ที่ใช้:</span>
                <span id="used-space">350.0 GB</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">พื้นที่ว่าง:</span>
                <span id="free-space">150.0 GB</span>
            </div>
            <div class="metric-item">
                <span class="metric-label">อัตราการใช้:</span>
                <span id="usage-percent">70.0%</span>
            </div>
        </div>
        
        <!-- Storage Bar -->
        <div class="storage-bar">
            <div class="storage-fill" id="storage-fill" style="width: 70%"></div>
        </div>
        
        <div class="storage-status-badge" id="storage-status-badge">
            <span class="badge bg-success">Healthy</span>
        </div>
    </div>
    
    <!-- Cleanup Operations -->
    <div class="cleanup-operations">
        <h4>การทำความสะอาด</h4>
        <div class="cleanup-controls">
            <button class="btn btn-primary" onclick="startCleanup()">
                เริ่มการทำความสะอาด
            </button>
            <button class="btn btn-warning" onclick="stopCleanup()">
                หยุดการทำความสะอาด
            </button>
        </div>
        
        <div class="cleanup-progress" id="cleanup-progress" style="display: none;">
            <div class="progress">
                <div class="progress-bar" id="cleanup-progress-bar" style="width: 0%"></div>
            </div>
            <div class="progress-text" id="cleanup-progress-text">0%</div>
        </div>
    </div>
    
    <!-- File Statistics -->
    <div class="file-statistics">
        <h4>สถิติไฟล์</h4>
        <div class="stats-grid">
            <div class="stat-item">
                <span class="stat-label">ไฟล์ทั้งหมด:</span>
                <span id="total-files">1,250</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">ไฟล์เก่า (>7 วัน):</span>
                <span id="old-files">150</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">ขนาดรวม:</span>
                <span id="total-size">2.5 GB</span>
            </div>
        </div>
    </div>
    
    <!-- Recent Cleanup Reports -->
    <div class="cleanup-reports">
        <h4>รายงานการทำความสะอาดล่าสุด</h4>
        <div id="recent-reports">
            <!-- Dynamic content -->
        </div>
    </div>
</div>
```

### 6.2 การแสดงผลแบบ Real-time

```javascript
function updateStorageStatus(status) {
    // อัปเดตตัวเลข
    document.getElementById('total-space').textContent = `${status.total_gb.toFixed(1)} GB`;
    document.getElementById('used-space').textContent = `${status.used_gb.toFixed(1)} GB`;
    document.getElementById('free-space').textContent = `${status.free_gb.toFixed(1)} GB`;
    document.getElementById('usage-percent').textContent = `${status.usage_percent.toFixed(1)}%`;
    
    // อัปเดต storage bar
    const storageFill = document.getElementById('storage-fill');
    storageFill.style.width = `${status.usage_percent}%`;
    
    // อัปเดตสถานะ
    const statusBadge = document.getElementById('storage-status-badge');
    let badgeClass = 'bg-success';
    let badgeText = 'Healthy';
    
    if (status.status === 'critical') {
        badgeClass = 'bg-danger';
        badgeText = 'Critical';
    } else if (status.status === 'warning') {
        badgeClass = 'bg-warning';
        badgeText = 'Warning';
    }
    
    statusBadge.innerHTML = `<span class="badge ${badgeClass}">${badgeText}</span>`;
}

function updateCleanupProgress(progress) {
    const progressContainer = document.getElementById('cleanup-progress');
    const progressBar = document.getElementById('cleanup-progress-bar');
    const progressText = document.getElementById('cleanup-progress-text');
    
    // แสดง progress container
    progressContainer.style.display = 'block';
    
    // อัปเดต progress bar
    progressBar.style.width = `${progress.progress_percent}%`;
    progressText.textContent = `${progress.progress_percent.toFixed(1)}%`;
    
    // อัปเดตข้อมูล
    document.getElementById('files-processed').textContent = progress.files_processed;
    document.getElementById('files-deleted').textContent = progress.files_deleted;
    document.getElementById('cleanup-errors').textContent = progress.errors;
}

function showCleanupComplete(summary) {
    // ซ่อน progress
    document.getElementById('cleanup-progress').style.display = 'none';
    
    // แสดงผลลัพธ์
    const resultMessage = `
        <div class="alert alert-success">
            <h5>การทำความสะอาดเสร็จสิ้น</h5>
            <p>ลบไฟล์: ${summary.files_deleted} ไฟล์</p>
            <p>พื้นที่ที่ได้: ${summary.space_freed_gb.toFixed(2)} GB</p>
            <p>ข้อผิดพลาด: ${summary.errors} รายการ</p>
            <p>เวลาใช้: ${summary.duration_seconds} วินาที</p>
        </div>
    `;
    
    // แสดงผลลัพธ์ในหน้า
    const resultsContainer = document.getElementById('cleanup-results');
    resultsContainer.innerHTML = resultMessage;
    
    // อัปเดตสถานะพื้นที่จัดเก็บ
    socket.emit('storage_status_request');
}
```

## 7) การผนวกรวมกับระบบ (System Integration)

### 7.1 การผนวกรวมกับ Detection Module

```python
class DetectionStorageIntegration:
    """การผนวกรวมกับ Detection Module"""
    
    def __init__(self, storage_manager, detection_processor):
        self.storage_manager = storage_manager
        self.detection_processor = detection_processor
    
    def save_detection_result(self, frame, detection_result):
        """บันทึกผลการตรวจจับพร้อมตรวจสอบพื้นที่"""
        # ตรวจสอบพื้นที่ก่อนบันทึก
        if not self.storage_manager.check_space_before_save():
            self.storage_manager.trigger_cleanup()
            # รอให้การทำความสะอาดเสร็จ
            if not self.storage_manager.wait_for_cleanup_complete(timeout=60):
                raise StorageError("Storage cleanup failed")
        
        # บันทึกภาพ
        image_path = self.detection_processor.save_detection_image(frame)
        
        # บันทึกผลลัพธ์
        result_path = self.detection_processor.save_detection_result(detection_result)
        
        return {
            'image_path': image_path,
            'result_path': result_path,
            'storage_status': self.storage_manager.get_storage_status()
        }
```

### 7.2 การผนวกรวมกับ Health Monitor

```python
class StorageHealthIntegration:
    """การผนวกรวมกับ Health Monitor"""
    
    def __init__(self, storage_manager, health_monitor):
        self.storage_manager = storage_manager
        self.health_monitor = health_monitor
    
    def check_storage_health(self):
        """ตรวจสอบสุขภาพของพื้นที่จัดเก็บ"""
        storage_status = self.storage_manager.get_storage_status()
        
        health_check = {
            'component': 'storage_manager',
            'status': 'healthy',
            'message': 'Storage space is sufficient',
            'details': storage_status
        }
        
        # ตรวจสอบสถานะพื้นที่
        if storage_status['status'] == 'critical':
            health_check['status'] = 'unhealthy'
            health_check['message'] = 'Critical storage space'
        elif storage_status['status'] == 'warning':
            health_check['status'] = 'warning'
            health_check['message'] = 'Low storage space'
        
        # เพิ่มข้อมูลเพิ่มเติม
        health_check['details']['cleanup_needed'] = storage_status['action_required']
        health_check['details']['estimated_cleanup_time'] = self.estimate_cleanup_time()
        
        return health_check
    
    def estimate_cleanup_time(self):
        """ประมาณเวลาที่ใช้ในการทำความสะอาด"""
        old_files_count = self.storage_manager.count_old_files()
        batch_size = self.storage_manager.config.batch_size
        
        # ประมาณ 0.1 วินาทีต่อไฟล์
        estimated_seconds = (old_files_count / batch_size) * 0.1
        return max(estimated_seconds, 1)  # ขั้นต่ำ 1 วินาที
```

## 8) การตั้งค่าและการติดตั้ง (Configuration & Installation)

### 8.1 การตั้งค่า Service

```python
# dependency_container.py
if STORAGE_MANAGER_ENABLED:
    from src.services.storage_manager import StorageManager
    from src.services.storage_service import StorageService
    
    # ลงทะเบียน Storage Service
    self.register_service('storage_service', StorageService, 
                         singleton=True, dependencies={'logger': 'logger'})
    
    # ลงทะเบียน Storage Manager
    self.register_service('storage_manager', StorageManager, 
                         singleton=True, dependencies={
                             'storage_service': 'storage_service',
                             'logger': 'logger'
                         })
```

### 8.2 การตั้งค่า Scheduler

```python
# app.py หรือ main service
def setup_storage_scheduler():
    """ตั้งค่า scheduler สำหรับ Storage Manager"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from src.services.storage_manager import StorageManager
    
    scheduler = BackgroundScheduler()
    storage_manager = get_service('storage_manager')
    
    # ตรวจสอบพื้นที่ทุก 5 นาที
    scheduler.add_job(
        storage_manager.check_and_cleanup,
        'interval',
        minutes=5,
        id='storage_cleanup_check'
    )
    
    # รายงานสถานะทุก 1 ชั่วโมง
    scheduler.add_job(
        storage_manager.generate_status_report,
        'interval',
        hours=1,
        id='storage_status_report'
    )
    
    scheduler.start()
    return scheduler
```

## 9) การทดสอบและการตรวจสอบ (Testing & Validation)

### 9.1 Unit Tests

```python
def test_storage_space_check():
    """ทดสอบการตรวจสอบพื้นที่ดิสก์"""
    storage_service = get_service('storage_service')
    
    # ทดสอบพื้นที่เพียงพอ
    space_info = storage_service.check_disk_space('/tmp')
    assert space_info is not None
    assert 'total_gb' in space_info
    assert 'free_gb' in space_info
    assert 'usage_percent' in space_info

def test_file_selection():
    """ทดสอบการเลือกไฟล์สำหรับการลบ"""
    storage_service = get_service('storage_service')
    
    # สร้างไฟล์ทดสอบ
    test_files = create_test_files()
    
    # ทดสอบการเลือกไฟล์เก่า
    old_files = storage_service.select_files_for_deletion(
        '/tmp/test', retention_days=1
    )
    
    assert len(old_files) > 0
    assert all('age_days' in f for f in old_files)

def test_batch_deletion():
    """ทดสอบการลบไฟล์แบบ batch"""
    storage_service = get_service('storage_service')
    
    # สร้างไฟล์ทดสอบ
    test_files = create_test_files(count=50)
    
    # ทดสอบการลบแบบ batch
    result = storage_service.process_batch_deletion(test_files, batch_size=10)
    
    assert result['total_files'] == 50
    assert result['processed_files'] == 50
    assert result['deleted_files'] >= 45  # อาจมีข้อผิดพลาดบ้าง
```

### 9.2 Integration Tests

```python
def test_storage_integration():
    """ทดสอบการผนวกรวมกับระบบ"""
    storage_manager = get_service('storage_manager')
    detection_processor = get_service('detection_processor')
    
    # ทดสอบการบันทึกผลการตรวจจับ
    test_frame = create_test_frame()
    test_result = create_test_detection_result()
    
    # บันทึกผลลัพธ์
    result = storage_manager.save_detection_result(test_frame, test_result)
    
    assert 'image_path' in result
    assert 'result_path' in result
    assert 'storage_status' in result

def test_health_integration():
    """ทดสอบการผนวกรวมกับ Health Monitor"""
    storage_manager = get_service('storage_manager')
    health_monitor = get_service('health_monitor')
    
    # ตรวจสอบสุขภาพพื้นที่จัดเก็บ
    health_check = health_monitor.check_storage_health()
    
    assert health_check['component'] == 'storage_manager'
    assert 'status' in health_check
    assert 'details' in health_check
```

## 10) การแก้ไขปัญหาและการ Debug (Troubleshooting & Debug)

### 10.1 ปัญหาที่พบบ่อย

#### **ปัญหา 1: การลบไฟล์ล้มเหลว**
```bash
# ตรวจสอบสิทธิ์การเข้าถึง
ls -la /home/camuser/aicamera/edge/captured_images/

# ตรวจสอบ disk space
df -h /home/camuser/aicamera/edge/captured_images/

# ตรวจสอบ inode
df -i /home/camuser/aicamera/edge/captured_images/

# ตรวจสอบ logs
journalctl -u aicamera_lpr.service -n 100 | grep -i storage
```

#### **ปัญหา 2: การตรวจสอบพื้นที่ช้า**
```python
# ตรวจสอบการทำงานของ disk
def check_disk_performance(self, path):
    """ตรวจสอบประสิทธิภาพของดิสก์"""
    import time
    
    start_time = time.time()
    
    # ทดสอบการอ่าน
    test_file = os.path.join(path, '.test_performance')
    with open(test_file, 'w') as f:
        f.write('test')
    
    read_start = time.time()
    with open(test_file, 'r') as f:
        f.read()
    read_time = time.time() - read_start
    
    # ทดสอบการเขียน
    write_start = time.time()
    with open(test_file, 'w') as f:
        f.write('test' * 1000)
    write_time = time.time() - write_start
    
    # ทำความสะอาด
    os.remove(test_file)
    
    total_time = time.time() - start_time
    
    return {
        'read_time_ms': read_time * 1000,
        'write_time_ms': write_time * 1000,
        'total_time_ms': total_time * 1000,
        'disk_health': 'healthy' if total_time < 1.0 else 'slow'
    }
```

#### **ปัญหา 3: การทำความสะอาดไม่เสร็จ**
```python
# ตรวจสอบการทำงานของ cleanup process
def debug_cleanup_process(self):
    """Debug การทำงานของ cleanup process"""
    import psutil
    import threading
    
    # ตรวจสอบ threads ที่ทำงาน
    current_thread = threading.current_thread()
    all_threads = threading.enumerate()
    
    # ตรวจสอบ process info
    process = psutil.Process()
    threads = process.threads()
    
    debug_info = {
        'current_thread': current_thread.name,
        'total_threads': len(all_threads),
        'process_threads': len(threads),
        'cpu_percent': process.cpu_percent(),
        'memory_mb': process.memory_info().rss / (1024 * 1024)
    }
    
    return debug_info
```

### 10.2 คำสั่งวินิจฉัยระบบ

```bash
# ตรวจสอบ Storage Manager Service
curl -s http://localhost/storage/status | python3 -m json.tool

# ดูข้อมูลโฟลเดอร์ภาพ
curl -s http://localhost/storage/images/info | python3 -m json.tool

# ดูรายการไฟล์เก่า
curl -s "http://localhost/storage/images/old?limit=20" | python3 -m json.tool

# เริ่มการทำความสะอาด
curl -s -X POST http://localhost/storage/cleanup/start \
  -H 'Content-Type: application/json' \
  -d '{"retention_days": 7, "batch_size": 100, "max_files": 500}'

# ดูสถานะการทำความสะอาด
curl -s http://localhost/storage/cleanup/status | python3 -m json.tool

# ดูรายงานการทำความสะอาด
curl -s "http://localhost/storage/cleanup/reports?days=7" | python3 -m json.tool

# ตรวจสอบ disk space
df -h /home/camuser/aicamera/edge/captured_images/

# ตรวจสอบไฟล์ในโฟลเดอร์
ls -la /home/camuser/aicamera/edge/captured_images/ | head -20

# ตรวจสอบไฟล์เก่า
find /home/camuser/aicamera/edge/captured_images/ -type f -mtime +7 | head -10
```

## 11) การปรับแต่งประสิทธิภาพ (Performance Optimization)

### 11.1 การปรับแต่งการประมวลผล

```python
class StoragePerformanceOptimizer:
    """การปรับแต่งประสิทธิภาพของ Storage Manager"""
    
    def __init__(self):
        self.optimization_config = {
            'parallel_processing': True,
            'async_operations': True,
            'memory_pool_size': 100,
            'file_cache_size': 1000,
            'batch_optimization': True
        }
    
    def optimize_batch_processing(self, files, batch_size):
        """ปรับแต่งการประมวลผลแบบ batch"""
        if not self.optimization_config['batch_optimization']:
            return files
        
        # จัดกลุ่มไฟล์ตามขนาด
        small_files = [f for f in files if f['size_mb'] < 1.0]
        medium_files = [f for f in files if 1.0 <= f['size_mb'] < 5.0]
        large_files = [f for f in files if f['size_mb'] >= 5.0]
        
        # ประมวลผลไฟล์เล็กก่อน (เร็ว)
        optimized_batches = []
        
        # เพิ่มไฟล์เล็กใน batches
        for i in range(0, len(small_files), batch_size):
            optimized_batches.append(small_files[i:i + batch_size])
        
        # เพิ่มไฟล์ขนาดกลาง
        for i in range(0, len(medium_files), batch_size):
            optimized_batches.append(medium_files[i:i + batch_size])
        
        # เพิ่มไฟล์ขนาดใหญ่ (ช้า)
        for i in range(0, len(large_files), batch_size):
            optimized_batches.append(large_files[i:i + batch_size])
        
        return optimized_batches
```

### 11.2 การจัดการ Memory

```python
def optimize_memory_usage(self):
    """ปรับแต่งการใช้ memory"""
    import gc
    
    # บังคับ garbage collection
    gc.collect()
    
    # ล้าง cache ของไฟล์
    if hasattr(self, '_file_cache'):
        self._file_cache.clear()
    
    # ลดขนาด memory pool
    if hasattr(self, '_memory_pool'):
        self._memory_pool.trim()
    
    # บันทึก memory usage
    import psutil
    process = psutil.Process()
    memory_mb = process.memory_info().rss / (1024 * 1024)
    
    self.logger.info(f"Memory usage after optimization: {memory_mb:.2f} MB")
```

### 11.3 การปรับแต่งการจัดเก็บ

```python
def optimize_storage_operations(self):
    """ปรับแต่งการทำงานของ storage"""
    # ใช้ compression สำหรับไฟล์เก่า
    if self.config.enable_compression:
        self.enable_compression_for_old_files()
    
    # ใช้ incremental backup
    if self.config.enable_incremental_backup:
        self.setup_incremental_backup()
    
    # ใช้ cloud storage สำหรับข้อมูลเก่า
    if self.config.enable_cloud_storage:
        self.setup_cloud_storage_migration()
```

## 12) การพัฒนาต่อในอนาคต (Future Enhancements)

### 12.1 คุณสมบัติใหม่ที่วางแผน

1. **Intelligent File Management**
   - AI-driven file prioritization
   - Predictive storage optimization
   - Automatic retention policy adjustment

2. **Advanced Compression**
   - Lossless compression algorithms
   - Adaptive compression based on content
   - Real-time compression during save

3. **Cloud Integration**
   - Automatic cloud backup
   - Hybrid storage management
   - Multi-cloud support

4. **Performance Analytics**
   - Storage performance metrics
   - Bottleneck identification
   - Optimization recommendations

### 12.2 การปรับปรุงประสิทธิภาพ

1. **Parallel Processing**
   - Multi-threaded file operations
   - Distributed storage management
   - GPU acceleration for compression

2. **Smart Caching**
   - Predictive file caching
   - Adaptive cache sizing
   - Intelligent cache invalidation

---

## 📋 **สรุป**

โมดูลจัดการพื้นที่จัดเก็บของ AI Camera v2.0 เป็นระบบที่ครบครันสำหรับการจัดการพื้นที่ดิสก์และการจัดเก็บภาพการตรวจจับแบบหมุนเวียน

### **จุดเด่น:**
- ✅ **การจัดการพื้นที่อัตโนมัติ**: ตรวจสอบและรักษาพื้นที่ว่างให้เพียงพอ
- ✅ **นโยบายการเก็บรักษา**: กำหนดอายุการเก็บไฟล์ตามประเภท
- ✅ **การประมวลผลแบบ Batch**: ประมวลผลไฟล์เป็นชุดเพื่อประสิทธิภาพ
- ✅ **การผนวกรวมระบบ**: เชื่อมต่อกับ Detection Module และ Health Monitor
- ✅ **Real-time Monitoring**: ติดตามสถานะพื้นที่จัดเก็บแบบเรียลไทม์
- ✅ **Modular Architecture**: สามารถเปิด/ปิดได้โดยไม่กระทบระบบหลัก

### **การใช้งาน:**
1. **สำหรับนักพัฒนา**: จัดการพื้นที่จัดเก็บและป้องกันการล้นพื้นที่
2. **สำหรับระบบ**: รักษาประสิทธิภาพการทำงานของระบบ
3. **สำหรับผู้ใช้**: รับประกันการทำงานต่อเนื่องของระบบตรวจจับ

เอกสารนี้เป็นคู่มือครบถ้วนสำหรับการพัฒนา บำรุงรักษา และใช้งานโมดูลจัดการพื้นที่จัดเก็บของระบบ AI Camera v2.0
