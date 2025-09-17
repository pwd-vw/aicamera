##ใช้ user postgres ของระบบ Linux (ไม่ต้องใช้รหัสผ่าน PostgreSQL):
```bash
 sudo -u postgres psql
```
## ใน prompt ของ psql พิมพ์:
 -- ดูรายชื่อฐานข้อมูล
และรายชื่อ database เช่น:
``` sql
\l
```
List of databases
aicamera_db  | postgres | UTF8 | libc | en_US.UTF-8 | en_US.UTF-8  =Tc/postgres postgres=CTc/postgres +aicamera_user=CTc/postgres

-- ดูรายชื่อผู้ใช้ / roles
```sql
 \du
 ```
 aicamera_user | Create DB

 Exit psql:
```sql
 \q
```

## รีเซ็ตรหัสผ่านผู้ใช้
```bash
 sudo -u postgres psql
```
```sql
 ALTER USER aicamera_user WITH PASSWORD 'new_secure_password';
 \q
```

## 3. ตรวจสอบ connection ด้วย CLI
# psql -U aicamera_user -d aicamera_db -h localhost -W
# -W → ให้ prompt ใส่รหัสผ่าน
# ถ้าสำเร็จ → คุณไม่ต้องสร้างฐานข้อมูลใหม่

#ใช้คำสั่ง GRANT CONNECT ให้ user สามารถเชื่อมต่อฐานข้อมูล:
#GRANT CONNECT ON DATABASE aicamera_db TO aicamera_user;

#ให้สิทธิ์ใช้งาน schema / ตาราง
#โดย default ตารางทั้งหมดอยู่ใน public schema ของ database
#\c aicamera_db
GRANT USAGE ON SCHEMA public TO aicamera_user;
GRANT CREATE ON SCHEMA public TO aicamera_user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aicamera_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aicamera_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO aicamera_user;

#USAGE → ใช้งาน schema ได้
#ALL PRIVILEGES → SELECT, INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
#ใช้ ALTER DEFAULT PRIVILEGES เพื่อให้ future tables ก็สืบทอดสิทธิ์:
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO aicamera_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO aicamera_user;

(Optional) ให้สิทธิ์สร้าง table / schema
ถ้าอยากให้ aicamera_user สร้าง table หรือ schema ใหม่:
ALTER USER aicamera_user CREATEDB;
ALTER USER aicamera_user CREATEROLE; -- ถ้าต้องการสร้าง user ใหม่

4. ตรวจสอบสิทธิ์
\l                -- ดูสิทธิ์ database
\dn+               -- ดู schema privileges
\dp                -- ดู table privileges

สรุป

GRANT CONNECT ON DATABASE → ให้เข้าฐานข้อมูลได้

GRANT USAGE / ALL PRIVILEGES ON SCHEMA/TABLES/SEQUENCES/FUNCTIONS → ให้ใช้งานข้อมูลใน DB

ALTER DEFAULT PRIVILEGES → ให้สิทธิ์สำหรับ object ใหม่ในอนาคต

รายชื่อผู้ใช้ในระบบ (ตาราง public.users)
admin | admin@aicamera.com | role: admin | active: true
ถ้า admin เข้าระบบไม่ได้ (admin / admin123):
สาเหตุที่พบบ่อย: เปลี่ยนรหัสผ่านไปแล้ว, ระบบใช้ hash bcrypt, หรือ login ใช้ email แทน username
แก้ไขแบบเร็ว (รีเซ็ตรหัสผ่านผู้ใช้ admin):
1) สร้าง hash ของรหัสผ่านใหม่
สั่งรัน: node -e "console.log(require('bcryptjs').hashSync('NewStrongPass123', 10))"
จะได้สตริง hash ออกมา
2) อัปเดตในฐานข้อมูล
psql "postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db" -c "UPDATE public.users SET password='ใส่ค่า_HASH_ที่ได้', \"updated_at\"=NOW() WHERE username='admin';"
3) ลองล็อกอินใหม่ด้วย: username: admin, password: NewStrongPass123
หมายเหตุ:
psql ไม่รองรับพารามิเตอร์ ?schema= ในคอนเนคชันสตริง ให้ใช้แบบไม่ใส่ query string ตามตัวอย่างด้านบน
หากระบบรองรับล็อกอินด้วย email ให้ลองด้วย email: admin@aicamera.com ด้วยรหัสผ่านใหม่เช่นกัน

