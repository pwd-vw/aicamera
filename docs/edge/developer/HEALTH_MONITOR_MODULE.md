# โมดูล Health Monitor – AI Camera v2.0

เวอร์ชัน: 2.0  
ปรับปรุงล่าสุด: 2025-09-01  
ผู้เขียน: AI Camera Team

## 1) วัตถุประสงค์ (Health Objectives)

Health Monitor มีเป้าหมายเพื่อตรวจวัดและรายงานสุขภาพของระบบ AI Camera แบบเรียลไทม์ ครอบคลุมทั้งฮาร์ดแวร์ กล้อง โมดูลตรวจจับโมเดล (Detection) ทรัพยากรระบบ ฐานข้อมูล และการเชื่อมต่อเครือข่าย เพื่อให้ระบบทำงานได้เสถียรและแก้ปัญหาได้อย่างรวดเร็ว

- ตรวจสอบสถานะกล้อง (Initialized/Streaming)
- ตรวจสอบพื้นที่จัดเก็บภาพ (Disk Space) ในโฟลเดอร์ภาพ `/home/camuser/aicamera/edge/captured_images`
- ตรวจสอบ CPU, RAM, อุณหภูมิ
- ตรวจสอบการโหลดโมเดล AI และ EasyOCR
- ตรวจสอบฐานข้อมูล (เชื่อมต่อ/คิวรีได้)
- ตรวจสอบเครือข่าย (Google DNS, WebSocket)
- บันทึกผลตรวจสุขภาพลงฐานข้อมูลและแสดงผลผ่านแดชบอร์ดแบบเรียลไทม์

## 2) สถาปัตยกรรมและองค์ประกอบ (Architecture & Components)

```
Health Monitor Architecture
├── HealthMonitor (Component)
│   ├── check_camera()
│   ├── check_disk_space()
│   ├── check_cpu_ram()
│   ├── check_model_loading()
│   ├── check_easyocr_init()
│   ├── check_database_connection()
│   └── check_network_connectivity()
├── HealthService (Service Layer)
│   ├── get_system_health()
│   ├── get_health_logs()
│   └── start_monitoring()
└── Health Blueprint (Web Interface)
    ├── /health/system
    ├── /health/logs
    └── /health/monitor/*
```

แหล่งข้อมูลและรูปแบบสถานะ Detection ที่ใช้งานใน Health:

- Detection Manager Status
```python
{
  'service_running': bool,
  'thread_alive': bool,
  'auto_start': bool,
  'detection_interval': float,
  'detection_processor_status': {
    'models_loaded': bool,
    'vehicle_model_available': bool,
    'lp_detection_model_available': bool,
    'lp_ocr_model_available': bool,
    'easyocr_available': bool,
    'processing_stats': {
      'total_processed': int,
      'vehicles_detected': int,
      'plates_detected': int,
      'successful_ocr': int
    }
  }
}
```

## 3) อัลกอริทึมและลำดับขั้นการทำงาน (Algorithm & Procedure)

### 3.1 ขั้นตอนการตรวจสุขภาพ (Single Run)

1. HealthMonitor เรียกใช้เมธอดชุดตรวจสุขภาพ: กล้อง ดิสก์ ระบบ โมเดล EasyOCR ฐานข้อมูล เครือข่าย
2. เก็บผลลัพธ์เป็นระดับ PASS/WARNING/FAIL พร้อมรายละเอียดเชิงลึก
3. บันทึกผลลงฐานข้อมูลตาราง `health_checks`
4. HealthService รวมผลและส่งออกผ่าน REST/WebSocket ให้แดชบอร์ด

### 3.2 เกณฑ์สถานะสำคัญ

- กล้อง: PASS เมื่อ initialized และ streaming, WARNING เมื่อ initialized อย่างเดียว, FAIL หากไม่พร้อม
- ดิสก์: PASS เมื่อว่าง ≥ 1GB, FAIL เมื่อว่าง < 1GB
- ระบบ: WARNING เมื่อ CPU/RAM ≥ 90%
- Detection: 
  - healthy = service_running + thread_alive + models_loaded
  - warning = service_running + thread_alive แต่โมเดลยังไม่พร้อม
  - unhealthy = service ไม่รันหรือเธรดไม่ทำงาน

### 3.3 Auto-Startup Sequence (เชื่อมต่อกับระบบ)

```
Systemd (aicamera_lpr) → Gunicorn (Unix socket) → Nginx (Port 80) → Flask App
  → Camera Manager (Auto-start) → Detection Manager (Auto-start)
  → Health Service ตั้ง thread monitoring อัตโนมัติ เมื่อ Camera + Detection พร้อม
```

ตรรกะ Auto-start ของ Health Service (ย่อ):

