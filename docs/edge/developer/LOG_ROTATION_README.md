# การกำหนดค่าหมุนเวียนไฟล์ Log ภายใน (AI Camera Internal Log Rotation)

## ภาพรวม (Overview)

เอกสารนี้อธิบายการตั้งค่าการหมุนเวียนไฟล์ log (log rotation) ภายในของระบบ AI Camera โดยใช้กลไกการหมุนเวียนของ Python เอง ระบบจะหมุนไฟล์ log อัตโนมัติทุกวันเวลา 00:01 และเก็บสำเนาสำรองไว้ 3 วัน เพื่อลดความเสี่ยงพื้นที่ดิสก์เต็ม นอกจากนี้ ชั้นการบันทึก log ของแอปยังลด noise ด้วยการจำกัดอัตรา (rate‑limit) และบันทึกเฉพาะเมื่อสถานะมีการเปลี่ยนแปลง (state‑change) เพื่อให้ระบบทำงานได้เบาเครื่อง

## ไฟล์ Log ที่ดูแล (Log Files Managed)

ไฟล์ต่อไปนี้ถูกหมุนเวียนโดยระบบบันทึก log ภายในของ Python:

1. **aicamera.log** - Log หลักของแอปพลิเคชัน (ดู `logging_config.py`)
2. **gunicorn_access.log** - Log การเข้าถึงของเว็บเซิร์ฟเวอร์ Gunicorn (ดู `setup_gunicorn_log_rotation.py`)
3. **gunicorn_error.log** - Log ข้อผิดพลาดของ Gunicorn (ดู `setup_gunicorn_log_rotation.py`)
4. **hailort.log** - Log ของ HailoRT runtime (ดู `hailort_logging.py`)

## รายละเอียดการกำหนดค่า (Configuration Details)

### ตารางการหมุนเวียน (Rotation Schedule)
- **ความถี่**: ทุกวันเวลา 00:01 (เที่ยงคืน + 1 นาที)
- **ระยะเก็บสำรอง**: 3 วัน
- **วิธีการ**: Python `TimedRotatingFileHandler`
- **ที่เก็บสำรอง**: ไดเรกทอรีเดียวกัน ต่อท้ายด้วย `.1`, `.2`, `.3`
- **ลด Noise**: ใช้ `RateLimitedLogger` และสรุปแบบเป็นช่วง ๆ (periodic summaries)

### ตำแหน่งไฟล์การตั้งค่าภายใน (Internal Configuration)
- **Main Logs**: `edge/src/core/utils/logging_config.py`
- **Gunicorn Logs**: `edge/scripts/setup_gunicorn_log_rotation.py`
- **HailoRT Logs**: `edge/config/hailort_logging.py`

### การเพิ่มประสิทธิภาพการ Log ของแอป (Application Log Optimizations)
- จำกัดอัตราการบันทึกข้อความซ้ำ (rate‑limited info/warning/error)
- บันทึกเฉพาะเมื่อสถานะเปลี่ยน (state‑change‑only)
- รายงานสถิติเป็นระยะ (เช่น ทุก 30 วินาที) แทนการบันทึกทุก iteration

## คำสั่งใช้งาน (Manual Commands)

### ทดสอบระบบบันทึก Log หลัก (Test Logging System)
```bash
cd /home/camuser/aicamera
python3 -c "
import sys
sys.path.insert(0, '/home/camuser/aicamera')
from edge.src.core.utils.logging_config import setup_logging
logger = setup_logging('INFO')
logger.info('Testing internal log rotation system')
"
```

### ทดสอบ HailoRT Logging
```bash
cd /home/camuser/aicamera
python3 -c "
import sys
sys.path.insert(0, '/home/camuser/aicamera')
from edge.config.hailort_logging import configure_hailort_logging
configure_hailort_logging()
"
```

### ทดสอบ Gunicorn Log Rotation
```bash
cd /home/camuser/aicamera/edge
python3 scripts/setup_gunicorn_log_rotation.py
```

## โครงสร้างไฟล์ (File Structure)

```
/home/camuser/aicamera/edge/logs/
├── aicamera.log                    # Log หลักปัจจุบัน
├── aicamera.log.1                 # ของเมื่อวาน
├── aicamera.log.2                 # ย้อนหลัง 2 วัน
├── aicamera.log.3                 # ย้อนหลัง 3 วัน
├── gunicorn_access.log            # Access log ปัจจุบัน
├── gunicorn_access.log.1          # Access log ของเมื่อวาน
├── gunicorn_error.log             # Error log ปัจจุบัน
├── gunicorn_error.log.1           # Error log ของเมื่อวาน
├── hailort.log                    # HailoRT log ปัจจุบัน
├── hailort.log.1                  # HailoRT log ของเมื่อวาน
└── archive/                       # ไดเรกทอรีเก็บถาวร (legacy)
```

## การติดตาม (Monitoring)

### ตรวจสอบขนาดไฟล์ Log
```bash
ls -lh /home/camuser/aicamera/edge/logs/*.log
```

