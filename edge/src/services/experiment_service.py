# src/services/experiment_service.py
#!/usr/bin/env python3
"""
Experiment Service for AI Camera v2.0

This service manages camera experiments and research functionality:
- Experiment configuration and execution
- Data collection and logging
- Image capture with metadata
- License plate detection and OCR
- Results analysis and reporting

Author: AI Camera Team
Version: 2.0
Date: August 10, 2025
"""

import os
import json
import csv
import cv2
import time
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import IMAGE_SAVE_DIR, EXPERIMENT_RESULTS_DIR
from edge.src.components.experiment_isolator import ExperimentIsolator

logger = get_logger(__name__)


@dataclass
class ExperimentResult:
    """ผลลัพธ์การทดลอง"""
    experiment_id: str
    experiment_type: str
    timestamp: str
    image_source: str
    camera_config: Dict[str, Any]
    detection_result: Dict[str, Any]
    processing_time: float
    frame_info: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExperimentConfig:
    """การตั้งค่าการทดลอง"""
    experiment_type: str
    image_source: str = 'camera'
    camera_config: str = 'current'
    custom_config: Optional[Dict[str, Any]] = None
    start_length: Optional[float] = None
    max_length: Optional[float] = None
    step: Optional[float] = None
    enable_auto_focus: bool = True


