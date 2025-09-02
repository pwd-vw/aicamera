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

