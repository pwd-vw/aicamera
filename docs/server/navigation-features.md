# การนำทางและการจัดการผู้ใช้ - Navigation & User Management Features

## 📋 ภาพรวม

ระบบ AI Camera ได้รับการอัปเดตเพิ่มระบบการนำทางที่ครอบคลุมและการจัดการผู้ใช้แบบเต็มรูปแบบ พร้อมระบบรักษาความปลอดภัยตามบทบาทผู้ใช้

## 🎯 ฟีเจอร์ใหม่

### 1. ระบบนำทาง (Navigation System)
- **เมนูหลัก**: เมนูนำทางที่ส่วนบนของทุกหน้า
- **การ์ดนำทาง**: การ์ดในหน้า Dashboard สำหรับเข้าถึงฟีเจอร์ต่างๆ
- **การควบคุมตามบทบาท**: เมนูที่แสดงแตกต่างกันตามบทบาทผู้ใช้

### 2. การจัดการผู้ใช้ (User Management)
- **สร้างผู้ใช้ใหม่**: เฉพาะ Admin
- **จัดการสถานะผู้ใช้**: เปิด/ปิดใช้งาน
- **ลบผู้ใช้**: ลบผู้ใช้ออกจากระบบ
- **ดูรายการผู้ใช้**: ข้อมูลผู้ใช้ทั้งหมด

### 3. การจัดการโปรไฟล์ (Profile Management)
- **แก้ไขข้อมูลส่วนตัว**: อีเมล, ชื่อ, นามสกุล
- **เปลี่ยนรหัสผ่าน**: เปลี่ยนรหัสผ่านด้วยตนเอง
- **ดูข้อมูลบัญชี**: วันที่สมัคร, เข้าใช้ครั้งล่าสุด

## 🗺️ โครงสร้างการนำทาง

### เมนูหลัก (Header Navigation)
```
[AI Camera Dashboard] ────────────── [ชื่อผู้ใช้ (บทบาท)] [User Management*] [Profile] [Logout]
                                                          (* เฉพาะ Admin)
```

### การ์ดนำทาง (Dashboard Cards)
```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   📹 Cameras    │ │  🚗 Detections  │ │ 👥 User Mgmt*   │
│   จัดการกล้อง   │ │  ดูการตรวจจับ   │ │ จัดการผู้ใช้     │
└─────────────────┘ └─────────────────┘ └─────────────────┘

┌─────────────────┐ ┌─────────────────┐
│  📊 Analytics   │ │ 📈 Visualizations│
│  วิเคราะห์ข้อมูล │ │  แสดงผลข้อมูล   │
└─────────────────┘ └─────────────────┘
```
*เฉพาะ Admin

## 🔐 ระบบรักษาความปลอดภัย

### การควบคุมการเข้าถึงตามบทบาท

#### Admin Users
- ✅ เข้าถึงทุกฟีเจอร์
- ✅ User Management
- ✅ สร้าง/ลบ/จัดการผู้ใช้
- ✅ สร้างผู้ดูแลคนใหม่

#### Regular Users (Viewer)
- ✅ ดู Dashboard
- ✅ จัดการ Profile ส่วนตัว
- ✅ ดูข้อมูลกล้องและการตรวจจับ
- ❌ ไม่เข้าถึง User Management

### Route Guards
```typescript
// Admin-only routes
{ path: '/users', meta: { requiresAdmin: true } }

// ตรวจสอบ JWT token
const payload = JSON.parse(atob(token.split('.')[1]));
if (payload.role !== 'admin') {
  // Redirect to dashboard with access denied
}
```

## 👥 การจัดการผู้ใช้ (User Management)

### การเข้าถึง
- **URL**: `/users`
- **สิทธิ์**: Admin เท่านั้น
- **การเข้าถึง**: เมนูหลัก หรือ Dashboard card

### ฟีเจอร์การจัดการ

#### 1. สร้างผู้ใช้ใหม่
```typescript
interface CreateUserData {
  username: string;      // ชื่อผู้ใช้ (ห้ามซ้ำ)
  email: string;         // อีเมล (ห้ามซ้ำ)
  password: string;      // รหัสผ่าน
  firstName?: string;    // ชื่อจริง (ไม่บังคับ)
  lastName?: string;     // นามสกุล (ไม่บังคับ)
  role: 'viewer' | 'admin'; // บทบาท
}
```

#### 2. ดูรายการผู้ใช้
ตารางแสดงข้อมูล:
- Username, Email, Role
- Status (Active/Inactive)
- Last Login
- Actions (Activate/Deactivate/Delete)

#### 3. การจัดการสถานะ
- **Activate**: เปิดใช้งานผู้ใช้
- **Deactivate**: ปิดใช้งานผู้ใช้
- **Delete**: ลบผู้ใช้ (ไม่สามารถลบตัวเองได้)

## 👤 การจัดการโปรไฟล์ (Profile Management)