### ดูบรรทัดล่าสุดของ Log
```bash
tail -f /home/camuser/aicamera/edge/logs/aicamera.log
tail -f /home/camuser/aicamera/edge/logs/gunicorn_error.log
```

### ตรวจสอบสถานะการหมุนเวียน (Rotation Status)
```bash
# ตรวจสอบว่ามีเธรด/โปรเซสเกี่ยวกับ rotation ทำงานหรือไม่
ps aux | grep -i rotation
```

### ประเมินการลด Noise ของ Log
```bash
grep -c "\[CAMERA\]" /home/camuser/aicamera/edge/logs/aicamera.log
grep -c "summary:" /home/camuser/aicamera/edge/logs/aicamera.log
```

## การแก้ปัญหา (Troubleshooting)

### หมุนเวียน Log ไม่ทำงาน
1. ตรวจสอบว่ามีการ initialize ระบบ logging หรือไม่: ทดสอบด้วยคำสั่งด้านบน
2. ตรวจสิทธิ์ไฟล์: `ls -la /home/camuser/aicamera/edge/logs/`
3. ตรวจสอบการตั้งค่า Python logging: ไฟล์ `logging_config.py` ถูก import หรือไม่

### ไฟล์ Log ใหญ่มาก
1. รีสตาร์ตแอปเพื่อกระตุ้นการหมุนเวียน
2. ลบไฟล์สำรองเก่าแบบแมนนวล: `rm /home/camuser/aicamera/edge/logs/*.log.*`

### ปัญหาสิทธิ์ (Permission Issues)
```bash
sudo chown -R camuser:camuser /home/camuser/aicamera/edge/logs/
sudo chmod 644 /home/camuser/aicamera/edge/logs/*.log
```

## ไฟล์การตั้งค่า (Configuration Files)

### Main Logging Config (`edge/src/core/utils/logging_config.py`)
```python
file_handler = TimedRotatingFileHandler(
    filename=str(log_file),
    when='midnight',        # หมุนเวียนตอนเที่ยงคืน
    interval=1,             # รายวัน
    backupCount=3,          # เก็บสำรอง 3 ชุด
    encoding='utf-8',
    atTime=datetime.strptime('00:01', '%H:%M').time()  # เวลา 00:01
)
```

### HailoRT Logging Config (`edge/config/hailort_logging.py`)
```python
# ตั้ง environment variables ให้ HailoRT เขียน log ไปยังโฟลเดอร์ logs
os.environ["HAILORT_LOGGER_PATH"] = str(logs_dir)
os.environ["HAILORT_LOG_FILE"] = str(log_file)
```

### Gunicorn Logging Config (`edge/scripts/setup_gunicorn_log_rotation.py`)
```python
# ตั้ง TimedRotatingFileHandler สำหรับ gunicorn logs
access_handler = TimedRotatingFileHandler(
    filename=str(access_log_file),
    when='midnight',
    interval=1,
    backupCount=3,
    atTime=datetime.strptime('00:01', '%H:%M').time()
)
```

## การผสานรวมกับแอปพลิเคชัน (Integration with Application)

การหมุนเวียน log ผสานรวมกับแอปดังนี้:

1. **Python Logging**: ใช้ `TimedRotatingFileHandler` หมุนเวียนรายวันเวลา 00:01
2. **Background Threads**: เธรด daemon จัดการการหมุนเวียน/ล้างไฟล์เก่า
3. **HailoRT Logging**: ตั้งค่าให้เขียนลงโฟลเดอร์ logs พร้อมรองรับการหมุนเวียน
4. **Gunicorn Logging**: ตัวจัดการหมุนเวียนแยกต่างหากสำหรับเว็บเซิร์ฟเวอร์

## การบำรุงรักษา (Maintenance)

### งานบำรุงรักษาประจำ
- เฝ้าระวังการใช้พื้นที่ดิสก์
- ตรวจขนาดไฟล์ log รายสัปดาห์
- ตรวจสอบการหมุนเวียนรายเดือน

### การล้างฉุกเฉิน (Emergency Cleanup)
หากพื้นที่ดิสก์ใกล้เต็ม:
```bash
# ลบไฟล์หมุนเวียนทั้งหมด
rm /home/camuser/aicamera/edge/logs/*.log.*
rm -rf /home/camuser/aicamera/edge/logs/archive/
```

## ประวัติรุ่น (Version History)

- **v2.0** (2025-09-12): ระบบหมุนเวียน log ภายใน
  - หมุนเวียนรายวัน 00:01 ด้วย TimedRotatingFileHandler
  - เก็บสำรอง 3 วัน พร้อมล้างอัตโนมัติ
  - เธรดพื้นหลังจัดการหมุนเวียน
  - ผสานกับ log ทุกประเภท (aicamera, gunicorn, hailort)

- **v1.0** (2025-09-12): ระบบ logrotate ภายนอก (ยกเลิกใช้)
  - หมุนเวียนทุกวัน 02:00 ด้วยระบบ logrotate
  - เปิดการบีบอัดไฟล์
  - ผสานกับ Gunicorn และ HailoRT logging
