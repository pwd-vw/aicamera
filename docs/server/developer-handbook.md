# คู่มือนักพัฒนา - AI Camera System

## 📋 ภาพรวม

คู่มือนักพัฒนานี้จะแนะนำการพัฒนาและบำรุงรักษา AI Camera System สำหรับนักพัฒนาและทีมเทคนิค ครอบคลุมตั้งแต่การตั้งค่าสภาพแวดล้อมการพัฒนา การเขียนโค้ด การทดสอบ และการ Deploy

## 🏗️ สถาปัตยกรรมระบบ

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

#### Backend (Server)
- **Framework**: NestJS
- **Database**: PostgreSQL + Prisma ORM
- **Cache**: Redis
- **Authentication**: JWT + Passport
- **Validation**: class-validator
- **Rate Limiting**: @nestjs/throttler

#### Frontend (Web)
- **Framework**: Vue.js 3
- **Language**: TypeScript
- **Build Tool**: Vite
- **State Management**: Pinia
- **Router**: Vue Router
- **HTTP Client**: Axios

#### Edge Device
- **Language**: Python 3.11+
- **AI Framework**: Hailo-8
- **Camera**: libcamera
- **Database**: SQLite
- **Web Framework**: Flask

## 🚀 การตั้งค่าสภาพแวดล้อมการพัฒนา

### ความต้องการของระบบ

#### Backend Development
```bash
# Node.js 18+
node --version

# PostgreSQL 14+
psql --version

# Redis 6+
redis-server --version

# npm หรือ yarn
npm --version

# systemd (สำหรับ production deployment)
systemctl --version
```

#### Frontend Development
```bash
# Node.js 18+
node --version

# npm หรือ yarn
npm --version

# Modern Browser
# Chrome, Firefox, Safari, Edge
```

#### Edge Development
```bash
# Python 3.11+
python3 --version

# pip
pip --version

# Virtual Environment
python3 -m venv --help
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

### การติดตั้ง Edge Device

```bash
# เข้าไปใน edge directory
cd edge

# สร้าง virtual environment
python3 -m venv venv_hailo
source venv_hailo/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# รัน application
python src/app.py
```

## 📁 โครงสร้างโปรเจกต์

### โครงสร้าง Backend (NestJS)

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

### โครงสร้าง Frontend (Vue.js)

```
server/frontend/
├── src/
│   ├── components/           # Reusable components
│   ├── views/                # Page components
│   ├── stores/               # Pinia stores
│   ├── services/             # API services
│   ├── utils/                # Utility functions
│   ├── router/               # Vue Router configuration
│   ├── App.vue               # Root component
│   └── main.ts               # Application entry point
├── public/                   # Static assets
├── package.json              # Frontend dependencies
├── tsconfig.json             # TypeScript configuration
├── tsconfig.app.json         # App-specific TypeScript config
├── tsconfig.node.json        # Node-specific TypeScript config
└── vite.config.ts            # Vite build configuration
```

### โครงสร้าง Edge Device

```
edge/
├── src/
│   ├── components/           # Camera components
│   ├── services/             # Business logic
│   ├── core/                 # Core functionality
│   ├── utils/                # Utility functions
│   └── app.py                # Main application
├── requirements.txt          # Python dependencies
├── tests/                    # Tests
└── scripts/                  # Scripts
```

## 🔧 การพัฒนา Backend

### การสร้าง Module ใหม่

```bash
# สร้าง module ใหม่
nest generate module new-module

# สร้าง controller
nest generate controller new-module

# สร้าง service
nest generate service new-module
```

### การสร้าง DTO

```typescript
// src/new-module/dto/create-new.dto.ts
import { IsString, IsNumber, IsOptional } from 'class-validator';

export class CreateNewDto {
  @IsString()
  name: string;

  @IsNumber()
  @IsOptional()
  value?: number;
}
```

### การสร้าง Entity

```typescript
// src/new-module/entities/new.entity.ts
import { Entity, PrimaryGeneratedColumn, Column } from 'typeorm';