```python
def _should_start_monitoring():
    camera_ready = (initialized and streaming)
    detection_ready = service_running and thread_alive and models_loaded
    return camera_ready and detection_ready
```

## 4) API สำหรับนักพัฒนา (Developer API Reference)

### 4.1 REST Endpoints

```http
GET /health/system            # ภาพรวมสถานะระบบปัจจุบัน
GET /health/logs?level=PASS&limit=100  # อ่านประวัติผลตรวจสุขภาพ
GET /health/status            # สถานะ service เฝ้าระวัง

POST /health/monitor/start
Content-Type: application/json
{ "interval": 60 }          # เริ่มตรวจสุขภาพแบบต่อเนื่องทุก 60 วินาที

POST /health/monitor/stop    # หยุดการตรวจสุขภาพแบบต่อเนื่อง

POST /health/check/run       # รันการตรวจสุขภาพ 1 ครั้ง (on-demand)
```

ตัวอย่าง Response (ย่อ) จาก `/health/system`:

```json
{
  "success": true,
  "health": {
    "overall_status": "healthy|warning|unhealthy",
    "components": {
      "camera": {"status": "healthy", "initialized": true, "streaming": true},
      "detection": {
        "status": "healthy",
        "models_loaded": true,
        "easyocr_available": true,
        "service_running": true,
        "thread_alive": true
      },
      "database": {"status": "healthy"},
      "system": {"status": "healthy"}
    }
  },
  "timestamp": "2025-08-09T18:36:57.390144"
}
```

### 4.2 WebSocket Events (ย่อ)

Client → Server
```javascript
socket.emit('health_status_request');
socket.emit('health_logs_request', { level: 'PASS', limit: 100 });
socket.emit('health_monitor_start', { interval: 60 });
socket.emit('health_monitor_stop');
socket.emit('health_check_run');
socket.emit('join_health_room');
socket.emit('leave_health_room');
```

Server → Client
```javascript
socket.on('health_status_update', (data) => { /* ภาพรวมสถานะระบบ */ });
socket.on('health_logs_update', (data) => { /* ข้อมูล log เฮลท์ */ });
socket.on('health_monitor_response', (data) => { /* ผลลัพธ์ควบคุม monitor */ });
socket.on('health_check_response', (data) => { /* ผลรันตรวจสุขภาพ */ });
```

## 5) บันทึกลงฐานข้อมูล (Persistence)

ตาราง `health_checks`

```sql
CREATE TABLE health_checks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  timestamp TEXT NOT NULL,
  component TEXT NOT NULL,
  status TEXT NOT NULL,
  message TEXT,
  details TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 6) เส้นทางข้อมูลและการผนวกรวม Detection (Integration)

- Health ใช้สถานะจริงจาก Detection Manager/Processor (ไม่เดา) เพื่อความแม่นยำ
- เริ่ม Monitoring อัตโนมัติเฉพาะเมื่อกล้องพร้อม (initialized+streaming) และ detection พร้อม (service+thread+models)
- แยกประเภทสถานะ `healthy / warning / unhealthy / unknown` อย่างมีนัยสำคัญ

## 7) การตั้งค่าและตำแหน่งจัดเก็บ (Configuration & Storage)

- โฟลเดอร์จัดเก็บรูป: `/home/camuser/aicamera/edge/captured_images`
- Nginx เสิร์ฟรูปผ่าน path `/captured_images/` (alias ไปยังโฟลเดอร์ข้างต้น)
- แนะนำไม่ตั้ง `IMAGE_SAVE_DIR` แบบ relative ใน `.env.production` เพื่อลดความสับสนใน monorepo

## 8) คำสั่งทดสอบ/วินิจฉัย (Diagnostics)

```bash
# อ่านสถานะระบบ (ผ่าน nginx)
curl -s http://localhost/health/system | python3 -m json.tool

# ดูเฮลท์ล็อกล่าสุด
curl -s "http://localhost/health/logs?level=PASS&limit=50" | python3 -m json.tool

# เริ่ม/หยุด monitoring
curl -s -X POST http://localhost/health/monitor/start -H 'Content-Type: application/json' -d '{"interval":60}'
curl -s -X POST http://localhost/health/monitor/stop
```

## 9) คำอธิบายสถานะ (Quick Reference)

- camera.status: healthy | initialized | not_ready
- detection.status: healthy | warning | unhealthy | unknown
- overall_status: healthy | warning | unhealthy (รวมจากคอมโพเนนต์ทั้งหมด)

---

เอกสารนี้เป็นสรุปแบบย่อเพื่อใช้งานและพัฒนา Health Monitor ในสภาพแวดล้อมผลิตจริง (systemd + gunicorn + nginx) ให้สอดคล้องกับโมดูล Detection และโครงสร้างระบบทั้งหมดของ AI Camera v2.0


