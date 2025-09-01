# โมดูลการทดลอง (Experiment Module) – AI Camera v2.0

เวอร์ชัน: 2.0.0  
ปรับปรุงล่าสุด: 2025-01-09  
ผู้เขียน: AI Camera Team  
หมวดหมู่: Technical Analysis  
สถานะ: Active

## 1) วัตถุประสงค์ (Objectives)

โมดูลการทดลองมีเป้าหมายเพื่อสร้างระบบทดสอบและวิจัยกล้องแบบครบวงจรในระบบ AI Camera โดยใช้ detection pipeline ที่มีอยู่แล้ว เพื่อหาการตั้งค่ากล้องที่เหมาะสมที่สุดสำหรับการตรวจจับป้ายทะเบียนและ OCR

### เป้าหมายหลัก:
- **ทดสอบการตรวจจับแบบ Single Shot**: ใช้ภาพนิ่งหรือเฟรมจากกล้อง
- **ทดสอบการตรวจจับตามความยาว**: ใช้ auto focus และการตั้งค่าเริ่มต้น
- **ทดสอบการตั้งค่ากล้องแบบยืดหยุ่น**: ผู้ใช้กำหนดการตั้งค่าเอง
- **การวิเคราะห์และประเมินผล**: สรุปผลการทดลองทั้ง 3 ประเภท
- **การเปรียบเทียบประสิทธิภาพ**: หาการตั้งค่าที่ดีที่สุด

## 2) สถาปัตยกรรมและ Pipeline (Architecture & Pipeline)

### 2.1 โครงสร้างโมดูล (Module Structure)
```
Experiment Module Architecture
├── Experiment Service (Core Logic)
│   ├── Single Detection Pipeline
│   ├── Length Detection Pipeline
│   ├── Flexible Configuration Pipeline
│   └── Analysis & Assessment
├── Experiment Manager (Orchestration)
│   ├── Experiment Execution
│   ├── Data Collection
│   ├── Result Aggregation
│   └── Report Generation
├── Experiment Blueprint (Web API)
│   ├── Experiment Creation
│   ├── Execution Control
│   └── Results Viewing
├── Dashboard JavaScript (Frontend)
│   ├── Real-time Monitoring
│   ├── Configuration Control
│   └── Results Visualization
└── Experiment Template (UI)
    ├── Experiment Dashboard
    ├── Configuration Forms
    └── Results Analysis
```

### 2.2 การผนวกรวมกับ Detection Pipeline
```
Camera Frame → Experiment Configuration → Detection Pipeline → Results Collection → Analysis
     ↓                    ↓                      ↓                ↓              ↓
  Still Image        User Settings        Vehicle Detection    Data Storage   Performance
  or Live Frame      or Auto Config      → LP Detection      → CSV Logging   Assessment
                                      → OCR Processing      → Image Save    → Summary
```

## 3) ประเภทการทดลอง (Experiment Types)

### 3.1 การทดลองแบบ Single Detection Pipeline

#### **วัตถุประสงค์:**
ทดสอบ detection pipeline ด้วยภาพนิ่งหรือเฟรมเดียวจากกล้อง โดยใช้การตั้งค่าปัจจุบัน

#### **ขั้นตอนการทำงาน:**
```python
def run_single_detection_experiment(self, image_source='camera'):
    """
    ทดลอง detection pipeline แบบ single shot
    Args:
        image_source: 'camera' (live frame) หรือ 'still' (still image)
    """
    # 1. เลือกแหล่งภาพ
    if image_source == 'camera':
        frame = self.camera_manager.capture_main_frame()
        source_type = "Live Camera Frame"
    else:
        frame = self.load_still_image()
        source_type = "Still Image"
    
    # 2. ใช้การตั้งค่ากล้องปัจจุบัน
    current_config = self.get_current_camera_config()
    
    # 3. รัน detection pipeline
    detection_result = self.run_detection_pipeline(frame, current_config)
    
    # 4. บันทึกผลลัพธ์
    self.log_experiment_result({
        'experiment_type': 'single_detection',
        'image_source': source_type,
        'camera_config': current_config,
        'detection_result': detection_result,
        'timestamp': datetime.now().isoformat()
    })
    
    return detection_result
```