@Entity()
export class New {
  @PrimaryGeneratedColumn('uuid')
  id: string;

  @Column()
  name: string;

  @Column({ nullable: true })
  value?: number;

  @Column({ type: 'timestamp', default: () => 'CURRENT_TIMESTAMP' })
  createdAt: Date;
}
```

### การสร้าง Service

```typescript
// src/new-module/new.service.ts
import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { CreateNewDto } from './dto/create-new.dto';

@Injectable()
export class NewService {
  constructor(private prisma: PrismaService) {}

  async create(createNewDto: CreateNewDto) {
    return this.prisma.new.create({
      data: createNewDto,
    });
  }

  async findAll() {
    return this.prisma.new.findMany();
  }

  async findOne(id: string) {
    return this.prisma.new.findUnique({
      where: { id },
    });
  }
}
```

### การสร้าง Controller

```typescript
// src/new-module/new.controller.ts
import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { NewService } from './new.service';
import { CreateNewDto } from './dto/create-new.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';

@Controller('new')
@UseGuards(JwtAuthGuard, RolesGuard)
export class NewController {
  constructor(private readonly newService: NewService) {}

  @Post()
  @Roles('admin')
  create(@Body() createNewDto: CreateNewDto) {
    return this.newService.create(createNewDto);
  }

  @Get()
  findAll() {
    return this.newService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    return this.newService.findOne(id);
  }
}
```

### การใช้ Prisma

```typescript
// การใช้งาน Prisma Service
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class ExampleService {
  constructor(private prisma: PrismaService) {}

  // สร้างข้อมูล
  async create(data: any) {
    return this.prisma.example.create({
      data,
    });
  }

  // ค้นหาข้อมูล
  async findMany(where?: any) {
    return this.prisma.example.findMany({
      where,
      include: {
        related: true,
      },
    });
  }

  // อัพเดทข้อมูล
  async update(id: string, data: any) {
    return this.prisma.example.update({
      where: { id },
      data,
    });
  }

  // ลบข้อมูล
  async delete(id: string) {
    return this.prisma.example.delete({
      where: { id },
    });
  }
}
```

### การสร้าง Custom Validation

```typescript
// src/decorators/custom-validation.decorator.ts
import { registerDecorator, ValidationOptions, ValidationArguments } from 'class-validator';

export function IsStrongPassword(validationOptions?: ValidationOptions) {
  return function (object: Object, propertyName: string) {
    registerDecorator({
      name: 'isStrongPassword',
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      validator: {
        validate(value: any) {
          return /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/.test(value);
        },
        defaultMessage() {
          return 'รหัสผ่านต้องมีตัวพิมพ์เล็ก ตัวพิมพ์ใหญ่ ตัวเลข และอักขระพิเศษอย่างน้อย 8 ตัว';
        },
      },
    });
  };
}
```

## 🎨 การพัฒนา Frontend

### การสร้าง Component ใหม่

```vue
<!-- src/components/NewComponent.vue -->
<template>
  <div class="new-component">
    <h3>{{ title }}</h3>
    <div class="content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string;
}

const props = defineProps<Props>();
</script>

<style scoped>
.new-component {
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  padding: 1rem;
}

.content {
  margin-top: 1rem;
}
</style>
```

### การสร้าง View ใหม่

```vue
<!-- src/views/NewView.vue -->
<template>
  <div class="new-view">
    <div class="view-header">
      <h1>{{ title }}</h1>
      <button @click="createNew" class="btn-primary">Create New</button>
    </div>
    
    <div class="view-content">
      <DataTable
        :columns="columns"
        :items="items"
        :loading="loading"
        @refresh="loadData"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from '../components/DataTable.vue';
import { apiService } from '../services';

const router = useRouter();
const title = 'New Items';
const loading = ref(false);
const items = ref([]);

const columns = [
  { key: 'name', label: 'Name', sortable: true },
  { key: 'value', label: 'Value', sortable: true },
  { key: 'actions', label: 'Actions', sortable: false },
];

