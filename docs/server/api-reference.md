# API Reference - คู่มือการใช้งาน API

## 📋 ภาพรวม

AI Camera System API เป็น RESTful API ที่พัฒนาด้วย NestJS สำหรับจัดการระบบกล้องตรวจจับอัจฉริยะ ประกอบด้วยระบบ Authentication, การจัดการกล้อง, การตรวจจับ, และการวิเคราะห์ข้อมูล

## 🔐 การยืนยันตัวตน (Authentication)

### การเข้าสู่ระบบ

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "เข้าสู่ระบบสำเร็จ",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": "uuid",
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  },
  "timestamp": "2025-08-25T21:30:00Z"
}
```

### การลงทะเบียน

```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "firstName": "ชื่อ",
  "lastName": "นามสกุล",
  "role": "operator"
}
```

### การรีเฟรช Token

```http
POST /auth/refresh
Authorization: Bearer <refresh_token>
```

### การออกจากระบบ

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

### การดูข้อมูลโปรไฟล์

```http
GET /auth/profile
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "id": "f2572f97-2922-4a94-8f99-2c3ca6a90c58",
  "email": "admin@aicamera.com",
  "username": "admin",
  "role": "admin",
  "firstName": null,
  "lastName": null,
  "isActive": true,
  "lastLogin": "2025-08-26T14:48:05.116Z",
  "createdAt": "2025-08-26T14:48:05.116Z",
  "updatedAt": "2025-08-26T14:48:05.116Z"
}
```

### การแก้ไขข้อมูลโปรไฟล์

```http
PUT /auth/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "firstName": "ชื่อใหม่",
  "lastName": "นามสกุลใหม่"
}
```

### การเปลี่ยนรหัสผ่าน

```http
PUT /auth/change-password
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "currentPassword": "oldpassword123",
  "newPassword": "newpassword123"
}
```

### การสร้างผู้ดูแลระบบ (Admin Only)

```http
POST /auth/create-admin
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "username": "newadmin",
  "email": "admin@example.com",
  "password": "password123",
  "firstName": "ชื่อ",
  "lastName": "นามสกุล"
}
```

**Response:**
```json
{
  "id": "4eb5a9f6-8230-4cfe-be64-e91b958e88f9",
  "email": "admin@example.com",
  "username": "newadmin",
  "role": "admin",
  "firstName": "ชื่อ",
  "lastName": "นามสกุล",
  "isActive": true,
  "lastLogin": null,
  "createdAt": "2025-08-26T14:48:05.116Z",
  "updatedAt": "2025-08-26T14:48:05.116Z"
}
```

## 🖥️ การจัดการระบบ (System Management)

### ดูสถานะระบบ

```http
GET /system/status
```

**Response:**
```json
{
  "success": true,
  "status": "[2025-08-26 15:23:50] AI Camera Services Status\n==================================\naicamera-backend: ACTIVE\naicamera-frontend: ACTIVE\nnginx: ACTIVE\n\n[2025-08-26 15:23:50] Service Status:\nNginx (Port 80):\n  Port 80 is in use\ntcp6       0      0 :::80                   :::*                    LISTEN      nginx\n\nBackend Unix Socket:\n  Unix socket exists: /tmp/aicamera-backend.sock\nsrw-rw-rw- 1 devuser devuser 0 Aug 26 21:40 /tmp/aicamera-backend.sock\n\n[2025-08-26 15:23:50] Service Logs (last 5 lines):\n...",
  "timestamp": "2025-08-26T08:23:50.830Z"
}
```

### ติดตั้ง Services

```http
POST /system/install
```

**Response:**
```json
{
  "success": true,
  "message": "Services installed successfully",
  "output": "[2025-08-26 15:16:31] Installing AI Camera services...\n[2025-08-26 15:16:31] Installing aicamera-backend...\nCreated symlink /home/devuser/.config/systemd/user/default.target.wants/aicamera-backend.service\n[2025-08-26 15:16:31] aicamera-backend installed and enabled\n...",
  "timestamp": "2025-08-26T08:16:31.123Z"
}
```

### เริ่มต้น Services

```http
POST /system/start
```

**Response:**
```json
{
  "success": true,
  "message": "Services started successfully",
  "output": "[2025-08-26 15:23:22] Starting AI Camera services...\n[2025-08-26 15:23:22] Starting aicamera-backend...\n[2025-08-26 15:23:22] aicamera-backend started successfully\n...",
  "timestamp": "2025-08-26T08:23:22.456Z"
}
```

### หยุด Services

```http
POST /system/stop
```

**Response:**
```json
{
  "success": true,
  "message": "Services stopped successfully",
  "output": "[2025-08-26 15:25:10] Stopping AI Camera services...\n[2025-08-26 15:25:10] Stopping aicamera-backend...\n[2025-08-26 15:25:10] aicamera-backend stopped\n...",
  "timestamp": "2025-08-26T08:25:10.789Z"
}
```

### รีสตาร์ท Services

```http
POST /system/restart
```

**Response:**
```json
{
  "success": true,
  "message": "Services restarted successfully",
  "output": "[2025-08-26 15:26:15] Restarting AI Camera services...\n[2025-08-26 15:26:15] Restarting aicamera-backend...\n[2025-08-26 15:26:15] aicamera-backend restarted successfully\n...",
  "timestamp": "2025-08-26T08:26:15.012Z"
}
```

### Build และ Deploy

```http
POST /system/build
```

**Response:**
```json
{
  "success": true,
  "message": "Build and deploy completed successfully",
  "output": "[2025-08-26 15:27:30] Building and deploying AI Camera...\n[2025-08-26 15:27:30] Building backend...\n[2025-08-26 15:27:35] Building frontend...\n[2025-08-26 15:27:40] Build completed successfully\n...",
  "timestamp": "2025-08-26T08:27:40.345Z"
}
```

## 📹 การจัดการกล้อง (Cameras)

### ดูรายการกล้องทั้งหมด

```http
GET /cameras
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "success": true,
  "message": "ดึงข้อมูลกล้องสำเร็จ",
  "data": [
    {
      "id": "uuid",
      "cameraId": "CAM001",
      "name": "กล้องทางเข้า",
      "locationLat": 13.7563,
      "locationLng": 100.5018,
      "locationAddress": "ถนนสุขุมวิท กรุงเทพฯ",
      "status": "active",
      "detectionEnabled": true,
      "imageQuality": "high",
      "uploadInterval": 30,
      "createdAt": "2025-08-25T10:00:00Z",
      "updatedAt": "2025-08-25T21:30:00Z"
    }
  ],
  "timestamp": "2025-08-25T21:30:00Z"
}
```

### ดูข้อมูลกล้องเฉพาะ

```http
GET /cameras/{id}
Authorization: Bearer <access_token>
```

### สร้างกล้องใหม่

```http
POST /cameras
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "cameraId": "CAM002",
  "name": "กล้องทางออก",
  "locationLat": 13.7563,
  "locationLng": 100.5018,
  "locationAddress": "ถนนสุขุมวิท กรุงเทพฯ",
  "imageQuality": "high",
  "uploadInterval": 30,
  "detectionEnabled": true
}
```

### แก้ไขข้อมูลกล้อง

```http
PUT /cameras/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "กล้องทางออก (อัพเดท)",
  "status": "inactive"
}
```

### ลบกล้อง

```http
DELETE /cameras/{id}
Authorization: Bearer <access_token>
```

### ดูสถานะสุขภาพกล้อง

```http
GET /cameras/{id}/health
Authorization: Bearer <access_token>
```

## 🚗 การจัดการการตรวจจับ (Detections)

### ดูรายการการตรวจจับ

```http
GET /detections
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `cameraId`: ID ของกล้อง
- `licensePlate`: ป้ายทะเบียน
- `status`: สถานะ (pending, processed, failed)
- `startDate`: วันที่เริ่มต้น
- `endDate`: วันที่สิ้นสุด
- `minConfidence`: ความเชื่อมั่นขั้นต่ำ
- `maxConfidence`: ความเชื่อมั่นสูงสุด
- `page`: หน้า
- `limit`: จำนวนรายการต่อหน้า

