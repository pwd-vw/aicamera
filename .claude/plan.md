# WebSocket (Socket.IO) Payload Samples — AI Camera → Server

รูปแบบข้อมูลจริงที่ Edge (AI Camera) ส่งมายัง WebSocket server เครื่องนี้ ผ่าน Socket.IO เพื่อให้ฝั่ง server เตรียมจัดการข้อมูลได้ถูกต้อง

## การเชื่อมต่อ
- **Transport**: Socket.IO (path มักเป็น `/ws/` บน Nginx)

## Events ที่ Edge ส่งออก

| Event | คำอธิบาย | เมื่อไหร่ |
|-------|----------|-----------|
| `camera_register` | ลงทะเบียนกล้องหลังเชื่อมต่อ | หลัง connect สำเร็จ |
| `message` | metadata ผล detection (ป้ายทะเบียน) | แต่ละครั้งที่มีการตรวจจับ |
| `image` | ภาพถ่าย (base64) คู่กับ detection | หลังส่ง `message` ถ้ามีรูป |
| `health_status` | สถานะสุขภาพกล้อง/ระบบ | ตามช่วงเวลาที่กำหนด |

---

## 1. Event: `camera_register`

ส่งครั้งเดียวหลังเชื่อมต่อ Socket.IO สำเร็จ

```json
{
  "camera_id": "aicam_001",
  "checkpoint_id": "cp_gate_01",
  "timestamp": "2025-02-21T10:30:00.123456"
}
```

| Field | Type | คำอธิบาย |
|-------|------|----------|
| `camera_id` | string | รหัสกล้อง (จาก AICAMERA_ID) |
| `checkpoint_id` | string | รหัสจุดตรวจ (จาก CHECKPOINT_ID) |
| `timestamp` | string | ISO 8601 |

---

## 2. Event: `message` (Detection Result)

ส่งทุกครั้งที่มีผลการตรวจจับป้ายทะเบียน (metadata เท่านั้น ไม่มีรูปใน event นี้)

```json
{
  "content": {
    "type": "detection_result",
    "aicamera_id": "aicam_001",
    "checkpoint_id": "cp_gate_01",
    "timestamp": "2025-02-21T10:31:05.123456",
    "vehicles_count": 2,
    "plates_count": 2,
    "ocr_results": [
      { "text": "กก 1234", "confidence": 0.88 },
      { "text": "ขข 5678", "confidence": 0.91 }
    ],
    "vehicle_detections": [
      { "bbox": [80, 100, 280, 280], "confidence": 0.92 },
      { "bbox": [300, 100, 500, 280], "confidence": 0.90 }
    ],
    "plate_detections": [
      { "bbox": [100, 220, 260, 270], "confidence": 0.88 },
      { "bbox": [320, 220, 480, 270], "confidence": 0.86 }
    ],
    "processing_time_ms": 180.5,
    "created_at": "2025-02-21T10:31:05.123456"
  },
  "camera_id": "aicam_001"
}
```

| Field | Type | คำอธิบาย |
|-------|------|----------|
| `content.type` | string | เสมอ `"detection_result"` |
| `content.aicamera_id` | string | รหัสกล้อง |
| `content.checkpoint_id` | string | รหัสจุดตรวจ |
| `content.timestamp` | string | ISO 8601 เวลาที่ตรวจจับ |
| `content.vehicles_count` | number | จำนวนรถที่ตรวจจับได้ |
| `content.plates_count` | number | จำนวนป้ายที่อ่านได้ |
| `content.ocr_results` | array | ข้อความป้าย + confidence แต่ละป้าย |
| `content.vehicle_detections` | array | bbox [x1,y1,x2,y2] + confidence ของรถ |
| `content.plate_detections` | array | bbox + confidence ของป้าย |
| `content.processing_time_ms` | number | เวลาประมวลผล (มิลลิวินาที) |
| `content.created_at` | string | ISO 8601 |
| `camera_id` | string | ซ้ำกับ aicamera_id สำหรับความสะดวก |

**หมายเหตุ**: หลังส่ง event นี้ Edge อาจส่ง event `image` ทันที (รูป base64) เพื่อให้ server ผูกรูปกับ detection นี้ได้ (เช่น ใช้ timestamp หรือลำดับการส่ง)

---

## 3. Event: `image`

ส่งหลัง `message` (detection_result) เมื่อมีไฟล์รูปถ่าย

```json
{
  "data": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBEQACEQADAPwC/wD/2Q==",
  "filename": "detection_20250221_103105.jpg",
  "camera_id": "aicam_001"
}
```

| Field | Type | คำอธิบาย |
|-------|------|----------|
| `data` | string | รูปภาพเข้ารหัส base64 (JPEG) |
| `filename` | string | ชื่อไฟล์แนะนำ รูปแบบ `detection_YYYYMMDD_HHMMSS.jpg` |
| `camera_id` | string | รหัสกล้อง |

