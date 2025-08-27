# CI/CD Setup Guide

## ภาพรวม

ระบบ CI/CD นี้ถูกออกแบบสำหรับการ deploy โปรเจกต์ AI Camera ไปยัง:
- **LPR Server**: `lprserver.tail605477.ts.net` (Node.js/NestJS backend)
- **Edge Devices**: `aicamera1.tail605477.ts.net`, `aicamera2.tail605477.ts.net`, `aicamera3.tail605477.ts.net` (Python/Flask edge applications)

## โครงสร้าง Workflow

### 1. Multi-Environment Deployment (`deploy.yml`)

Workflow หลักสำหรับการ deploy ไปยังทุก environment:

```yaml
# Trigger conditions
on:
  push:
    branches: [ main ]
    paths:
      - 'server/**'
      - 'edge/**'
      - '.github/workflows/deploy.yml'
  workflow_dispatch:  # Manual trigger with options
```

#### Jobs:

1. **test-and-build**: ทดสอบและ build โปรเจกต์
2. **deploy-server**: Deploy ไปยัง LPR Server
3. **deploy-edge**: Deploy ไปยัง Edge Devices (parallel)
4. **notify-deployment**: แจ้งผลการ deploy

## การตั้งค่า

### 1. GitHub Repository Variables

ตั้งค่าตัวแปรต่อไปนี้ใน GitHub repository settings:

#### Variables (Settings > Secrets and variables > Actions > Variables):

```bash
ENABLE_SERVER_DEPLOYMENT=true
ENABLE_EDGE_DEPLOYMENT=true
```

#### Secrets (Settings > Secrets and variables > Actions > Secrets):

```bash
SSH_PRIVATE_KEY=your_ssh_private_key
SERVER_USER=lpruser
EDGE_USER=camuser
```

### 2. SSH Key Setup

#### สร้าง SSH Key Pair:

```bash
# สร้าง SSH key pair
ssh-keygen -t ed25519 -C "github-actions@aicamera" -f ~/.ssh/github_actions

# ดู public key
cat ~/.ssh/github_actions.pub
```

#### ติดตั้ง Public Key บน Server และ Edge Devices:

```bash
# บน LPR Server
ssh lpruser@lprserver.tail605477.ts.net
mkdir -p ~/.ssh
echo "your_public_key_here" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# บน Edge Devices
ssh camuser@aicamera1.tail605477.ts.net
mkdir -p ~/.ssh
echo "your_public_key_here" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# ทำแบบเดียวกันกับ aicamera2 และ aicamera3
```

#### เพิ่ม Private Key ใน GitHub Secrets:

1. ไปที่ GitHub repository > Settings > Secrets and variables > Actions
2. สร้าง secret ชื่อ `SSH_PRIVATE_KEY`
3. คัดลอกเนื้อหาของ `~/.ssh/github_actions` (private key)

### 3. Self-Hosted Runner Setup

#### ติดตั้ง Runner บนเครื่อง Local:

```bash
# ให้สิทธิ์การ execute
chmod +x scripts/setup-github-runner.sh

# รันสคริปต์
./scripts/setup-github-runner.sh
```

#### ข้อมูลที่ต้องเตรียม:

1. **GitHub Personal Access Token**:
   - ไปที่ GitHub > Settings > Developer settings > Personal access tokens
   - สร้าง token ใหม่ด้วยสิทธิ์ `repo` และ `admin:org`
   - หรือใช้ Fine-grained token สำหรับ repository นี้

2. **Repository URL**: `owner/repo-name`

3. **Runner Labels**: `self-hosted,linux,local`

#### การจัดการ Runner:

```bash
# ดูสถานะ
github-runner-status

# รีสตาร์ท
github-runner-restart

# ดู logs
github-runner-logs

# อัพเดท runner
github-runner-update <new_token>
```

## การใช้งาน

### 1. Automatic Deployment

เมื่อ push ไปยัง branch `main` และมีการเปลี่ยนแปลงใน:
- `server/**`
- `edge/**`
- `.github/workflows/deploy.yml`

ระบบจะ:
1. รัน tests
2. Build โปรเจกต์
3. Deploy ไปยัง server และ edge devices (ถ้าเปิดใช้งาน)

### 2. Manual Deployment

ไปที่ GitHub repository > Actions > Multi-Environment Deployment > Run workflow

#### Options:

- **Deploy to LPR Server**: เลือก deploy ไปยัง server หรือไม่
- **Deploy to Edge Devices**: เลือก deploy ไปยัง edge devices หรือไม่
- **Force deployment**: ข้ามการตรวจสอบ environment variables
- **Target specific edge device**: เลือก deploy เฉพาะเครื่องใดเครื่องหนึ่ง

