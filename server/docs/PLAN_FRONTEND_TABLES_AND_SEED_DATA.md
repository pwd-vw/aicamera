# แผนปรับปรุง /server/ Frontend: แสดงทุกตาราง + ข้อมูลตัวอย่าง

## เป้าหมาย

- ให้หน้า **http(s)://.../server/** แสดงผล **ทุกตาราง** จากฐานข้อมูล (ทั้งที่มีข้อมูลแล้วและที่ยังไม่มี)
- สำหรับตารางที่ยังไม่มีข้อมูล ให้ **insert ข้อมูลตัวอย่าง**ตามประเภท/ลักษณะของข้อมูลที่เป็นไปได้ เพื่อใช้ในการออกแบบ UI และพัฒนาระบบในภาพรวม

---

## 1. สถานะปัจจุบัน

- **Frontend** ([server/frontend-app/src/views/ServerHome.vue](server/frontend-app/src/views/ServerHome.vue)): มี `tableConfig` สำหรับ 7 ตาราง — Cameras, Detections, Camera Health, Analytics, System Events, Visualizations, Analytics Events — และดึงข้อมูลจาก API แล้วแสดงเป็น `<table>`
- **ปัญหา:** เมื่อตารางไม่มี record (`rows.length === 0`) ฟังก์ชัน `tableColumns(key)` return `[]` (เพราะใช้ key จากแถวแรก) จึงไม่มีหัวคอลัมน์ แสดงแค่แถว "ไม่มีข้อมูล" โดยไม่มีโครงตารางให้เห็น
- **Backend API**: มี endpoint ครบสำหรับทุกตาราง (GET /cameras, /detections, /camera-health, /analytics, /system-events, /visualizations, /analytics-events)
- **Schema** ([server/database/schema.sql](server/database/schema.sql)): มีแค่ **INSERT ตัวอย่าง cameras** 3 แถว (cam-001, cam-002, cam-003); ตารางอื่นยังไม่มีข้อมูลตัวอย่าง

---

## 2. สิ่งที่ต้องทำ

### 2.1 Frontend: แสดงหัวคอลัมน์แม้ตารางว่าง

เพื่อให้ตารางที่ยังไม่มีข้อมูลยังแสดง **โครงสร้างคอลัมน์** ให้เห็นสำหรับออกแบบ UI:

- กำหนด **รายการคอลัมน์คงที่ (fallback)** ต่อตาราง ใน `ServerHome.vue` (หรือ config แยก) ตาม schema จริง:
  - **cameras**: id, camera_id, name, location_lat, location_lng, location_address, status, detection_enabled, image_quality, upload_interval, configuration, created_at, updated_at
  - **detections**: id, camera_id, timestamp, license_plate, confidence, image_url, image_path, status, metadata, created_at, updated_at (+ _image_link ถ้ามี image)
  - **camera_health**: id, camera_id, timestamp, status, cpu_usage, memory_usage, disk_usage, metadata, created_at
  - **analytics**: id, camera_id, date, total_detections, unique_plates, average_confidence, created_at, updated_at
  - **system_events**: id, camera_id, event_type, event_level, message, metadata, created_at
  - **visualizations**: id, name, description, type, configuration, data_source, refresh_interval, is_active, created_at, updated_at
  - **analytics_events**: id, event_type, event_category, user_id, camera_id, visualization_id, event_data, created_at
- ใน `tableColumns(key)` ถ้า `rows.length === 0` ให้ return รายการคอลัมน์ fallback นี้ แทนการ return `[]`
- ผลลัพธ์: ทุกตารางแสดงหัวคอลัมน์เสมอ และแถวเดียว "ไม่มีข้อมูล" เมื่อยังไม่มี record

### 2.2 ข้อมูลตัวอย่าง (Seed Data)

สร้างไฟล์ SQL สำหรับ insert ข้อมูลตัวอย่าง **ต่อตารางที่มักว่าง** โดยอ้างอิง [server/database/schema.sql](server/database/schema.sql) และความสัมพันธ์ FK:

