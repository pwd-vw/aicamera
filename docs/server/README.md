# AI Camera Server - คู่มือการใช้งาน

## 📋 ภาพรวม

AI Camera Server เป็นระบบจัดการข้อมูลและ API สำหรับ AI Camera System ที่พัฒนาด้วย NestJS และ Vue.js โดยมีการแยก build process ระหว่าง Backend และ Frontend เพื่อประสิทธิภาพและความยืดหยุ่นในการพัฒนา

## 🏗️ สถาปัตยกรรม

### โครงสร้างระบบ
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

### เทคโนโลยีที่ใช้

#### Backend (NestJS)
- **Framework**: NestJS
- **Database**: PostgreSQL + Prisma ORM
- **Cache**: Redis
- **Authentication**: JWT + Passport
- **Validation**: class-validator
- **Rate Limiting**: @nestjs/throttler

#### Frontend (Vue.js)
- **Framework**: Vue.js 3
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Router**: Vue Router
- **HTTP Client**: Axios

## 🚀 การติดตั้ง

### ความต้องการของระบบ

```bash
# Node.js 18+
node --version

# PostgreSQL 14+
psql --version

# Redis 6+
redis-server --version

# npm หรือ yarn
npm --version
```

### การติดตั้ง Backend

```bash
# Clone repository
git clone https://github.com/your-org/aicamera.git
cd aicamera/server

# ติดตั้ง dependencies
npm install

# ตั้งค่าฐานข้อมูล
npx prisma generate
npx prisma migrate dev

# ตั้งค่า environment variables
cp .env.example .env
# แก้ไข .env file ตามความเหมาะสม

# รัน development server
npm run start:dev
```

### การติดตั้ง Frontend

```bash
# เข้าไปใน frontend directory
cd frontend

# ติดตั้ง dependencies
npm install

# รัน development server
npm run dev
```

## 🔨 การ Build

### การ Build แยกกัน (Recommended)

```bash
# Build Backend only
cd server
npm run build

# Build Frontend only
cd server/frontend
npm run build

# Build both (from root)
cd server
npm run build:all
```

### การ Build Scripts

```json
{
  "scripts": {
    "build": "nest build",
    "build:frontend": "cd frontend && npm run build",
    "build:all": "npm run build && npm run build:frontend",
    "start:dev": "nest start --watch",
    "start:frontend": "cd frontend && npm run dev",
    "dev": "concurrently \"npm run start:dev\" \"npm run start:frontend\""
  }
}
```

### การตั้งค่า TypeScript Configuration

#### Backend (tsconfig.json)
```json
{
  "compilerOptions": {
    "module": "commonjs",
    "target": "ES2020",
    "outDir": "./dist",
    "baseUrl": "./",
    "strict": true,
    "skipLibCheck": true
  },
  "exclude": [
    "frontend/**/*",
    "node_modules"
  ]
}
```

#### Frontend (tsconfig.app.json)
```json
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "compilerOptions": {
    "strict": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"]
}
```

## 📁 โครงสร้างโปรเจกต์

```
server/
├── src/
│   ├── auth/                 # Authentication modules
│   ├── communication/        # Communication protocols
│   ├── controllers/          # API controllers
│   ├── database/             # Database configuration
│   ├── decorators/           # Custom decorators
│   ├── dto/                  # Data Transfer Objects
│   ├── guards/               # Authentication guards
│   ├── interceptors/         # Request/Response interceptors
│   ├── modules/              # Feature modules
│   ├── services/             # Business logic services
│   └── main.ts               # Application entry point
├── prisma/                   # Database schema
├── frontend/                 # Vue.js frontend (separate build)
├── package.json              # Dependencies
└── tsconfig.json             # TypeScript configuration
```

## 🔧 การพัฒนา

### การรัน Development Server

```bash
# รัน Backend และ Frontend พร้อมกัน
npm run dev

# รัน Backend เท่านั้น
npm run start:dev

# รัน Frontend เท่านั้น
cd frontend && npm run dev
```

### การแก้ไขปัญหา Build

#### Backend Build Issues
```bash
# ลบ dist folder และ build ใหม่
rm -rf dist/
npm run build

# ตรวจสอบ TypeScript errors
npx tsc --noEmit
```