**Response:**
```json
{
  "success": true,
  "message": "ดึงข้อมูลการตรวจจับสำเร็จ",
  "data": [
    {
      "id": "uuid",
      "cameraId": "CAM001",
      "timestamp": "2025-08-25T21:30:00Z",
      "licensePlate": "กข1234",
      "confidence": 0.95,
      "imageUrl": "https://example.com/images/detection.jpg",
      "locationLat": 13.7563,
      "locationLng": 100.5018,
      "vehicleMake": "Toyota",
      "vehicleModel": "Camry",
      "vehicleColor": "ขาว",
      "vehicleType": "รถยนต์",
      "status": "processed",
      "createdAt": "2025-08-25T21:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 100,
    "totalPages": 10
  },
  "timestamp": "2025-08-25T21:30:00Z"
}
```

### ดูข้อมูลการตรวจจับเฉพาะ

```http
GET /detections/{id}
Authorization: Bearer <access_token>
```

### สร้างการตรวจจับใหม่

```http
POST /detections
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "cameraId": "CAM001",
  "licensePlate": "กข1234",
  "confidence": 0.95,
  "imageUrl": "https://example.com/images/detection.jpg",
  "vehicleMake": "Toyota",
  "vehicleModel": "Camry",
  "vehicleColor": "ขาว"
}
```