การจับคู่ message–image: ใช้ลำดับการรับ (message ก่อน แล้วตามด้วย image ของ detection นั้น) หรือถ้า server ต้องการอาจออกแบบให้ฝั่ง Edge ส่ง `detection_id` / `timestamp` ใน payload image ในอนาคต

---

## 4. Event: `health_status`

ส่งเป็นระยะ (health check)

```json
{
  "type": "health_check",
  "aicamera_id": "aicam_001",
  "checkpoint_id": "cp_gate_01",
  "timestamp": "2025-02-21T10:35:00.000000",
  "component": "camera",
  "status": "healthy",
  "message": "Camera stream OK",
  "details": "{\"fps\": 15, \"resolution\": \"1920x1080\"}",
  "created_at": "2025-02-21T10:35:00.000000"
}
```

| Field | Type | คำอธิบาย |
|-------|------|----------|
| `type` | string | เสมอ `"health_check"` |
| `aicamera_id` | string | รหัสกล้อง |
| `checkpoint_id` | string | รหัสจุดตรวจ |
| `timestamp` | string | ISO 8601 |
| `component` | string | เช่น `"camera"`, `"detection"`, `"system"` |
| `status` | string | เช่น `"healthy"`, `"degraded"`, `"error"` |
| `message` | string | ข้อความสั้นๆ |
| `details` | string | JSON string เพิ่มเติม (อาจเป็น `"{}"`) |
| `created_at` | string | ISO 8601 |

---

## Response Events (Server → Edge)

ฝั่ง Edge รับ event เหล่านี้จาก server ได้ (ถ้า server ส่งกลับ):

| Event | การใช้งาน |
|-------|-----------|
| `message_saved` | บอกว่า message (detection) ถูกบันทึกแล้ว อาจมี `record_id` เพื่อให้ Edge อัปเดตสถานะ sent |
| `image_saved` | บอกว่ารูปถูกบันทึกแล้ว |
| `message_error` | ข้อผิดพลาดจากการบันทึก message |
| `image_error` | ข้อผิดพลาดจากการบันทึก image |

ตัวอย่าง `message_saved` ที่มี `record_id`:

```json
{
  "record_id": 12345,
  "message": "message_saved"
}
```

---

## ไฟล์ตัวอย่าง JSON

ตัวอย่าง payload แบบเต็ม (ใช้กับ automation หรือ unit test ฝั่ง server):

``` json
 {
  "description": "Sample payloads sent by AI Camera Edge to WebSocket server (Socket.IO). Use for server validation and handlers.",
  "camera_register": {
    "event": "camera_register",
    "payload": {
      "camera_id": "aicam_001",
      "checkpoint_id": "cp_gate_01",
      "timestamp": "2025-02-21T10:30:00.123456"
    }
  },
  "message_detection_result": {
    "event": "message",
    "payload": {
      "content": {
        "type": "detection_result",
        "aicamera_id": "aicam_001",
        "checkpoint_id": "cp_gate_01",
        "timestamp": "2025-02-21T10:31:05.123456",
        "vehicles_count": 2,
        "plates_count": 2,
        "ocr_results": [
          { "text": "กก 1234", "confidence": 0.88 },
          { "text": "ขข 5678", "confidence": 0.91 }
        ],
        "vehicle_detections": [
          { "bbox": [80, 100, 280, 280], "confidence": 0.92 }, 
          { "bbox": [300, 100, 500, 280], "confidence": 0.90 }
        ],
        "plate_detections": [
          { "bbox": [100, 220, 260, 270], "confidence": 0.88 },
          { "bbox": [320, 220, 480, 270], "confidence": 0.86 }
        ],
        "processing_time_ms": 180.5,
        "created_at": "2025-02-21T10:31:05.123456"
      },
      "camera_id": "aicam_001"
    }
  },
  "image": {
    "event": "image",
    "payload": {
      "data": "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBEQACEQADAPwC/wD/2Q==",
      "filename": "detection_20250221_103105.jpg",
      "camera_id": "aicam_001"
    }
  },
  "health_status": {
    "event": "health_status",
    "payload": {
      "type": "health_check",
      "aicamera_id": "aicam_001",
      "checkpoint_id": "cp_gate_01",
      "timestamp": "2025-02-21T10:35:00.000000",
      "component": "camera",
      "status": "healthy",
      "message": "Camera stream OK",
      "details": "{\"fps\": 15, \"resolution\": \"1920x1080\"}",
      "created_at": "2025-02-21T10:35:00.000000"
    }
  },
  "response_message_saved": {
    "event": "message_saved",
    "payload_example_from_server": {
      "record_id": 12345,
      "message": "message_saved"
    }
  }
}
```