const loadData = async () => {
  loading.value = true;
  try {
    const response = await apiService.getNewItems();
    items.value = response.data;
  } catch (error) {
    console.error('Error loading data:', error);
  } finally {
    loading.value = false;
  }
};

const createNew = () => {
  router.push('/new/create');
};

onMounted(() => {
  loadData();
});
</script>
```

### การสร้าง Store

```typescript
// src/stores/new.ts
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { apiService } from '../services';

export const useNewStore = defineStore('new', () => {
  const items = ref([]);
  const loading = ref(false);
  const error = ref(null);

  const getItems = computed(() => items.value);
  const getLoading = computed(() => loading.value);
  const getError = computed(() => error.value);

  const fetchItems = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      const response = await apiService.getNewItems();
      items.value = response.data;
    } catch (err) {
      error.value = err.message;
    } finally {
      loading.value = false;
    }
  };

  const createItem = async (itemData: any) => {
    try {
      const response = await apiService.createNewItem(itemData);
      items.value.push(response.data);
      return response.data;
    } catch (err) {
      error.value = err.message;
      throw err;
    }
  };

  return {
    items,
    loading,
    error,
    getItems,
    getLoading,
    getError,
    fetchItems,
    createItem,
  };
});
```

### การสร้าง Service

```typescript
// src/services/new.service.ts
import api from '../utils/api';

export interface NewItem {
  id: string;
  name: string;
  value: number;
  createdAt: string;
}

export interface CreateNewItemDto {
  name: string;
  value: number;
}

export class NewService {
  async getItems(): Promise<NewItem[]> {
    const response = await api.get('/new');
    return response.data;
  }

  async getItem(id: string): Promise<NewItem> {
    const response = await api.get(`/new/${id}`);
    return response.data;
  }

  async createItem(data: CreateNewItemDto): Promise<NewItem> {
    const response = await api.post('/new', data);
    return response.data;
  }

  async updateItem(id: string, data: Partial<CreateNewItemDto>): Promise<NewItem> {
    const response = await api.put(`/new/${id}`, data);
    return response.data;
  }

  async deleteItem(id: string): Promise<void> {
    await api.delete(`/new/${id}`);
  }
}

export const newService = new NewService();
```

## 🔨 การ Build และ Deploy

### การ Build Backend (NestJS)

```bash
# Development build
npm run build

# Production build
npm run build:prod

# Build with optimization
npm run build:optimized
```

### การ Build Frontend (Vue.js)

```bash
# เข้าไปใน frontend directory
cd frontend

# Development build
npm run build

# Production build
npm run build:prod

# Preview production build
npm run preview
```

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

### การ Deploy Backend

```bash
# Using PM2
pm2 start dist/main.js --name aicamera-backend

# Using Docker
docker build -t aicamera-backend .
docker run -p 3000:3000 aicamera-backend
```

### การ Deploy Frontend

```bash
# Build production
npm run build

# Deploy to static server
# Copy dist/ folder to web server

# Using Docker
docker build -t aicamera-frontend .
docker run -p 80:80 aicamera-frontend
```

### การ Deploy Edge Device

```bash
# Install as systemd service
sudo cp aicamera.service /etc/systemd/system/
sudo systemctl enable aicamera
sudo systemctl start aicamera

# Using Docker
docker build -t aicamera-edge .
docker run --privileged aicamera-edge
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

### การ Monitor Frontend

```typescript
// การใช้ Error Boundary
import { onErrorCaptured } from 'vue';

onErrorCaptured((error, instance, info) => {
  console.error('Error captured:', error);
  console.error('Component:', instance);
  console.error('Info:', info);
  
  // Send to error tracking service
  errorTrackingService.captureException(error);
  
  return false; // Prevent error from propagating
});
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

### การรักษาความปลอดภัย Frontend

```typescript
// การจัดการ Token
const token = localStorage.getItem('token');
if (token) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
}

