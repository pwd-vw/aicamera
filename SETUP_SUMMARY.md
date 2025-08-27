# AI Camera CI/CD Setup Summary

## 🎯 เป้าหมาย

ตั้งค่าระบบ CI/CD สำหรับการ deploy โปรเจกต์ AI Camera ไปยัง:
- **LPR Server**: `lprserver.tail605477.ts.net` (Node.js/NestJS backend)
- **Edge Devices**: `aicamera1.tail605477.ts.net`, `aicamera2.tail605477.ts.net`, `aicamera3.tail605477.ts.net` (Python/Flask edge applications)

## 📁 ไฟล์ที่สร้างขึ้น

### 1. GitHub Actions Workflow
- `.github/workflows/deploy.yml` - Main deployment workflow

### 2. Setup Scripts
- `scripts/setup-ssh-keys.sh` - SSH key setup และทดสอบการเชื่อมต่อ
- `scripts/setup-github-secrets.sh` - GitHub repository variables และ secrets
- `scripts/setup-github-runner.sh` - Self-hosted runner setup (Linux/macOS)
- `scripts/setup-github-runner.ps1` - Self-hosted runner setup (Windows PowerShell)
- `scripts/setup-github-runner.bat` - Self-hosted runner setup (Windows Batch)

### 3. Documentation
- `README_CI_CD.md` - Quick start guide
- `docs/project/CI_CD_SETUP.md` - Detailed setup guide
- `WINDOWS_SETUP_GUIDE.md` - Windows-specific setup guide
- `SETUP_SUMMARY.md` - This file

## 🚀 ขั้นตอนการติดตั้ง

### Step 1: ติดตั้ง Dependencies
```bash
# ติดตั้ง GitHub CLI
sudo apt install gh  # Ubuntu/Debian
# หรือ
brew install gh      # macOS

# Authenticate with GitHub
gh auth login
```

### Step 2: ตั้งค่า SSH Keys
```bash
chmod +x scripts/setup-ssh-keys.sh
./scripts/setup-ssh-keys.sh
```

### Step 3: ตั้งค่า GitHub Repository
```bash
chmod +x scripts/setup-github-secrets.sh
./scripts/setup-github-secrets.sh
```

### Step 4: ตั้งค่า Self-Hosted Runner (Optional)

#### สำหรับ Linux/macOS:
```bash
chmod +x scripts/setup-github-runner.sh
./scripts/setup-github-runner.sh
```

#### สำหรับ Windows:
```powershell
# PowerShell Script (แนะนำ)
.\scripts\setup-github-runner.ps1

# หรือ Batch Script
.\scripts\setup-github-runner.bat
```

## 🔧 การใช้งาน

### Automatic Deployment
เมื่อ push ไปยัง branch `main` และมีการเปลี่ยนแปลงใน:
- `server/**`
- `edge/**`
- `.github/workflows/deploy.yml`

### Manual Deployment
```bash
# ใช้สคริปต์ที่สร้างขึ้น
deploy-manual

# หรือใช้ GitHub CLI
gh workflow run deploy.yml --field deploy_server=true --field deploy_edge=true
```

### ตรวจสอบสถานะ
```bash
# ตรวจสอบสถานะ deployment
check-deployment

# ตรวจสอบ SSH connections
test-ssh-connections

# ตรวจสอบ deployment บน servers
deploy-test
```

## 🔐 Security Configuration

### SSH Keys
- สร้าง SSH key เฉพาะสำหรับ CI/CD
- ติดตั้ง public key บน target servers
- เพิ่ม private key ใน GitHub Secrets

### GitHub Secrets
- `SSH_PRIVATE_KEY` - SSH private key สำหรับ CI/CD
- `SERVER_USER` - Username สำหรับ LPR server (lpruser)
- `EDGE_USER` - Username สำหรับ edge devices (camuser)

### GitHub Variables
- `ENABLE_SERVER_DEPLOYMENT` - เปิด/ปิดการ deploy ไปยัง server
- `ENABLE_EDGE_DEPLOYMENT` - เปิด/ปิดการ deploy ไปยัง edge devices

## 📊 Monitoring

### Health Checks
```bash
# Server API
curl http://lprserver.tail605477.ts.net:3000/health

# Edge Devices
curl http://aicamera1.tail605477.ts.net/health
curl http://aicamera2.tail605477.ts.net/health
curl http://aicamera3.tail605477.ts.net/health
```

### Service Status
```bash
# Server
ssh lprserver "sudo systemctl status aicamera_server.service"

# Edge Devices
ssh aicamera1 "sudo systemctl status aicamera_lpr.service"
ssh aicamera2 "sudo systemctl status aicamera_lpr.service"
ssh aicamera3 "sudo systemctl status aicamera_lpr.service"
```

## 🔄 Deployment Process

