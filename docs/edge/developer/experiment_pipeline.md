🧭 แผนการพัฒนา Experiment Module สำหรับ LPR System
1. ออกแบบโครงสร้างโมดูล
# จัดการคำสั่งจาก user เช่น start/stop test
# UI หรือ API สำหรับเลือกภาพนิ่ง / live frame
# เรียกใช้ detection pipeline แบบ isolated
# จัดการผลลัพธ์ เช่น bounding box, accuracy
# วาดกรอบผลลัพธ์บนภาพ
# เก็บภาพนิ่งสำหรับทดสอบ
# config สำหรับ experiment เช่น threshold
2. แยกการทำงานจาก operating pipeline
flag is_experiment_mode = True
stop operating pipeline
หยุดประมวลผลจาก camera manager

3. สร้าง UI/API สำหรับควบคุมการทดสอบ
ให้ user เลือก:
ภาพนิ่งจาก /assets
หรือ live frame จาก camera_manager.get_low_res_stream()

4. เรียกใช้ detection pipeline แบบ isolated
ใน experiment:
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

🧪 ลำดับการทำงาน
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
ใช้ config แยก