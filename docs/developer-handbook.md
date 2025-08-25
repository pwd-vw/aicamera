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
cp .env.example .env
# แก้ไขไฟล์ .env ตามการตั้งค่าของคุณ

# สร้างฐานข้อมูล
npx prisma migrate dev

# สร้างผู้ดูแลระบบ
npm run setup:admin

# เริ่มต้น development server
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
python3 -m venv venv_hailo
source venv_hailo/bin/activate

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า environment
cp .env.example .env
# แก้ไขไฟล์ .env ตามการตั้งค่าของคุณ

# เริ่มต้นระบบ
python -m edge.src.app
```

## 📁 โครงสร้างโปรเจค

### โครงสร้าง Backend

```
server/
├── src/
│   ├── auth/                 # ระบบ Authentication
│   ├── cameras/              # การจัดการกล้อง
│   ├── detections/           # การจัดการการตรวจจับ
│   ├── analytics/            # การวิเคราะห์ข้อมูล
│   ├── visualizations/       # การแสดงผลข้อมูล
│   ├── users/                # การจัดการผู้ใช้
│   ├── rate-limit/           # การจำกัดการใช้งาน
│   ├── communication/        # ระบบการสื่อสาร
│   ├── common/               # โค้ดที่ใช้ร่วมกัน
│   └── main.ts               # Entry point
├── prisma/
│   ├── schema.prisma         # Database schema
│   └── migrations/           # Database migrations
├── frontend/                 # Vue.js frontend
├── docs/                     # Documentation
├── scripts/                  # Scripts
└── package.json
```

### โครงสร้าง Frontend

```
server/frontend/
├── src/
│   ├── components/           # Vue components
│   ├── views/                # Vue views
│   ├── stores/               # Pinia stores
│   ├── services/             # API services
│   ├── utils/                # Utility functions
│   ├── router/               # Vue Router
│   ├── types/                # TypeScript types
│   └── main.ts               # Entry point
├── public/                   # Static files
├── docs/                     # Documentation
└── package.json
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

### การจัดการ Authentication

```typescript
// การใช้ Guards
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Get('admin-only')
adminOnly() {
  return 'Admin only content';
}

// การเข้าถึง User จาก Request
@Get('profile')
@UseGuards(JwtAuthGuard)
getProfile(@Request() req) {
  return req.user;
}
```

### การจัดการ Validation

```typescript
// การสร้าง Custom Validator
import { registerDecorator, ValidationOptions } from 'class-validator';

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

### การจัดการ Routing

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard',
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../views/LoginView.vue'),
    meta: { public: true },
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../views/DashboardView.vue'),
  },
  {
    path: '/new',
    name: 'new',
    component: () => import('../views/NewView.vue'),
  },
  {
    path: '/new/create',
    name: 'new-create',
    component: () => import('../views/NewCreateView.vue'),
  },
  {
    path: '/new/:id',
    name: 'new-detail',
    component: () => import('../views/NewDetailView.vue'),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  
  if (to.meta.public) {
    next();
  } else if (!authStore.isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

export default router;
```

## 🧪 การทดสอบ

### การทดสอบ Backend

```typescript
// src/new/new.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { NewService } from './new.service';
import { PrismaService } from '../prisma/prisma.service';

describe('NewService', () => {
  let service: NewService;
  let prisma: PrismaService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        NewService,
        {
          provide: PrismaService,
          useValue: {
            new: {
              create: jest.fn(),
              findMany: jest.fn(),
              findUnique: jest.fn(),
              update: jest.fn(),
              delete: jest.fn(),
            },
          },
        },
      ],
    }).compile();

    service = module.get<NewService>(NewService);
    prisma = module.get<PrismaService>(PrismaService);
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('create', () => {
    it('should create a new item', async () => {
      const createDto = { name: 'Test', value: 100 };
      const expected = { id: '1', ...createDto, createdAt: new Date() };
      
      jest.spyOn(prisma.new, 'create').mockResolvedValue(expected);
      
      const result = await service.create(createDto);
      
      expect(result).toEqual(expected);
      expect(prisma.new.create).toHaveBeenCalledWith({ data: createDto });
    });
  });
});
```

### การทดสอบ Frontend

```typescript
// src/components/__tests__/NewComponent.spec.ts
import { mount } from '@vue/test-utils';
import { describe, it, expect } from 'vitest';
import NewComponent from '../NewComponent.vue';

describe('NewComponent', () => {
  it('renders title correctly', () => {
    const wrapper = mount(NewComponent, {
      props: {
        title: 'Test Title',
      },
    });

    expect(wrapper.find('h3').text()).toBe('Test Title');
  });

  it('renders slot content', () => {
    const wrapper = mount(NewComponent, {
      props: {
        title: 'Test',
      },
      slots: {
        default: '<p>Slot content</p>',
      },
    });

    expect(wrapper.find('.content p').text()).toBe('Slot content');
  });
});
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

# Coverage
npm run test:cov
```

## 🔧 การ Deploy

### การ Deploy Backend

```bash
# Build production
npm run build

# Start production server
npm run start:prod

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
# Backend debugging
npm run start:debug

# Frontend debugging
npm run dev

# Edge debugging
python -m pdb edge/src/app.py
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