#### **การตั้งค่า:**
- **Image Source**: เลือกระหว่างภาพนิ่งหรือเฟรมจากกล้อง
- **Camera Configuration**: ใช้การตั้งค่าปัจจุบันของกล้อง
- **Detection Pipeline**: ใช้ detection pipeline ที่มีอยู่แล้ว

### 3.2 การทดลองแบบ Length Detection with Auto Focus

#### **วัตถุประสงค์:**
ทดสอบการตรวจจับตามความยาวของวัตถุ โดยใช้ auto focus และการตั้งค่าเริ่มต้นของกล้อง

#### **ขั้นตอนการทำงาน:**
```python
def run_length_detection_experiment(self, start_length=1, max_length=10, step=1):
    """
    ทดลอง detection ตามความยาวของวัตถุ
    Args:
        start_length: ความยาวเริ่มต้น (เมตร)
        max_length: ความยาวสูงสุด (เมตร)
        step: ขั้นความยาว (เมตร)
    """
    results = []
    
    for distance in range(start_length, max_length + 1, step):
        # 1. ตั้งค่า auto focus ตามความยาว
        self.set_auto_focus_for_distance(distance)
        
        # 2. รอให้ auto focus เสร็จ
        self.wait_for_auto_focus()
        
        # 3. ใช้การตั้งค่าเริ่มต้นของกล้อง
        default_config = self.get_default_camera_config()
        
        # 4. เก็บภาพและรัน detection
        frame = self.camera_manager.capture_main_frame()
        detection_result = self.run_detection_pipeline(frame, default_config)
        
        # 5. บันทึกผลลัพธ์
        result = {
            'distance': distance,
            'focus_position': self.get_current_focus_position(),
            'camera_config': default_config,
            'detection_result': detection_result,
            'image_quality': self.analyze_image_quality(frame)
        }
        results.append(result)
        
        # 6. บันทึกลง CSV
        self.log_length_experiment_result(result)
    
    return results
```

#### **การตั้งค่า:**
- **Distance Range**: 1-10 เมตร (ปรับได้)
- **Auto Focus**: เปิดใช้งานอัตโนมัติ
- **Camera Configuration**: ใช้การตั้งค่าเริ่มต้น
- **Sequential Processing**: ประมวลผลตามลำดับความยาว

### 3.3 การทดลองแบบ Flexible Experimental Configuration

#### **วัตถุประสงค์:**
ผู้ใช้กำหนดการตั้งค่ากล้องเอง แล้วรัน detection pipeline ตามลำดับความยาวที่กำหนด

#### **ขั้นตอนการทำงาน:**
```python
def run_flexible_experiment(self, user_config, start_length=1, max_length=10, step=1):
    """
    ทดลองด้วยการตั้งค่าที่ผู้ใช้กำหนดเอง
    Args:
        user_config: การตั้งค่ากล้องที่ผู้ใช้กำหนด
        start_length: ความยาวเริ่มต้น (เมตร)
        max_length: ความยาวสูงสุด (เมตร)
        step: ขั้นความยาว (เมตร)
    """
    results = []
    
    # 1. อัปเดตการตั้งค่ากล้องตามที่ผู้ใช้กำหนด
    self.update_camera_configuration(user_config)
    
    # 2. รัน detection pipeline ตามลำดับความยาว
    for distance in range(start_length, max_length + 1, step):
        # ตั้งค่า auto focus
        self.set_auto_focus_for_distance(distance)
        self.wait_for_auto_focus()
        
        # เก็บภาพและรัน detection
        frame = self.camera_manager.capture_main_frame()
        detection_result = self.run_detection_pipeline(frame, user_config)
        
        # บันทึกผลลัพธ์
        result = {
            'distance': distance,
            'user_config': user_config,
            'focus_position': self.get_current_focus_position(),
            'detection_result': detection_result,
            'image_quality': self.analyze_image_quality(frame)
        }
        results.append(result)
        
        # บันทึกลง CSV
        self.log_flexible_experiment_result(result)
    
    return results
```

#### **การตั้งค่า:**
- **User Configuration**: ผู้ใช้กำหนดการตั้งค่ากล้องเอง
- **Distance Range**: ปรับได้ตามต้องการ
- **Auto Focus**: เปิดใช้งาน
- **Custom Parameters**: Exposure, Gain, Focus, Sharpness, etc.

