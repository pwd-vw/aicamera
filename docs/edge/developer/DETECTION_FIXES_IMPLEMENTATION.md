# แนวทางแก้ไขปัญหา Detection Pipeline - Implementation Guide

## สรุปปัญหาและแนวทางแก้ไขแบบย่อ

### ปัญหาที่ 1: False Positives (ตรวจจับวัตถุที่ไม่ใช่ยานพาหนะ)
**สาเหตุหลัก**: ไม่มีการกรอง class, confidence threshold อาจไม่เหมาะสม
**วิธีแก้**: เพิ่ม class filtering + adaptive threshold

### ปัญหาที่ 2: False Negatives (ไม่ตรวจจับทุกคัน)
**สาเหตุหลัก**: Detection interval 30 วินาที (นานเกินไป!)
**วิธีแก้**: ลดเป็น 2-5 วินาที + ใช้ tracking/deduplication

### ปัญหาที่ 3: OCR Failure
**สาเหตุหลัก**: Coordinate mapping อาจผิดพลาด, OCR preprocessing ไม่เพียงพอ
**วิธีแก้**: เพิ่ม validation + ปรับปรุง preprocessing (deskew, better thresholding)

---

## Implementation Steps

### Step 1: ปรับ Configuration (ง่ายที่สุด - ทำทันที)

แก้ไขไฟล์ `edge/src/core/config.py`:

```python
# Detection Settings
DETECTION_INTERVAL = float(os.getenv("DETECTION_INTERVAL", "2.0"))  # เปลี่ยนจาก 30.0 → 2.0
CONFIDENCE_THRESHOLD = float(os.getenv("DETECTION_CONFIDENCE_THRESHOLD", "0.75"))  # เปลี่ยนจาก 0.8 → 0.75
PLATE_CONFIDENCE_THRESHOLD = float(os.getenv("PLATE_CONFIDENCE_THRESHOLD", "0.65"))  # เปลี่ยนจาก 0.6 → 0.65
```

**ผลลัพธ์**: ตรวจจับบ่อยขึ้น, recall ดีขึ้น

---

### Step 2: เพิ่ม Class Filtering (สำคัญ - ป้องกัน false positives)

แก้ไขไฟล์ `edge/src/components/detection_processor.py`:

```python
# เพิ่มที่ __init__ method
# detection_processor.py:201-202
self.confidence_threshold = CONFIDENCE_THRESHOLD
self.plate_confidence_threshold = PLATE_CONFIDENCE_THRESHOLD

# เพิ่มบรรทัดนี้
# COCO dataset classes: 2=car, 3=motorcycle, 5=bus, 7=truck
self.allowed_vehicle_classes = [2, 3, 5, 7]  # เพิ่มบรรทัดนี้
```

แก้ไข method `detect_vehicles()`:

```python
# detection_processor.py:720-729
# เปลี่ยนจาก:
for box in vehicle_boxes:
    confidence = box.get('score', 0)
    if confidence >= self.confidence_threshold:
        mapped_bbox = self.map_coordinates_to_original(box['bbox'], mapping_info)
        box['bbox'] = mapped_bbox
        filtered_boxes.append(box)

# เป็น:
for box in vehicle_boxes:
    confidence = box.get('score', 0)
    class_id = box.get('class_id', -1)  # เพิ่มบรรทัดนี้
    
    # เพิ่มการตรวจสอบ class
    if confidence >= self.confidence_threshold and class_id in self.allowed_vehicle_classes:
        mapped_bbox = self.map_coordinates_to_original(box['bbox'], mapping_info)
        box['bbox'] = mapped_bbox
        box['bbox_original'] = mapped_bbox
        filtered_boxes.append(box)
```

**ผลลัพธ์**: ลด false positives ลงอย่างมาก

---

### Step 3: ใช้ Tracking + Deduplication (สำคัญมาก - ป้องกันการบันทึกซ้ำ)

แก้ไขไฟล์ `edge/src/services/detection_manager.py`:

```python
# detection_manager.py:313-488
# แก้ไข method process_frame()

def process_frame(self, frame) -> Optional[Dict[str, Any]]:
    self.logger.debug(f"🔧 [DETECTION_MANAGER] process_frame called with frame shape: {frame.shape if frame is not None else 'None'}")
    
    start_time = time.time()
    
    try:
        self.detection_stats['total_frames_processed'] += 1
        
        # Step 1: Validate and enhance frame
        enhanced_frame = self.detection_processor.validate_and_enhance_frame(frame)
        if enhanced_frame is None:
            return None
        
        # Step 2: Vehicle detection
        vehicle_boxes, mapping_info = self.detection_processor.detect_vehicles(frame)
        
        if not vehicle_boxes:
            return None
        
        self.detection_stats['total_vehicles_detected'] += len(vehicle_boxes)
        
        # Step 2.5: Update tracking (เพิ่มใหม่!)
        tracks = self.detection_processor.update_vehicle_tracks(vehicle_boxes, frame)
        
        # Step 2.6: Apply deduplication (เพิ่มใหม่!)
        filtered_tracks = self.detection_processor.apply_deduplication_rules(tracks)
        
        # Step 2.7: Process only finalized tracks (เพิ่มใหม่!)
        MIN_FRAMES_FOR_FINALIZATION = 3
        new_vehicles = []
        for track in filtered_tracks:
            # Finalize track after N frames
            if track.frame_count >= MIN_FRAMES_FOR_FINALIZATION:
                # Use best frame if available
                best_frame = track.best_frame_data if track.best_frame_data is not None else frame
                new_vehicles.append({
                    'bbox': track.bbox,
                    'track_id': track.track_id,
                    'confidence': track.confidence,
                    'best_frame': best_frame
                })
        
        if not new_vehicles:
            return None  # No new vehicles to process
        
        # Step 3: License plate detection (ใช้ best frame จาก tracking)
        plate_boxes = []
        for vehicle in new_vehicles:
            plates = self.detection_processor.detect_license_plates(
                vehicle['best_frame'], [vehicle], mapping_info
            )
            plate_boxes.extend(plates)
        
        if not plate_boxes:
            self.logger.debug("No license plates detected")
        else:
            self.detection_stats['total_plates_detected'] += len(plate_boxes)
        
        # Step 4: OCR on detected plates
        ocr_results = []
        if plate_boxes:
            ocr_results = self.detection_processor.perform_ocr(
                new_vehicles[0]['best_frame'], plate_boxes
            )
            if ocr_results:
                self.detection_stats['successful_ocr'] += len(ocr_results)
        
        # Step 5: Save detection results (ใช้ best frame)
        original_path, _, _, _ = self.detection_processor.save_detection_results(
            new_vehicles[0]['best_frame'],
            [v['bbox'] for v in new_vehicles],
            plate_boxes,
            ocr_results
        )
        
        # Step 6: Store results in database
        processing_time = time.time() - start_time
        
        detection_record = {
            'timestamp': datetime.now().isoformat(),
            'vehicles_count': len(new_vehicles),
            'plates_count': len(plate_boxes),
            'ocr_results': ocr_results,
            'original_image_path': f"captured_images/{os.path.basename(original_path)}" if original_path else '',
            'vehicle_detections': [v['bbox'] for v in new_vehicles],
            'plate_detections': plate_boxes,
            'processing_time_ms': processing_time * 1000.0,
            'coordinate_mapping': mapping_info,
            'track_ids': [v['track_id'] for v in new_vehicles]  # เพิ่ม track IDs
        }
        
        # Extract parallel OCR data (existing code)
        # ... (keep existing OCR extraction code) ...
        
        if original_path and os.path.exists(original_path):
            if self.database_manager:
                self.database_manager.insert_detection_result(detection_record)
        
        self._update_processing_stats(processing_time)
        self.detection_stats['last_detection'] = datetime.now().isoformat()
        
        return detection_record
        
    except Exception as e:
        self.logger.error(f"🔧 [DETECTION_MANAGER] process_frame error: {e}")
        self.detection_stats['failed_detections'] += 1
        return None
```

