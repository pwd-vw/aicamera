# คู่มือนักพัฒนา - AI Camera System

## 📋 ภาพรวม

คู่มือนักพัฒนานี้จะแนะนำการพัฒนาและบำรุงรักษา AI Camera System สำหรับนักพัฒนาและทีมเทคนิค ครอบคลุมตั้งแต่การตั้งค่าสภาพแวดล้อมการพัฒนา การเขียนโค้ด การทดสอบ การแก้ไขปัญหา และการ Deploy ในสภาพแวดล้อม Production

## 🎯 เป้าหมายของคู่มือนี้

- **การพัฒนา**: Best practices สำหรับการพัฒนา Backend และ Frontend
- **การทดสอบ**: วิธีการทดสอบระบบอย่างครอบคลุม
- **การแก้ไขปัญหา**: Troubleshooting guide สำหรับปัญหาที่พบบ่อย
- **การ Deploy**: การ Deploy ในสภาพแวดล้อม Development และ Production
- **การบำรุงรักษา**: การดูแลรักษาระบบในระยะยาว

## 🏗️ สถาปัตยกรรมระบบ

### โครงสร้างระบบ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Device   │    │   Server API    │    │   Web Frontend  │
│                 │    │                 │    │                 │
│ • Raspberry Pi  │◄──►│ • NestJS        │◄──►│ • Vue.js 3      │
│ • Hailo-8       │    │ • PostgreSQL    │    │ • TypeScript    │
│ • Camera Module │    │ • Redis         │    │ • Pinia         │
│ • LPR Detection │    │ • JWT Auth      │    │ • User Mgmt     │
│                 │    │ • Unix Socket   │    │ • Profile Mgmt  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### สถาปัตยกรรมใหม่ (Production Architecture)

```
┌─────────────────┐    ┌─────────────────┐    ┌──────────────────┐
│   Browser       │    │     Nginx       │    │   Backend        │
│   :80           │◄──►│   Port 80       │◄──►│ Unix Socket      │
│                 │    │                 │    │ /tmp/aicamera-   │
│ - Frontend UI   │    │ - Static Files  │    │ backend.sock     │
│ - User Mgmt     │    │ - Reverse Proxy │    │ - NestJS API     │
│ - Profile Mgmt  │    │ - CORS Headers  │    │ - JWT Auth       │
│ - Role-based UI │    │ - Security      │    │ - Role Control   │
└─────────────────┘    └─────────────────┘    └──────────────────┘
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
- **Router**: Vue Router with Role-based Guards
- **HTTP Client**: Axios
- **Navigation**: Multi-level navigation system
- **User Management**: Complete CRUD interface
- **Profile Management**: User settings and security

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

## 🚀 Best Practices สำหรับการพัฒนา

### 📋 การพัฒนา Backend (NestJS)

#### 🎯 หลักการสำคัญ
- **Clean Architecture**: แยก Business Logic, Data Access, และ Presentation
- **SOLID Principles**: Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion
- **DRY (Don't Repeat Yourself)**: หลีกเลี่ยงการเขียนโค้ดซ้ำ
- **KISS (Keep It Simple, Stupid)**: เขียนโค้ดให้เรียบง่ายและเข้าใจง่าย

#### 🏗️ การออกแบบ API
```typescript
// ✅ ดี - ใช้ DTO สำหรับ validation
@Post('cameras')
async createCamera(@Body() createCameraDto: CreateCameraDto) {
  return this.cameraService.create(createCameraDto);
}

// ❌ ไม่ดี - ไม่มี validation
@Post('cameras')
async createCamera(@Body() data: any) {
  return this.cameraService.create(data);
}
```

#### 🔐 การจัดการ Authentication & Authorization
```typescript
// ✅ ดี - ใช้ Guards และ Decorators
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(UserRole.ADMIN)
@Post('admin-only')
async adminOnlyEndpoint() {
  // Admin only logic
}

// ✅ ดี - ใช้ Public decorator สำหรับ public endpoints
@Public()
@Post('login')
async login(@Body() loginDto: LoginDto) {
  return this.authService.login(loginDto);
}
```

#### 📊 การจัดการ Database
```typescript
// ✅ ดี - ใช้ Prisma Service
@Injectable()
export class CameraService {
  constructor(private prisma: PrismaService) {}