## 4) การวิเคราะห์และประเมินผล (Analysis & Assessment)

### 4.1 การวิเคราะห์ผลการทดลอง

#### **การประเมินประสิทธิภาพ:**
```python
def analyze_experiment_results(self, experiment_type):
    """
    วิเคราะห์ผลการทดลองตามประเภท
    """
    if experiment_type == 'single_detection':
        return self.analyze_single_detection_results()
    elif experiment_type == 'length_detection':
        return self.analyze_length_detection_results()
    elif experiment_type == 'flexible_config':
        return self.analyze_flexible_experiment_results()
    else:
        return self.analyze_all_experiment_results()
```

#### **การวิเคราะห์ Single Detection:**
```python
def analyze_single_detection_results(self):
    """วิเคราะห์ผลการทดลอง single detection"""
    results = self.get_experiment_results('single_detection')
    
    analysis = {
        'total_experiments': len(results),
        'success_rate': self.calculate_success_rate(results),
        'average_confidence': self.calculate_average_confidence(results),
        'best_configuration': self.find_best_configuration(results),
        'performance_comparison': self.compare_image_sources(results)
    }
    
    return analysis
```

#### **การวิเคราะห์ Length Detection:**
```python
def analyze_length_detection_results(self):
    """วิเคราะห์ผลการทดลองตามความยาว"""
    results = self.get_experiment_results('length_detection')
    
    analysis = {
        'distance_performance': self.analyze_distance_performance(results),
        'focus_optimization': self.analyze_focus_optimization(results),
        'optimal_distance': self.find_optimal_distance(results),
        'quality_trends': self.analyze_quality_trends(results)
    }
    
    return analysis
```

#### **การวิเคราะห์ Flexible Configuration:**
```python
def analyze_flexible_experiment_results(self):
    """วิเคราะห์ผลการทดลองการตั้งค่าแบบยืดหยุ่น"""
    results = self.get_experiment_results('flexible_config')
    
    analysis = {
        'configuration_performance': self.analyze_config_performance(results),
        'parameter_optimization': self.analyze_parameter_optimization(results),
        'best_parameters': self.find_best_parameters(results),
        'customization_impact': self.analyze_customization_impact(results)
    }
    
    return analysis
```

### 4.2 การสรุปผลการทดลอง

#### **สรุปภาพรวม:**
```python
def generate_experiment_summary(self):
    """สร้างสรุปผลการทดลองทั้งหมด"""
    summary = {
        'experiment_overview': {
            'total_experiments': self.get_total_experiment_count(),
            'success_rate_overall': self.calculate_overall_success_rate(),
            'best_performing_type': self.identify_best_experiment_type()
        },
        'single_detection_summary': self.analyze_single_detection_results(),
        'length_detection_summary': self.analyze_length_detection_results(),
        'flexible_config_summary': self.analyze_flexible_experiment_results(),
        'recommendations': self.generate_recommendations(),
        'performance_metrics': self.calculate_performance_metrics()
    }
    
    return summary
```

#### **การสร้างคำแนะนำ:**
```python
def generate_recommendations(self):
    """สร้างคำแนะนำจากการทดลอง"""
    recommendations = {
        'optimal_camera_config': self.find_optimal_camera_config(),
        'best_distance_range': self.find_best_distance_range(),
        'focus_settings': self.find_optimal_focus_settings(),
        'parameter_tuning': self.suggest_parameter_tuning(),
        'environmental_factors': self.analyze_environmental_factors()
    }
    
    return recommendations
```

## 5) การจัดเก็บข้อมูลและผลลัพธ์ (Data Storage & Results)

### 5.1 โครงสร้างการจัดเก็บข้อมูล

```
experiment_results/
├── single_detection/
│   ├── experiment_log.csv
│   ├── images/
│   └── metadata/
├── length_detection/
│   ├── experiment_log.csv
│   ├── images/
│   └── metadata/
├── flexible_config/
│   ├── experiment_log.csv
│   ├── images/
│   └── metadata/
└── analysis_reports/
    ├── summary_report.json
    ├── performance_charts/
    └── recommendations.txt
```

### 5.2 โครงสร้าง CSV Log

