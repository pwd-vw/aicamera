# คู่มือนักพัฒนา — Server (LPR / AI Camera)

เอกสารนี้สรุปโครงสร้างสถาปัตยกรรม โครงสร้างไฟล์ URL/credentials การ setup และ config การเริ่มระบบ และการแก้ปัญหาส่วน Server เพื่อให้สามารถกลับมาอ่านและพัฒนาต่อยอดได้

---

## 1. โครงสร้างสถาปัตยกรรม (ส่วน Server)

### 1.1 ไดอะแกรมโดยรวม

```mermaid
flowchart TB
  subgraph client [Client]
    Browser[Browser]
    Edge[Edge Client]
  end
  subgraph nginx [Nginx :80]
    Landing["/ → landing"]
    Frontend["/server/ → static"]
    API["/server/api/ → proxy"]
    WS["/ws/ → proxy"]
  end
  subgraph services [Services]
    Backend[backend-api :3000]
    WSService[ws-service :3001]
    MQTTService[mqtt-service]
  end
  subgraph data [Data]
    DB[(PostgreSQL)]
    Storage[storage/]
  end
  Browser --> Landing
  Browser --> Frontend
  Browser --> API
  Browser --> WS
  Edge --> WS
  Edge --> MQTTService
  API --> Backend
  WS --> WSService
  WSService --> Backend
  WSService --> Storage
  Backend --> DB
  Backend --> Storage
```

- **Nginx (port 80):** จุดเข้าเดียวจากภายนอก
  - `location = /` และ `location /` → Landing page จาก `server/landing/`
  - `location /server/` → ไฟล์ static จาก `server/frontend-app/dist/` (Vue SPA)
  - `location /server/api/` → proxy ไป `http://127.0.0.1:3000/server/api/`
  - `location /ws/` → proxy ไป `http://127.0.0.1:3001/ws/` (Socket.IO)
- **backend-api (port 3000):** REST API + TypeORM ต่อ PostgreSQL; global prefix `server/api`
- **ws-service (port 3001):** Socket.IO gateway ที่ path `/ws/` รับข้อมูลจาก Edge แล้วเรียก backend-api (HTTP) และบันทึกภาพที่ `storage/`
- **mqtt-service:** NestJS microservice ต่อ MQTT broker; subscribe topics จาก Edge; ปัจจุบันบันทึกเฉพาะ log ไฟล์

Config อ้างอิง:
- Nginx: [../nginx-lprserver.conf](../nginx-lprserver.conf)
- Backend: [../backend-api/src/main.ts](../backend-api/src/main.ts) (prefix `server/api`, port 3000)
- ws-service: [../ws-service/src/main.ts](../ws-service/src/main.ts) (port 3001)
- mqtt-service: [../mqtt-service/src/main.ts](../mqtt-service/src/main.ts) (MQTT_URL)

---

## 2. โครงสร้างไฟล์/โฟลเดอร์ส่วน Server

| โฟลเดอร์/ไฟล์ | คำอธิบาย |
|----------------|----------|
| `backend-api/` | NestJS REST API (port 3000), TypeORM ต่อ PostgreSQL, serve static frontend ที่ `/server` เมื่อรันตรง |
| `ws-service/` | NestJS WebSocket service (port 3001), Socket.IO path `/ws/`, รับ events จาก Edge → เรียก backend-api + บันทึกภาพที่ storage |
| `mqtt-service/` | NestJS MQTT microservice, subscribe topics จาก Edge, ปัจจุบันบันทึก log อย่างเดียว |
| `frontend-app/` | Vue SPA, build → `dist/`, Nginx serve ที่ `/server/` |
| `database/` | สคริปต์สร้าง DB, schema, grant (schema.sql, init-aicamera-app.sh, grant-lpruser.sql) |
| `landing/` | หน้า Landing (index.html) ที่ `/` |
| `storage/` | โฟลเดอร์เก็บภาพจาก ws-service (และ log ข้อความที่ `receive_message.log` ระดับ server root) |
| `scripts/` | สคริปต์ทดสอบและตรวจสอบ (test_websocket_message.js, verify_services.sh ฯลฯ) |
| `systemd_service/` | systemd units: backend-api.service, websocket.service, mqtt.service |
| `docs/` | เอกสารรวมถึงคู่มือนี้ |

---

## 3. URL และ Credentials

### 3.1 URLs

| ประเภท | URL ตัวอย่าง | หมายเหตุ |
|--------|---------------|----------|
| Landing | `http(s)://<host>/` | ตัวอย่าง host: `localhost:3000` (dev ตรง backend), `lprserver.tail605477.ts.net` (ผ่าน Nginx 80) |
| Frontend (Dashboard) | `http(s)://<host>/server/` | Vue app |
| API base | `http(s)://<host>/server/api` | ใช้เป็น base สำหรับเรียก REST (cameras, detections, camera-health ฯลฯ) |
| WebSocket (Socket.IO) | `http(s)://<host>/ws/` | Path ของ Socket.IO คือ `/ws/` |

