ปรับปรุง detection processor pipeline
ให้มีประสิทธิภาพ รองรับการตราวจจับยานพาหนะที่วิ่งเข้าหากล้อง ให้สามารถตรวจจับยานพาหนะได้ดีที่สุด ไม่ซ้ำกัน รองรับหลายสภาพแสดง รองรับการปรับขนาดโดยยังคงสัดส่วนภาพสำหรับการบันทึกและการแสดงผล และการจัดการพื้นที่จัดเก็บ ให้ทำงานได้ต่อเนื่อง ดังนี้
1. pre-image processing , post-image, pre-OCR processing
1.1 ตรวจสอบว่า frame เปลี่ยนแปลงพอจะทำ inference ได้หรือไม่จาก motion/change detection
1.2 ปรับภาพสำหรับ inference (illumination/contrast/denoise)
1.3 ปรับภาพสำหรับบันทึก ( post processing) ให้มีสีธรรมชาติ
1.4 ปรับภาพสำหรับ OCR (Pre-OCR) ให้สามารถอ่านข้อความได้ง่าย ขอบตัวอักษรชัดเจน
2. Algorithm สำหรับจัดการยานพาหนะ (Tracking & deduplication & select best frame)
2.1 ตรวจจับ object enter/leave
2.2 หลีกเลี่ยงการบันทึกซ้ำ (same car) โดยใช้ Track id + temporal window +IoU history
2.3 เลือกภาพที่ดีที่สุดสำหรับอ่านป้าย (best_frame) โดยใช้ weighted score = a sharpness + b plate_conf + y area_ratio + k (plate_centeredness)
3. Deduplication rule 
3.1 ถ้ารถคันเดิมมี track id เดิม อย่าบันทึกใหม่ถ้าช่วงเวลาระหว่าง finalize ของ track เก่าและ start ของ track ใหม่ < re rentry_time_thresh และ similarity (IoU or small desplacement)> 0.2
3.2 ระบุ unique vehicle event โดยใช้ (track_id, approximate arrival_time) หรือ fingerprinting (plate OCR result) เมื่อมี OCR
4. Detection pipeline orchestration (efficiency-focused)
4.1 ออกแบบ pipeline แบบ event-driven และ resource-limited โดย Flow ดังนี้
4.1.1 Capture Frame (raw), keep circular buffer of last N full-res frames and small-res frames for diff (use exist cameraHandler's method)
4.1.2 Compute motion on small frames -> if motion_changed == False skip entirely.
4.1.3 If motion true -> apply enhance_for_detection on small/medium frame -> resize to vehicle detection model input and call vehicle detecion
4.1.4 For each vehicle detection with conf >= conf1_thresh:
- add to tracker.update(detections)
- store candidate crop in track
4.1.5 Periodically (or when track finalize ) for each track candidate run plate detection model on cropped region:
- if plate_conf >= conf2_thresh then crop plate bbox (pad a bit), send to pre_OCR processing and then to OCR workers
- else record detection result and archive frames
4.1.6 OCR run two OCR branches in parallel
(a) custom OCR model accelerated on Hailo if available
(b) easyOCR on CPU as parallel for Thai alphabet.
-Merge results both for manual review.
4.1.7 Save to DB (Vehicle_event_id, track_metadata,vehicle bbox in original scale,plate bbox in original scale, plate text, original scale image path, timestamps, detection confs (vehicle, plate))
5. Resize/ corrdinate mapping/ cropping utilities
5.1 ต้องการ mapping ระหว่าง original <->resized (for model inputs) และ crop แบบ safe padding โดยใช้ letterbox resizing (scale + padding) เพื่อให้ mapping ถูกต้องสำหรับ model
6. Performance, Reliability, Ops
6.1 Resoure tuning and Robustness for CPU, RAM 
6.2 บันทึกภาพต้นฉบับ เมื่อการตรวจจับยานพาหนะได้พร้อมอ่านข้อความได้ชัดเจนที่สุด หรือภาพที่ยานพาหนะชัดเจนที่สุดเมื่อไม่สามารถอ่าน OCR ได้ โดยสิ่งที่คาดหวังดีที่สุดตามบำดับความสำคัญคือ  อ่านข้อความได้ดีที่สุด, ป้ายทะเบียนชัดเจนที่สุด , ภาพยานพาหนะชัดเจนที่สุด ตามลำดับ
6.3 บันทึกไฟล์ภาพที่คุณภาพ 85% เพื่อประหยัดพื้นที่
ุ6.4 Night/headlights: use temporal averaging and highlight suppression( detect over-exposed regions and reduce their weight in preprocing for OCR)