// การตรวจสอบ Token expiration
const isTokenExpired = (token: string) => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return payload.exp * 1000 < Date.now();
  } catch {
    return true;
  }
};
```

## 🚀 การ Build Process แยกกัน

### เหตุผลในการแยก Build Process

#### **Backend (NestJS)**
- **TypeScript Compilation**: Compile TypeScript เป็น JavaScript
- **Module Resolution**: จัดการ dependencies และ modules
- **API Generation**: สร้าง API documentation
- **Database Migration**: จัดการ database schema

#### **Frontend (Vue.js)**
- **Vue Compilation**: Compile Vue components
- **Asset Optimization**: Optimize CSS, images, fonts
- **Code Splitting**: แยก code เป็น chunks
- **Bundle Optimization**: ลดขนาดไฟล์

### การตั้งค่า TypeScript Configuration

#### **Backend (tsconfig.json)**
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

#### **Frontend (tsconfig.app.json)**
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

### การ Build Scripts

#### **Package.json Scripts**
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
### Development Mode (Recommended for development)
```bash
# Start both backend and frontend in development mode
cd /home/devuser/aicamera
npm run dev
```
### Individual Development
```bash
# Backend only (NestJS with hot reload)
cd /home/devuser/aicamera
npm run dev:server

# Frontend only (Vite with hot reload)
cd /home/devuser/aicamera
npm run dev:frontend
```
### การ Build Commands
#### Build Both
```bash
# Build backend and frontend for production
cd /home/devuser/aicamera
npm run build
```
#### **Backend Build**
```bash
# Build backend only
cd /home/devuser/aicamera
npm run build:server

# Build Issues แก้ปัญหา ลบ dist folder และ build ใหม่
rm -rf dist/
npm run build

# ตรวจสอบ TypeScript errors
npx tsc --noEmit

# ตรวจสอบ dependencies
npm audit
npm outdated
```

#### **Frontend Build Issues**
```bash
# Build frontend only
cd /home/devuser/aicamera
npm run build:frontend

# Build Issues เข้าไปใน frontend directory
cd frontend

# ลบ node_modules และติดตั้งใหม่
rm -rf node_modules/
npm install

# Build ใหม่
npm run build

# ตรวจสอบ TypeScript errors
npx vue-tsc --noEmit
```

#### **Vue Import Issues**
```bash
# ตรวจสอบ Vue file paths
find . -name "*.vue" -type f

# ตรวจสอบ import statements
grep -r "import.*\.vue" src/

# แก้ไข TypeScript configuration
# เพิ่ม moduleResolution: "bundler" ใน tsconfig.app.json
```
## 🏃‍♂️ Production Start
### Start Production Backend
``` bash
cd /home/devuser/aicamera
npm run start:server
```

### Preview Production Frontend
```bash
cd /home/devuser/aicamera/server/frontend
npm run preview
```
## �� Service URLs
Backend API: http://localhost:3000
Frontend Dashboard: http://localhost:5173
Backend Health Check: http://localhost:3000/communication/status
Frontend Login: http://localhost:5173/login

## 🔧 Manual Commands
### Backend Manual
```bash
cd /home/devuser/aicamera/server
npm run start:dev    # Development with watch
npm run build        # Build for production
npm run start:prod   # Start production build
```
สั่งแบบ foreground (เช่น npm run start:dev หรือ npm run start:prod) ต้องปล่อยให้ Terminal ค้างไว้เพื่อให้ backend ทำงานต่อเนื่อง
ทางเลือกถ้าไม่อยากค้าง Terminal:
- รันแบบ background ชั่วคราว
```bash
cd /home/devuser/aicamera/server
npm run start:prod & disown
```
- ใช้ตัวจัดการโปรเซสสำหรับ production (แนะนำ)
```bash
npm i -g pm2
pm2 start dist/src/main.js --name aicamera-server
pm2 save
pm2 status
```
ใช้ตัว multiplexer เพื่อไม่ต้องค้างหน้าจอ
```bash
tmux new -s aicamera
# ใน tmux: cd /home/devuser/aicamera/server && npm run start:dev
# แยกหน้าจอ: กด Ctrl+b แล้ว d
tmux attach -t aicamera
```

## 🖥️ การจัดการระบบด้วย Systemd Services

### ภาพรวม

ระบบ AI Camera ได้รับการออกแบบให้ทำงานผ่าน systemd services เพื่อการจัดการที่เสถียรและอัตโนมัติ ประกอบด้วย:

- **aicamera-backend.service**: บริการ NestJS backend
- **aicamera-frontend.service**: บริการ Vite preview frontend
- **aicamera-control.sh**: สคริปต์ควบคุมระบบ

### การติดตั้ง Services

#### 1. ติดตั้ง Services
```bash
cd /home/devuser/aicamera
./scripts/aicamera-control.sh install
```

#### 2. เริ่มต้น Services
```bash
./scripts/aicamera-control.sh start
```

#### 3. ตรวจสอบสถานะ
```bash
./scripts/aicamera-control.sh status
```

### คำสั่งควบคุมระบบ

#### การจัดการ Services
```bash
# เริ่มต้น services
./scripts/aicamera-control.sh start