เมื่อรัน backend ตรงที่ port 3000 (ไม่มี Nginx): เปิด `http://localhost:3000` จะถูก redirect ไป `/server/` และ API อยู่ที่ `http://localhost:3000/server/api`. WebSocket ที่ localhost:3000 จะไม่ทำงานถ้าไม่มี proxy `/ws/` ไป 3001.

### 3.2 Ports

| บริการ | Port | หมายเหตุ |
|--------|------|----------|
| Nginx | 80 | จุดเข้าเดียวจากภายนอก |
| backend-api | 3000 | ภายในเครื่อง |
| ws-service | 3001 | ภายในเครื่อง, เปิดผ่าน Nginx ที่ `/ws/` เท่านั้น |
| PostgreSQL | 5432 | localhost หรือตาม POSTGRES_HOST |
| MQTT broker | 1883 | ตาม MQTT_URL |

### 3.3 Credentials และตัวแปร Environment

**ไม่ hardcode รหัสผ่านในเอกสารหรือใน repo.** ใช้เฉพาะตัวแปร environment:

- **Database (backend-api):**
  - `DATABASE_URL` — รูปแบบ `postgresql://USER:PASSWORD@HOST:PORT/DATABASE` (แนะนำใช้กับ `aicamera_app`)
  - หรือแยก: `POSTGRES_HOST`, `POSTGRES_USER` (default `postgres`), `POSTGRES_PASSWORD`, `POSTGRES_PORT` (default 5432), `POSTGRES_DB` (default `aicamera`)
  - User ตามที่ grant ใน [../database/grant-lpruser.sql](../database/grant-lpruser.sql) (เช่น `lpruser`). รหัสผ่านตั้งใน `.env` ของ backend-api เท่านั้น.
  - อ้างอิง: [../backend-api/src/app.module.ts](../backend-api/src/app.module.ts)

- **Backend API (จาก ws-service):**
  - `BACKEND_API_URL` — **ต้องชี้ไปที่ base ของ API รวม path** เช่น `http://localhost:3000/server/api` เพื่อให้ request ไปที่ `/server/api/cameras/register`, `/server/api/detections` ฯลฯ ถูกต้อง (backend ใช้ `setGlobalPrefix('server/api')`).
  - ค่า default ในโค้ดคือ `http://localhost:3000` — ถ้าไม่ใส่ path `/server/api` จะได้ 404.

- **Storage (ws-service):**
  - `STORAGE_ROOT` — path ระดับ server root (default คือ `process.cwd()/..`). ภาพบันทึกที่ `storage/` และ message log ที่ `receive_message.log` ภายใต้ root นี้.

- **MQTT (mqtt-service):**
  - `MQTT_URL` — เช่น `mqtt://localhost:1883` หรือ `mqtt://broker:1883`
  - `MQTT_RECEIVE_LOG` — path ไฟล์ log (default ใต้ server root: `mqtt_receive.log`)
  - ถ้า broker ใช้ username/password ต้องตั้งใน connection options ของ client (อ้างอิง [../mqtt-service/MQTT_CLIENT_GUIDE.md](../mqtt-service/MQTT_CLIENT_GUIDE.md))

ตัวอย่าง env ฝั่ง backend-api ดูที่ [../backend-api/.env.example](../backend-api/.env.example) (ไม่มีรหัสผ่านจริง).

---

## 4. การ Setup และ Config

### 4.1 Database

1. สร้างฐานข้อมูลและรัน schema (รันครั้งเดียว, ต้องมีสิทธิ์ sudo):
   ```bash
   cd /home/devuser/aicamera
   ./server/database/init-aicamera-app.sh
   ```
   หรือรันทีละขั้นตาม [../database/README-aicamera-app.md](../database/README-aicamera-app.md)
2. ตั้งค่า environment ของ backend-api ให้ชี้ไปที่ `aicamera_app`:
   ```bash
   export DATABASE_URL="postgresql://lpruser:YOUR_PASSWORD@localhost:5432/aicamera_app"
   ```
   หรือคัดลอก `.env.example` เป็น `.env` แล้วแก้รหัสผ่าน

### 4.2 Network (Nginx)

- ใช้ config ตัวอย่าง: [../nginx-lprserver.conf](../nginx-lprserver.conf)
- สิ่งที่สำคัญ:
  - `location /server/api/` ต้องใช้ `proxy_pass http://127.0.0.1:3000/server/api/` (ส่ง path เต็มไป backend)
  - `location /ws/` → `proxy_pass http://127.0.0.1:3001/ws/`
