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