  async findAll(): Promise<Camera[]> {
    return this.prisma.camera.findMany({
      include: {
        detections: true,
      },
    });
  }
}

// ✅ ดี - ใช้ Transactions
async createCameraWithDetection(data: CreateCameraWithDetectionDto) {
  return this.prisma.$transaction(async (tx) => {
    const camera = await tx.camera.create({ data: data.camera });
    const detection = await tx.detection.create({
      data: { ...data.detection, cameraId: camera.id },
    });
    return { camera, detection };
  });
}
```

#### 🚨 Error Handling
```typescript
// ✅ ดี - ใช้ Custom Exceptions
@Injectable()
export class CameraService {
  async findOne(id: string): Promise<Camera> {
    const camera = await this.prisma.camera.findUnique({
      where: { id },
    });

    if (!camera) {
      throw new NotFoundException(`Camera with ID ${id} not found`);
    }

    return camera;
  }
}

// ✅ ดี - ใช้ Global Exception Filter
@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse();
    const request = ctx.getRequest();

    const status = exception instanceof HttpException
      ? exception.getStatus()
      : HttpStatus.INTERNAL_SERVER_ERROR;

    response.status(status).json({
      statusCode: status,
      timestamp: new Date().toISOString(),
      path: request.url,
      message: exception instanceof HttpException
        ? exception.message
        : 'Internal server error',
    });
  }
}
```

### 🎨 การพัฒนา Frontend (Vue.js 3)

#### 🎯 หลักการสำคัญ
- **Component-Based Architecture**: แยก UI เป็น Components ที่ใช้ซ้ำได้
- **Composition API**: ใช้ Composition API สำหรับ Logic Reusability
- **TypeScript**: ใช้ TypeScript เพื่อ Type Safety
- **Reactive Data**: ใช้ Vue's Reactivity System อย่างมีประสิทธิภาพ

#### 🧩 การออกแบบ Components
```vue
<!-- ✅ ดี - ใช้ Composition API -->
<template>
  <div class="camera-card">
    <h3>{{ camera.name }}</h3>
    <p>{{ camera.status }}</p>
    <button @click="handleClick">View Details</button>
  </div>
</template>

<script setup lang="ts">
import { defineProps, defineEmits } from 'vue';
import type { Camera } from '@/types';

interface Props {
  camera: Camera;
}

interface Emits {
  (e: 'click', camera: Camera): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const handleClick = () => {
  emit('click', props.camera);
};
</script>
```

#### 🗃️ การจัดการ State (Pinia)
```typescript
// ✅ ดี - ใช้ Pinia Store
export const useCameraStore = defineStore('camera', () => {
  const cameras = ref<Camera[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const fetchCameras = async () => {
    loading.value = true;
    error.value = null;
    
    try {
      cameras.value = await apiService.getCameras();
    } catch (err) {
      error.value = 'Failed to fetch cameras';
      console.error('Error fetching cameras:', err);
    } finally {
      loading.value = false;
    }
  };

  return {
    cameras: readonly(cameras),
    loading: readonly(loading),
    error: readonly(error),
    fetchCameras,
  };
});
```

#### 🔄 การจัดการ API Calls
```typescript
// ✅ ดี - ใช้ Service Layer
export class ApiService {
  private api = axios.create({
    baseURL: '/api',
    timeout: 15000,
  });

  async getCameras(): Promise<Camera[]> {
    const response = await this.api.get('/cameras');
    return response.data;
  }

  async createCamera(data: CreateCameraDto): Promise<Camera> {
    const response = await this.api.post('/cameras', data);
    return response.data;
  }
}
```

### 🧪 การทดสอบ (Testing)

#### 🔧 การตั้งค่า Testing Environment
```bash
# Backend Testing
npm install --save-dev @nestjs/testing jest supertest

# Frontend Testing
npm install --save-dev vitest @vue/test-utils jsdom
```

#### 🧪 Unit Testing - Backend
```typescript
// ✅ ดี - Unit Test สำหรับ Service
describe('CameraService', () => {
  let service: CameraService;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        CameraService,
        {
          provide: PrismaService,
          useValue: {
            camera: {
              findMany: jest.fn(),
              findUnique: jest.fn(),
              create: jest.fn(),
            },
          },
        },
      ],
    }).compile();