# หยุด services
./scripts/aicamera-control.sh stop

# รีสตาร์ท services
./scripts/aicamera-control.sh restart

# ตรวจสอบสถานะ
./scripts/aicamera-control.sh status

# ดู logs
./scripts/aicamera-control.sh logs aicamera-backend
./scripts/aicamera-control.sh logs aicamera-frontend
```

#### การ Build และ Deploy
```bash
# Build และ deploy
./scripts/aicamera-control.sh deploy

# Build เท่านั้น
./scripts/aicamera-control.sh build
```

#### การจัดการ Services
```bash
# ติดตั้ง services
./scripts/aicamera-control.sh install

# ลบ services
./scripts/aicamera-control.sh uninstall
```

### การแก้ไขปัญหา

#### Port Conflicts
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

#### Service Failures
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

#### Group Permission Issues
หากเกิด status 216/GROUP error:

```bash
# ตรวจสอบ groups ของ user
groups devuser

# ลบและติดตั้ง services ใหม่
./scripts/aicamera-control.sh uninstall
./scripts/aicamera-control.sh install
```

### การ Monitor และ Logs

#### ดู Logs แบบ Real-time
```bash
# ดู logs ของ backend
journalctl --user -u aicamera-backend -f

# ดู logs ของ frontend
journalctl --user -u aicamera-frontend -f

# ดู logs ทั้งหมด
journalctl --user -f -u aicamera-backend -u aicamera-frontend
```

#### ตรวจสอบสถานะ Services
```bash
# ตรวจสอบสถานะ systemd
systemctl --user status aicamera-backend
systemctl --user status aicamera-frontend

# ตรวจสอบ enabled services
systemctl --user list-unit-files | grep aicamera
```

### การตั้งค่า Environment Variables

#### Backend Environment
```bash
# ตั้งค่าใน systemd service
Environment=NODE_ENV=production
Environment=PORT=3000
Environment=PATH=/usr/bin:/usr/local/bin:/home/devuser/.npm-global/bin
```

#### Frontend Environment
```bash
# ตั้งค่าใน systemd service
Environment=HOST=0.0.0.0
Environment=PORT=5173
Environment=PATH=/usr/bin:/usr/local/bin:/home/devuser/.npm-global/bin
```

### การตั้งค่า Auto-start

Services จะเริ่มต้นอัตโนมัติเมื่อระบบ boot:

```bash
# ตรวจสอบ auto-start
systemctl --user is-enabled aicamera-backend
systemctl --user is-enabled aicamera-frontend

# เปิด/ปิด auto-start
systemctl --user enable aicamera-backend
systemctl --user disable aicamera-backend
```

### การ Backup และ Restore

#### Backup Services
```bash
# Backup service files
cp ~/.config/systemd/user/aicamera-*.service /backup/

