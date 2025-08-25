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
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- npm หรือ yarn

#### Frontend (Web)
- Node.js 18+
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

## 🤝 การมีส่วนร่วม

เรายินดีรับการมีส่วนร่วมจากชุมชน! กรุณาอ่าน [คู่มือการมีส่วนร่วม](CONTRIBUTING.md) สำหรับรายละเอียด

### การรายงานปัญหา
- ใช้ [GitHub Issues](https://github.com/your-org/aicamera/issues) สำหรับรายงานปัญหา
- กรุณาระบุรายละเอียดของปัญหาและขั้นตอนการทำซ้ำ

### การเสนอแนะฟีเจอร์
- ใช้ [GitHub Discussions](https://github.com/your-org/aicamera/discussions) สำหรับการเสนอแนะ
- อธิบายประโยชน์และกรณีการใช้งานของฟีเจอร์ที่เสนอ

## 📄 License

โปรเจคนี้อยู่ภายใต้ [MIT License](LICENSE)

## 👥 ทีมพัฒนา

- **Project Lead**: [ชื่อผู้ดูแลโปรเจค]
- **Backend Developer**: [ชื่อนักพัฒนา Backend]
- **Frontend Developer**: [ชื่อนักพัฒนา Frontend]
- **AI/ML Engineer**: [ชื่อวิศวกร AI/ML]
- **DevOps Engineer**: [ชื่อวิศวกร DevOps]

## 📞 การติดต่อ

- **Email**: support@aicamera.com
- **Website**: https://aicamera.com
- **Documentation**: https://docs.aicamera.com
- **GitHub**: https://github.com/your-org/aicamera

## 🙏 การขอบคุณ

ขอบคุณชุมชน Open Source และผู้มีส่วนร่วมทุกท่านที่ทำให้โปรเจคนี้เป็นไปได้

---

*AI Camera System - ระบบกล้องตรวจจับอัจฉริยะสำหรับอนาคต* 🚗📹🤖
