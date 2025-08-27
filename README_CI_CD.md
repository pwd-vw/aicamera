# AI Camera CI/CD Setup Guide

## ภาพรวม

ระบบ CI/CD นี้ถูกออกแบบสำหรับการ deploy โปรเจกต์ AI Camera ไปยัง:
- **LPR Server**: `lprserver.tail605477.ts.net` (Node.js/NestJS backend)
- **Edge Devices**: `aicamera1.tail605477.ts.net`, `aicamera2.tail605477.ts.net`, `aicamera3.tail605477.ts.net` (Python/Flask edge applications)

## การติดตั้งอย่างรวดเร็ว

### 1. ติดตั้ง Dependencies

```bash
# ติดตั้ง GitHub CLI
sudo apt install gh  # Ubuntu/Debian
# หรือ
brew install gh      # macOS

# Authenticate with GitHub
gh auth login
```

### 2. ตั้งค่า SSH Keys

```bash
# ให้สิทธิ์การ execute
chmod +x scripts/setup-ssh-keys.sh

# รันสคริปต์ตั้งค่า SSH keys
./scripts/setup-ssh-keys.sh
```

### 3. ตั้งค่า GitHub Repository

```bash
# ให้สิทธิ์การ execute
chmod +x scripts/setup-github-secrets.sh

# รันสคริปต์ตั้งค่า repository
./scripts/setup-github-secrets.sh
```

### 4. ตั้งค่า Self-Hosted Runner (Optional)

#### สำหรับ Linux/macOS:
```bash
# ให้สิทธิ์การ execute
chmod +x scripts/setup-github-runner.sh

# รันสคริปต์ตั้งค่า runner
./scripts/setup-github-runner.sh
```

#### สำหรับ Windows:
```powershell
# รันสคริปต์ PowerShell (แนะนำ)
.\scripts\setup-github-runner.ps1

# หรือรันสคริปต์ Batch
.\scripts\setup-github-runner.bat
```

## โครงสร้างไฟล์

```
├── .github/
│   └── workflows/
│       ├── deploy.yml              # Main deployment workflow
│       ├── edge-deploy.yml         # Legacy edge deployment
│       └── version.yml             # Version management
├── scripts/
│   ├── setup-ssh-keys.sh          # SSH key setup
│   ├── setup-github-secrets.sh    # GitHub repository setup
│   ├── setup-github-runner.sh     # Self-hosted runner setup (Linux/macOS)
│   ├── setup-github-runner.ps1    # Self-hosted runner setup (Windows PowerShell)
│   └── setup-github-runner.bat    # Self-hosted runner setup (Windows Batch)
├── docs/project/
│   └── CI_CD_SETUP.md             # Detailed setup guide
└── README_CI_CD.md                # This file
```

## การใช้งาน

### Automatic Deployment

เมื่อ push ไปยัง branch `main` และมีการเปลี่ยนแปลงใน:
- `server/**`
- `edge/**`
- `.github/workflows/deploy.yml`

ระบบจะ:
1. รัน tests
2. Build โปรเจกต์
3. Deploy ไปยัง server และ edge devices (ถ้าเปิดใช้งาน)

### Manual Deployment

```bash
# Deploy ไปยังทุก environment
deploy-manual

# หรือใช้ GitHub CLI โดยตรง
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

## การ Monitor

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
# บน LPR Server
ssh lprserver "sudo systemctl status aicamera_server.service"

# บน Edge Devices
ssh aicamera1 "sudo systemctl status aicamera_lpr.service"
ssh aicamera2 "sudo systemctl status aicamera_lpr.service"
ssh aicamera3 "sudo systemctl status aicamera_lpr.service"
```

### Logs

```bash
# Server logs
ssh lprserver "sudo journalctl -u aicamera_server.service -f"

# Edge logs
ssh aicamera1 "sudo journalctl -u aicamera_lpr.service -f"
```

## การ Troubleshooting

### ปัญหาที่พบบ่อย

1. **SSH Connection Failed**
   ```bash
   # ตรวจสอบ SSH key
   test-ssh-connections
   
   # ตรวจสอบ SSH config
   cat ~/.ssh/config
   ```

2. **Service Failed to Start**
   ```bash
   # ตรวจสอบ logs
   ssh lprserver "sudo journalctl -u aicamera_server.service -f"
   
   # ตรวจสอบ dependencies
   ssh lprserver "cd /home/lpruser/aicamera/server && npm install"
   ```

3. **Health Check Failed**
   ```bash
   # ตรวจสอบ service status
   ssh lprserver "sudo systemctl status aicamera_server.service"
   
   # ตรวจสอบ port
   ssh lprserver "sudo netstat -tlnp | grep :3000"
   ```

4. **Build Failed**
   ```bash
   # ตรวจสอบ Node.js version
   node --version
   
   # ตรวจสอบ Python version
   python3 --version
   ```

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

## Security

### SSH Key Management

- ใช้ SSH key เฉพาะสำหรับ CI/CD
- จำกัดสิทธิ์การเข้าถึง key
- หมุนเวียน key เป็นประจำ

### GitHub Token Security

- ใช้ Fine-grained token เมื่อเป็นไปได้
- จำกัดสิทธิ์ให้เฉพาะที่จำเป็น
- หมุนเวียน token เป็นประจำ

### Network Security

- ใช้ Tailscale VPN สำหรับการเชื่อมต่อ
- จำกัดการเข้าถึง SSH เฉพาะ IP ที่อนุญาต
- ใช้ firewall rules ที่เหมาะสม

## การอัพเดท

### อัพเดท Workflow

```bash
# Pull latest changes
git pull origin main

# ตรวจสอบ workflow syntax
yamllint .github/workflows/deploy.yml
```

### อัพเดท Runner

```bash
# อัพเดท runner version
github-runner-update <new_token>
```

### อัพเดท Dependencies

```bash
# Server dependencies
cd server && npm update

# Edge dependencies
cd edge && pip install -r requirements.txt --upgrade
```

## คำสั่งที่มีประโยชน์

### การจัดการ Runner

#### สำหรับ Linux/macOS:
```bash
# ดูสถานะ
github-runner-status

# รีสตาร์ท
github-runner-restart

# ดู logs
github-runner-logs
```

#### สำหรับ Windows:
```powershell
# ดูสถานะ
github-runner-status.ps1

# รีสตาร์ท
github-runner-restart.ps1

# ดู logs
github-runner-logs.ps1
```

```batch
# หรือใช้ Batch scripts
github-runner-status.bat
github-runner-restart.bat
github-runner-logs.bat
```

### การจัดการ Deployment

```bash
# Deploy manual
deploy-manual

# ตรวจสอบสถานะ
check-deployment

# ตรวจสอบ connections
test-ssh-connections
```

### การจัดการ SSH

```bash
# Quick connect
ssh lprserver
ssh aicamera1
ssh aicamera2
ssh aicamera3

# Test connections
test-ssh-connections
```

## URLs ที่สำคัญ

- **Repository**: https://github.com/your-username/your-repo
- **Actions**: https://github.com/your-username/your-repo/actions
- **Settings**: https://github.com/your-username/your-repo/settings/secrets/actions

## การขอความช่วยเหลือ

1. ตรวจสอบ GitHub Actions logs
2. ตรวจสอบ system logs บน target servers
3. ตรวจสอบ network connectivity
4. ติดต่อทีม DevOps หรือ System Administrator

## เอกสารเพิ่มเติม

- [Detailed CI/CD Setup Guide](docs/project/CI_CD_SETUP.md)
- [Architecture Documentation](docs/project/README.md)
- [API Reference](docs/edge/api-reference.md)