class ExperimentService:
    """Service หลักสำหรับการทดลอง"""
    
    def __init__(self, camera_manager, detection_processor, isolator: ExperimentIsolator):
        self.camera_manager = camera_manager
        self.detection_processor = detection_processor
        self.isolator = isolator
        self.current_experiment: Optional[str] = None
        self.experiment_results: List[ExperimentResult] = []
        
        # สร้างโฟลเดอร์สำหรับเก็บผลการทดลอง
        self._setup_experiment_directories()
        
        logger.info("Experiment Service initialized")
    
    def _setup_experiment_directories(self):
        """สร้างโฟลเดอร์สำหรับเก็บผลการทดลอง"""
        try:
            # โฟลเดอร์หลักสำหรับผลการทดลอง
            self.results_dir = Path(EXPERIMENT_RESULTS_DIR or '/home/camuser/aicamera/experiment_results')
            self.results_dir.mkdir(parents=True, exist_ok=True)
            
            # โฟลเดอร์ย่อยสำหรับแต่ละประเภทการทดลอง
            self.single_detection_dir = self.results_dir / 'single_detection'
            self.length_detection_dir = self.results_dir / 'length_detection'
            self.flexible_config_dir = self.results_dir / 'flexible_config'
            
            for directory in [self.single_detection_dir, self.length_detection_dir, self.flexible_config_dir]:
                directory.mkdir(exist_ok=True)
                (directory / 'images').mkdir(exist_ok=True)
                (directory / 'metadata').mkdir(exist_ok=True)
            
            logger.info(f"Experiment directories created at {self.results_dir}")
            
        except Exception as e:
            logger.error(f"Failed to create experiment directories: {e}")
            raise
    
    def run_single_detection_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        """ทดลอง detection pipeline แบบ single shot"""
        experiment_id = self._generate_experiment_id('single_detection')
        
        try:
            # เข้าสู่โหมด experiment
            if not self.isolator.enter_experiment_mode():
                raise RuntimeError("Cannot enter experiment mode")
            
            self.current_experiment = experiment_id
            logger.info(f"Starting single detection experiment: {experiment_id}")
            
            # เลือกแหล่งภาพ
            frame, source_type = self._get_image_frame(config.image_source)
            
            # ใช้การตั้งค่ากล้อง
            camera_config = self._get_camera_config(config)
            
            # รัน detection pipeline แบบ isolated
            start_time = time.time()
            detection_result = self._run_isolated_detection(frame, camera_config)
            processing_time = time.time() - start_time
            
            # สร้างผลลัพธ์การทดลอง
            experiment_result = ExperimentResult(
                experiment_id=experiment_id,
                experiment_type='single_detection',
                timestamp=datetime.now().isoformat(),
                image_source=source_type,
                camera_config=camera_config,
                detection_result=detection_result,
                processing_time=processing_time,
                frame_info={
                    'width': frame.shape[1],
                    'height': frame.shape[0],
                    'channels': frame.shape[2]
                }
            )
            
            # บันทึกผลลัพธ์
            self._save_experiment_result(experiment_result, frame)
            self.experiment_results.append(experiment_result)
            
            logger.info(f"Single detection experiment completed: {experiment_id}")
            return experiment_result
            
        except Exception as e:
            logger.error(f"Single detection experiment failed: {e}")
            raise
        finally:
            # ออกจากโหมด experiment
            self.isolator.exit_experiment_mode()
            self.current_experiment = None
    
    def run_length_detection_experiment(self, config: ExperimentConfig) -> List[ExperimentResult]:
        """ทดลอง detection ตามความยาวของวัตถุ"""
        experiment_id = self._generate_experiment_id('length_detection')
        
        try:
            # เข้าสู่โหมด experiment
            if not self.isolator.enter_experiment_mode():
                raise RuntimeError("Cannot enter experiment mode")
            
            self.current_experiment = experiment_id
            logger.info(f"Starting length detection experiment: {experiment_id}")
            
            results = []
            
            # ตรวจสอบพารามิเตอร์
            if not all([config.start_length, config.max_length, config.step]):
                raise ValueError("Missing length parameters for length detection")
            
            if config.start_length >= config.max_length:
                raise ValueError("start_length must be less than max_length")
            
            # รันการทดลองตามลำดับความยาว
            for distance in np.arange(config.start_length, config.max_length + config.step, config.step):
                logger.info(f"Processing distance: {distance}m")
                
                # ตั้งค่า auto focus (ถ้ารองรับ)
                if config.enable_auto_focus:
                    self._set_auto_focus_for_distance(distance)
                    time.sleep(1)  # รอ auto focus
                
                # เก็บภาพและรัน detection
                frame = self._capture_frame()
                detection_result = self._run_isolated_detection(frame)
                
                # สร้างผลลัพธ์
                result = ExperimentResult(
                    experiment_id=experiment_id,
                    experiment_type='length_detection',
                    timestamp=datetime.now().isoformat(),
                    image_source='camera',
                    camera_config=self._get_camera_config(config),
                    detection_result=detection_result,
                    processing_time=0.0,  # จะคำนวณในภายหลัง
                    frame_info={
                        'width': frame.shape[1],
                        'height': frame.shape[0],
                        'channels': frame.shape[2]
                    },
                    metadata={
                        'distance': distance,
                        'focus_position': self._get_current_focus_position(),
                        'image_quality': self._analyze_image_quality(frame)
                    }
                )
                
                results.append(result)
                self._save_experiment_result(result, frame)
            
            # บันทึกผลลัพธ์ทั้งหมด
            self.experiment_results.extend(results)
            
            logger.info(f"Length detection experiment completed: {experiment_id}")
            return results
            
        except Exception as e:
            logger.error(f"Length detection experiment failed: {e}")
            raise
        finally:
            # ออกจากโหมด experiment
            self.isolator.exit_experiment_mode()
            self.current_experiment = None
    
    def run_flexible_experiment(self, config: ExperimentConfig) -> List[ExperimentResult]:
        """ทดลองด้วยการตั้งค่ากล้องที่กำหนดเอง"""
        experiment_id = self._generate_experiment_id('flexible_config')
        
        try:
            # เข้าสู่โหมด experiment
            if not self.isolator.enter_experiment_mode():
                raise RuntimeError("Cannot enter experiment mode")
            
            self.current_experiment = experiment_id
            logger.info(f"Starting flexible experiment: {experiment_id}")
            
            # อัปเดตการตั้งค่ากล้องตามที่กำหนด
            if config.custom_config:
                self._update_camera_configuration(config.custom_config)
            
            # รันการทดลองตามลำดับความยาว
            if config.start_length and config.max_length and config.step:
                return self.run_length_detection_experiment(config)
            else:
                # ทดลองแบบ single shot
                return [self.run_single_detection_experiment(config)]
            
        except Exception as e:
            logger.error(f"Flexible experiment failed: {e}")
            raise
        finally:
            # ออกจากโหมด experiment
            self.isolator.exit_experiment_mode()
            self.current_experiment = None
    
    def _get_image_frame(self, image_source: str) -> Tuple[np.ndarray, str]:
        """ดึงภาพจากแหล่งที่กำหนด"""
        if image_source == 'camera':
            frame = self._capture_frame()
            return frame, "Live Camera Frame"
        else:
            frame = self._load_still_image(image_source)
            return frame, "Still Image"
    
    def _capture_frame(self) -> np.ndarray:
        """เก็บภาพจากกล้อง"""
        try:
            if hasattr(self.camera_manager, 'capture_main_frame'):
                frame = self.camera_manager.capture_main_frame()
            elif hasattr(self.camera_manager, 'get_frame'):
                frame = self.camera_manager.get_frame()
            else:
                raise RuntimeError("Camera manager has no frame capture method")
            
            if frame is None:
                raise RuntimeError("Failed to capture frame from camera")
            
            return frame
            
        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            raise
    
    def _load_still_image(self, image_path: str) -> np.ndarray:
        """โหลดภาพนิ่ง"""
        try:
            # ค้นหาภาพในโฟลเดอร์ assets
            assets_dir = Path('/home/camuser/aicamera/edge/assets')
            image_file = assets_dir / image_path
            
            if not image_file.exists():
                raise FileNotFoundError(f"Image not found: {image_file}")
            
            frame = cv2.imread(str(image_file))
            if frame is None:
                raise RuntimeError(f"Failed to load image: {image_file}")
            
            return frame
            
        except Exception as e:
            logger.error(f"Error loading still image: {e}")
            raise
    
    def _get_camera_config(self, config: ExperimentConfig) -> Dict[str, Any]:
        """ดึงการตั้งค่ากล้อง"""
        if config.camera_config == 'current':
            return self._get_current_camera_config()
        elif config.camera_config == 'default':
            return self._get_default_camera_config()
        elif config.camera_config == 'custom' and config.custom_config:
            return config.custom_config
        else:
            return self._get_current_camera_config()
    
    def _get_current_camera_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่ากล้องปัจจุบัน"""
        try:
            if hasattr(self.camera_manager, 'get_camera_config'):
                return self.camera_manager.get_camera_config()
            elif hasattr(self.camera_manager, 'camera_config'):
                return self.camera_manager.camera_config
            else:
                return {'status': 'unknown'}
        except Exception as e:
            logger.warning(f"Error getting current camera config: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_default_camera_config(self) -> Dict[str, Any]:
        """ดึงการตั้งค่ากล้องเริ่มต้น"""
        return {
            'exposure_time': 100000,
            'analog_gain': 1.0,
            'lens_position': 0.0,
            'sharpness': 1.0,
            'status': 'default'
        }
    
    def _update_camera_configuration(self, config: Dict[str, Any]):
        """อัปเดตการตั้งค่ากล้อง"""
        try:
            if hasattr(self.camera_manager, 'update_camera_config'):
                self.camera_manager.update_camera_config(config)
            elif hasattr(self.camera_manager, 'set_camera_config'):
                self.camera_manager.set_camera_config(config)
            else:
                logger.warning("Camera manager has no config update method")
        except Exception as e:
            logger.error(f"Error updating camera config: {e}")
            raise
    
    def _run_isolated_detection(self, frame: np.ndarray, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """รัน detection แบบ isolated"""
        try:
            if hasattr(self.detection_processor, 'process_frame'):
                return self.detection_processor.process_frame(frame, config)
            elif hasattr(self.detection_processor, 'detect'):
                return self.detection_processor.detect(frame)
            else:
                raise RuntimeError("Detection processor has no detection method")
        except Exception as e:
            logger.error(f"Error in isolated detection: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'vehicles_detected': 0,
                'plates_detected': 0,
                'ocr_success': False,
                'ocr_confidence': 0.0
            }
    
    def _set_auto_focus_for_distance(self, distance: float):
        """ตั้งค่า auto focus ตามความยาว"""
        try:
            if hasattr(self.camera_manager, 'set_auto_focus_for_distance'):
                self.camera_manager.set_auto_focus_for_distance(distance)
            elif hasattr(self.camera_manager, 'set_focus_distance'):
                self.camera_manager.set_focus_distance(distance)
            else:
                logger.warning("Camera manager has no auto focus method")
        except Exception as e:
            logger.warning(f"Error setting auto focus: {e}")
    
    def _get_current_focus_position(self) -> float:
        """ดึงตำแหน่ง focus ปัจจุบัน"""
        try:
            if hasattr(self.camera_manager, 'get_focus_position'):
                return self.camera_manager.get_focus_position()
            elif hasattr(self.camera_manager, 'focus_position'):
                return self.camera_manager.focus_position
            else:
                return 0.0
        except Exception:
            return 0.0
    
    def _analyze_image_quality(self, frame: np.ndarray) -> Dict[str, Any]:
        """วิเคราะห์คุณภาพภาพ"""
        try:
            # คำนวณความคมชัด (Laplacian variance)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # คำนวณความสว่างเฉลี่ย
            brightness = np.mean(gray)
            
            # คำนวณ contrast
            contrast = np.std(gray)
            
            return {
                'sharpness': laplacian_var,
                'brightness': brightness,
                'contrast': contrast,
                'quality_score': min(laplacian_var / 100, 1.0)  # Normalize to 0-1
            }
        except Exception as e:
            logger.warning(f"Error analyzing image quality: {e}")
            return {
                'sharpness': 0.0,
                'brightness': 0.0,
                'contrast': 0.0,
                'quality_score': 0.0
            }
    
    def _save_experiment_result(self, result: ExperimentResult, frame: np.ndarray):
        """บันทึกผลลัพธ์การทดลอง"""
        try:
            # บันทึกภาพ
            image_filename = f"{result.experiment_id}_{result.experiment_type}.jpg"
            image_path = self._get_experiment_image_path(result.experiment_type) / image_filename
            cv2.imwrite(str(image_path), frame)
            
            # บันทึก metadata
            metadata_filename = f"{result.experiment_id}_{result.experiment_type}.json"
            metadata_path = self._get_experiment_metadata_path(result.experiment_type) / metadata_filename
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, ensure_ascii=False)
            
            # บันทึกลง CSV
            self._append_to_csv(result)
            
            logger.debug(f"Saved experiment result: {result.experiment_id}")
            
        except Exception as e:
            logger.error(f"Error saving experiment result: {e}")
    
    def _get_experiment_image_path(self, experiment_type: str) -> Path:
        """ดึงเส้นทางโฟลเดอร์ภาพตามประเภทการทดลอง"""
        if experiment_type == 'single_detection':
            return self.single_detection_dir / 'images'
        elif experiment_type == 'length_detection':
            return self.length_detection_dir / 'images'
        elif experiment_type == 'flexible_config':
            return self.flexible_config_dir / 'images'
        else:
            return self.results_dir / 'images'
    
    def _get_experiment_metadata_path(self, experiment_type: str) -> Path:
        """ดึงเส้นทางโฟลเดอร์ metadata ตามประเภทการทดลอง"""
        if experiment_type == 'single_detection':
            return self.single_detection_dir / 'metadata'
        elif experiment_type == 'length_detection':
            return self.length_detection_dir / 'metadata'
        elif experiment_type == 'flexible_config':
            return self.flexible_config_dir / 'metadata'
        else:
            return self.results_dir / 'metadata'
    
    def _append_to_csv(self, result: ExperimentResult):
        """เพิ่มผลลัพธ์ลงในไฟล์ CSV"""
        try:
            csv_filename = f"{result.experiment_type}_results.csv"
            csv_path = self.results_dir / csv_filename
            
            # สร้างไฟล์ CSV ถ้ายังไม่มี
            if not csv_path.exists():
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        'ExperimentID', 'ExperimentType', 'Timestamp', 'ImageSource',
                        'VehiclesDetected', 'PlatesDetected', 'OCRSuccess', 'OCRConfidence',
                        'ProcessingTime', 'ImageQuality', 'CameraConfig'
                    ])
            
            # เพิ่มข้อมูลใหม่
            with open(csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    result.experiment_id,
                    result.experiment_type,
                    result.timestamp,
                    result.image_source,
                    result.detection_result.get('vehicles_detected', 0),
                    result.detection_result.get('plates_detected', 0),
                    result.detection_result.get('ocr_success', False),
                    result.detection_result.get('ocr_confidence', 0.0),
                    result.processing_time,
                    result.frame_info.get('width', 0) * result.frame_info.get('height', 0),
                    json.dumps(result.camera_config)
                ])
                
        except Exception as e:
            logger.error(f"Error appending to CSV: {e}")
    
    def _generate_experiment_id(self, experiment_type: str) -> str:
        """สร้าง ID สำหรับการทดลอง"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{experiment_type}_{timestamp}_{len(self.experiment_results)}"
    
    def get_experiment_status(self) -> Dict[str, Any]:
        """ดึงสถานะการทำงานของ experiment service"""
        return {
            'current_experiment': self.current_experiment,
            'total_experiments': len(self.experiment_results),
            'isolator_status': self.isolator.get_experiment_status(),
            'results_directory': str(self.results_dir)
        }
    
    def get_available_experiments(self) -> List[Dict[str, Any]]:
        """ดึงรายการการทดลองที่สามารถทำได้"""
        return [
            {
                'type': 'single_detection',
                'name': 'Single Detection Pipeline',
                'description': 'ทดสอบ detection pipeline ด้วยภาพนิ่งหรือเฟรมเดียว',
                'parameters': ['image_source', 'camera_config']
            },
            {
                'type': 'length_detection',
                'name': 'Length Detection with Auto Focus',
                'description': 'ทดสอบการตรวจจับตามความยาวด้วย auto focus',
                'parameters': ['start_length', 'max_length', 'step', 'enable_auto_focus']
            },
            {
                'type': 'flexible_config',
                'name': 'Flexible Experimental Configuration',
                'description': 'กำหนดการตั้งค่ากล้องเองและทดสอบ',
                'parameters': ['custom_config', 'start_length', 'max_length', 'step']
            }
        ]
    
    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            if self.current_experiment:
                logger.warning("Cleaning up while experiment is running")
                self.isolator.exit_experiment_mode()
            
            self.experiment_results.clear()
            logger.info("Experiment Service cleaned up")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")


# Factory function for dependency injection
def create_experiment_service(camera_manager, detection_processor, isolator: ExperimentIsolator) -> ExperimentService:
    """สร้าง Experiment Service instance"""
    return ExperimentService(camera_manager, detection_processor, isolator)