# Backup control script
cp scripts/aicamera-control.sh /backup/
```

#### Restore Services
```bash
# Restore service files
cp /backup/aicamera-*.service ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

# Restart services
./scripts/aicamera-control.sh restart
```
### Frontend Manual
```bash
cd /home/devuser/aicamera/server/frontend
npm run dev          # Development server
npm run build        # Build for production
npm run preview      # Preview production build
```
## �� What's Working Now
✅ Backend: NestJS server running on port 3000 with WebSocket support
✅ Frontend: Vue.js dashboard running on port 5173
✅ Communication: WebSocket protocol configured
✅ Build System: Both services build successfully

## 📚 Best Practices

### Backend Best Practices

1. **ใช้ TypeScript**: ใช้ TypeScript เพื่อ type safety
2. **ใช้ DTOs**: ใช้ DTOs สำหรับ validation
3. **ใช้ Guards**: ใช้ Guards สำหรับ authorization
4. **ใช้ Interceptors**: ใช้ Interceptors สำหรับ logging
5. **ใช้ Pipes**: ใช้ Pipes สำหรับ transformation

### Frontend Best Practices

1. **ใช้ Composition API**: ใช้ Composition API สำหรับ Vue 3
2. **ใช้ TypeScript**: ใช้ TypeScript เพื่อ type safety
3. **ใช้ Stores**: ใช้ Pinia stores สำหรับ state management
4. **ใช้ Components**: แยก components ให้เหมาะสม
5. **ใช้ Services**: ใช้ services สำหรับ API calls

### Database Best Practices

1. **ใช้ Migrations**: ใช้ Prisma migrations
2. **ใช้ Indexes**: สร้าง indexes สำหรับ performance
3. **ใช้ Transactions**: ใช้ transactions สำหรับ data integrity
4. **ใช้ Relations**: ใช้ relations อย่างเหมาะสม
5. **ใช้ Validation**: ใช้ database constraints

## 🆘 การแก้ไขปัญหา

### ปัญหาที่พบบ่อย

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

#### Edge Device Issues
- **Camera Access**: ตรวจสอบ camera permissions
- **Hailo SDK**: ตรวจสอบ Hailo SDK installation
- **Network**: ตรวจสอบ network connectivity
- **Storage**: ตรวจสอบ disk space

### การ Debug

```bash
echo "=== Current Process Status ===" && ps aux | grep -E "(nest|vite|node.*main)" | grep -v grep
# ตรวจสอบว่า Backend และ Frontend ทำงานหรือไม่ที่ port 3000 , frontend 5173
echo "=== Port Status ===" && netstat -tlnp | grep -E ":3000|:5173" || echo "No services on target ports"
# Backend Health Check
echo "=== Backend Health Check ===" && curl -s http://localhost:3000/communication/status | jq . 2>/dev/null || curl -s http://localhost:3000/communication/status
# Frontedn Status
echo "=== Frontend Status ===" && curl -s http://localhost:5173 | head -5 || echo "Frontend not responding"
sleep 5 && echo "=== Frontend Test ===" && curl -s http://localhost:5173 | head -10
# Backend debugging
npm run start:debug

# Frontend debugging
npm run dev

# Edge debugging
python -m pdb edge/src/app.py

journalctl --user -u aicamera-backend --no-pager -l -n 20
```

## 📞 การสนับสนุน

### ช่องทางการติดต่อ

- **Email**: dev-support@aicamera.com
- **Slack**: #aicamera-dev
- **GitHub Issues**: https://github.com/your-org/aicamera/issues
- **Documentation**: https://docs.aicamera.com

### การมีส่วนร่วม

1. **Fork repository**
2. **สร้าง feature branch**
3. **เขียน code และ tests**
4. **สร้าง pull request**
5. **รอ code review**

---

*คู่มือนักพัฒนา - AI Camera System* 👨‍💻🔧
