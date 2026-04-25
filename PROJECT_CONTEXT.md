# โครงการ AI Camera — Context Engineering สำหรับ CLAUDE

เอกสารนี้สรุปบริบทโครงการจากที่ได้คุยและพัฒนาร่วมกัน เพื่อใช้เป็น **Context** และ **Rule** สำหรับ CLAUDE ในการพัฒนาต่อไป

---

## 1. วัตถุประสงค์โครงการ

- **ระบบ LPR / AI Camera**: Edge (Python, Raspberry Pi + Hailo) ตรวจจับป้ายทะเบียน ส่งข้อมูลและภาพมายัง Server
- **Server**: รับข้อมูลจาก Edge ผ่าน **WebSocket (Socket.IO)** และ **MQTT** บันทึกลง PostgreSQL และเก็บภาพที่ storage แสดงผลบน Dashboard (Vue) ที่ `/server/`

---

## 2. สิ่งที่พัฒนาร่วมกัน (ส่วน Server ใหม่)

### 2.1 โครงสร้างภายใต้ `server/`

| ส่วน | เทคโนโลยี | หน้าที่ |
|------|-----------|---------|
| **backend-api** | NestJS, TypeORM, PostgreSQL | REST API ที่ global prefix `server/api` (port 3000); serve static frontend ที่ `/server` เมื่อรันตรง |
| **ws-service** | NestJS, Socket.IO | Gateway ที่ path `/ws/` (port 3001); รับ events จาก Edge → เรียก backend-api ผ่าน HTTP + บันทึกภาพที่ storage |
| **mqtt-service** | NestJS, MQTT client | Subscribe topics จาก Edge; บันทึก `camera/+/health` และ `camera/+/status` ลง DB ผ่าน BackendApiService (cameras + camera_health); log ไฟล์ด้วย |
| **frontend-app** | Vue 3 SPA | Build → `dist/`; Nginx serve ที่ `/server/`; ดึงข้อมูลจาก API base `origin + '/server/api'` |
| **database** | PostgreSQL | schema.sql, init-aicamera-app.sh, grant-lpruser.sql, seed-sample-data.sql; DB ชื่อ `aicamera_app` |
| **nginx-lprserver.conf** | Nginx | Proxy `/` → landing, `/server/` → static, `/server/api/` → backend-api, `/ws/` → ws-service |
| **landing** | HTML | หน้า Landing ที่ `/` |
| **storage** | โฟลเดอร์ | ภาพจาก ws-service; backend-api อ่านจาก `detection.imagePath` เพื่อ serve `GET /server/api/detections/:id/image` |
| **docs** | Markdown | DEVELOPER_HANDBOOK.md, แผนและคู่มือ |

### 2.2 Data Flow ที่ทำแล้ว

- **WebSocket (สมบูรณ์):** Edge → Socket.IO `/ws/` → ws-service → BackendApiService (HTTP) → backend-api → PostgreSQL; ภาพ → StorageService → `storage/`; Frontend ดึง cameras, detections, camera-health, ภาพ ผ่าน `/server/api`
- **MQTT (camera/+/health, camera/+/status → DB):** Edge → MQTT topics → mqtt-service → BackendApiService (HTTP) → backend-api → cameras + camera_health; ใช้แสดงใน Edge Control Dashboard (`/server/edge_control`). Topics อื่นยัง log ไฟล์เท่านั้น

### 2.3 ไฟล์อ้างอิงหลัก

- **สถาปัตยกรรมและ setup:** `server/docs/DEVELOPER_HANDBOOK.md`
- **Payload จาก Edge (WebSocket):** `.cursor/plan.md` หรือ `server/ws-service/WEBSOCKET_CLIENT_GUIDE.md`
- **MQTT topics และ payload:** `server/mqtt-service/MQTT_CLIENT_GUIDE.md`
- **Database:** `server/database/README-aicamera-app.md`, `server/database/schema.sql`, `server/database/seed-sample-data.sql`
- **Nginx:** `server/nginx-lprserver.conf`
- **Frontend /server/ (ทุกตาราง):** `server/frontend-app/src/views/ServerHome.vue` (fallback columns เมื่อตารางว่าง)
- **Frontend Edge Control:** `server/frontend-app/src/views/EdgeControl.vue`, `EdgeControlCamera.vue` (dashboard + รายละเอียดกล้อง + log camera_health)
- **E2E ทดสอบและ Debug:** `server/docs/E2E_TEST_AND_DEBUG.md`

---

## 3. URLs และ Environment (สรุป)