    service = module.get<CameraService>(CameraService);
    prisma = module.get<PrismaService>(PrismaService);
  });

  it('should return all cameras', async () => {
    const mockCameras = [
      { id: '1', name: 'Camera 1', status: 'active' },
      { id: '2', name: 'Camera 2', status: 'inactive' },
    ];

    jest.spyOn(prisma.camera, 'findMany').mockResolvedValue(mockCameras);

    const result = await service.findAll();

    expect(result).toEqual(mockCameras);
    expect(prisma.camera.findMany).toHaveBeenCalled();
  });
});
```

#### 🧪 Integration Testing - Backend
```typescript
// ✅ ดี - Integration Test
describe('CameraController (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/cameras (GET)', () => {
    return request(app.getHttpServer())
      .get('/cameras')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body)).toBe(true);
      });
  });
});
```

#### 🧪 Component Testing - Frontend
```typescript
// ✅ ดี - Component Test
import { mount } from '@vue/test-utils';
import CameraCard from '@/components/CameraCard.vue';

describe('CameraCard', () => {
  it('renders camera information correctly', () => {
    const camera = {
      id: '1',
      name: 'Test Camera',
      status: 'active',
    };

    const wrapper = mount(CameraCard, {
      props: { camera },
    });

    expect(wrapper.text()).toContain('Test Camera');
    expect(wrapper.text()).toContain('active');
  });

  it('emits click event when button is clicked', async () => {
    const camera = { id: '1', name: 'Test Camera', status: 'active' };
    const wrapper = mount(CameraCard, {
      props: { camera },
    });

    await wrapper.find('button').trigger('click');

    expect(wrapper.emitted('click')).toBeTruthy();
    expect(wrapper.emitted('click')?.[0]).toEqual([camera]);
  });
});
```

### 🚨 การแก้ไขปัญหา (Troubleshooting)

#### 🔍 ปัญหาที่พบบ่อย - Backend

**1. Database Connection Issues**
```bash
# ตรวจสอบ Database Connection
npm run prisma:studio

# ตรวจสอบ Migration Status
npx prisma migrate status

# รัน Migration ใหม่
npx prisma migrate dev
```

**2. TypeScript Compilation Errors**
```bash
# ตรวจสอบ TypeScript Errors
npm run build

# แก้ไข Type Errors
npx tsc --noEmit

# ตรวจสอบ Prisma Types
npx prisma generate
```

**3. Authentication Issues**
```typescript
// ตรวจสอบ JWT Secret
console.log('JWT Secret:', process.env.JWT_SECRET);

// ตรวจสอบ Token Validation
const token = req.headers.authorization?.replace('Bearer ', '');
const decoded = jwt.verify(token, process.env.JWT_SECRET);
```

#### 🔍 ปัญหาที่พบบ่อย - Frontend

**1. API Connection Issues**
```typescript
// ตรวจสอบ API Base URL
console.log('API Base URL:', import.meta.env.VITE_API_BASE_URL);

// ตรวจสอบ Network Requests
// เปิด Browser DevTools > Network Tab
```

**2. Vue Router Issues**
```typescript
// ตรวจสอบ Route Configuration
const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: DashboardView },
  { path: '/map', component: MapView },
];
```

**3. State Management Issues**
```typescript
// ตรวจสอบ Pinia Store
const store = useCameraStore();
console.log('Store state:', store.$state);

// ตรวจสอบ Reactive Data
watch(() => store.cameras, (newCameras) => {
  console.log('Cameras updated:', newCameras);
}, { deep: true });
```

### 🚀 การรัน Development Environment

#### 🔧 Backend Development
```bash
# รัน Backend ใน Development Mode
cd /home/devuser/aicamera/server
npm run start:dev