#### **Single Detection CSV:**
```csv
Timestamp,ExperimentID,ImageSource,CameraConfig,VehiclesDetected,PlatesDetected,OCRSuccess,OCRConfidence,ProcessingTime,ImageQuality
2025-01-09T15:30:00,SD_001,Live Camera,Default,2,1,True,0.95,45.2,High
2025-01-09T15:31:00,SD_002,Still Image,Default,1,1,True,0.88,42.1,Medium
```

#### **Length Detection CSV:**
```csv
Timestamp,ExperimentID,Distance,FocusPosition,VehiclesDetected,PlatesDetected,OCRSuccess,OCRConfidence,ImageQuality,ProcessingTime
2025-01-09T15:35:00,LD_001,1,0.05,2,1,True,0.95,High,43.2
2025-01-09T15:36:00,LD_001,2,0.10,2,1,True,0.92,High,44.1
2025-01-09T15:37:00,LD_001,3,0.15,1,1,True,0.88,Medium,45.8
```

#### **Flexible Configuration CSV:**
```csv
Timestamp,ExperimentID,Distance,UserConfig,FocusPosition,VehiclesDetected,PlatesDetected,OCRSuccess,OCRConfidence,ImageQuality,ProcessingTime
2025-01-09T15:40:00,FC_001,1,Custom_Config_1,0.05,2,1,True,0.96,High,42.5
2025-01-09T15:41:00,FC_001,2,Custom_Config_1,0.10,2,1,True,0.93,High,43.2
```

### 5.3 การจัดเก็บภาพและ Metadata

```python
def save_experiment_data(self, experiment_type, result, frame):
    """จัดเก็บข้อมูลการทดลอง"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # บันทึกภาพ
    image_filename = f"{timestamp}_{experiment_type}_{result['distance']}m.jpg"
    image_path = os.path.join(self.image_save_dir, experiment_type, image_filename)
    cv2.imwrite(image_path, frame)
    
    # บันทึก metadata
    metadata_filename = f"{timestamp}_{experiment_type}_{result['distance']}m.json"
    metadata_path = os.path.join(self.metadata_save_dir, experiment_type, metadata_filename)
    
    metadata = {
        'experiment_type': experiment_type,
        'timestamp': timestamp,
        'camera_config': result.get('camera_config', {}),
        'focus_position': result.get('focus_position', 0),
        'distance': result.get('distance', 0),
        'detection_result': result.get('detection_result', {}),
        'image_quality': result.get('image_quality', {}),
        'image_path': image_path
    }
    
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    return image_path, metadata_path
```

## 6) API และการเชื่อมต่อ (API & Integration)

### 6.1 REST Endpoints

```http
# สร้างการทดลองใหม่
POST /experiments/create
Content-Type: application/json
{
    "experiment_type": "single_detection|length_detection|flexible_config",
    "parameters": {
        "start_length": 1,
        "max_length": 10,
        "step": 1,
        "user_config": {...}
    }
}

# เริ่มการทดลอง
POST /experiments/run/{experiment_id}

# หยุดการทดลอง
POST /experiments/stop/{experiment_id}

# ดูสถานะการทดลอง
GET /experiments/status/{experiment_id}

# ดูผลลัพธ์การทดลอง
GET /experiments/results/{experiment_id}

# ดูสรุปผลการทดลองทั้งหมด
GET /experiments/summary

# ดาวน์โหลดรายงาน
GET /experiments/report/{experiment_id}?format=csv|json|pdf
```

### 6.2 WebSocket Events

```javascript
// Client → Server
socket.emit('create_experiment', experimentConfig);
socket.emit('start_experiment', experimentId);
socket.emit('stop_experiment', experimentId);
socket.emit('join_experiment_room', experimentId);

// Server → Client
socket.on('experiment_status_update', (status) => {
    updateExperimentStatus(status);
});

socket.on('experiment_progress', (progress) => {
    updateExperimentProgress(progress);
});

socket.on('experiment_result', (result) => {
    addExperimentResult(result);
});

socket.on('experiment_complete', (summary) => {
    showExperimentComplete(summary);
});
```

## 7) แดชบอร์ดและการแสดงผล (Dashboard & Visualization)

### 7.1 โครงสร้างแดชบอร์ด

