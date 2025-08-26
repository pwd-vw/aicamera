🧭 แผนการพัฒนา Experiment Module สำหรับ LPR System
1. ออกแบบโครงสร้างโมดูล
experiment/
├── controller.py         # จัดการคำสั่งจาก user เช่น start/stop test
├── interface.py          # UI หรือ API สำหรับเลือกภาพนิ่ง / live frame
├── runner.py             # เรียกใช้ detection pipeline แบบ isolated
├── result_manager.py     # จัดการผลลัพธ์ เช่น bounding box, accuracy
├── visualizer.py         # วาดกรอบผลลัพธ์บนภาพ
├── assets/               # เก็บภาพนิ่งสำหรับทดสอบ
└── config.py             # config สำหรับ experiment เช่น threshold
2. แยกการทำงานจาก operating pipeline
เพิ่ม flag is_experiment_mode ใน detection_manager

เมื่อเริ่ม experiment:

หยุดการส่ง frame ไปยัง operating pipeline

redirect frame ไปยัง experiment.runner

ใช้ threading.Lock() หรือ asyncio.Lock() เพื่อป้องกัน race condition ระหว่าง operating กับ experiment

3. สร้าง UI/API สำหรับควบคุมการทดสอบ
ให้ user เลือก:

ภาพนิ่งจาก /experiment/assets

หรือ live frame จาก camera_manager.get_low_res_stream()

API ตัวอย่าง:
POST /experiment/start
{
  "mode": "static", // หรือ "live"
  "image_path": "assets/test1.jpg"
}
4. เรียกใช้ detection pipeline แบบ isolated
ใน experiment.runner.py:

โหลดภาพหรือ frame

ส่งเข้า detection_processor.run(frame)

เก็บผลลัพธ์ใน result_manager

5. วาดผลลัพธ์และสรุปการทดสอบ
ใช้ visualizer.draw_boxes(frame, detections)

คำนวณ metrics เช่น:

จำนวนป้ายที่ตรวจพบ

ความแม่นยำ (precision/recall)

เวลาประมวลผลต่อ frame

แสดงผลผ่าน API หรือ UI dashboard

6. จัดการการกลับสู่โหมดปกติ
เมื่อ experiment เสร็จ:

clear buffer

reset flag is_experiment_mode = False

resume operating pipeline

🧪 ตัวอย่างลำดับการทำงาน
[User] → เริ่มทดสอบผ่าน API/UI
       → หยุด operating pipeline
       → เลือกภาพนิ่งหรือ live frame
       → ส่งเข้า detection pipeline
       → วาดผลลัพธ์ + คำนวณ metrics
       → แสดงผลลัพธ์
       → กลับสู่โหมดปกติ
🛡️ แนวทางป้องกันผลกระทบต่อระบบหลัก
ใช้ thread isolation หรือ async task queue สำหรับ experiment

ไม่เขียนผลลัพธ์ลง database production โดยตรง

จำกัด experiment ให้ทำงานได้ทีละ session

ใช้ config แยก เช่น experiment_config.yaml