# หรือใช้ Simple Server สำหรับ Testing
node simple-server.js
```

#### 🎨 Frontend Development
```bash
# รัน Frontend ใน Development Mode
cd /home/devuser/aicamera/server/frontend
npm run dev
```

#### 🌐 Full Stack Development
```bash
# Terminal 1: Backend
cd /home/devuser/aicamera/server
npm run start:dev

# Terminal 2: Frontend
cd /home/devuser/aicamera/server/frontend
npm run dev

# Terminal 3: Database (ถ้าจำเป็น)
npx prisma studio
```

### 🏭 การรัน Production Environment

#### 🔧 Production Setup
```bash
# 1. Build Frontend
cd /home/devuser/aicamera/server/frontend
npm run build

# 2. Build Backend
cd /home/devuser/aicamera/server
npm run build

# 3. Start Backend
npm run start:prod

# 4. Configure Nginx
sudo cp nginx-simple.conf /etc/nginx/sites-available/aicamera
sudo ln -sf /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### 🌐 Nginx Configuration
```nginx
# /etc/nginx/sites-available/aicamera
server {
    listen 80;
    server_name _;
    
    # Frontend
    root /home/devuser/aicamera/server/frontend/dist;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API Proxy
    location /api/ {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 📊 การ Monitor และ Debug

#### 🔍 Logging
```typescript
// Backend Logging
import { Logger } from '@nestjs/common';

@Injectable()
export class CameraService {
  private readonly logger = new Logger(CameraService.name);

  async createCamera(data: CreateCameraDto) {
    this.logger.log(`Creating camera: ${data.name}`);
    
    try {
      const camera = await this.prisma.camera.create({ data });
      this.logger.log(`Camera created successfully: ${camera.id}`);
      return camera;
    } catch (error) {
      this.logger.error(`Failed to create camera: ${error.message}`);
      throw error;
    }
  }
}
```

#### 📈 Performance Monitoring
```typescript
// Frontend Performance
import { onMounted, onUnmounted } from 'vue';

export function usePerformanceMonitor() {
  const startTime = performance.now();
  
  onMounted(() => {
    const endTime = performance.now();
    console.log(`Component mounted in ${endTime - startTime}ms`);
  });
}
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

## 🚀 การ Deploy และ Maintenance

### 🏗️ Deployment Strategies

#### 🔄 Blue-Green Deployment
```bash
# 1. Deploy to Green Environment
cd /home/devuser/aicamera/server
git checkout main
npm run build
npm run start:prod

# 2. Test Green Environment
curl http://localhost:3000/health

# 3. Switch Nginx to Green
sudo nginx -s reload

# 4. Keep Blue as Backup
```

#### 🔄 Rolling Deployment
```bash
# 1. Deploy New Version
git pull origin main
npm install
npm run build

# 2. Restart Services
sudo systemctl restart aicamera-backend
sudo systemctl restart nginx

# 3. Verify Deployment
curl http://localhost/health
```

### 🔧 Production Environment Setup

#### 🐧 System Requirements
```bash
# Ubuntu 20.04+ / CentOS 8+
# Node.js 18+
# PostgreSQL 13+
# Redis 6+
# Nginx 1.18+
```

#### 🔐 Security Configuration
```bash
# 1. Firewall Setup
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# 2. SSL Certificate (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com

# 3. Environment Variables
sudo nano /etc/environment
# Add: JWT_SECRET=your-secret-key
# Add: DATABASE_URL=postgresql://user:pass@localhost:5432/aicamera
```

#### 🗄️ Database Setup
```bash
# 1. Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# 2. Create Database
sudo -u postgres createdb aicamera
sudo -u postgres createuser aicamera_user

# 3. Run Migrations
cd /home/devuser/aicamera/server
npx prisma migrate deploy

# 4. Seed Data
npx prisma db seed
```

### 🔄 CI/CD Pipeline

#### 📋 GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd server
          npm ci
          cd ../server/frontend
          npm ci
      
      - name: Run tests
        run: |
          cd server
          npm run test
          cd ../server/frontend
          npm run test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /home/devuser/aicamera
            git pull origin main
            cd server
            npm install
            npm run build
            cd frontend
            npm install
            npm run build
            sudo systemctl restart aicamera-backend
            sudo systemctl restart nginx