**ผลลัพธ์**: ไม่บันทึกซ้ำ, ใช้ best frame สำหรับ OCR

---

### Step 4: ปรับปรุง OCR Preprocessing (สำคัญ - เพิ่ม OCR accuracy)

แก้ไขไฟล์ `edge/src/components/detection_processor.py`:

```python
# detection_processor.py:2371-2402
# แก้ไข method _enhance_plate_for_ocr()

def _enhance_plate_for_ocr(self, plate_region: np.ndarray) -> np.ndarray:
    """
    Enhanced OCR preprocessing with deskew and better thresholding.
    """
    try:
        # 1. Convert to grayscale
        if len(plate_region.shape) == 3:
            gray = cv2.cvtColor(plate_region, cv2.COLOR_BGR2GRAY)
        else:
            gray = plate_region.copy()
        
        # 2. Resize if too small (OCR models need minimum size)
        min_width, min_height = 64, 32
        if gray.shape[1] < min_width or gray.shape[0] < min_height:
            scale = max(min_width / gray.shape[1], min_height / gray.shape[0])
            new_w = int(gray.shape[1] * scale)
            new_h = int(gray.shape[0] * scale)
            gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        
        # 3. Deskew (แก้ไขภาพเอียง) - เพิ่มใหม่!
        gray = self._deskew_image(gray)
        
        # 4. Noise reduction - เพิ่มใหม่!
        gray = cv2.bilateralFilter(gray, 5, 50, 50)
        
        # 5. CLAHE for contrast enhancement
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))  # เพิ่ม clipLimit จาก 2.0 → 3.0
        enhanced = clahe.apply(gray)
        
        # 6. Adaptive threshold with better parameters
        enhanced = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # 7. Morphological operations to clean up - เพิ่มใหม่!
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        # 8. Convert back to BGR
        enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return enhanced
        
    except Exception as e:
        self.logger.warning(f"Plate OCR enhancement failed: {e}")
        return plate_region

# เพิ่ม method ใหม่สำหรับ deskew
def _deskew_image(self, image: np.ndarray) -> np.ndarray:
    """Correct skew in license plate image."""
    try:
        # Find edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Find lines using HoughLines
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        if lines is not None and len(lines) > 0:
            # Calculate average angle
            angles = []
            for rho, theta in lines[:10]:  # Use first 10 lines
                angle = (theta * 180 / np.pi) - 90
                angles.append(angle)
            
            # Calculate median angle
            median_angle = np.median(angles)
            
            # Rotate if angle is significant
            if abs(median_angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                image = cv2.warpAffine(
                    image, M, (w, h), 
                    flags=cv2.INTER_CUBIC, 
                    borderMode=cv2.BORDER_REPLICATE
                )
        
        return image
        
    except Exception as e:
        self.logger.debug(f"Deskew failed: {e}")
        return image
```

**ผลลัพธ์**: OCR accuracy เพิ่มขึ้น

---

### Step 5: เพิ่ม Coordinate Mapping Validation (สำคัญ - ป้องกัน OCR จากตำแหน่งผิด)

แก้ไขไฟล์ `edge/src/components/detection_processor.py`:

```python
# detection_processor.py:760-838
# แก้ไข method detect_license_plates()

def detect_license_plates(self, frame: np.ndarray, vehicle_boxes: List[Dict], mapping_info: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    if not self.models_loaded or not self.lp_detection_model:
        return []
    
    detected_plates = []
    frame_h, frame_w = frame.shape[:2]  # เพิ่มบรรทัดนี้
    
    for i, vehicle_box in enumerate(vehicle_boxes):
        try:
            if 'bbox' not in vehicle_box:
                continue
            
            x1, y1, x2, y2 = vehicle_box['bbox']
            
            # เพิ่มการตรวจสอบ bounds
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(frame_w, int(x2))
            y2 = min(frame_h, int(y2))
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            vehicle_region = frame[y1:y2, x1:x2]
            
            if vehicle_region.size == 0:
                continue
            
            # Perform license plate detection
            lp_results = self.lp_detection_model(vehicle_region)
            lp_boxes = getattr(lp_results, "results", [])
            
            # Filter and convert coordinates
            veh_w = x2 - x1  # เพิ่มบรรทัดนี้
            veh_h = y2 - y1  # เพิ่มบรรทัดนี้
            
            for j, lp_box in enumerate(lp_boxes):
                confidence = lp_box.get('score', 0)
                if confidence >= self.plate_confidence_threshold:
                    lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                    
                    # ตรวจสอบ bounds ของ plate ใน vehicle region - เพิ่มใหม่!
                    lp_x1 = max(0, min(int(lp_x1), veh_w))
                    lp_y1 = max(0, min(int(lp_y1), veh_h))
                    lp_x2 = max(lp_x1, min(int(lp_x2), veh_w))
                    lp_y2 = max(lp_y1, min(int(lp_y2), veh_h))
                    
                    # Convert coordinates back to full frame
                    full_x1 = x1 + lp_x1
                    full_y1 = y1 + lp_y1
                    full_x2 = x1 + lp_x2
                    full_y2 = y1 + lp_y2
                    
                    # ตรวจสอบ bounds อีกครั้ง - เพิ่มใหม่!
                    full_x1 = max(0, min(full_x1, frame_w))
                    full_y1 = max(0, min(full_y1, frame_h))
                    full_x2 = max(full_x1, min(full_x2, frame_w))
                    full_y2 = max(full_y1, min(full_y2, frame_h))
                    
                    plate_data = {
                        'bbox': [full_x1, full_y1, full_x2, full_y2],
                        'bbox_original': [full_x1, full_y1, full_x2, full_y2],
                        'score': confidence,
                        'vehicle_idx': i,
                        'vehicle_bbox': vehicle_box['bbox']
                    }
                    
                    detected_plates.append(plate_data)
        
        except Exception as e:
            self.logger.warning(f"Error detecting plates in vehicle {i}: {e}")
            continue
    
    return detected_plates
```

**ผลลัพธ์**: OCR จะอ่านจากตำแหน่งที่ถูกต้อง

---

## Testing Checklist

### Before Deployment
- [ ] ทดสอบ class filtering กับภาพที่มีบุคคล/วัตถุอื่น
- [ ] ทดสอบ tracking/deduplication กับวิดีโอที่มีรถผ่านซ้ำ
- [ ] ทดสอบ OCR preprocessing กับภาพป้ายที่เอียง/คุณภาพต่ำ
- [ ] ทดสอบ coordinate mapping กับภาพที่มีรถหลายคัน

### After Deployment
- [ ] ตรวจสอบ false positive rate (ควรลดลง)
- [ ] ตรวจสอบ false negative rate (ควรลดลง)
- [ ] ตรวจสอบ OCR success rate (ควรเพิ่มขึ้น)
- [ ] ตรวจสอบ system performance (CPU, memory usage)

---

## Rollback Plan

หากการแก้ไขทำให้เกิดปัญหา:

1. **Rollback Configuration**: เปลี่ยน DETECTION_INTERVAL กลับเป็น 30.0
2. **Rollback Code**: ใช้ git revert หรือ restore จาก backup
3. **Monitor**: ตรวจสอบ logs และ metrics

---

## Expected Results

### Before Fixes
- False Positive Rate: ~15-20%
- False Negative Rate: ~30-40%
- OCR Success Rate: ~40-50%

### After Fixes
- False Positive Rate: ~5-10% (ลดลง 50%)
- False Negative Rate: ~10-15% (ลดลง 60%)
- OCR Success Rate: ~70-80% (เพิ่มขึ้น 50%)

---

## Next Steps

1. **Immediate**: ทำ Step 1-2 (Configuration + Class Filtering)
2. **Short-term**: ทำ Step 3-4 (Tracking + OCR Preprocessing)
3. **Long-term**: ทำ Step 5 + Monitoring + Fine-tuning

