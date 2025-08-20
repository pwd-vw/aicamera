**Raspberry Pi 5 + Camera Module 3 + Hailo 8 AI Accelerator** 🚀  

# 🚗 Edge AI LPR - Automated License Plate Recognition  
**ใช้ Raspberry Pi 5 + Camera Module 3 + Hailo 8 AI Accelerator**  

## 🔹 Overview
Edge AI LPR เป็นโครงการสำหรับตรวจจับป้ายทะเบียนรถ **แบบ Real-time** บน **Raspberry Pi 5** พร้อมใช้งาน **Camera Module 3** และ **Hailo 8 AI Accelerator** เพื่อให้การประมวลผลเร็วขึ้นโดยใช้ Edge Computing 

## Hardware ที่ต้องใช้
- Raspberry Pi 5 (8GB recommended)
- An official Raspberry Pi camera (e.g., Camera Module 3 or High-Quality Camera)
- Raspberry Pi 5 AI KIT (option 1)
- - Raspberry Pi M.2 M-Key HAT
- - Hailo-8L M.2 M-Key module (Hailo-8 is also supported)
- Raspberry Pi 5 AI HAT (option 2)
- - 26TOPs and 13TOPs are supported
- Active Cooler for the Raspberry Pi 5
- Optional: Heat sink
- Optional: USB camera

## การติดตั้ง Raspberry Pi 5 ร่วมกับ Hailo AI Accelerator:

# 🚀 การติดตั้ง Raspberry Pi 5 + Hailo AI Accelerator  