```html
<!-- Experiment Dashboard -->
<div class="experiment-dashboard">
    <!-- Experiment Types -->
    <div class="experiment-types">
        <div class="experiment-card" data-type="single_detection">
            <h4>Single Detection Pipeline</h4>
            <p>ทดสอบ detection pipeline ด้วยภาพนิ่งหรือเฟรมเดียว</p>
            <button class="btn btn-primary" onclick="createExperiment('single_detection')">
                สร้างการทดลอง
            </button>
        </div>
        
        <div class="experiment-card" data-type="length_detection">
            <h4>Length Detection with Auto Focus</h4>
            <p>ทดสอบการตรวจจับตามความยาวด้วย auto focus</p>
            <button class="btn btn-primary" onclick="createExperiment('length_detection')">
                สร้างการทดลอง
            </button>
        </div>
        
        <div class="experiment-card" data-type="flexible_config">
            <h4>Flexible Experimental Configuration</h4>
            <p>กำหนดการตั้งค่ากล้องเองและทดสอบ</p>
            <button class="btn btn-primary" onclick="createExperiment('flexible_config')">
                สร้างการทดลอง
            </button>
        </div>
    </div>
    
    <!-- Active Experiments -->
    <div class="active-experiments">
        <h4>การทดลองที่กำลังดำเนินการ</h4>
        <div id="active-experiments-list">
            <!-- Dynamic content -->
        </div>
    </div>
    
    <!-- Results Summary -->
    <div class="results-summary">
        <h4>สรุปผลการทดลอง</h4>
        <div id="experiment-summary">
            <!-- Dynamic content -->
        </div>
    </div>
</div>
```

### 7.2 การแสดงผลแบบ Real-time

```javascript
function updateExperimentProgress(progress) {
    const progressBar = document.getElementById(`progress-${progress.experiment_id}`);
    if (progressBar) {
        progressBar.style.width = `${progress.percentage}%`;
        progressBar.textContent = `${progress.percentage}%`;
    }
    
    // อัปเดตสถานะ
    const statusElement = document.getElementById(`status-${progress.experiment_id}`);
    if (statusElement) {
        statusElement.textContent = progress.status;
    }
    
    // แสดงผลลัพธ์ล่าสุด
    if (progress.latest_result) {
        addExperimentResult(progress.latest_result);
    }
}

function addExperimentResult(result) {
    const resultsContainer = document.getElementById('experiment-results');
    
    const resultCard = document.createElement('div');
    resultCard.className = 'result-card';
    resultCard.innerHTML = `
        <div class="result-header">
            <span class="experiment-type">${result.experiment_type}</span>
            <span class="timestamp">${result.timestamp}</span>
        </div>
        <div class="result-details">
            <p><strong>Distance:</strong> ${result.distance}m</p>
            <p><strong>Vehicles Detected:</strong> ${result.vehicles_detected}</p>
            <p><strong>Plates Detected:</strong> ${result.plates_detected}</p>
            <p><strong>OCR Success:</strong> ${result.ocr_success ? 'Yes' : 'No'}</p>
            <p><strong>OCR Confidence:</strong> ${(result.ocr_confidence * 100).toFixed(1)}%</p>
        </div>
    `;
    
    resultsContainer.appendChild(resultCard);
}
```

## 8) การตั้งค่าและการติดตั้ง (Configuration & Installation)

### 8.1 Environment Variables

```bash
# /edge/installation/.env.production
# Experiment Configuration
EXPERIMENT_ENABLED=true
EXPERIMENT_AUTO_SAVE=true
EXPERIMENT_MAX_RETRIES=3
EXPERIMENT_RESULTS_DIR=/home/camuser/aicamera/experiment_results
EXPERIMENT_IMAGE_QUALITY=95
EXPERIMENT_MAX_DISTANCE=20
EXPERIMENT_DEFAULT_STEP=1
```

### 8.2 การตั้งค่า Dependencies

```python
# requirements.txt
easyocr==1.7.0
scikit-image==0.21.0
opencv-python==4.8.1.78
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
pandas==2.0.3
```

### 8.3 การตั้งค่า Service

```python
# dependency_container.py
if EXPERIMENT_ENABLED:
    from src.services.experiment_service import ExperimentService
    self.register_service('experiment_service', ExperimentService, 
                         singleton=True, dependencies={'logger': 'logger'})
```