```

### 🔍 Health Checks และ Monitoring

#### 🏥 Health Check Endpoints
```typescript
// Backend Health Check
@Get('health')
async getHealth() {
  return {
    status: 'ok',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    database: await this.checkDatabase(),
    redis: await this.checkRedis(),
  };
}

private async checkDatabase() {
  try {
    await this.prisma.$queryRaw`SELECT 1`;
    return { status: 'connected' };
  } catch (error) {
    return { status: 'disconnected', error: error.message };
  }
}
```

#### 📊 System Monitoring
```bash
# 1. Install monitoring tools
sudo apt install htop iotop nethogs

# 2. Create monitoring script
cat > /home/devuser/monitor.sh << 'EOF'
#!/bin/bash
echo "=== System Status ==="
echo "Date: $(date)"
echo "Uptime: $(uptime)"
echo "Memory: $(free -h)"
echo "Disk: $(df -h /)"
echo "CPU: $(top -bn1 | grep "Cpu(s)")"

echo "=== Services Status ==="
systemctl is-active nginx
systemctl is-active aicamera-backend
systemctl is-active postgresql
systemctl is-active redis

echo "=== Application Health ==="
curl -s http://localhost/health | jq .
EOF

chmod +x /home/devuser/monitor.sh

# 3. Setup cron job
echo "*/5 * * * * /home/devuser/monitor.sh >> /var/log/aicamera-monitor.log" | sudo crontab -
```

### 🔧 Backup และ Recovery

#### 💾 Database Backup
```bash
# 1. Create backup script
cat > /home/devuser/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/devuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/aicamera_$DATE.sql"

mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U aicamera_user aicamera > $BACKUP_FILE

# Compress backup
gzip $BACKUP_FILE

# Keep only last 7 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE.gz"
EOF

chmod +x /home/devuser/backup-db.sh

# 2. Setup daily backup
echo "0 2 * * * /home/devuser/backup-db.sh" | sudo crontab -
```

#### 🔄 Application Backup
```bash
# 1. Create application backup script
cat > /home/devuser/backup-app.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/devuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/devuser/aicamera"
BACKUP_FILE="$BACKUP_DIR/aicamera_app_$DATE.tar.gz"

mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_FILE -C $APP_DIR .

# Keep only last 3 days
find $BACKUP_DIR -name "aicamera_app_*.tar.gz" -mtime +3 -delete

echo "Application backup completed: $BACKUP_FILE"
EOF

chmod +x /home/devuser/backup-app.sh

# 2. Setup weekly backup
echo "0 3 * * 0 /home/devuser/backup-app.sh" | sudo crontab -
```

### 🚨 Disaster Recovery

#### 🔄 Recovery Procedures
```bash
# 1. Database Recovery
# Restore from backup
gunzip -c /home/devuser/backups/aicamera_20240101_020000.sql.gz | psql -h localhost -U aicamera_user aicamera

# 2. Application Recovery
# Restore application
tar -xzf /home/devuser/backups/aicamera_app_20240101_030000.tar.gz -C /home/devuser/aicamera

# 3. Service Recovery
sudo systemctl restart aicamera-backend
sudo systemctl restart nginx
```

### 📈 Performance Optimization

#### ⚡ Backend Optimization
```typescript
// 1. Database Query Optimization
async getCamerasWithDetections() {
  return this.prisma.camera.findMany({
    include: {
      detections: {
        take: 10,
        orderBy: { createdAt: 'desc' },
      },
    },
    // Use indexes
    where: {
      status: 'active',
    },
  });
}

// 2. Caching
@Injectable()
export class CameraService {
  constructor(
    private prisma: PrismaService,
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
  ) {}

  async findAll(): Promise<Camera[]> {
    const cacheKey = 'cameras:all';
    let cameras = await this.cacheManager.get<Camera[]>(cacheKey);
    
    if (!cameras) {
      cameras = await this.prisma.camera.findMany();
      await this.cacheManager.set(cacheKey, cameras, 300); // 5 minutes
    }
    
    return cameras;
  }
}
```

#### ⚡ Frontend Optimization
```typescript
// 1. Lazy Loading
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/views/DashboardView.vue'),
  },
  {
    path: '/map',
    component: () => import('@/views/MapView.vue'),
  },
];