- **cameras**: มีอยู่แล้วใน schema (cam-001, cam-002, cam-003) — ไม่ต้อง seed ซ้ำ; ถ้า DB ใหม่ที่ยังไม่มี ใช้ INSERT ใน schema หรือรัน seed ที่มี INSERT cameras ด้วย
- **detections**: ต้องมี `camera_id` (UUID จาก cameras) — ใช้ subquery `(SELECT id FROM cameras LIMIT 1)` หรือกำหนดจาก camera ที่มีอยู่; ใส่ตัวอย่างเช่น license_plate, confidence, timestamp, status, metadata (และ image_path เป็น null หรือ path ตัวอย่างถ้าต้องการ)
- **analytics**: หนึ่งแถวต่อ (camera_id, date); ใส่ total_detections, unique_plates, average_confidence
- **camera_health**: ใส่ camera_id, timestamp, status ('healthy'/'degraded'), cpu_usage, memory_usage, disk_usage, metadata
- **system_events**: ใส่ event_type, event_level ('info','warning','error'), message, metadata; camera_id เป็น NULL ได้
- **visualizations**: ใส่ name, description, type ('chart','graph','table','metric','map'), configuration (JSONB), data_source, refresh_interval, is_active
- **analytics_events**: ใส่ event_type, event_category ('user_interaction','system_event','performance','error','security'), event_data (JSONB); camera_id, visualization_id เป็น NULL ได้

**ตำแหน่งไฟล์ที่แนะนำ:** [server/database/seed-sample-data.sql](server/database/seed-sample-data.sql)

**ลำดับการรัน:** ต้องรัน **หลัง** schema (และหลังมี cameras แล้ว) — เพราะ detections, analytics, camera_health, system_events, analytics_events อ้างอิง cameras; analytics_events อาจอ้างอิง visualizations ถ้าใส่

```bash
# หลังสร้าง DB และรัน schema แล้ว (ด้วย postgres)
sudo -u postgres psql -d aicamera_app -f /home/devuser/aicamera/server/database/seed-sample-data.sql
```

หรือถ้าใช้ DB ชื่ออื่น แทน `aicamera_app` ด้วยชื่อนั้น

### 2.3 (ถ้าต้องการ) เอกสารอ้างอิง

- อัปเดต [server/database/README-aicamera-app.md](server/database/README-aicamera-app.md) ให้มีหัวข้อ "ข้อมูลตัวอย่าง (Seed)" และอ้างอิงไฟล์ `seed-sample-data.sql` กับคำสั่งรันด้านบน

---

## 3. สรุปงานที่ต้องทำ

| ลำดับ | งาน | รายละเอียด |
|-------|-----|------------|
| 1 | Frontend: fallback columns | ใน ServerHome.vue เพิ่มรายการคอลัมน์คงที่ต่อ table key; ปรับ tableColumns(key) ให้เมื่อไม่มีแถวใช้รายการนี้เป็นหัวตาราง |
| 2 | สร้าง seed-sample-data.sql | ไฟล์ SQL insert ข้อมูลตัวอย่างสำหรับ detections, analytics, camera_health, system_events, visualizations, analytics_events (อ้างอิง cameras ที่มีอยู่) |
| 3 | อัปเดต README (ถ้าต้องการ) | เพิ่มคำอธิบายและคำสั่งรัน seed ใน README-aicamera-app.md |

---

## 4. ผลลัพธ์ที่ได้

- หน้า /server/ แสดง **ทุกตาราง** พร้อม **หัวคอลัมน์** ชัดเจนแม้ตารางว่าง
- หลังรัน seed แล้ว แต่ละตารางมี **ข้อมูลตัวอย่าง** ตามประเภทที่เหมาะสม ทำให้ออกแบบ UI แสดงผล (ขนาดคอลัมน์ การจัดรูปแบบ JSON วันที่ ฯลฯ) และพัฒนาระบบในภาพรวมได้สะดวก