### แก้ไขข้อมูลการตรวจจับ

```http
PUT /detections/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "status": "processed",
  "vehicleColor": "ดำ"
}
```

### ลบการตรวจจับ

```http
DELETE /detections/{id}
Authorization: Bearer <access_token>
```

### ดูสถิติการตรวจจับ

```http
GET /detections/stats
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `cameraId`: ID ของกล้อง
- `startDate`: วันที่เริ่มต้น
- `endDate`: วันที่สิ้นสุด
- `groupBy`: จัดกลุ่มตาม (day, hour, camera)

## 📊 การวิเคราะห์ข้อมูล (Analytics)

### ดูรายการเหตุการณ์การวิเคราะห์

```http
GET /analytics-events
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `eventType`: ประเภทเหตุการณ์
- `eventCategory`: หมวดหมู่เหตุการณ์
- `userId`: ID ผู้ใช้
- `cameraId`: ID กล้อง
- `startDate`: วันที่เริ่มต้น
- `endDate`: วันที่สิ้นสุด

### สร้างเหตุการณ์การวิเคราะห์

```http
POST /analytics-events
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "eventType": "detection",
  "eventCategory": "system_event",
  "cameraId": "CAM001",
  "eventData": {
    "licensePlate": "กข1234",
    "confidence": 0.95
  }
}
```

### ดูสถิติการวิเคราะห์

```http
GET /analytics-events/stats
Authorization: Bearer <access_token>
```

## 📈 การแสดงผลข้อมูล (Visualizations)

### ดูรายการการแสดงผล

```http
GET /visualizations
Authorization: Bearer <access_token>
```

### สร้างการแสดงผลใหม่

```http
POST /visualizations
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "กราฟการตรวจจับรายวัน",
  "description": "แสดงจำนวนการตรวจจับต่อวัน",
  "type": "chart",
  "configuration": {
    "chartType": "line",
    "dataSource": "detections",
    "xAxis": "date",
    "yAxis": "count"
  },
  "dataSource": "detections",
  "refreshInterval": 300,
  "isActive": true
}
```

### แก้ไขการแสดงผล

```http
PUT /visualizations/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "กราฟการตรวจจับรายวัน (อัพเดท)",
  "isActive": false
}
```

### ลบการแสดงผล

```http
DELETE /visualizations/{id}
Authorization: Bearer <access_token>
```

## 👥 การจัดการผู้ใช้ (Users)

### ดูรายการผู้ใช้ (Admin Only)

```http
GET /users
Authorization: Bearer <access_token>
```

### ดูข้อมูลผู้ใช้เฉพาะ

```http
GET /users/{id}
Authorization: Bearer <access_token>
```

### แก้ไขข้อมูลผู้ใช้

```http
PUT /users/{id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "firstName": "ชื่อใหม่",
  "lastName": "นามสกุลใหม่",
  "role": "operator"
}
```

### ลบผู้ใช้

```http
DELETE /users/{id}
Authorization: Bearer <access_token>
```

## 🚦 การจำกัดการใช้งาน (Rate Limiting)

### ดูสถิติการจำกัดการใช้งาน (Admin Only)

```http
GET /rate-limit-monitoring/stats
Authorization: Bearer <access_token>
```

### ดูการแจ้งเตือนการจำกัดการใช้งาน (Admin Only)

```http
GET /rate-limit-monitoring/alerts
Authorization: Bearer <access_token>
```

## 🔧 ระบบสุขภาพ (Health)

### ดูสถานะระบบ

```http
GET /health
```

**Response:**
```json
{
  "success": true,
  "message": "ระบบทำงานปกติ",
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-25T21:30:00Z",
    "uptime": 86400,
    "version": "2.0.0",
    "services": {
      "database": "connected",
      "redis": "connected",
      "websocket": "connected"
    }
  },
  "timestamp": "2025-08-25T21:30:00Z"
}
```

### ดูสถานะระบบแบบละเอียด

```http
GET /status
Authorization: Bearer <access_token>
```

## 📁 การอัพโหลดไฟล์ (File Upload)

### อัพโหลดไฟล์ทั่วไป

```http
POST /upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <file>
metadata: {
  "type": "detection_image",
  "cameraId": "CAM001"
}
```

### อัพโหลดภาพ

```http
POST /upload/image
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

file: <image_file>
metadata: {
  "cameraId": "CAM001",
  "detectionId": "uuid"
}
```

## 🔒 การจัดการข้อผิดพลาด (Error Handling)

