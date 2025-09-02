## สรุปงานประจำวัน (2025-09-02)

### ภาพรวมการเปลี่ยนแปลง
- ปรับปรุงการแสดงผลวิดีโอสดในหน้า `experiments/singleshot_detection`
- เปลี่ยนไปใช้สตรีมแบบความละเอียดต่ำ (lores) ให้สอดคล้องกับสตรีมที่ใช้ในงานตรวจจับ
- เพิ่มปลายทางสตรีม lores บนฝั่งแบ็กเอนด์
- จัดแมปตัวแปรเมทาดาทากล้องจากแบ็กเอนด์มายังฟรอนต์เอนด์ให้ถูกต้อง
- จัดรูปแบบตัวเลขแสดงผลเป็นทศนิยม 3 ตำแหน่ง

### รายละเอียดสำคัญ
- แก้ปัญหา “Loading video feed...” ไม่หาย โดย:
  - เพิ่มกลไกตรวจสอบ `naturalWidth` ของ `<img>` แบบเป็นช่วง เพื่อแสดงสตรีมทันทีเมื่อมีเฟรมแรก แม้เหตุการณ์ `load` ของ MJPEG จะไม่ยิง
  - ปรับปรุงการสลับสถานะ visibility ทั้งคลาส Bootstrap และ inline style เพื่อให้ภาพแสดงผลแน่นอน
  - ยืดเวลาหน่วงก่อนขึ้น error เพื่อลด false negative ระหว่างสตรีมวอร์มอัพ

- ย้ายสคริปต์เพจไปไว้ในบล็อก `additional_js` ของ `base.html` เพื่อให้สคริปต์ถูกโหลดและรันจริงบนเพจ

- เปลี่ยนสตรีมบนหน้า Single Shot ไปใช้ lores:
  - เพิ่มเอ็นด์พอยต์ใหม่ `GET /camera/video_feed_lores` (เลือกใช้บริการสตรีมถ้ามี ไม่เช่นนั้นใช้ตัวสร้างเฟรม lores โดยตรง)
  - ปรับ `img#liveStream` และลิงก์ “Open stream in new tab” ให้ชี้ไปยัง lores
  - อัปเดตโค้ด cache-busting ให้ใช้ URL lores

- ปรับแมปเมทาดาทากล้องบริเวณ `#cameraMetadata`:
  - ดึงค่าจาก `GET /camera/api/metadata_summary`
    - exposureTime ← `camera_settings.exposure_time_ms`
    - analogGain ← `camera_settings.total_gain`
    - lensPosition ← `camera_settings.focus_distance`
    - focusFoM ← `experimental_indicators.focus_confidence` (หรือตกลง `image_quality.focus_quality`)
  - สำหรับค่า Temperature และ Lux ดึงจาก `GET /camera/api/metadata` (เช็คใน `frame_metadata`)

- จัดรูปแบบการแสดงตัวเลขเป็นทศนิยม 3 ตำแหน่งในฟรอนต์เอนด์ เพื่อให้ค่าดูอ่านง่ายและสอดคล้องกัน

### ไฟล์ที่แก้ไข/เพิ่ม
- เพิ่ม: `edge/src/web/blueprints/camera.py` → เอ็นด์พอยต์ใหม่ `/camera/video_feed_lores`
- แก้ไข: `edge/src/web/templates/experiments/singleshot_detection.html`
  - สลับ URL สตรีมไปยัง lores
  - ปรับกลไกแสดง/ซ่อนวิดีโอและตัวตรวจสอบเฟรมแรก
  - ย้ายสคริปต์ไปยังบล็อก `additional_js`
  - จัดแมปเมทาดาทา และฟอร์แมตตัวเลข 3 ตำแหน่ง

### ผลกระทบ
- การแสดงผลวิดีโอในหน้า Single Shot โหลดได้เสถียรมากขึ้น และใช้แหล่งสตรีมเดียวกับงานตรวจจับจริง (lores) ช่วยลดแรงประมวลผล
- เมทาดาทากล้องแสดงค่าที่ถูกต้องและอ่านง่ายขึ้น

### ขั้นตอนถัดไป (ถ้ามี)
- เพิ่มตัวบ่งชี้หน่วย (เช่น ms, °C) ใต้ค่าที่แสดงในเมทาดาทา
- เพิ่มตัวเลือกสลับระหว่าง main stream และ lores ตามความต้องการใช้งาน

---

### รายการ Commit วันนี้ (YYYY-MM-DD)
หมายเหตุ: เวลาเป็นเขตเวลาเซิร์ฟเวอร์ (local)

- 43a4287 | 2025-09-02 19:09:46 | docs: add ExclusiveSummary_20250902 (Thai) summarizing today’s changes
- cb742e6 | 2025-09-02 19:07:22 | experiments: switch to lores stream, improve live stream visibility, map camera metadata, and format values to 3 decimals
- 085b0cb | 2025-09-02 17:32:33 | Fix ARIA accessibility issues and implement cache busting for detection dashboard
- 15bac4c | 2025-09-02 17:01:17 | Footer attribution update and recent detection UI fallbacks/fixes.
- 0565c5f | 2025-09-02 16:59:49 | chore(web): update footer attribution; detection UI fixes and fallbacks
- 97f349e | 2025-09-02 16:45:32 | chore(web): add favicon.ico and link in base template to fix 404
- 446ede1 | 2025-09-02 16:06:42 | feat(detection): DB-backed stats on dashboard; show model names; periodic refresh; fix missing CSS reference and extra endblock; update API docs for status payload
- 70943f9 | 2025-09-02 14:26:49 | detection: harden image saving and DB consistency
- 02e7c81 | 2025-09-02 14:18:04 | docs: Merge variable conflict prevention guide into VARIABLE_MANAGEMENT.md
- 6e07d27 | 2025-09-02 14:13:19 | docs: Merge API documentation into single comprehensive reference
- bd80278 | 2025-09-02 14:04:25 | remove duplicate document
- 656b602 | 2025-09-02 14:03:39 | docs: Update VARIABLE_MANAGEMENT.md with today's dashboard improvements
- 8ee426c | 2025-09-02 13:58:16 | docs: Update API reference and create UI Dashboard documentation
- 93d40a5 | 2025-09-02 13:52:04 | feat: Enhance main dashboard with toggle functionality and health monitoring improvements
- b17386b | 2025-09-02 11:36:56 | fix: Complete CSS performance optimization and cache-control headers
- da63307 | 2025-09-02 11:29:11 | fix: Optimize CSS performance and cache-control headers
- f93e055 | 2025-09-02 11:22:18 | fix: Remove deprecated Pragma headers for security compliance
- c005281 | 2025-09-02 11:14:53 | fix: Resolve 'str' object has no attribute 'headers' error
- e545fba | 2025-09-02 10:05:23 | fix: Resolve CSS compatibility and cache-control issues
- df8194d | 2025-09-02 09:51:25 | fix: Add accessibility attributes to all buttons
- 51d62f2 | 2025-09-02 09:31:34 | refactor: Reorganize systemd services and cleanup files
- 21477ab | 2025-09-02 09:30:03 | feat: Implement Manual Capture System for Camera Dashboard
- 4bed349 | 2025-09-02 00:10:58 | Complete AI Camera v2.0 fixes: video feed, WebSocket stability, navigation browser connection, and smart kiosk browser handler