#### Frontend Build Issues
```bash
# เข้าไปใน frontend directory
cd frontend

# ลบ node_modules และติดตั้งใหม่
rm -rf node_modules/
npm install

# Build ใหม่
npm run build
```

## 📊 การ Monitor และ Logging

### การ Monitor Backend

```typescript
// การใช้ Winston Logger
import { Logger } from '@nestjs/common';

@Injectable()
export class ExampleService {
  private readonly logger = new Logger(ExampleService.name);

  async someMethod() {
    this.logger.log('Starting some operation');
    
    try {
      // Some operation
      this.logger.log('Operation completed successfully');
    } catch (error) {
      this.logger.error('Operation failed', error.stack);
      throw error;
    }
  }
}
```

## 🔒 ความปลอดภัย

### การรักษาความปลอดภัย Backend

```typescript
// การใช้ Helmet
import { NestFactory } from '@nestjs/core';
import helmet from 'helmet';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  app.use(helmet());
  app.enableCors({
    origin: process.env.FRONTEND_URL,
    credentials: true,
  });
  
  await app.listen(3000);
}
```

## 📚 เอกสารเพิ่มเติม

- [API Reference](./api-reference.md) - เอกสาร API endpoints
- [User Manual](./user-manual.md) - คู่มือผู้ใช้
- [Developer Handbook](./developer-handbook.md) - คู่มือนักพัฒนา
- [Database Template](./database-template.md) - คู่มือการจัดการฐานข้อมูล

## 🖥️ การจัดการระบบ (System Management)

### ภาพรวม

ระบบ AI Camera ใช้ systemd services สำหรับการจัดการที่เสถียรและอัตโนมัติ:

- **aicamera-backend.service**: บริการ NestJS backend
- **aicamera-frontend.service**: บริการ Vite preview frontend
- **aicamera-control.sh**: สคริปต์ควบคุมระบบ

### การติดตั้งและใช้งาน

#### การติดตั้ง Services
```bash
cd /home/devuser/aicamera
./scripts/aicamera-control.sh install
```

#### การเริ่มต้น Services
```bash
./scripts/aicamera-control.sh start
```

#### การตรวจสอบสถานะ
```bash
./scripts/aicamera-control.sh status
```

### คำสั่งควบคุมระบบ

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
```

### การแก้ไขปัญหา Port Conflicts

หากเกิด port conflict (EADDRINUSE):

```bash
# ตรวจสอบ port ที่ใช้งาน
netstat -tulpn | grep :3000
netstat -tulpn | grep :5173

# หยุด process ที่ใช้ port
kill -9 <PID>

# รีสตาร์ท services
./scripts/aicamera-control.sh restart
```

### การ Monitor และ Logs

```bash
# ดู logs แบบ real-time
journalctl --user -u aicamera-backend -f
journalctl --user -u aicamera-frontend -f

# ตรวจสอบสถานะ services
systemctl --user status aicamera-backend
systemctl --user status aicamera-frontend
```

## 🆘 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

#### System Management Issues
- **Port Conflicts**: ตรวจสอบ port usage และ kill processes
- **Service Failures**: ตรวจสอบ logs และ reset failed services
- **Group Permission Issues**: ลบและติดตั้ง services ใหม่

#### Backend Issues
- **Database Connection**: ตรวจสอบ connection string
- **JWT Issues**: ตรวจสอบ JWT secret
- **CORS Issues**: ตรวจสอบ CORS configuration
- **Rate Limiting**: ตรวจสอบ rate limit configuration

#### Frontend Issues
- **Build Errors**: ตรวจสอบ TypeScript errors
- **API Calls**: ตรวจสอบ API endpoints
- **State Management**: ตรวจสอบ Pinia stores
- **Routing**: ตรวจสอบ Vue Router configuration

### การ Debug

```bash
# Backend debugging
npm run start:debug

# Frontend debugging
npm run dev
```

## 📞 การสนับสนุน

### ช่องทางการติดต่อ

- **Email**: dev-support@aicamera.com
- **Slack**: #aicamera-dev
- **GitHub Issues**: https://github.com/your-org/aicamera/issues
- **Documentation**: https://docs.aicamera.com

---

*AI Camera Server - คู่มือการใช้งาน* 🚀📋