- ติดตั้งและ reload:
  ```bash
  sudo cp /home/devuser/aicamera/server/nginx-lprserver.conf /etc/nginx/sites-available/lprserver
  sudo ln -sf /etc/nginx/sites-available/lprserver /etc/nginx/sites-enabled/
  sudo nginx -t && sudo systemctl reload nginx
  ```

### 4.3 WebSocket

- ws-service รันที่ port 3001; เปิดสู่ภายนอกผ่าน Nginx ที่ path `/ws/` เท่านั้น (ไม่ expose 3001 โดยตรง)
- ตั้ง `BACKEND_API_URL` (รวม `/server/api`) และ `STORAGE_ROOT` ถ้าไม่ใช้ default
- รูปแบบ topic/payload จาก Edge ดูได้ที่ [../ws-service/WEBSOCKET_CLIENT_GUIDE.md](../ws-service/WEBSOCKET_CLIENT_GUIDE.md)

### 4.4 MQTT

- รัน MQTT broker แยก (ถ้าต้องการ) แล้วตั้ง `MQTT_URL`, `MQTT_RECEIVE_LOG`
- รูปแบบ topic และ payload จาก Edge ดูได้ที่ [../mqtt-service/MQTT_CLIENT_GUIDE.md](../mqtt-service/MQTT_CLIENT_GUIDE.md)

---

## 5. ลำดับการเริ่มทำงาน

อ้างอิง [../systemd_service/README.md](../systemd_service/README.md):

1. **Nginx (port 80)** — เริ่มก่อนหรือพร้อมเครือข่าย
2. **backend-api, websocket, mqtt** — เริ่มหลัง network พร้อม (systemd enable/start)
3. **Frontend** — ไม่มี process แยก; ต้อง build ครั้งเดียว (`npm run build` ใน frontend-app) แล้ว Nginx serve จาก `frontend-app/dist` ที่ `/server/`

คำสั่งตัวอย่าง:
```bash
sudo systemctl enable nginx && sudo systemctl start nginx
sudo cp /home/devuser/aicamera/server/systemd_service/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable backend-api websocket mqtt
sudo systemctl start backend-api websocket mqtt
```

---

## 6. การแก้ปัญหาที่อาจเกิดขึ้น

| อาการ | สาเหตุที่พบบ่อย | วิธีตรวจ/แก้ |
|--------|------------------|----------------|
| API แสดง Not Found เมื่อเข้าผ่าน Nginx (เช่น lprserver) | Nginx ส่ง path ไม่ครบไป backend | ตรวจ `proxy_pass` สำหรับ `/server/api/` ต้องเป็น `http://127.0.0.1:3000/server/api/` (มี path `/server/api/` ด้วย) |
| WebSocket ไม่เชื่อมต่อที่ localhost:3000 | ไม่มี proxy `/ws/` เมื่อรัน backend อย่างเดียว | ใช้ Nginx proxy `/ws/` ไป 3001 หรือทดสอบ ws-service ที่ port 3001 โดยตรง |
| ข้อมูลจาก DB ไม่แสดงใน Dashboard | backend-api ไม่รัน หรือ DATABASE_URL ผิด หรือ Nginx proxy ผิด | ตรวจว่า backend-api รันและ `DATABASE_URL` ถูกต้อง; ตรวจ Nginx ตามข้อแรก |
| ws-service เรียก backend ไม่ถึง (404) | BACKEND_API_URL ไม่มี path `/server/api` | ตั้ง `BACKEND_API_URL=http://localhost:3000/server/api` (หรือ host จริงที่ backend รัน) |
| ภาพ detection ไม่โหลด | backend อ่านไฟล์จาก `detection.imagePath` ไม่ได้ | ให้ backend กับ ws-service ใช้ filesystem เดียวกัน (หรือ shared storage) สำหรับ `storage/` |
| MQTT ได้แค่ log ไม่เห็นใน Dashboard | mqtt-service ยังไม่เขียนลง DB | ปัจจุบันออกแบบให้ log อย่างเดียว; ดูแผนพัฒนาต่อ MQTT → DB ด้านล่าง |

---

## 7. สรุป Data Flow และสถานะความพร้อม

### 7.1 ไดอะแกรม Data Flow

