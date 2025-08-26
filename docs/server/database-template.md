# คู่มือการจัดการ PostgreSQL Database - AI Camera System

## การเชื่อมต่อฐานข้อมูล

### 1. ใช้ user postgres ของระบบ Linux:
```bash
sudo -u postgres psql
```

### 2. ดูรายชื่อฐานข้อมูลและผู้ใช้:
```sql
-- ดูรายชื่อฐานข้อมูล
\l

-- ดูรายชื่อผู้ใช้ / roles
\du

-- ออกจาก psql
\q
```

### 3. สร้างฐานข้อมูลและผู้ใช้ (ตัวอย่าง):
```sql
-- สร้างฐานข้อมูล
CREATE DATABASE your_database_name;

-- สร้างผู้ใช้
CREATE USER your_username WITH PASSWORD 'your_secure_password';

-- ให้สิทธิ์ผู้ใช้
GRANT ALL PRIVILEGES ON DATABASE your_database_name TO your_username;
```

### 4. รีเซ็ตรหัสผ่านผู้ใช้:
```sql
ALTER USER your_username WITH PASSWORD 'new_secure_password';
```

### 5. ตรวจสอบ connection ด้วย CLI:
```bash
psql -U your_username -d your_database_name -h localhost -W
```

## การจัดการสิทธิ์

### ให้สิทธิ์เชื่อมต่อฐานข้อมูล:
```sql
GRANT CONNECT ON DATABASE your_database_name TO your_username;
```

### ให้สิทธิ์ใช้งาน schema และตาราง:
```sql
-- เชื่อมต่อฐานข้อมูล
\c your_database_name

-- ให้สิทธิ์ schema
GRANT USAGE ON SCHEMA public TO your_username;
GRANT CREATE ON SCHEMA public TO your_username;

-- ให้สิทธิ์ตาราง
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO your_username;
```

### ให้สิทธิ์สำหรับตารางใหม่ในอนาคต:
```sql
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO your_username;
```

### สิทธิ์เพิ่มเติม (Optional):
```sql
-- ให้สิทธิ์สร้างฐานข้อมูล
ALTER USER your_username CREATEDB;

-- ให้สิทธิ์สร้างผู้ใช้
ALTER USER your_username CREATEROLE;
```

## การตรวจสอบสิทธิ์

```sql
\l                -- ดูสิทธิ์ database
\dn+              -- ดู schema privileges
\dp               -- ดู table privileges
```

## สรุปสิทธิ์

- **GRANT CONNECT ON DATABASE**: ให้เข้าฐานข้อมูลได้
- **GRANT USAGE / ALL PRIVILEGES ON SCHEMA/TABLES/SEQUENCES/FUNCTIONS**: ให้ใช้งานข้อมูลใน DB
- **ALTER DEFAULT PRIVILEGES**: ให้สิทธิ์สำหรับ object ใหม่ในอนาคต

## หมายเหตุความปลอดภัย

⚠️ **คำเตือน**: 
- อย่าใช้รหัสผ่านที่อ่อนแอ
- เปลี่ยนรหัสผ่านเป็นประจำ
- ใช้ environment variables สำหรับข้อมูลที่ละเอียดอ่อน
- ตรวจสอบสิทธิ์ผู้ใช้อย่างสม่ำเสมอ
- สำรองข้อมูลเป็นประจำ

## การตั้งค่า Environment Variables

สร้างไฟล์ `.env` ในโฟลเดอร์ server:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
DB_USER=your_username
DB_PASSWORD=your_secure_password

# Connection String
DATABASE_URL=postgresql://your_username:your_secure_password@localhost:5432/your_database_name
```

## การสำรองข้อมูล

```bash
# สำรองฐานข้อมูล
pg_dump -U your_username -d your_database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# กู้คืนฐานข้อมูล
psql -U your_username -d your_database_name < backup_file.sql
```