## 📌 ขั้นตอนการติดตั้ง  
### **1️⃣ ติดตั้งกล้อง**  
เชื่อมต่อ **Camera Module** กับบอร์ด **Raspberry Pi 5** ตามคำแนะนำใน [คู่มือการติดตั้ง Raspberry Pi Camera](https://www.raspberrypi.com/documentation/computers/camera.html)  
💡 **ไม่ต้องเชื่อมต่อพลังงานระหว่างขั้นตอนนี้ เพราะต้องถอดสายไฟอีกครั้งในขั้นตอนถัดไป**

### **2️⃣ ติดตั้ง AI Accelerator (NPU)**
ขึ้นอยู่กับประเภทของ **AI Accelerator** ที่ใช้:
- **AI Kit**: ติดตั้งตามคู่มือของ **AI Kit**
- **AI HAT+**: ติดตั้งตามคู่มือของ **AI HAT+**

### **3️⃣ ตั้งค่า PCIe เป็น Gen3 เพื่อเพิ่มประสิทธิภาพสูงสุด**
```bash
sudo raspi-config
```
เลือก **"6 Advanced Options"** แล้วเลือก **"A8 PCIe Speed"**  
เลือก **"Yes"** เพื่อเปิดใช้งาน **PCIe Gen 3 Mode** → กด **Finish** เพื่อออก  
รีบูต Raspberry Pi:
```bash
sudo reboot
```
💡 **หากใช้ Hailo AI HAT ระบบจะตั้งค่า Gen3 อัตโนมัติ แต่หากใช้ M.2 HAT ต้องกำหนดเอง**

---

## 🔧 **4️⃣ ติดตั้งไลบรารีที่จำเป็น**
```bash
sudo apt install hailo-all
```
### 🚀 **Software ที่ติดตั้งประกอบด้วย**  
✅ **4.1** ไดรเวอร์เคอร์เนลและเฟิร์มแวร์ของ Hailo  
✅ **4.2** HailoRT Middleware ([รายละเอียดเพิ่มเติม](https://github.com/hailo-ai/HailoRT))  
✅ **4.3** Hailo TAPPAS Core (GStreamer + Post-processing) ([ข้อมูลเพิ่มเติม](https://github.com/hailo-ai/Hailo-TAPPAS))  
✅ **4.4** rpicam-apps สำหรับการประมวลผลภาพ ([ตัวอย่างจาก Raspberry Pi](https://www.raspberrypi.com/documentation/))  

📌 **รีบูต Raspberry Pi อีกครั้งเพื่อให้การติดตั้งสมบูรณ์**
```bash
sudo reboot
```

---

## ✅ **5️⃣ ตรวจสอบการติดตั้ง**
เช็คว่า Raspberry Pi ตรวจพบ **Hailo AI Accelerator**
```bash
hailortcli fw-control identify
```
💡 **ถ้าอุปกรณ์ Hailo ถูกต้อง ระบบจะแสดงข้อมูลเกี่ยวกับเวอร์ชันเฟิร์มแวร์และอุปกรณ์**

---

## 🛠 **6️⃣ ทดสอบ TAPPAS Core**
### **6.1 ตรวจสอบ GStreamer Plugin สำหรับ Hailo**
```bash
gst-inspect-1.0 hailotools
```
### **6.2 ตรวจสอบ GStreamer Element สำหรับ Hailo Inference**
```bash
gst-inspect-1.0 hailo
```

---

## 🎥 **7️⃣ ทดลองใช้งาน rpicam-apps**
รันคำสั่งเพื่อแสดงหน้าต่างแสดงภาพจากกล้อง:
```bash
sudo apt update && sudo apt install rpicam-apps
rpicam-hello -t 10s
```
💡 **แสดงภาพจากกล้องเป็นเวลา 10 วินาทีเพื่อตรวจสอบว่ากล้องติดตั้งสำเร็จหรือไม่**

---

## 🤖 **8️⃣ การทดสอบ Object Detection ด้วย Hailo**
### 🟢 **YOLOv6 Model**
```bash
rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolov6_inference.json
```
### 🔵 **YOLOv8 Model**
```bash
rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolov8_inference.json
```
### 🟠 **YoloX Model**
```bash
rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolox_inference.json
```
### 🟣 **YOLOv5 Person & Face Model**
```bash
rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolov5_personface.json
```

---


## 📦 Installation & Setup  
### **1️⃣ Clone Repository**
```bash
git clone https://github.com/popwandee/aicamera.git
cd aicamera
```
### **2️⃣ Configure Environment**
Copy the environment template and customize for your installation:
```bash
# Copy environment template
cp env.template .env.production

# Edit the configuration file
nano .env.production
```

**Important Configuration Options:**
- **AICAMERA_ID**: Unique identifier for this camera (e.g., "1", "2", "main_gate")
- **CHECKPOINT_ID**: Location identifier (e.g., "1", "entrance", "exit")
- **LOCATION_LAT/LOCATION_LON**: GPS coordinates for this camera
- **VEHICLE_DETECTION_MODEL**: Choose Hailo8 or Hailo8L models based on your device
- **CAMERA_LOCATION**: Human-readable location name

### **3️⃣ Validate Configuration**
Run the validation script to check your setup:
```bash
python scripts/validate_config.py
```

### **4️⃣ Install Dependencies**
Run the following script to automate the installation process (installs Python deps, initializes DB, sets up systemd, configures Nginx proxy on port 80 to Gunicorn unix socket):
```bash
# Install all dependencies including gunicorn for production
./install.sh
```

The installation script will:
- ✅ Install all Python dependencies
- ✅ Create necessary directories and files
- ✅ Set up environment configuration
- ✅ Initialize database schema up-front (fresh installs)
- ✅ Configure and start systemd service (Gunicorn via unix:/tmp/aicamera.sock)
- ✅ Install and configure Nginx (port 80) to proxy to Gunicorn socket
- ✅ Validate the installation
- ✅ Open browser to verify the service

### **5️⃣ Verify Installation**
After installation, verify everything is working:
```bash
# Check installation status
python scripts/validate_installation.py

# Check service and proxy
sudo systemctl status aicamera_v1.3.service
sudo systemctl status nginx
curl -i http://localhost/health
```
### **6️⃣ Configure & Setup**
- ตั้งค่า **Camera Module 3**
- **Camera Module 3**: ตั้งค่าแสง โฟกัส และความคมชัด
- ตรวจสอบ **Hailo 8 AI Accelerator**
- **Hailo 8 AI Accelerator**: โหลดโมเดล YOLOv8  
- ตั้งค่า **Systemd สำหรับการรันอัตโนมัติ**
- **Systemd**: ตั้งค่าให้ระบบทำงานอัตโนมัติ

## 🛠️ Troubleshooting

### **Common Issues**

#### **WebSocket Logging Errors**
If you see "Error logging WebSocket action" in the logs:
```bash
# Update database schema
python v1_3/scripts/update_database_schema.py

# Restart service
sudo systemctl restart aicamera_v1.3.service
```

#### **Service Won't Start**
```bash
# Check service status
sudo systemctl status aicamera_v1.3.service

# View detailed logs
sudo journalctl -u aicamera_v1.3.service -f

# Validate installation
python scripts/validate_installation.py

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
sudo tail -n 200 /var/log/nginx/error.log
```

#### **Configuration Issues**
```bash
# Validate configuration
python scripts/validate_config.py

# Check environment file
cat .env.production
```

### **Useful Commands**
```bash
# Service management
sudo systemctl start aicamera_v1.3.service
sudo systemctl stop aicamera_v1.3.service
sudo systemctl restart aicamera_v1.3.service
sudo systemctl status aicamera_v1.3.service

# Log viewing
sudo journalctl -u aicamera_v1.3.service -f
sudo journalctl -u aicamera_v1.3.service --since "1 hour ago"

# Validation
python scripts/validate_installation.py
python scripts/validate_config.py
```  

---

## 🎥 Advanced Camera Configuration (Picamera2)
เพื่อให้ได้ภาพที่คมชัดและเหมาะกับการตรวจจับป้ายทะเบียน **Camera Module 3** สามารถปรับค่าต่าง ๆ ได้ดังนี้  

### **🔍 การตั้งค่าแสง**
```python
picam2.set_controls({"AeExposureMode": 1, "Brightness": 0.5, "Contrast": 1.2})
```
### **🔍 การตั้งค่าโฟกัส**
```python
picam2.set_controls({"AfMode": 1})  # Autofocus Mode
picam2.set_controls({"LensPosition": 50})  # Manual focus adjustment
```
### **🔍 การตั้งค่าความคมชัด**
```python
picam2.set_controls({"Sharpness": 1.5})
```

---

## 🤖 AI Model Configuration (YOLOv8 for Hailo8 & EasyOCR for Thai Plates)
โครงการนี้ใช้โมเดลที่ **Pre-trained** และจัดเก็บใน `resources/`  
| Model | Task | File |
|--------|-----------------|---------------------------------------------|
| Vehicle Detection | ตรวจจับยานพาหนะ | `yolov8n_relu6_car--640x640_quant_hailort_hailo8_1.hef` |
| License Plate Detection | ตรวจจับป้ายทะเบียน | `yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1.hef` |
| Universal License Plate OCR | อ่านป้ายทะเบียนสากล | `yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1.hef` |
| Thai License Plate OCR | ใช้ EasyOCR ชั่วคราว | EasyOCR |

### **🔹 โหลด AI Model และใช้งาน**
```python
import degirum as dg

vehicle_detection_model = dg.load_model("resources/yolov8n_relu6_car--640x640_quant_hailort_hailo8_1.hef")
license_plate_model = dg.load_model("resources/yolov8n_relu6_lp--640x640_quant_hailort_hailo8_1.hef")
ocr_model = dg.load_model("resources/yolov8n_relu6_lp_ocr--256x128_quant_hailort_hailo8_1.hef")
```

---

## 🚀 Running the Project
### ** Use Virtual Environment**
```bash
source setup_env.sh
```
### **🔍 License Plate Detection**
```bash
python detection.py
```
### **📡 System Status Monitoring**
```bash
python edge_status.py
```
### **🔗 Sending Data to Server via SocketIO**
```bash
python send_socket.py
```

---

## 🧪 Testing & Debugging
### **Run Automated Test**
```bash
./run_test.sh
```

---

## ⚙️ Auto-Start with Systemd
Systemd Automation
### **1️⃣ Create a Systemd Service**
```bash
sudo nano /etc/systemd/system/lpr.service
```
### **2️⃣ Add Service Configuration**
```ini
[Unit]
Description=LPR Edge AI Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/aicamera/detection.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```
### **3️⃣ Enable & Start Service**

```bash
sudo systemctl enable lpr.service
sudo systemctl start lpr.service
```
### **🔧 ในส่วนของ Systemd**
เพื่อให้ `send_socket.py` ทำงานอัตโนมัติหลังจากระบบเริ่มต้น **เพิ่มไฟล์ Systemd Service ดังนี้**

#### **1️⃣ สร้างไฟล์ Service**
```bash
sudo nano /etc/systemd/system/send_socket.service
```
#### **2️⃣ เพิ่มการตั้งค่าในไฟล์**
```ini
[Unit]
Description=Send LPR Data to Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/aicamera/send_socket.py
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

#### **3️⃣ เปิดใช้งานและเริ่มต้น Service**
```bash
sudo systemctl enable send_socket.service
sudo systemctl start send_socket.service
```
---

## 📖 Documentation  
สำหรับรายละเอียดของโครงการ อ่านเอกสารเพิ่มเติมใน  
📂 `doc/` (โฟลเดอร์ที่รวบรวมคู่มือการใช้งานและ API Reference)
`doc/docker.md` (การใช้งาน docker เบื้องต้น)
`doc/git.md` (การใช้งาน git control)

---

## 💡 Contributing  
### **🛠 วิธีการมีส่วนร่วม**  
1. Fork Repository  
2. แก้ไขโค้ดและทำ Pull Request  
3. Review & Merge  

### **👥 Contributors**
- [popwandee](https://github.com/popwandee) (Maintainer)
- รายชื่อผู้มีส่วนร่วมอื่น ๆ

---

## 🔐 License  
โครงการนี้เป็น **Open Source** ภายใต้ **MIT License**  
📜 ดูรายละเอียดที่ `LICENSE.md`

---

## ⚠️ Disclaimer  
โครงการนี้พัฒนาเพื่อการศึกษาและการทดลองใช้งานใน Edge AI เท่านั้น 🚀  
ทีมพัฒนาไม่รับผิดชอบต่อการใช้งานในเชิงพาณิชย์หรือการนำไปใช้ในระบบที่ต้องการความแม่นยำสูง

---
 
---
# detection.py

### **🔹 Features in Version 1**
✅ **Real-time License Plate Detection with YOLOv8 (Hailo 8)**  
✅ **OCR Processing for English & Thai Plates (EasyOCR for Thai)**  
✅ **Image Processing & Enhancement (Adaptive Thresholding for OCR)**  
✅ **Automatic Data Saving to SQLite (License Plates & Image Paths)**  
✅ **Similarity Filtering to Avoid Duplicate Entries (OCR & Image Comparison)**  
✅ **Capturing & Processing Video Frames (Picamera2 with Autofocus)**  
✅ **Automatic Image Saving (Timestamp-based Naming)**  
✅ **System Status Logging (Debugging & Performance Tracking)**  
✅ **Auto-Startup via Systemd (Optional)**  

---

### **🔹 Properties & Capabilities**
| **Feature**            | **Description** |
|------------------------|----------------|
| **Vehicle Detection** | Uses YOLOv8 on Hailo8 to detect vehicles |
| **License Plate Detection** | YOLOv8 Model for detecting plates |
| **OCR Processing** | EasyOCR for Thai plates, Hailo OCR for Universal |
| **Image Enhancement** | Adaptive Thresholding for better OCR accuracy |
| **Database Storage** | Saves detection results in SQLite |
| **Similarity Check** | Filters duplicate license plates using text & image comparison |
| **Autofocus Control** | Uses Picamera2 controls for better image capture |
| **Real-time Processing** | Processes frames continuously until stopped |
| **System Monitoring** | Debug logs for image processing, OCR results, and database updates |

---
### **🔎 รายละเอียดคุณสมบัติของเวอร์ชัน 1**
ในเวอร์ชันแรกของระบบ **Edge AI LPR** สำหรับ **Raspberry Pi 5 + Camera Module 3 + Hailo 8 AI Accelerator** มีฟีเจอร์ที่สำคัญดังต่อไปนี้  

✅ **การตรวจจับป้ายทะเบียนแบบเรียลไทม์ด้วย YOLOv8 และ Hailo 8**  
- ใช้โมเดล **YOLOv8** เพื่อระบุ **ยานพาหนะ** และ **ป้ายทะเบียน**  
- ทำงานบน **Hailo 8 AI Accelerator** เพื่อให้การประมวลผลเร็วขึ้น  

✅ **การประมวลผล OCR สำหรับป้ายทะเบียนภาษาอังกฤษและไทย**  
- ใช้ **Hailo OCR** สำหรับป้ายทะเบียนสากล  
- ใช้ **EasyOCR** สำหรับป้ายทะเบียนภาษาไทย (ชั่วคราว)  

✅ **การปรับปรุงภาพเพื่อเพิ่มความแม่นยำของ OCR**  
- ใช้ **Adaptive Thresholding** เพื่อลดแสงสะท้อนบนป้ายทะเบียน  
- แปลงภาพเป็น **Grayscale และ Contrast Enhancement**  

✅ **การบันทึกข้อมูลอัตโนมัติลงฐานข้อมูล SQLite**  
- บันทึก **หมายเลขทะเบียน, เส้นทางไฟล์ภาพ, และเวลาที่ตรวจจับ**  
- รองรับการเรียกดูข้อมูลย้อนหลัง  

✅ **การตรวจจับซ้ำและกรองข้อมูลที่ซ้ำกัน**  
- เปรียบเทียบ **ข้อความที่อ่านจาก OCR กับข้อมูลก่อนหน้า**  
- วิเคราะห์ **ความคล้ายคลึงของภาพป้ายทะเบียน** เพื่อลดการบันทึกที่ไม่จำเป็น  

✅ **การจับภาพและประมวลผลวิดีโอจากกล้องแบบต่อเนื่อง**  
- ใช้ **Picamera2** พร้อม **Autofocus Control**  
- ตั้งค่าโฟกัสให้เหมาะสมกับการตรวจจับ **ป้ายทะเบียนที่เคลื่อนที่เร็ว**  

✅ **การบันทึกภาพอัตโนมัติ พร้อมตั้งชื่อไฟล์ตามเวลา**  
- ใช้ **Timestamp-based Naming** เช่น `20250602_185118_vehicle_detected.jpg`  
- แยกประเภทภาพ **ยานพาหนะ, ป้ายทะเบียน, และภาพที่ใช้ OCR**  

✅ **ระบบการตรวจสอบสถานะและบันทึก Log สำหรับการวิเคราะห์ประสิทธิภาพ**  
- แสดงผลการตรวจจับ และบันทึกข้อมูลทุกขั้นตอน  
- รองรับ **Debugging และการติดตามข้อผิดพลาด**  

✅ **รองรับการทำงานอัตโนมัติผ่าน Systemd (Optional)**  
- สามารถตั้งค่าให้ระบบ **เริ่มทำงานโดยอัตโนมัติหลังจากบูตเครื่อง**  
- ช่วยให้ระบบตรวจจับ **ทำงานต่อเนื่องโดยไม่ต้องเริ่มด้วยมือ**  

---

### **🔎 คุณสมบัติของระบบ**
| **ฟีเจอร์** | **รายละเอียด** |
|-------------|-------------|
| **ตรวจจับยานพาหนะ** | ใช้ **YOLOv8 บน Hailo 8** เพื่อแยกแยะประเภทของยานพาหนะ |
| **ตรวจจับป้ายทะเบียน** | ใช้ **YOLOv8** แยกตำแหน่งป้ายทะเบียนบนรถยนต์ |
| **การอ่านหมายเลขทะเบียน (OCR)** | ใช้ **Hailo OCR สำหรับป้ายทะเบียนสากล**, **EasyOCR สำหรับภาษาไทย** |
| **การปรับปรุงคุณภาพภาพ** | ใช้ **Adaptive Thresholding, Contrast Enhancement** |
| **การบันทึกข้อมูลลงฐานข้อมูล** | เก็บข้อมูลหมายเลขทะเบียน, เส้นทางภาพ, ตำแหน่งกล้อง |
| **การกรองข้อมูลซ้ำซ้อน** | เปรียบเทียบ **หมายเลขทะเบียนและภาพก่อนบันทึกลงฐานข้อมูล** |
| **การจับภาพอัตโนมัติ** | ตั้งค่าการถ่ายภาพและบันทึกภาพแบบต่อเนื่อง |
| **การควบคุมโฟกัสอัตโนมัติ** | ใช้ **Picamera2 Autofocus** เพื่อให้ภาพคมชัด |
| **การประมวลผลแบบเรียลไทม์** | ตรวจจับและอ่านหมายเลขทะเบียนจากกล้อง **แบบต่อเนื่อง** |
| **ระบบตรวจสอบและบันทึกสถานะ** | แสดงผล **Log สำหรับตรวจสอบระบบ** |

---
## send_socket.py
### **🔹 ฟีเจอร์หลักของ `send_socket.py`**
✅ **เชื่อมต่อกับเซิร์ฟเวอร์ผ่าน WebSocket (`ws://lprserver`)**  
✅ **อ่านข้อมูลป้ายทะเบียนที่ยังไม่ส่งจากฐานข้อมูล SQLite**  
✅ **บีบอัดภาพเพื่อประหยัดแบนด์วิดท์ก่อนส่งไปเซิร์ฟเวอร์**  
✅ **แปลงค่าตำแหน่ง GPS (`latitude, longitude`) ให้เป็นข้อมูลที่เซิร์ฟเวอร์ใช้ได้**  
✅ **ส่งข้อมูลไปยังเซิร์ฟเวอร์แบบ Asynchronous (`asyncio`) เพื่อเพิ่มประสิทธิภาพ**  
✅ **อัปเดตสถานะในฐานข้อมูล (`sent_to_server = 1`) เมื่อส่งข้อมูลสำเร็จ**  
✅ **บันทึก Log ข้อมูลที่ส่งไม่สำเร็จเพื่อลองใหม่ภายหลัง**  
✅ **ตั้งค่าการเช็คข้อมูลใหม่ทุก 5 วินาที (`asyncio.sleep(5)`)**  

---

### **🔹 คุณสมบัติและฟังก์ชันสำคัญ**
| **ฟังก์ชัน** | **รายละเอียด** |
|-------------|-------------|
| `send_data(payload)` | ส่งข้อมูลไปยังเซิร์ฟเวอร์ผ่าน WebSocket และรอรับการตอบกลับ |
| `check_new_license_plates()` | ตรวจสอบข้อมูลที่ยังไม่ถูกส่งและส่งไปยังเซิร์ฟเวอร์ |
| `compress_image_bytes(image_path, max_size, quality)` | บีบอัดไฟล์ภาพเพื่อลดขนาดก่อนส่ง |
| `asyncio.sleep(5)` | เช็คข้อมูลใหม่จากฐานข้อมูลทุก 5 วินาที |

---

### **สรุปภาพรวมของโปรแกรมนี้**
## 🔥 **การเตรียมอุปกรณ์**
📌 **ติดตั้ง Raspberry Pi 5 + Hailo AI Accelerator เพื่อใช้งาน Edge AI**  
📌 **ตั้งค่า PCIe ให้เป็น Gen3 เพื่อประสิทธิภาพสูงสุด**  
📌 **ติดตั้งซอฟต์แวร์ที่จำเป็น รวมถึง TAPPAS Core และ GStreamer Plugin**  
📌 **ตรวจสอบการติดตั้ง Hailo AI Accelerator และรันการทดสอบ AI Model**  
📌 **ใช้ rpicam-apps เพื่อแสดงผลจากกล้องและรัน AI Object Detection**

## 🔥 **คุณสมบัติของระบบ**
🚗 **ระบบตรวจจับยานพาหนะและป้ายทะเบียนด้วย AI Accelerator**  
🔤 **อ่านหมายเลขทะเบียนภาษาอังกฤษและไทยผ่าน OCR อัจฉริยะ**  
📸 **ปรับปรุงคุณภาพภาพเพื่อเพิ่มความแม่นยำของ OCR**  
🗃️ **บันทึกข้อมูลลงฐานข้อมูล SQLite พร้อมระบบกรองข้อมูลซ้ำ**  
🎥 **ประมวลผลวิดีโอจากกล้อง Picamera2 แบบต่อเนื่อง**  
⚙️ **รองรับการทำงานอัตโนมัติผ่าน Systemd**  
✅ `send_socket.py` มีหน้าที่ส่งข้อมูล **ป้ายทะเบียนรถที่ตรวจพบ** ไปยัง **เซิร์ฟเวอร์ผ่าน WebSocket**
- ✅ ใช้ **ฐานข้อมูล SQLite** ในการดึงข้อมูลและอัปเดตสถานะ  
- ✅ ปรับปรุง **ระบบบีบอัดภาพ** เพื่อลดขนาดก่อนส่งข้อมูล  
- ✅ ตั้งค่าให้ทำงานอัตโนมัติผ่าน **Systemd (`send_socket.service`)**  
---

## 📋 **เวอร์ชันปัจจุบัน: v1.3.9** (อัปเดตล่าสุด: August 2025)

### 🎯 **สถานะปัจจุบันของโครงการ**
✅ **ระบบ Edge AI LPR** ทำงานบน **Raspberry Pi 5 + Camera Module 3 + Hailo 8 AI Accelerator**  
✅ **สถาปัตยกรรมแบบ Modular** ที่แยกส่วนการทำงานของแต่ละบริการอย่างชัดเจน  
✅ **ระบบ Dashboard แบบ Real-time** ที่แสดงสถานะของทุกบริการ  
✅ **การจัดการสถานะแบบ Modular** ที่ป้องกันการขัดแย้งระหว่างบริการ  
✅ **ระบบ Health Monitoring** ที่ตรวจสอบสถานะของระบบอย่างต่อเนื่อง  
✅ **WebSocket Communication** สำหรับการส่งข้อมูลไปยังเซิร์ฟเวอร์  
✅ **Storage Management** สำหรับการจัดการพื้นที่จัดเก็บข้อมูล  
✅ **Experiments System** สำหรับการทดสอบและปรับแต่งโมเดล AI  

### 🔧 **สถาปัตยกรรมระบบ**
- **Camera Service**: จัดการกล้องและสตรีมมิ่งวิดีโอ
- **Detection Service**: ตรวจจับยานพาหนะและป้ายทะเบียนด้วย AI
- **Health Monitor**: ตรวจสอบสถานะระบบและประสิทธิภาพ
- **WebSocket Sender**: ส่งข้อมูลไปยังเซิร์ฟเวอร์
- **Storage Manager**: จัดการพื้นที่จัดเก็บและไฟล์
- **Database Manager**: จัดการฐานข้อมูล SQLite

---

## 📝 **Changelog: v1.3.3 → v1.3.9**

### 🚀 **v1.3.9 - Checkpoint Vehicle Tracking & Storage Optimization** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **เพิ่มระบบ Vehicle Tracking** ใช้ IoU และ Distance-based tracking เพื่อติดตามรถยนต์ข้ามเฟรม
- ✅ **เพิ่ม Best Detection Selection Algorithm** เลือกการตรวจจับที่ดีที่สุดจากหลายการตรวจจับของรถคันเดียวกัน
- ✅ **เพิ่ม Storage Optimization** ลดการใช้พื้นที่จัดเก็บ 90% (1 การตรวจจับ vs 10-20 ต่อรถยนต์)
- ✅ **เพิ่ม Automatic Cleanup** ลบข้อมูลเก่าและคุณภาพต่ำอัตโนมัติ
- ✅ **เพิ่ม Enhanced Database Schema** รองรับ vehicle tracking และ best detection marking
- ✅ **เพิ่ม Checkpoint Deployment Documentation** คู่มือการใช้งานสำหรับจุดตรวจ

**การเปลี่ยนแปลงทางเทคนิค:**
- เพิ่ม Vehicle Lifecycle Management (Active → Completed → Expired)
- เพิ่ม Selective Image Storage (เฉพาะ best detection)
- เพิ่ม Image Compression based on quality
- เพิ่ม Composite Score Algorithm (OCR confidence + vehicle confidence + distance + image quality)
- เพิ่ม Vehicle Tracking Tables และ Enhanced Detection Results Schema

### 🚀 **v1.3.8 - Modular Dashboard Architecture** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **แก้ไขปัญหาการขัดแย้งของสถานะกล้อง** ระหว่าง Health Service และ Camera Service
- ✅ **เพิ่มฟังก์ชันอัปเดตเฉพาะสำหรับแต่ละบริการ** เพื่อให้แต่ละบริการอัปเดตเฉพาะองค์ประกอบของตัวเอง
- ✅ **ปรับปรุงการจัดการข้อผิดพลาด** สำหรับแต่ละโมดูลบริการ
- ✅ **เพิ่มการติดตามสถานะ** เพื่อป้องกันการเขียนทับข้อมูล
- ✅ **ลบฟังก์ชันที่ล้าสมัย** เพื่อป้องกันความขัดแย้ง
- ✅ **ปรับปรุงความสม่ำเสมอของการแสดงสถานะ** และการติดตาม

**การเปลี่ยนแปลงทางเทคนิค:**
- แยกฟังก์ชัน `updateCameraStatusFromAPI()`, `updateDetectionStatusFromAPI()`, `updateStorageStatusFromAPI()`, `updateExperimentsStatusFromAPI()`, `updateWebSocketSenderStatus()`
- เพิ่มฟังก์ชัน `clearCameraStatus()` และ `isCameraStatusAvailable()`
- ปรับปรุง `updateHealthStatus()` ให้ไม่เขียนทับสถานะกล้องเมื่อมีข้อมูลเฉพาะของกล้อง
- ลบฟังก์ชันที่ล้าสมัย: `setupStatusUpdates()`, `updateSystemStatus()`, `loadInitialStatus()`, `setupWebSocket()`, `updateStreamingStatus()`

### 🔧 **v1.3.7 - System Integration & Documentation** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **อัปเดต README และคู่มือการติดตั้ง**
- ✅ **เพิ่มการตั้งค่า nginx และการเริ่มต้นฐานข้อมูล**
- ✅ **ปรับปรุงการนำเข้า picamera2/libcamera แบบ Lazy Import**
- ✅ **เพิ่มการเปิดใช้งาน venv และ PYTHONPATH สำหรับ libcamera**

### 🛠️ **v1.3.6 - Installation & Database Automation** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **เพิ่มการตรวจสอบการติดตั้งแบบครอบคลุม**
- ✅ **เพิ่มการสร้างฐานข้อมูลอัตโนมัติ**
- ✅ **ปรับปรุงระบบการติดตั้ง**

### ⚙️ **v1.3.5 - Configuration System** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **เพิ่มระบบการตั้งค่าแบบครอบคลุม**
- ✅ **จัดระเบียบเอกสาร**
- ✅ **ปรับปรุงการจัดการการตั้งค่า**

### 🔄 **v1.3.4 - Core System Improvements** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **ปรับปรุงระบบหลัก**
- ✅ **แก้ไขข้อผิดพลาด**
- ✅ **เพิ่มประสิทธิภาพ**

### 🎯 **v1.3.3 - Initial Modular Release** ( August 2025)
**การปรับปรุงหลัก:**
- ✅ **เปิดตัวระบบแบบ Modular Architecture**
- ✅ **แยกส่วนการทำงานของแต่ละบริการ**
- ✅ **เพิ่มระบบ Dashboard แบบ Real-time**
- ✅ **เพิ่มการจัดการสถานะของระบบ**

---

## 🎯 **แผนการพัฒนาต่อ**
- 🔄 **การปรับปรุงประสิทธิภาพของโมเดล AI**
- 📊 **เพิ่มระบบ Analytics และรายงาน**
- 🔐 **เพิ่มระบบความปลอดภัย**
- 🌐 **เพิ่มการรองรับการทำงานแบบ Cloud**
- 📱 **เพิ่ม Mobile Dashboard**
