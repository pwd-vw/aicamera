# AI Camera System - ระบบกล้องตรวจจับอัจฉริยะ

## 📋 ภาพรวม

AI Camera System เป็นระบบตรวจจับป้ายทะเบียนรถยนต์แบบอัจฉริยะที่พัฒนาด้วยเทคโนโลยีล่าสุด ประกอบด้วย Edge Device (Raspberry Pi 5 + Hailo AI Accelerator) และ Server System (NestJS + Vue.js) ที่ทำงานร่วมกันเพื่อตรวจจับและวิเคราะห์ข้อมูลการจราจรแบบ Real-time

## 🏗️ สถาปัตยกรรมระบบ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Device   │    │   Server API    │    │   Web Frontend  │
│                 │    │                 │    │                 │
│ • Raspberry Pi  │◄──►│ • NestJS        │◄──►│ • Vue.js 3      │
│ • Hailo-8       │    │ • PostgreSQL    │    │ • TypeScript    │
│ • Camera Module │    │ • Redis         │    │ • Pinia         │
│ • LPR Detection │    │ • JWT Auth      │    │ • Real-time UI  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ คุณสมบัติหลัก

### 🔐 ระบบความปลอดภัย
- **JWT Authentication**: ระบบยืนยันตัวตนด้วย Token
- **Role-Based Access Control**: ระบบสิทธิ์แบบ Admin, Operator, Viewer
- **Rate Limiting**: จำกัดการเรียก API ป้องกันการใช้งานเกินขีดจำกัด
- **Input Validation**: ตรวจสอบข้อมูลที่รับเข้ามาอย่างเข้มงวด

### 📡 ระบบการสื่อสาร
- **REST API**: API หลักสำหรับการทำงาน
- **WebSocket**: การสื่อสารแบบ Real-time
- **MQTT**: การสื่อสารแบบ Lightweight สำหรับ IoT
- **Automatic Fallback**: ระบบสำรองเมื่อการเชื่อมต่อล้มเหลว

### 🎯 การตรวจจับและวิเคราะห์
- **License Plate Recognition**: ตรวจจับป้ายทะเบียนรถยนต์
- **Real-time Processing**: ประมวลผลแบบ Real-time
- **Image Storage**: เก็บภาพการตรวจจับ
- **Analytics Dashboard**: แสดงผลการวิเคราะห์

### 🖥️ ระบบผู้ใช้
- **Responsive Design**: ใช้งานได้ทุกอุปกรณ์
- **Real-time Updates**: อัพเดทข้อมูลแบบ Real-time
- **Interactive Maps**: แสดงตำแหน่งกล้องและการตรวจจับ
- **Data Visualization**: แสดงข้อมูลในรูปแบบกราฟและตาราง

## 🚀 การติดตั้งและใช้งาน

### ความต้องการของระบบ

#### Backend (Server)
- Node.js 22+
- PostgreSQL 17+
- Redis 7+
- npm หรือ yarn

#### Frontend (Web)
- Node.js 22+
- npm หรือ yarn
- Modern Browser (Chrome, Firefox, Safari, Edge)

#### Edge Device
- Raspberry Pi 5
- Hailo-8 AI Accelerator
- Camera Module 3
- Python 3.11+

### การติดตั้ง Backend

```bash
# Clone repository
git clone https://github.com/your-org/aicamera.git
cd aicamera/server

# ติดตั้ง dependencies
npm install

# ตั้งค่าฐานข้อมูล
cp .env.example .env
# แก้ไขไฟล์ .env ตามการตั้งค่าของคุณ

# สร้างฐานข้อมูล
npx prisma migrate dev

# สร้างผู้ดูแลระบบ
npm run setup:admin

# เริ่มต้นเซิร์ฟเวอร์
npm run start:dev
```

### การติดตั้ง Frontend

```bash
# ไปยังโฟลเดอร์ frontend
cd server/frontend

# ติดตั้ง dependencies
npm install

# ตั้งค่า environment
cp .env.example .env
# แก้ไขไฟล์ .env ให้ชี้ไปยัง Backend API

# เริ่มต้น development server
npm run dev
```

### การติดตั้ง Edge Device

```bash
# Clone repository
git clone https://github.com/your-org/aicamera.git
cd aicamera/edge

# สร้าง virtual environment
python -m venv venv_hailo
source venv_hailo/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า environment
cp .env.example .env
# แก้ไขไฟล์ .env ตามการตั้งค่าของคุณ

# เริ่มต้นระบบ
python -m edge.src.app
```

## 📚 เอกสารประกอบ

### สำหรับผู้ใช้
- [คู่มือผู้ใช้ (User Manual)](docs/user-manual.md)
- [คู่มือการใช้งาน API](docs/api-reference.md)
- [คู่มือการติดตั้ง](docs/installation-guide.md)

### สำหรับนักพัฒนา
- [คู่มือนักพัฒนา (Developer Handbook)](docs/developer-handbook.md)
- [API Documentation](docs/api-reference.md)
- [สถาปัตยกรรมระบบ](docs/architecture.md)
- [คู่มือการ Deploy](docs/deployment-guide.md)
- [License Analysis Report](docs/edge/license-analysis-report.md)
- [License Compliance Summary](docs/edge/license-compliance-summary.md)

## 🔧 การพัฒนา

### โครงสร้างโปรเจค

```
aicamera/
├── edge/                    # Edge Device Application
│   ├── src/                # Source code
│   ├── requirements.txt    # Python dependencies
│   └── tests/             # Python tests
├── server/                 # Backend Server
│   ├── src/               # NestJS source code
│   ├── prisma/            # Database schema
│   ├── frontend/          # Vue.js frontend
│   └── docs/              # Documentation
├── docs/                   # Project documentation
└── scripts/               # Build and deployment scripts
```