// 2. Component Optimization
export default defineComponent({
  name: 'CameraList',
  setup() {
    const cameras = ref<Camera[]>([]);
    
    // Debounce search
    const debouncedSearch = debounce(async (query: string) => {
      cameras.value = await apiService.searchCameras(query);
    }, 300);
    
    return {
      cameras,
      debouncedSearch,
    };
  },
});
```

### 🔧 Maintenance Tasks

#### 📅 Daily Tasks
```bash
# 1. Check system status
/home/devuser/monitor.sh

# 2. Check logs
sudo journalctl -u aicamera-backend --since "1 day ago"
sudo tail -f /var/log/nginx/access.log

# 3. Check disk space
df -h
```

#### 📅 Weekly Tasks
```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade

# 2. Clean old logs
sudo journalctl --vacuum-time=7d

# 3. Check backup status
ls -la /home/devuser/backups/
```

#### 📅 Monthly Tasks
```bash
# 1. Security updates
sudo apt update && sudo apt upgrade

# 2. Database maintenance
sudo -u postgres psql -c "VACUUM ANALYZE;"

# 3. Review logs for issues
grep -i error /var/log/nginx/error.log
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

## 📚 Quick Reference Commands

### 🚀 Development Commands

#### Backend Development
```bash
# Start development server
cd /home/devuser/aicamera/server
npm run start:dev

# Start simple server for testing
node simple-server.js

# Build for production
npm run build

# Run tests
npm run test
npm run test:e2e

# Database operations
npx prisma generate
npx prisma migrate dev
npx prisma migrate deploy
npx prisma studio
```

#### Frontend Development
```bash
# Start development server
cd /home/devuser/aicamera/server/frontend
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run tests
npm run test
```

#### Full Stack Development
```bash
# Terminal 1: Backend
cd /home/devuser/aicamera/server && npm run start:dev

# Terminal 2: Frontend
cd /home/devuser/aicamera/server/frontend && npm run dev

# Terminal 3: Database
cd /home/devuser/aicamera/server && npx prisma studio
```

### 🏭 Production Commands

#### Production Setup
```bash
# Build everything
cd /home/devuser/aicamera/server/frontend && npm run build
cd /home/devuser/aicamera/server && npm run build

# Start production server
cd /home/devuser/aicamera/server && npm run start:prod

# Configure nginx
sudo cp nginx-simple.conf /etc/nginx/sites-available/aicamera
sudo ln -sf /etc/nginx/sites-available/aicamera /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### Service Management
```bash
# Check service status
sudo systemctl status nginx
sudo systemctl status aicamera-backend

# Restart services
sudo systemctl restart nginx
sudo systemctl restart aicamera-backend

# View logs
sudo journalctl -u aicamera-backend -f
sudo tail -f /var/log/nginx/access.log
```

### 🔍 Troubleshooting Commands

#### System Diagnostics
```bash
# Check system resources
htop
df -h
free -h

# Check network
netstat -tlnp
ss -tlnp

# Check processes
ps aux | grep node
ps aux | grep nginx
```

#### Application Diagnostics
```bash
# Test API endpoints
curl http://localhost:3000/health
curl http://localhost/api/health
curl http://localhost/api/cameras

# Test authentication
curl -X POST http://localhost/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testuser123"}'

# Check database connection
npx prisma db pull
```

#### Log Analysis
```bash
# Backend logs
sudo journalctl -u aicamera-backend --since "1 hour ago"

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# System logs
sudo dmesg | tail
```

### 🚨 Emergency Procedures

#### Service Recovery
```bash
# Restart all services
sudo systemctl restart nginx
sudo systemctl restart aicamera-backend
sudo systemctl restart postgresql
sudo systemctl restart redis

# Check service status
sudo systemctl status nginx aicamera-backend postgresql redis
```

#### Database Recovery
```bash
# Restore from backup
gunzip -c /home/devuser/backups/aicamera_$(date +%Y%m%d)_*.sql.gz | \
psql -h localhost -U aicamera_user aicamera