### รูปแบบการตอบกลับข้อผิดพลาด

```json
{
  "success": false,
  "message": "เกิดข้อผิดพลาด",
  "error": {
    "code": "VALIDATION_ERROR",
    "details": "ข้อมูลไม่ถูกต้อง",
    "fields": {
      "email": "อีเมลไม่ถูกต้อง",
      "password": "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร"
    }
  },
  "timestamp": "2025-08-25T21:30:00Z"
}
```

### รหัสข้อผิดพลาด

| รหัส | คำอธิบาย |
|------|----------|
| `AUTHENTICATION_ERROR` | ข้อผิดพลาดการยืนยันตัวตน |
| `AUTHORIZATION_ERROR` | ข้อผิดพลาดสิทธิ์การเข้าถึง |
| `VALIDATION_ERROR` | ข้อผิดพลาดการตรวจสอบข้อมูล |
| `NOT_FOUND_ERROR` | ไม่พบข้อมูล |
| `RATE_LIMIT_ERROR` | เกินขีดจำกัดการใช้งาน |
| `INTERNAL_ERROR` | ข้อผิดพลาดภายในระบบ |

## 📡 WebSocket Events

### การเชื่อมต่อ

```javascript
const socket = io('ws://localhost:3000', {
  auth: {
    token: 'your_jwt_token'
  }
});
```

### Events ที่รับได้

#### Camera Events
- `camera_status_update`: อัพเดทสถานะกล้อง
- `camera_connected`: กล้องเชื่อมต่อ
- `camera_disconnected`: กล้องตัดการเชื่อมต่อ

#### Detection Events
- `detection_update`: อัพเดทการตรวจจับ
- `new_detection`: การตรวจจับใหม่

#### System Events
- `system_event`: เหตุการณ์ระบบ
- `health_update`: อัพเดทสุขภาพระบบ

### Events ที่ส่งได้

#### Client Events
- `camera_status_request`: ขอสถานะกล้อง
- `camera_config_request`: ขอการตั้งค่ากล้อง
- `camera_config_update`: อัพเดทการตั้งค่ากล้อง
- `camera_control`: ควบคุมกล้อง

## 📋 การจำกัดการใช้งาน (Rate Limits)

### ขีดจำกัดตามสิทธิ์

| สิทธิ์ | จำนวนคำขอต่อนาที | จำนวนคำขอต่อชั่วโมง |
|--------|------------------|-------------------|
| `viewer` | 60 | 1000 |
| `operator` | 120 | 2000 |
| `admin` | 300 | 5000 |

### ขีดจำกัดเฉพาะ Endpoint

| Endpoint | ขีดจำกัด |
|----------|----------|
| `/auth/login` | 5 ครั้งต่อนาที |
| `/auth/register` | 3 ครั้งต่อชั่วโมง |
| `/upload/*` | 10 ครั้งต่อนาที |

## 🔐 การรักษาความปลอดภัย

### Headers ที่จำเป็น

```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### การตรวจสอบสิทธิ์

- **Public**: ไม่ต้องยืนยันตัวตน
- **Authenticated**: ต้องยืนยันตัวตน
- **Admin**: ต้องมีสิทธิ์ Admin
- **Operator**: ต้องมีสิทธิ์ Operator หรือ Admin

## 📚 ตัวอย่างการใช้งาน

### JavaScript/TypeScript

```javascript
// การเข้าสู่ระบบ
const login = async (username, password) => {
  const response = await fetch('/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ username, password })
  });
  return response.json();
};

// การดึงข้อมูลกล้อง
const getCameras = async (token) => {
  const response = await fetch('/cameras', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  return response.json();
};

// การสร้างการตรวจจับใหม่
const createDetection = async (token, detectionData) => {
  const response = await fetch('/detections', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(detectionData)
  });
  return response.json();
};
```

### Python

```python
import requests

# การเข้าสู่ระบบ
def login(username, password):
    response = requests.post('/auth/login', json={
        'username': username,
        'password': password
    })
    return response.json()

# การดึงข้อมูลกล้อง
def get_cameras(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get('/cameras', headers=headers)
    return response.json()

# การสร้างการตรวจจับใหม่
def create_detection(token, detection_data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.post('/detections', 
                           json=detection_data, 
                           headers=headers)
    return response.json()
```

## 📞 การสนับสนุน

หากมีคำถามหรือปัญหาการใช้งาน API กรุณาติดต่อ:

- **Email**: api-support@aicamera.com
- **Documentation**: https://docs.aicamera.com/api
- **GitHub Issues**: https://github.com/your-org/aicamera/issues

---

*API Reference - คู่มือการใช้งาน API สำหรับ AI Camera System* 📡🔧