node -e "console.log(require('bcryptjs').hashSync('admin123', 10))"
psql "postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db" -c "UPDATE public.users SET password='$2a$10$bba24MaQPJlyDscEi0EKbOR3pziWywWib.gCQJXblxjwfglUiaE5e', \"updated_at\"=NOW() WHERE username='admin';"

cd server && npm run build | cat

cd .. && ./scripts/aicamera-control.sh restart | cat

journalctl --user -u aicamera-backend -n 20 --no-pager | cat

ls -la server/dist/generated/ | cat
ls -la server/dist/ | cat
find server/dist -name "*prisma*" -type f | cat
ls -la server/dist/generated/ | cat
cd server && npx prisma generate | cat && ls -la dist/generated/ | cat
ls -la dist/generated/prisma/ | cat
npm run build | cat
cd .. && ./scripts/aicamera-control.sh restart | cat
journalctl --user -u aicamera-backend -n 10 --no-pager | cat
cd server && node dist/src/main.js | cat
ls -la dist/src/database/ | cat
cat dist/src/database/prisma.service.js | head -20 | cat
ls -la dist/generated/ | cat
find dist -name "generated" -type d | cat
npx prisma generate | cat && ls -la dist/generated/ | cat
npm run build | cat

## การตรวจสอบระบบ Authentication และ User Management

### สถานะปัจจุบันของระบบ Login

#### 1. ผู้ใช้ที่มีอยู่ในระบบ (ตาราง users)
```sql
SELECT id, username, email, role, is_active, last_login, created_at FROM users ORDER BY created_at;
```

**ผลลัพธ์:**
- **admin** | admin@aicamera.com | role: admin | active: true | last_login: 2025-08-26 11:07:39
- **testuser** | test@example.com | role: viewer | active: true | last_login: 2025-08-26 11:08:44

#### 2. การทดสอบ Login API

**Endpoint:** `POST /auth/login`
**Content-Type:** `application/json`

**ตัวอย่าง Request:**
```bash
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**Response สำเร็จ (HTTP 200):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "f2572f97-2922-4a94-8f99-2c3ca6a90c58",
    "email": "admin@aicamera.com",
    "username": "admin",
    "role": "admin",
    "firstName": null,
    "lastName": null
  }
}
```

#### 3. การทดสอบ Profile API

**Endpoint:** `GET /auth/profile`
**Authorization:** `Bearer <access_token>`

**ตัวอย่าง Request:**
```bash
curl -X GET http://localhost:3000/auth/profile \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Response สำเร็จ:**
```json
{
  "id": "f2572f97-2922-4a94-8f99-2c3ca6a90c58",
  "email": "admin@aicamera.com",
  "username": "admin",
  "role": "admin",
  "firstName": null,
  "lastName": null
}
```

#### 4. การทดสอบ Register API

**Endpoint:** `POST /auth/register`
**Content-Type:** `application/json`

**ตัวอย่าง Request:**
```bash
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "newpass123",
    "email": "newuser@example.com",
    "firstName": "New",
    "lastName": "User",
    "role": "viewer"
  }'
```

**Response สำเร็จ:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "bf38aa8c-5217-4bca-927d-258f5837f21d",
    "email": "newuser@example.com",
    "username": "newuser",
    "role": "viewer",
    "firstName": "New",
    "lastName": "User"
  }
}
```

### การแก้ไขปัญหา Login