# Reset database
npx prisma migrate reset
npx prisma db seed
```

#### Application Recovery
```bash
# Restore application
tar -xzf /home/devuser/backups/aicamera_app_$(date +%Y%m%d)_*.tar.gz \
-C /home/devuser/aicamera

# Rebuild and restart
cd /home/devuser/aicamera/server
npm install
npm run build
sudo systemctl restart aicamera-backend
```

### 📋 Troubleshooting Checklist

#### ✅ Common Issues Checklist

**Backend Issues:**
- [ ] Check if Node.js process is running: `ps aux | grep node`
- [ ] Check if port 3000 is available: `netstat -tlnp | grep :3000`
- [ ] Check database connection: `npx prisma db pull`
- [ ] Check environment variables: `cat .env`
- [ ] Check TypeScript compilation: `npm run build`
- [ ] Check Prisma schema: `npx prisma generate`

**Frontend Issues:**
- [ ] Check if Vite dev server is running: `ps aux | grep vite`
- [ ] Check if port 5174 is available: `netstat -tlnp | grep :5174`
- [ ] Check API base URL in browser DevTools
- [ ] Check CORS headers in Network tab
- [ ] Check Vue Router configuration
- [ ] Check Pinia store state

**Nginx Issues:**
- [ ] Check nginx status: `sudo systemctl status nginx`
- [ ] Check nginx config: `sudo nginx -t`
- [ ] Check nginx logs: `sudo tail -f /var/log/nginx/error.log`
- [ ] Check if port 80 is available: `netstat -tlnp | grep :80`
- [ ] Check site configuration: `ls -la /etc/nginx/sites-enabled/`

**Database Issues:**
- [ ] Check PostgreSQL status: `sudo systemctl status postgresql`
- [ ] Check database connection: `psql -h localhost -U aicamera_user aicamera`
- [ ] Check migration status: `npx prisma migrate status`
- [ ] Check database logs: `sudo tail -f /var/log/postgresql/postgresql-*.log`

**Authentication Issues:**
- [ ] Check JWT secret in environment variables
- [ ] Check token expiration in browser DevTools
- [ ] Check user exists in database: `SELECT * FROM "User";`
- [ ] Check password hash: `SELECT password FROM "User" WHERE username = 'testuser';`

### 📞 Support Contacts

#### Development Team
- **Lead Developer**: [Your Name] - [email@domain.com]
- **Backend Developer**: [Backend Dev] - [backend@domain.com]
- **Frontend Developer**: [Frontend Dev] - [frontend@domain.com]
- **DevOps Engineer**: [DevOps] - [devops@domain.com]

#### System Information
- **Server**: lprserver (192.168.100.117)
- **Domain**: [your-domain.com]
- **SSH Access**: `ssh devuser@192.168.100.117`
- **Documentation**: `/home/devuser/aicamera/docs/`

---

## 🎯 สรุป

คู่มือนักพัฒนานี้ครอบคลุมทุกด้านของการพัฒนาและบำรุงรักษา AI Camera System ตั้งแต่การตั้งค่าสภาพแวดล้อมการพัฒนา การเขียนโค้ดตาม Best Practices การทดสอบ การแก้ไขปัญหา และการ Deploy ในสภาพแวดล้อม Production

### 🔑 Key Takeaways

1. **การพัฒนา**: ใช้ Clean Architecture และ SOLID Principles
2. **การทดสอบ**: เขียน Unit Tests และ Integration Tests
3. **การแก้ไขปัญหา**: ใช้ Systematic Approach ในการ Debug
4. **การ Deploy**: ใช้ Blue-Green หรือ Rolling Deployment
5. **การบำรุงรักษา**: ตั้งค่า Monitoring, Backup, และ Recovery Procedures

### 📚 Additional Resources

- [NestJS Documentation](https://docs.nestjs.com/)
- [Vue.js 3 Documentation](https://vuejs.org/)
- [Prisma Documentation](https://www.prisma.io/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

**Last Updated**: 2024-09-05  
**Version**: 2.0.0  
**Maintainer**: AI Camera Development Team

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