### การรัน Tests

```bash
# Backend tests
cd server
npm run test

# Frontend tests
cd server/frontend
npm run test

# Edge tests
cd edge
python -m pytest
```

### การ Build

```bash
# Build Backend
cd server
npm run build

# Build Frontend
cd server/frontend
npm run build

# Build Edge
cd edge
python setup.py build
```

### การตรวจสอบ License

```bash
# ตรวจสอบ license แบบเร็ว
./scripts/check_licenses.sh --quick

# ตรวจสอบ license แบบเต็ม
./scripts/check_licenses.sh --full

# ดูรายงาน license
cat docs/edge/license-reports/compatibility_report_*.md
```

## 🤝 การมีส่วนร่วม

เรายินดีรับการมีส่วนร่วมจากชุมชน! กรุณาอ่าน [คู่มือการมีส่วนร่วม](CONTRIBUTING.md) สำหรับรายละเอียด

### Git Workflow

#### การ Clone และ Setup
```bash
# Clone repository
git clone https://github.com/your-org/aicamera.git
cd aicamera

# สร้าง branch ใหม่สำหรับการพัฒนา
git checkout -b feature/your-feature-name
```

#### การ Commit และ Push
```bash
# เพิ่มไฟล์ที่เปลี่ยนแปลง
git add .

# Commit ด้วยข้อความที่ชัดเจน
git commit -m "feat: เพิ่มฟีเจอร์ใหม่
- อธิบายการเปลี่ยนแปลง
- อ้างอิง issue ถ้ามี"

# Push ไปยัง remote
git push origin feature/your-feature-name
```

#### การ Merge
```bash
# Pull latest changes จาก main
git checkout main
git pull origin main

# Merge feature branch
git merge feature/your-feature-name

# Push ไปยัง main
git push origin main
```

### การรายงานปัญหา
- ใช้ [GitHub Issues](https://github.com/your-org/aicamera/issues) สำหรับรายงานปัญหา
- กรุณาระบุรายละเอียดของปัญหาและขั้นตอนการทำซ้ำ
- ใช้ template ที่กำหนดไว้สำหรับรายงานปัญหา

### การเสนอแนะฟีเจอร์
- ใช้ [GitHub Discussions](https://github.com/your-org/aicamera/discussions) สำหรับการเสนอแนะ
- อธิบายประโยชน์และกรณีการใช้งานของฟีเจอร์ที่เสนอ
- ระบุความสำคัญและผลกระทบต่อผู้ใช้

## 📄 License & Copyright

### License
โปรเจคนี้อยู่ภายใต้ [MIT License](LICENSE) ซึ่งเป็นไลเซนส์แบบ Permissive ที่อนุญาตให้:
- ✅ ใช้งานเชิงพาณิชย์ได้โดยไม่มีข้อจำกัด
- ✅ แก้ไขและปรับแต่งโค้ดได้
- ✅ แจกจ่ายและเผยแพร่ได้
- ✅ ใช้งานส่วนตัวได้
- ✅ รวมเข้ากับโปรเจคอื่นได้

### Copyright
**Copyright (c) 2024 Hailo** - สงวนลิขสิทธิ์

### Third-Party Licenses
โปรเจคนี้ใช้ไลบรารีจากบุคคลที่สามหลายตัว ดูรายละเอียดได้ที่ [LICENSE_ATTRIBUTION.md](LICENSE_ATTRIBUTION.md)

### License Compliance
- **Compatibility Rate**: 85% ของ dependencies เข้ากันได้กับ MIT License
- **Risk Level**: ต่ำ - ไม่มีข้อขัดแย้งทางไลเซนส์ที่สำคัญ
- **Automated Checking**: ใช้ `scripts/check_licenses.sh` สำหรับตรวจสอบไลเซนส์

## 👥 ทีมพัฒนา

- **Project Lead**: Surasak Popwandee
- **Backend Developer**: Surasak Popwandee
- **Frontend Developer**: Surasak Popwandee
- **AI/ML Engineer**: Surasak Popwandee
- **DevOps Engineer**: Surasak Popwandee

## 📞 การสนับสนุน

### ช่องทางการติดต่อ

- **Email**: popwandee@gmail.com
- **Website**: https://github.com/popwandee/aicamera
- **Documentation**: https://github.com/popwandee/aicamera
- **GitHub**: https://github.com/popwandee/aicamera

## 🙏 การขอบคุณ

ขอบคุณชุมชน Open Source และผู้มีส่วนร่วมทุกท่านที่ทำให้โปรเจคนี้เป็นไปได้

### Open Source Dependencies
โปรเจคนี้ใช้ไลบรารี Open Source มากกว่า 200+ packages ที่มีไลเซนส์ที่เข้ากันได้กับ MIT License:
- **Web Framework**: Flask, Jinja2, Werkzeug
- **AI/ML Libraries**: numpy, scipy, matplotlib, opencv-python
- **Image Processing**: Pillow, scikit-image
- **Web Technologies**: aiohttp, gunicorn, Socket.IO
- **Development Tools**: rich, loguru, attrs

### License Compliance
- **Total Dependencies**: 200+ packages
- **Compatible Licenses**: 85% (MIT, BSD, Apache 2.0, PSF)
- **Risk Assessment**: Low - No major license conflicts
- **Automated Monitoring**: Available via `scripts/check_licenses.sh`

---

*AI Camera System - ระบบกล้องตรวจจับอัจฉริยะสำหรับอนาคต* 🚗📹🤖

**License**: [MIT License](LICENSE) | **Copyright**: © 2024 Hailo | **Compliance**: ✅ Excellent
