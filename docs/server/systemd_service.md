# Systemd Service Management

## ภาพรวม

ระบบ AI Camera ใช้ systemd services สำหรับการจัดการที่เสถียรและอัตโนมัติ โดยมีการแยก build process ระหว่าง Backend และ Frontend เพื่อประสิทธิภาพและความยืดหยุ่นในการพัฒนา

## 🚀 การติดตั้งและใช้งาน

### การเตรียมระบบ

#### ติดตั้งและ build ครั้งแรก
```bash
cd /home/devuser/aicamera
npm ci && cd server && npm ci && cd frontend && npm ci
cd /home/devuser/aicamera && npm run build
```

### การติดตั้ง Services

#### ใช้ Control Script (แนะนำ)
```bash
# ติดตั้ง services
./scripts/aicamera-control.sh install

# เริ่มต้น services
./scripts/aicamera-control.sh start

# ตรวจสอบสถานะ
./scripts/aicamera-control.sh status
```

#### การจัดการ Services
```bash
# เริ่มต้น services
./scripts/aicamera-control.sh start

# หยุด services
./scripts/aicamera-control.sh stop

# รีสตาร์ท services
./scripts/aicamera-control.sh restart

# Build และ deploy
./scripts/aicamera-control.sh deploy

# ดู logs
./scripts/aicamera-control.sh logs aicamera-backend
./scripts/aicamera-control.sh logs aicamera-frontend
```

## 📋 Service Configuration

### 1. Backend Service (aicamera-backend.service)

```ini
[Unit]
Description=AI Camera Server Backend (NestJS)
After=network.target
Wants=network.target

[Service]
Type=simple
WorkingDirectory=/home/devuser/aicamera/server
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=PATH=/usr/bin:/usr/local/bin:/home/devuser/.npm-global/bin
ExecStart=/usr/bin/node /home/devuser/aicamera/server/dist/src/main.js
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aicamera-backend

[Install]
WantedBy=default.target
```

### 2. Frontend Service (aicamera-frontend.service)

```ini
[Unit]
Description=AI Camera Server Frontend (Vite Preview)
After=network.target
Wants=network.target

[Service]
Type=simple
WorkingDirectory=/home/devuser/aicamera/server/frontend
Environment=HOST=0.0.0.0
Environment=PORT=5173
Environment=PATH=/usr/bin:/usr/local/bin:/home/devuser/.npm-global/bin
ExecStart=/usr/bin/npm run preview -- --host 0.0.0.0 --port 5173
Restart=always
RestartSec=10
StartLimitInterval=60
StartLimitBurst=3
# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aicamera-frontend

[Install]
WantedBy=default.target
```

## 🔧 การจัดการแบบ Manual

### การใช้ systemctl โดยตรง

```bash
# โหลด unit files
systemctl --user daemon-reload

# เปิดให้เริ่มอัตโนมัติ
systemctl --user enable aicamera-backend
systemctl --user enable aicamera-frontend

# สตาร์ททันที
systemctl --user start aicamera-backend
systemctl --user start aicamera-frontend

# ดูสถานะ
systemctl --user status aicamera-backend
systemctl --user status aicamera-frontend

# tail log
journalctl --user -u aicamera-backend -f
journalctl --user -u aicamera-frontend -f
```

### การอัปเดตโค้ด/รีดีพลอย

หลัง pull หรือแก้ไขโค้ด:
```bash 
cd /home/devuser/aicamera
npm run build    # build ทั้ง backend+frontend
./scripts/aicamera-control.sh restart
```

หรือใช้ deploy command:
```bash
./scripts/aicamera-control.sh deploy
```

## 🧪 การทดสอบ

### ทดสอบ Backend
```bash
curl http://localhost:3000/communication/status
curl http://localhost:3000/system/status
```

### ทดสอบ Frontend
เปิด http://localhost:5173 ในเบราว์เซอร์

## 🆘 การแก้ไขปัญหา

### Port Conflicts (EADDRINUSE)

หากเกิด port conflict:
```bash
# ตรวจสอบ port ที่ใช้งาน
netstat -tulpn | grep :3000
netstat -tulpn | grep :5173

# หยุด process ที่ใช้ port
kill -9 <PID>

# รีสตาร์ท services
./scripts/aicamera-control.sh restart
```

### Service Failures

หาก service ไม่สามารถเริ่มต้นได้:
```bash
# ตรวจสอบสถานะ
./scripts/aicamera-control.sh status

# ดู logs
./scripts/aicamera-control.sh logs aicamera-backend

# รีเซ็ต failed services
systemctl --user reset-failed aicamera-backend.service
systemctl --user reset-failed aicamera-frontend.service

# รีสตาร์ท services
./scripts/aicamera-control.sh restart
```

### Group Permission Issues (status 216/GROUP)

หากเกิด group permission error:
```bash
# ตรวจสอบ groups ของ user
groups devuser

# ลบและติดตั้ง services ใหม่
./scripts/aicamera-control.sh uninstall
./scripts/aicamera-control.sh install
```

## 📊 การ Monitor และ Logs

### ดู Logs แบบ Real-time
```bash
# ดู logs ของ backend
journalctl --user -u aicamera-backend -f

# ดู logs ของ frontend
journalctl --user -u aicamera-frontend -f

# ดู logs ทั้งหมด
journalctl --user -f -u aicamera-backend -u aicamera-frontend
```

### ตรวจสอบสถานะ Services
```bash
# ตรวจสอบสถานะ systemd
systemctl --user status aicamera-backend
systemctl --user status aicamera-frontend

# ตรวจสอบ enabled services
systemctl --user list-unit-files | grep aicamera
```

## 🔄 การตั้งค่า Auto-start

Services จะเริ่มต้นอัตโนมัติเมื่อระบบ boot:

```bash
# ตรวจสอบ auto-start
systemctl --user is-enabled aicamera-backend
systemctl --user is-enabled aicamera-frontend

# เปิด/ปิด auto-start
systemctl --user enable aicamera-backend
systemctl --user disable aicamera-backend
```

## 📦 การ Backup และ Restore

### Backup Services
```bash
# Backup service files
cp ~/.config/systemd/user/aicamera-*.service /backup/

# Backup control script
cp scripts/aicamera-control.sh /backup/
```

### Restore Services
```bash
# Restore service files
cp /backup/aicamera-*.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Restart services
./scripts/aicamera-control.sh restart
```

## 🎯 ข้อดีของการใช้ Systemd Services

1. **ความเสถียร**: Services จะ restart อัตโนมัติเมื่อเกิดปัญหา
2. **การจัดการ Logs**: ใช้ journalctl สำหรับการจัดการ logs
3. **Auto-start**: Services เริ่มต้นอัตโนมัติเมื่อระบบ boot
4. **การ Monitor**: ง่ายต่อการ monitor และจัดการ
5. **การ Deploy**: ง่ายต่อการ deploy และอัปเดต
6. **การ Backup**: สามารถ backup และ restore ได้ง่าย