## 9) การทดสอบและการตรวจสอบ (Testing & Validation)

### 9.1 การทดสอบการทำงาน

```python
def test_single_detection_experiment():
    """ทดสอบการทดลอง single detection"""
    experiment_service = get_service('experiment_service')
    
    # ทดสอบด้วยภาพนิ่ง
    result = experiment_service.run_single_detection_experiment('still')
    assert result is not None
    assert 'detection_result' in result
    
    # ทดสอบด้วยเฟรมจากกล้อง
    result = experiment_service.run_single_detection_experiment('camera')
    assert result is not None
    assert 'detection_result' in result

def test_length_detection_experiment():
    """ทดสอบการทดลองตามความยาว"""
    experiment_service = get_service('experiment_service')
    
    results = experiment_service.run_length_detection_experiment(1, 5, 1)
    assert len(results) == 5
    
    for result in results:
        assert 'distance' in result
        assert 'detection_result' in result
        assert 'focus_position' in result

def test_flexible_config_experiment():
    """ทดสอบการทดลองการตั้งค่าแบบยืดหยุ่น"""
    experiment_service = get_service('experiment_service')
    
    user_config = {
        'exposure_time': 100000,
        'analog_gain': 2.0,
        'lens_position': 0.1
    }
    
    results = experiment_service.run_flexible_experiment(user_config, 1, 3, 1)
    assert len(results) == 3
    
    for result in results:
        assert 'user_config' in result
        assert result['user_config'] == user_config
```

### 9.2 การทดสอบการวิเคราะห์

```python
def test_experiment_analysis():
    """ทดสอบการวิเคราะห์ผลการทดลอง"""
    experiment_service = get_service('experiment_service')
    
    # ทดสอบการวิเคราะห์ single detection
    analysis = experiment_service.analyze_single_detection_results()
    assert 'success_rate' in analysis
    assert 'best_configuration' in analysis
    
    # ทดสอบการวิเคราะห์ length detection
    analysis = experiment_service.analyze_length_detection_results()
    assert 'optimal_distance' in analysis
    assert 'quality_trends' in analysis
    
    # ทดสอบการวิเคราะห์ flexible config
    analysis = experiment_service.analyze_flexible_experiment_results()
    assert 'best_parameters' in analysis
    assert 'customization_impact' in analysis
    
    # ทดสอบการสรุปผล
    summary = experiment_service.generate_experiment_summary()
    assert 'recommendations' in summary
    assert 'performance_metrics' in summary
```

## 10) การแก้ไขปัญหาและการ Debug (Troubleshooting & Debug)

### 10.1 ปัญหาที่พบบ่อย

#### **ปัญหา 1: การทดลองไม่เริ่มต้น**
```bash
# ตรวจสอบ service status
curl http://localhost/experiments/status

# ตรวจสอบ logs
journalctl -u aicamera_lpr.service -n 100 | grep -i experiment

# ตรวจสอบ configuration
echo $EXPERIMENT_ENABLED
```

#### **ปัญหา 2: Auto Focus ไม่ทำงาน**
```python
# ตรวจสอบ auto focus status
def check_auto_focus_status(self):
    try:
        focus_status = self.camera_handler.get_focus_status()
        if not focus_status['enabled']:
            self.logger.warning("Auto focus not enabled")
            return False
        return True
    except Exception as e:
        self.logger.error(f"Error checking auto focus: {e}")
        return False
```

#### **ปัญหา 3: การบันทึกข้อมูลล้มเหลว**
```python
# ตรวจสอบ disk space
def check_disk_space(self):
    try:
        statvfs = os.statvfs(self.results_dir)
        free_space = statvfs.f_frsize * statvfs.f_bavail
        if free_space < 1024 * 1024 * 100:  # 100MB
            self.logger.warning("Low disk space")
            return False
        return True
    except Exception as e:
        self.logger.error(f"Error checking disk space: {e}")
        return False
```

### 10.2 คำสั่งวินิจฉัยระบบ