### การเข้าถึง
- **URL**: `/profile`
- **สิทธิ์**: ผู้ใช้ทุกคน
- **การเข้าถึง**: เมนูหลัก

### ส่วนประกอบ

#### 1. ข้อมูลโปรไฟล์ (Profile Information)
```typescript
interface ProfileData {
  // แก้ไขได้
  email: string;
  firstName?: string;
  lastName?: string;
  
  // ดูได้อย่างเดียว
  username: string;
  role: string;
  isActive: boolean;
}
```

#### 2. การเปลี่ยนรหัสผ่าน (Change Password)
```typescript
interface ChangePasswordData {
  currentPassword: string;
  newPassword: string;
  confirmPassword: string;
}
```

#### 3. ข้อมูลบัญชี (Account Information)
- User ID
- Member Since (วันที่สมัคร)
- Last Login (เข้าใช้ครั้งล่าสุด)
- Profile Updated (อัปเดตครั้งล่าสุด)

## 🎨 ส่วนติดต่อผู้ใช้ (User Interface)

### การออกแบบ
- **Card-based Layout**: การ์ดสำหรับแต่ละส่วน
- **Responsive Design**: รองรับหน้าจอทุกขนาด
- **Consistent Styling**: สีและรูปแบบเดียวกันทั่วทั้งระบบ

### สีและสัญลักษณ์
- **Admin Role**: 🔴 สีแดง
- **Viewer Role**: 🟢 สีเขียว
- **Active Status**: 🟢 สีเขียว
- **Inactive Status**: ⚫ สีเทา

### ปุ่มและการโต้ตอบ
- **Primary Button**: สีเทาเข้ม
- **Secondary Button**: สีเทาอ่อน
- **Danger Button**: สีแดง (สำหรับการลบ)

## 🔧 การติดตั้งและการกำหนดค่า

### ความต้องการ
- ✅ Backend API ที่มี Auth endpoints
- ✅ Database ที่มีตาราง Users
- ✅ JWT Authentication
- ✅ Role-based permissions

### การตั้งค่าเส้นทาง (Routes)
```typescript
const routes = [
  { path: '/users', component: UserManagementView, meta: { requiresAdmin: true } },
  { path: '/profile', component: UserProfileView },
  // ... other routes
];
```

### การตั้งค่า Route Guards
```typescript
router.beforeEach((to, from, next) => {
  const requiresAdmin = to.matched.some(r => r.meta.requiresAdmin);
  
  if (requiresAdmin) {
    const token = localStorage.getItem('accessToken');
    const payload = JSON.parse(atob(token.split('.')[1]));
    
    if (payload.role !== 'admin') {
      alert('Access denied. Admin privileges required.');
      return next({ name: 'dashboard' });
    }
  }
  
  next();
});
```

## 📊 การใช้งานและสถิติ

### จำนวนผู้ใช้ตามบทบาท
- **Admin Users**: สามารถจัดการระบบทั้งหมด
- **Viewer Users**: ใช้งานฟีเจอร์พื้นฐาน

### การติดตาม
- **Last Login**: ติดตามการเข้าใช้ล่าสุด
- **Profile Updates**: ติดตามการอัปเดตข้อมูล
- **User Activity**: ติดตามกิจกรรมผู้ใช้

## 🚀 การใช้งานจริง

### สำหรับผู้ดูแลระบบ (Admin)
1. **เข้าสู่ระบบ** ด้วยบัญชี Admin
2. **จัดการผู้ใช้** ผ่าน User Management
3. **สร้างบัญชีใหม่** ตามความจำเป็น
4. **ตรวจสอบสถานะ** ผู้ใช้เป็นประจำ

### สำหรับผู้ใช้ทั่วไป (User)
1. **เข้าสู่ระบบ** ด้วยบัญชีที่ได้รับ
2. **อัปเดตโปรไฟล์** ตามต้องการ
3. **เปลี่ยนรหัสผ่าน** เป็นประจำ
4. **ใช้งานฟีเจอร์** ตามสิทธิ์ที่ได้รับ

## 🛡️ ความปลอดภัย

### มาตรการรักษาความปลอดภัย
- ✅ JWT Token validation
- ✅ Role-based access control
- ✅ Password hashing (bcrypt)
- ✅ Input validation
- ✅ CORS protection
- ✅ Rate limiting

### แนวทางปฏิบัติที่ดี
- 🔐 ใช้รหัสผ่านที่แข็งแกร่ง
- 🔄 เปลี่ยนรหัสผ่านเป็นประจำ
- 👥 จำกัดจำนวน Admin users
- 📊 ตรวจสอบ Activity logs
- 🚪 Logout เมื่อไม่ใช้งาน

## 📝 สรุป

ระบบการนำทางและการจัดการผู้ใช้ใหม่ของ AI Camera มีความสมบูรณ์และปลอดภัย พร้อมใช้งานในสภาพแวดล้อมการผลิตจริง ด้วยฟีเจอร์ที่ครอบคลุมและการออกแบบที่ใช้งานง่าย
