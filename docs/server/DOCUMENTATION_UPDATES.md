# Documentation Updates - System Management Features

## 📋 ภาพรวม

เอกสารนี้สรุปการอัปเดตเอกสารทั้งหมดที่เกี่ยวข้องกับการเพิ่มฟีเจอร์ System Management ใน AI Camera System

## 🔄 ไฟล์ที่อัปเดต

### 1. `api-reference.md`
**การเปลี่ยนแปลง:**
- เพิ่มส่วน **System Management API** ใหม่
- เพิ่ม endpoints สำหรับการจัดการระบบ:
  - `GET /system/status` - ดูสถานะระบบ
  - `POST /system/install` - ติดตั้ง services
  - `POST /system/start` - เริ่มต้น services
  - `POST /system/stop` - หยุด services
  - `POST /system/restart` - รีสตาร์ท services
  - `POST /system/build` - Build และ deploy

**ตัวอย่าง Response:**
```json
{
  "success": true,
  "status": "AI Camera Services Status\n==================================\naicamera-backend: ACTIVE\naicamera-frontend: ACTIVE\n...",
  "timestamp": "2025-08-26T08:23:50.830Z"
}
```

### 2. `developer-handbook.md`
**การเปลี่ยนแปลง:**
- เพิ่มความต้องการของระบบ: systemd สำหรับ production deployment
- เพิ่มส่วน **การจัดการระบบด้วย Systemd Services** ใหม่
- ครอบคลุม:
  - การติดตั้งและใช้งาน services
  - คำสั่งควบคุมระบบ
  - การแก้ไขปัญหา (Port Conflicts, Service Failures, Group Permission Issues)
  - การ Monitor และ Logs
  - การตั้งค่า Environment Variables
  - การตั้งค่า Auto-start
  - การ Backup และ Restore

### 3. `README.md`
**การเปลี่ยนแปลง:**
- เพิ่มส่วน **การจัดการระบบ (System Management)** ใหม่
- ครอบคลุม:
  - ภาพรวมของ systemd services
  - การติดตั้งและใช้งาน
  - คำสั่งควบคุมระบบ
  - การแก้ไขปัญหา Port Conflicts
  - การ Monitor และ Logs
- เพิ่ม System Management Issues ในส่วนการแก้ไขปัญหา

### 4. `systemd_service.md`
**การเปลี่ยนแปลง:**
- ปรับปรุงโครงสร้างเอกสารให้เป็นระบบมากขึ้น
- เพิ่มการใช้งาน Control Script
- อัปเดต Service Configuration ให้ตรงกับปัจจุบัน
- เพิ่มการแก้ไขปัญหาแบบครบถ้วน
- เพิ่มการ Monitor และ Logs
- เพิ่มการ Backup และ Restore
- เพิ่มข้อดีของการใช้ Systemd Services

## 🆕 ฟีเจอร์ใหม่ที่เพิ่ม

### 1. System Management API
- REST API สำหรับการจัดการระบบ
- การควบคุม services ผ่าน HTTP endpoints
- การ monitor สถานะระบบแบบ real-time

### 2. Control Script (`aicamera-control.sh`)
- สคริปต์ควบคุมระบบแบบครบถ้วน
- คำสั่ง: install, uninstall, start, stop, restart, status, logs, build, deploy
- การจัดการ services แบบอัตโนมัติ

### 3. Systemd Services
- `aicamera-backend.service`: บริการ NestJS backend
- `aicamera-frontend.service`: บริการ Vite preview frontend
- การจัดการแบบ user services (ไม่ต้องใช้ sudo)

### 4. Web-based Control Interface
- Vue.js component สำหรับการควบคุมระบบ
- Real-time status monitoring
- Service control buttons
- Activity logs display

## 🔧 การแก้ไขปัญหาที่ครอบคลุม

### 1. Port Conflicts (EADDRINUSE)
- การตรวจสอบ port usage
- การ kill processes ที่ใช้ port
- การ restart services

### 2. Service Failures
- การตรวจสอบสถานะ services
- การดู logs
- การ reset failed services

### 3. Group Permission Issues (status 216/GROUP)
- การแก้ไข group permission errors
- การลบและติดตั้ง services ใหม่

## 📊 การ Monitor และ Logs

### 1. Real-time Logs
- `journalctl --user -u aicamera-backend -f`
- `journalctl --user -u aicamera-frontend -f`

### 2. Service Status
- `systemctl --user status aicamera-backend`
- `systemctl --user status aicamera-frontend`

### 3. Control Script Logs
- `./scripts/aicamera-control.sh logs aicamera-backend`
- `./scripts/aicamera-control.sh logs aicamera-frontend`

## 🚀 การใช้งาน

### การติดตั้งครั้งแรก
```bash
cd /home/devuser/aicamera
./scripts/aicamera-control.sh install
./scripts/aicamera-control.sh start
./scripts/aicamera-control.sh status
```

### การใช้งานประจำวัน
```bash
# ตรวจสอบสถานะ
./scripts/aicamera-control.sh status

# รีสตาร์ท services
./scripts/aicamera-control.sh restart

# Build และ deploy
./scripts/aicamera-control.sh deploy

# ดู logs
./scripts/aicamera-control.sh logs aicamera-backend
```

## 🎯 ประโยชน์ที่ได้รับ

1. **ความเสถียร**: Services restart อัตโนมัติเมื่อเกิดปัญหา
2. **การจัดการที่ง่าย**: ใช้ control script เดียวสำหรับทุกการจัดการ
3. **การ Monitor**: ง่ายต่อการ monitor และจัดการ
4. **การ Deploy**: ง่ายต่อการ deploy และอัปเดต
5. **การแก้ไขปัญหา**: มีคำแนะนำการแก้ไขปัญหาที่ครบถ้วน
6. **การ Backup**: สามารถ backup และ restore ได้ง่าย

## 📚 เอกสารที่เกี่ยวข้อง

- [API Reference](./api-reference.md) - เอกสาร API endpoints
- [Developer Handbook](./developer-handbook.md) - คู่มือนักพัฒนา
- [Systemd Service](./systemd_service.md) - คู่มือการจัดการ systemd services
- [README](./README.md) - คู่มือการใช้งานทั่วไป

---

*อัปเดตเมื่อ: 2025-08-26*