```bash
# ตรวจสอบ Experiment Service
curl -s http://localhost/experiments/status | python3 -m json.tool

# ดูผลลัพธ์การทดลองล่าสุด
curl -s "http://localhost/experiments/results/recent?limit=5" | python3 -m json.tool

# ตรวจสอบไฟล์การทดลอง
ls -la /home/camuser/aicamera/experiment_results/

# ตรวจสอบ CSV logs
head -10 /home/camuser/aicamera/experiment_results/*/experiment_log.csv

# ตรวจสอบ system resources
df -h /home/camuser/aicamera/experiment_results/
free -h
```

## 11) การปรับแต่งประสิทธิภาพ (Performance Optimization)

### 11.1 การปรับแต่งการประมวลผล

```python
# การตั้งค่า batch processing
class ExperimentService:
    def __init__(self):
        self.batch_size = 5  # ประมวลผลทีละ 5 การทดลอง
        self.parallel_processing = True  # เปิด parallel processing
        self.cache_results = True  # เก็บ cache ผลลัพธ์
```

### 11.2 การจัดการ Memory

```python
def optimize_memory_usage(self):
    """ปรับแต่งการใช้ memory"""
    # ลบภาพเก่าที่เกินอายุ
    self.cleanup_old_images(max_age_hours=24)
    
    # ลบ metadata เก่า
    self.cleanup_old_metadata(max_age_hours=48)
    
    # บีบอัดภาพเก่า
    self.compress_old_images(max_age_hours=12)
```

### 11.3 การปรับแต่งการจัดเก็บ

```python
def optimize_storage(self):
    """ปรับแต่งการจัดเก็บ"""
    # ใช้ compression สำหรับภาพ
    self.enable_image_compression(quality=85)
    
    # ใช้ incremental backup
    self.enable_incremental_backup()
    
    # ใช้ cloud storage สำหรับข้อมูลเก่า
    self.enable_cloud_storage_for_old_data()
```

## 12) การพัฒนาต่อในอนาคต (Future Enhancements)

### 12.1 คุณสมบัติใหม่ที่วางแผน

1. **Machine Learning Integration**
   - AI-driven parameter optimization
   - Predictive performance analysis
   - Automated experiment design

2. **Advanced Analytics**
   - Statistical significance testing
   - Trend analysis and forecasting
   - Comparative performance metrics

3. **Multi-camera Support**
   - Simultaneous multi-camera testing
   - Camera synchronization
   - Distributed experiment execution

4. **Cloud Integration**
   - Remote experiment management
   - Cloud data storage and analysis
   - Collaborative experiment sharing

### 12.2 การปรับปรุงประสิทธิภาพ

1. **Parallel Processing**
   - Concurrent experiment execution
   - Multi-threaded data processing
   - GPU acceleration for analysis

2. **Real-time Optimization**
   - Live parameter adjustment
   - Adaptive experiment flow
   - Dynamic configuration updates

---

## 📋 **สรุป**

โมดูลการทดลองของ AI Camera v2.0 เป็นระบบที่ครบครันสำหรับการทดสอบและวิจัยกล้อง โดยใช้ detection pipeline ที่มีอยู่แล้ว เพื่อหาการตั้งค่าที่เหมาะสมที่สุด

### **จุดเด่น:**
- ✅ **3 ประเภทการทดลอง**: Single Detection, Length Detection, Flexible Configuration
- ✅ **การผนวกรวม Detection Pipeline**: ใช้ระบบที่มีอยู่แล้ว
- ✅ **Auto Focus Support**: รองรับการปรับ focus อัตโนมัติ
- ✅ **การวิเคราะห์ครบถ้วน**: วิเคราะห์ ประเมิน และสรุปผล
- ✅ **Real-time Monitoring**: ติดตามการทดลองแบบเรียลไทม์
- ✅ **Modular Architecture**: สามารถเปิด/ปิดได้โดยไม่กระทบระบบหลัก

### **การใช้งาน:**
1. **สำหรับนักวิจัย**: ทดสอบการตั้งค่ากล้องที่แตกต่างกัน
2. **สำหรับนักพัฒนา**: ทดสอบ detection pipeline ในสภาพแวดล้อมต่างๆ
3. **สำหรับผู้ใช้**: หาการตั้งค่าที่เหมาะสมที่สุดสำหรับการใช้งานจริง

เอกสารนี้เป็นคู่มือครบถ้วนสำหรับการพัฒนา บำรุงรักษา และใช้งานโมดูลการทดลองของระบบ AI Camera v2.0