### Server Deployment
1. สร้าง backup ของ deployment ปัจจุบัน
2. Pull latest changes จาก Git
3. อัพเดท dependencies และ build
4. อัพเดท database schema (Prisma)
5. รีสตาร์ท systemd service
6. รีสตาร์ท nginx
7. ทดสอบ health check
8. Rollback ถ้าเกิดปัญหา

### Edge Deployment
1. สร้าง backup ของ deployment ปัจจุบัน
2. Pull latest changes จาก Git
3. อัพเดท Python dependencies
4. รีสตาร์ท systemd service
5. รีสตาร์ท nginx
6. ทดสอบ health check
7. Rollback ถ้าเกิดปัญหา

## 🛠️ Management Commands

### SSH Management
```bash
# Quick connect
ssh lprserver
ssh aicamera1
ssh aicamera2
ssh aicamera3

# Test connections
test-ssh-connections
```

### Deployment Management
```bash
# Manual deploy
deploy-manual

# Check status
check-deployment

# Test deployment
deploy-test
```

### Runner Management (if using self-hosted runner)
```bash
# Status
github-runner-status

# Restart
github-runner-restart

# Logs
github-runner-logs

# Update
github-runner-update <new_token>
```

## 🔧 Troubleshooting

### ปัญหาที่พบบ่อย

1. **SSH Connection Failed**
   - ตรวจสอบ SSH key ใน GitHub secrets
   - ตรวจสอบ public key บน target servers
   - ตรวจสอบ network connectivity

2. **Service Failed to Start**
   - ตรวจสอบ logs: `sudo journalctl -u service_name -f`
   - ตรวจสอบ dependencies
   - ตรวจสอบ file permissions

3. **Health Check Failed**
   - ตรวจสอบ service status
   - ตรวจสอบ port configuration
   - ตรวจสอบ firewall rules

4. **Build Failed**
   - ตรวจสอบ Node.js และ Python versions
   - ตรวจสอบ dependencies
   - ตรวจสอบ build logs

### Rollback Manual
```bash
# บน Server
ssh lprserver
cd /home/lpruser/aicamera
sudo systemctl stop aicamera_server.service
sudo systemctl stop nginx
tar -xzf /home/lpruser/aicamera_backups/server_backup_YYYYMMDD_HHMMSS.tar.gz .
sudo systemctl start aicamera_server.service
sudo systemctl start nginx

# บน Edge
ssh aicamera1
cd /home/camuser/aicamera
sudo systemctl stop aicamera_lpr.service
sudo systemctl stop nginx
tar -xzf /home/camuser/aicamera_backups/edge_backup_DEVICE_YYYYMMDD_HHMMSS.tar.gz .
sudo systemctl start aicamera_lpr.service
sudo systemctl start nginx
```

## 📋 Checklist

### Pre-Setup
- [ ] ติดตั้ง GitHub CLI
- [ ] Authenticate with GitHub
- [ ] ตรวจสอบ network connectivity ไปยัง target servers

### SSH Setup
- [ ] รัน `setup-ssh-keys.sh`
- [ ] ตรวจสอบ SSH connections
- [ ] เพิ่ม SSH private key ใน GitHub Secrets

### GitHub Repository Setup
- [ ] รัน `setup-github-secrets.sh`
- [ ] ตรวจสอบ variables และ secrets
- [ ] ทดสอบ workflow

### Self-Hosted Runner (Optional)
- [ ] รัน `setup-github-runner.sh`
- [ ] ตรวจสอบ runner status
- [ ] ทดสอบ runner functionality

### Post-Setup
- [ ] ทดสอบ automatic deployment
- [ ] ทดสอบ manual deployment
- [ ] ตรวจสอบ health checks
- [ ] ทดสอบ rollback functionality

## 🌐 URLs ที่สำคัญ

- **Repository**: https://github.com/your-username/your-repo
- **Actions**: https://github.com/your-username/your-repo/actions
- **Settings**: https://github.com/your-username/your-repo/settings/secrets/actions

## 📚 เอกสารเพิ่มเติม

- [Quick Start Guide](README_CI_CD.md)
- [Detailed Setup Guide](docs/project/CI_CD_SETUP.md)
- [Architecture Documentation](docs/project/README.md)
- [API Reference](docs/edge/api-reference.md)

## 🆘 การขอความช่วยเหลือ

1. ตรวจสอบ GitHub Actions logs
2. ตรวจสอบ system logs บน target servers
3. ตรวจสอบ network connectivity
4. ติดต่อทีม DevOps หรือ System Administrator

---

**หมายเหตุ**: ระบบนี้ใช้ Tailscale VPN สำหรับการเชื่อมต่อระหว่าง servers และ edge devices ตรวจสอบให้แน่ใจว่า Tailscale ทำงานปกติก่อนการ deploy