```mermaid
flowchart LR
  subgraph edge [Edge]
    EdgeClient[Edge Client]
  end
  subgraph server [Server]
    WS[ws-service:3001]
    MQTT[mqtt-service]
    Backend[backend-api:3000]
    DB[(PostgreSQL)]
    Storage[storage/]
    Frontend[Frontend /server/]
  end
  EdgeClient -->|Socket.IO /ws/| WS
  EdgeClient -->|MQTT topics| MQTT
  WS -->|HTTP REST| Backend
  WS --> Storage
  Backend --> DB
  Backend -->|read image| Storage
  Frontend -->|/server/api| Backend
```

### 7.2 สถานะตามช่องทาง

| ช่องทาง | การรับข้อมูล | การบันทึก DB | การเก็บภาพ/storage | การแสดงผล Frontend |
|--------|----------------|-------------|---------------------|----------------------|
| **WebSocket** | สมบูรณ์: events.gateway.ts รับ `camera_register`, `message`, `image`, `health_status` | สมบูรณ์: ผ่าน BackendApiService เรียก backend-api → PostgreSQL | สมบูรณ์: StorageService บันทึกภาพที่ `storage/` และ log ที่ `receive_message.log` | สมบูรณ์: backend-api serve cameras, detections, detections/:id/image; ServerHome.vue ดึงแสดง |
| **MQTT** | สมบูรณ์: subscribe camera/+/status, health, detections, system/events, system/health | ยังไม่ทำ: บันทึกเฉพาะ log ไฟล์ `mqtt_receive.log` | ไม่มี | ข้อมูลจาก MQTT ไม่เข้า DB จึงไม่แสดงใน Dashboard |

**สรุป:** Flow ผ่าน WebSocket สมบูรณ์ (Edge → ws-service → backend-api → DB + storage → frontend). Flow ผ่าน MQTT รับและ log ได้ แต่ยังไม่เขียนลง DB จึงไม่แสดงใน UI.

### 7.3 คำแนะนำการทดสอบจาก Edge

- **WebSocket:** ใช้ [../ws-service/WEBSOCKET_CLIENT_GUIDE.md](../ws-service/WEBSOCKET_CLIENT_GUIDE.md)
  - เชื่อมต่อที่ `http(s)://<server>/ws/`
  - ส่ง `camera_register`, `message` (รวม `content.type === 'detection_result'`), `image`, `health_status` ตามรูปแบบที่ gateway รองรับ
  - ตรวจจาก UI ว่า camera / detection / health โผล่และภาพจาก `/server/api/detections/:id/image` แสดงได้
- **MQTT:** ใช้ [../mqtt-service/MQTT_CLIENT_GUIDE.md](../mqtt-service/MQTT_CLIENT_GUIDE.md)
  - Publish ไป topic `camera/<id>/status`, `camera/<id>/health`, `camera/<id>/detections`, `system/events`, `system/health`
  - ตรวจว่า server รับได้จากไฟล์ `mqtt_receive.log`
  - หมายเหตุ: ข้อมูลจาก MQTT ยังไม่แสดงใน Dashboard จนกว่าจะพัฒนาขั้นตอน MQTT → DB

**หมายเหตุ:** ภาพจาก detection ต้องให้ backend กับ ws-service ใช้ storage ร่วมกัน (path เดียวกันหรือ shared volume) เพื่อให้ `GET /server/api/detections/:id/image` อ่านไฟล์ได้

---

## 8. แผนพัฒนาต่อ (MQTT → DB)

เพื่อให้ข้อมูลจาก MQTT แสดงบน Dashboard เหมือน WebSocket:

1. **ออกแบบการเขียน MQTT → DB**
   - ตัวเลือก (ก): ให้ mqtt-service เรียก **backend-api** ผ่าน HTTP (ใช้ endpoint ที่มีอยู่ เช่น cameras/register, detections, camera-health) แบบเดียวกับ ws-service
   - ตัวเลือก (ข): ให้ mqtt-service เชื่อมต่อ **PostgreSQL โดยตรง** (TypeORM) และเขียนตาราง cameras, detections, camera_health ฯลฯ ตาม schema เดิม
   - แมป topic/payload จาก Edge กับรูปแบบที่ backend รองรับ (เช่น `camera/<id>/detections` → สร้าง detection records ผ่าน API หรือ entity)

2. **Implement ใน mqtt-service**
   - ใน handler ของ `camera/+/detections`, `camera/+/health`, `camera/+/status` ฯลฯ เรียก backend API หรือ repository เพื่อบันทึก; จัดการ camera_id → camera UUID (register ถ้ายังไม่มี) คล้าย ws-service

3. **ทดสอบและอัปเดตเอกสาร**
   - ทดสอบ publish จาก Edge ไป MQTT แล้วตรวจว่า record โผล่ใน Dashboard
   - อัปเดตคู่มือนี้และ MQTT_CLIENT_GUIDE ว่าข้อมูลจาก MQTT ถูกบันทึกและแสดงแล้ว