- **Frontend:** `http(s)://<host>/server/`  
- **API base:** `http(s)://<host>/server/api`  
- **WebSocket:** `http(s)://<host>/ws/` (path Socket.IO `/ws/`)
- **Ports:** Nginx 80, backend-api 3000, ws-service 3001, PostgreSQL 5432, MQTT 1883
- **Credentials:** ไม่ใส่รหัสผ่านจริงใน repo; ใช้ `DATABASE_URL`, `BACKEND_API_URL`, `MQTT_URL` ฯลฯ ใน `.env` (และ `.env.example` เป็น placeholder เท่านั้น)

---

## 4. หลักการที่ Cursor ต้องยึดถือ (Rules)

### 4.1 ความปลอดภัยและ Config

- **ห้าม hardcode รหัสผ่านหรือข้อมูลละเอียดอ่อน** ในโค้ดหรือเอกสาร; ใช้ตัวแปร environment และ placeholder (เช่น `YOUR_PASSWORD`) ในตัวอย่าง
- **BACKEND_API_URL (ws-service):** ต้องชี้ไปที่ **base ของ API รวม path** เช่น `http://localhost:3000/server/api` ไม่ใช่แค่ `http://localhost:3000` (backend ใช้ `setGlobalPrefix('server/api')`)
- **Nginx proxy `/server/api/`:** ต้องใช้ `proxy_pass http://127.0.0.1:3000/server/api/` (ส่ง path เต็มไป backend) ไม่ใช่ `proxy_pass http://127.0.0.1:3000/`

### 4.2 โครงสร้างและ Data Flow

- **backend-api** เป็นคนเขียน/อ่าน PostgreSQL โดยตรง; **ws-service** ไม่ต่อ DB โดยตรง แต่เรียก backend-api ผ่าน HTTP
- **ภาพ detection:** backend-api อ่านไฟล์จาก `detection.imagePath`; ต้องให้ backend กับ ws-service ใช้ **filesystem เดียวกัน** (หรือ shared storage) สำหรับ `storage/`
- **Frontend:** ใช้ `window.location.origin + '/server/api'` เป็น API base; ตารางที่ไม่มีข้อมูลให้แสดงหัวคอลัมน์จาก **fallbackColumns** ใน ServerHome.vue

### 4.3 การพัฒนาต่อ

- **MQTT → DB:** ทำแล้วสำหรับ `camera/+/health` และ `camera/+/status` (mqtt-service เรียก backend-api → cameras + camera_health); แสดงใน Edge Control (`/server/edge_control`). Topics อื่น (detections, system/events ฯลฯ) ยัง log อย่างเดียว — ถ้าต้องการให้เขียน DB เพิ่มให้แมป payload กับ endpoint ที่มีอยู่
- **เอกสาร:** อัปเดต `server/docs/DEVELOPER_HANDBOOK.md` เมื่อมีขั้นตอน setup หรือสถาปัตยกรรมเปลี่ยน
- **Payload จาก Edge:** รูปแบบ events (camera_register, message, image, health_status) ตาม `.cursor/plan.md` / WEBSOCKET_CLIENT_GUIDE; ถ้าเปลี่ยนรูปแบบต้องอัปเดตทั้ง gateway และเอกสาร

### 4.4 Git และ Repo

- ไฟล์ `.env` ต้องอยู่ใน `.gitignore` และไม่ commit รหัสผ่านจริง
- เอกสารตัวอย่าง (เช่น README) ใช้ placeholder `YOUR_PASSWORD` ไม่ใช้รหัสจริง

---

## 5. สรุปสถานะความพร้อม

| ส่วน | สถานะ |
|------|--------|
| Backend API (cameras, detections, camera-health, cameras/edge-status, analytics, system-events, visualizations, analytics-events, detections/:id/image; Cron ลบ camera_health > 30 วัน) | สมบูรณ์ |
| ws-service (camera_register, message, image, health_status → DB + storage) | สมบูรณ์ |
| mqtt-service (camera/+/health, camera/+/status → backend-api → cameras + camera_health) | สมบูรณ์ |
| Frontend /server/ (ทุกตาราง + fallback columns + Images จาก detections) | สมบูรณ์ |
| Frontend /server/edge_control (dashboard กล้อง + หลอดไฟ + หน้ารายละเอียด + log camera_health) | สมบูรณ์ |
| Nginx (proxy /server/api/, /ws/, static /server/) | สมบูรณ์ (ต้องใช้ path เต็มสำหรับ API) |
| Database (aicamera_app, schema, grant, seed-sample-data) | สมบูรณ์ |

---

การพัฒนาต่อ: อ่านเอกสารนี้ร่วมกับ `server/docs/DEVELOPER_HANDBOOK.md` และ rule ใน `.claude/rules/` (โดยเฉพาะ server-new-stack.mdc) แล้วยึดหลักการด้านบนเป็นหลักในการแก้ไขหรือเพิ่มฟีเจอร์