#### ปัญหาที่พบและวิธีแก้ไข

1. **รหัสผ่าน Hash ไม่ตรงกัน**
   - **สาเหตุ:** รหัสผ่านในฐานข้อมูลเป็น hash เก่าที่ไม่ตรงกับ bcrypt
   - **วิธีแก้ไข:**
   ```bash
   # สร้าง hash ใหม่สำหรับรหัสผ่าน
   node -e "const bcrypt = require('bcryptjs'); console.log(bcrypt.hashSync('admin123', 10));"
   
   # อัปเดตรหัสผ่านในฐานข้อมูล
   psql "postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db" \
     -c "UPDATE users SET password='\$2a\$10\$znU/ZX36Lmdtrt5bHl1ELOJAD.G5B5r8Ji05/TWZOD09t9KULTsUm', updated_at=NOW() WHERE username='admin';"
   ```

2. **Port Conflict (EADDRINUSE)**
   - **สาเหตุ:** มี Node.js process อื่นใช้ port 3000 อยู่
   - **วิธีแก้ไข:**
   ```bash
   # ตรวจสอบ process ที่ใช้ port 3000
   netstat -tulpn | grep :3000
   
   # ฆ่า process ที่ใช้ port 3000
   kill -9 <PID>
   # หรือ
   pkill -f "node.*main.js"
   ```

3. **AuthModule ไม่ได้ Import**
   - **สาเหตุ:** `AuthModule` ไม่ได้ถูก import ใน `AppModule`
   - **วิธีแก้ไข:** เพิ่ม `AuthModule` ใน `imports` array ของ `app.module.ts`

### สถานะปัจจุบันของระบบ

✅ **ระบบ Authentication ทำงานปกติ**
- Login API: `/auth/login` ✅
- Register API: `/auth/register` ✅  
- Profile API: `/auth/profile` ✅
- JWT Token Generation: ✅
- Password Hashing (bcrypt): ✅
- Database Connection: ✅

### ข้อมูลผู้ใช้เริ่มต้น

| Username | Password | Email | Role | Status |
|----------|----------|-------|------|--------|
| admin | admin123 | admin@aicamera.com | admin | active |
| testuser | testpass123 | test@example.com | viewer | active |

### คำสั่งที่มีประโยชน์

```bash
npx prisma studio --port 5555 &

# ตรวจสอบผู้ใช้ในฐานข้อมูล
psql "postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db" \
  -c "SELECT username, email, role, is_active, last_login FROM users;"

# ทดสอบ login
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# ตรวจสอบ JWT token
curl -X GET http://localhost:3000/auth/profile \
  -H "Authorization: Bearer <your_token>"

# สร้างผู้ใช้ใหม่
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"newuser","password":"newpass","email":"new@example.com","role":"viewer"}'
```
🚀 Next Steps for Complete System
To complete the setup, you need to:
Start PostgreSQL Database:
   sudo systemctl start postgresql
   # or start your PostgreSQL service
Verify Database Connection:
  psql "postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db"
Start the Full System:
   cd server
   DATABASE_URL="postgresql://aicamera_user:aicamera_password@localhost:5432/aicamera_db" \
   UNIX_SOCKET=/tmp/aicamera-backend.sock \
   JWT_SECRET=your-secret-key-change-in-production \
   node dist/src/main.js
Test Login Mechanism:
   curl -X POST http://localhost/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"admin123"}'

🎯 Benefits Achieved
✅ No Port Conflicts: Eliminated TCP ports 3000 and 5173
✅ Better Security: Unix socket provides local-only access
✅ Single Entry Point: All traffic through nginx port 80
✅ Production Ready: Proper caching, compression, security headers
✅ Simplified Deployment: Frontend served as static files
✅ Better Performance: Direct nginx ↔ static files, no JS server for frontend
The system is now configured for production deployment with nginx as the single entry point, eliminating the port conflict issues you experienced.