### 3. Deployment Process

#### Server Deployment:

1. สร้าง backup ของ deployment ปัจจุบัน
2. Pull latest changes จาก Git
3. อัพเดท dependencies และ build
4. อัพเดท database schema (Prisma)
5. รีสตาร์ท systemd service
6. รีสตาร์ท nginx
7. ทดสอบ health check
8. Rollback ถ้าเกิดปัญหา

#### Edge Deployment:

1. สร้าง backup ของ deployment ปัจจุบัน
2. Pull latest changes จาก Git
3. อัพเดท Python dependencies
4. รีสตาร์ท systemd service
5. รีสตาร์ท nginx
6. ทดสอบ health check
7. Rollback ถ้าเกิดปัญหา

## การ Monitor และ Troubleshooting

### 1. ดู Deployment Status

```bash
# บน LPR Server
ssh lpruser@lprserver.tail605477.ts.net
sudo systemctl status aicamera_server.service
sudo journalctl -u aicamera_server.service -f

# บน Edge Devices
ssh camuser@aicamera1.tail605477.ts.net
sudo systemctl status aicamera_lpr.service
sudo journalctl -u aicamera_lpr.service -f
```

### 2. Health Checks

```bash
# Server API
curl http://lprserver.tail605477.ts.net:3000/health

# Edge Devices
curl http://aicamera1.tail605477.ts.net/health
curl http://aicamera2.tail605477.ts.net/health
curl http://aicamera3.tail605477.ts.net/health
```

### 3. Backup Management

Backups จะถูกเก็บไว้ใน:
- Server: `/home/lpruser/aicamera_backups/`
- Edge: `/home/camuser/aicamera_backups/`

ระบบจะเก็บ backup ไว้ 5 ไฟล์ล่าสุด

### 4. Rollback Manual

```bash
# บน Server
cd /home/lpruser/aicamera
sudo systemctl stop aicamera_server.service
sudo systemctl stop nginx
tar -xzf /home/lpruser/aicamera_backups/server_backup_YYYYMMDD_HHMMSS.tar.gz .
sudo systemctl start aicamera_server.service
sudo systemctl start nginx

# บน Edge
cd /home/camuser/aicamera
sudo systemctl stop aicamera_lpr.service
sudo systemctl stop nginx
tar -xzf /home/camuser/aicamera_backups/edge_backup_DEVICE_YYYYMMDD_HHMMSS.tar.gz .
sudo systemctl start aicamera_lpr.service
sudo systemctl start nginx
```

## Security Considerations

### 1. SSH Key Security

- ใช้ SSH key เฉพาะสำหรับ CI/CD
- จำกัดสิทธิ์การเข้าถึง key
- หมุนเวียน key เป็นประจำ

### 2. GitHub Token Security

- ใช้ Fine-grained token เมื่อเป็นไปได้
- จำกัดสิทธิ์ให้เฉพาะที่จำเป็น
- หมุนเวียน token เป็นประจำ

### 3. Network Security

- ใช้ Tailscale VPN สำหรับการเชื่อมต่อ
- จำกัดการเข้าถึง SSH เฉพาะ IP ที่อนุญาต
- ใช้ firewall rules ที่เหมาะสม

## การอัพเดท

### 1. อัพเดท Workflow

```bash
# Pull latest changes
git pull origin main

# ตรวจสอบ workflow syntax
yamllint .github/workflows/deploy.yml
```

### 2. อัพเดท Runner

```bash
# อัพเดท runner version
github-runner-update <new_token>
```

### 3. อัพเดท Dependencies

```bash
# Server dependencies
cd server && npm update

# Edge dependencies
cd edge && pip install -r requirements.txt --upgrade
```

## Troubleshooting

### ปัญหาที่พบบ่อย:

1. **SSH Connection Failed**:
   - ตรวจสอบ SSH key ใน GitHub secrets
   - ตรวจสอบ public key บน target servers
   - ตรวจสอบ network connectivity

2. **Service Failed to Start**:
   - ตรวจสอบ logs: `sudo journalctl -u service_name -f`
   - ตรวจสอบ dependencies
   - ตรวจสอบ file permissions

3. **Health Check Failed**:
   - ตรวจสอบ service status
   - ตรวจสอบ port configuration
   - ตรวจสอบ firewall rules

4. **Build Failed**:
   - ตรวจสอบ Node.js และ Python versions
   - ตรวจสอบ dependencies
   - ตรวจสอบ build logs

### การขอความช่วยเหลือ:

1. ตรวจสอบ GitHub Actions logs
2. ตรวจสอบ system logs บน target servers
3. ตรวจสอบ network connectivity
4. ติดต่อทีม DevOps หรือ System Administrator
