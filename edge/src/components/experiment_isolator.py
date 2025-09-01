# src/components/experiment_isolator.py
#!/usr/bin/env python3
"""
Experiment Isolator for AI Camera v2.0

This component isolates experiment operations from the main pipeline
to prevent interference with production detection operations.

Author: AI Camera Team
Version: 2.0
Date: August 10, 2025
"""

import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass

from edge.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineState:
    """สถานะของ main pipeline ที่บันทึกไว้"""
    detection_running: bool = False
    camera_streaming: bool = False
    detection_interval: float = 0.1
    detection_thread_alive: bool = False
    camera_initialized: bool = False


class ExperimentIsolator:
    """แยกการทำงานของ experiment จาก main pipeline"""
    
    def __init__(self, camera_manager, detection_manager):
        self.camera_manager = camera_manager
        self.detection_manager = detection_manager
        self.is_experiment_mode = False
        self.original_pipeline_state: Optional[PipelineState] = None
        self.isolation_lock = threading.Lock()
        self.experiment_start_time: Optional[float] = None
        
        logger.info("Experiment Isolator initialized")
    
    def enter_experiment_mode(self) -> bool:
        """เข้าสู่โหมด experiment"""
        with self.isolation_lock:
            if self.is_experiment_mode:
                logger.warning("Already in experiment mode")
                return False
            
            try:
                # บันทึกสถานะปัจจุบันของ main pipeline
                self.original_pipeline_state = self._capture_pipeline_state()
                logger.info("Captured current pipeline state")
                
                # หยุด main pipeline ชั่วคราว
                self._pause_main_pipeline()
                
                # ตั้งค่าสถานะ experiment mode
                self.is_experiment_mode = True
                self.experiment_start_time = time.time()
                
                logger.info("Successfully entered experiment mode")
                return True
                
            except Exception as e:
                logger.error(f"Failed to enter experiment mode: {e}")
                # คืนค่าสถานะเดิม
                if self.original_pipeline_state:
                    self._restore_main_pipeline()
                return False
    
    def exit_experiment_mode(self) -> bool:
        """ออกจากโหมด experiment"""
        with self.isolation_lock:
            if not self.is_experiment_mode:
                logger.warning("Not in experiment mode")
                return False
            
            try:
                # คืนค่าสถานะ main pipeline
                self._restore_main_pipeline()
                
                # รีเซ็ตสถานะ
                self.is_experiment_mode = False
                self.original_pipeline_state = None
                
                # คำนวณเวลาที่ใช้ใน experiment mode
                if self.experiment_start_time:
                    duration = time.time() - self.experiment_start_time
                    logger.info(f"Exited experiment mode after {duration:.2f} seconds")
                
                self.experiment_start_time = None
                return True
                
            except Exception as e:
                logger.error(f"Failed to exit experiment mode: {e}")
                return False
    
    def _capture_pipeline_state(self) -> PipelineState:
        """บันทึกสถานะปัจจุบันของ main pipeline"""
        try:
            return PipelineState(
                detection_running=self._safe_check_detection_running(),
                camera_streaming=self._safe_check_camera_streaming(),
                detection_interval=self._safe_get_detection_interval(),
                detection_thread_alive=self._safe_check_detection_thread(),
                camera_initialized=self._safe_check_camera_initialized()
            )
        except Exception as e:
            logger.warning(f"Error capturing pipeline state: {e}")
            return PipelineState()
    
    def _pause_main_pipeline(self):
        """หยุด main pipeline ชั่วคราว"""
        try:
            # หยุด detection manager แต่ไม่หยุด camera
            if self._safe_check_detection_running():
                logger.info("Pausing detection manager")
                if hasattr(self.detection_manager, 'pause'):
                    self.detection_manager.pause()
                elif hasattr(self.detection_manager, 'stop'):
                    self.detection_manager.stop()
                else:
                    logger.warning("Detection manager has no pause/stop method")
            
            # รอให้ detection หยุดทำงาน
            self._wait_for_detection_stop()
            
            logger.info("Main pipeline paused successfully")
            
        except Exception as e:
            logger.error(f"Error pausing main pipeline: {e}")
            raise
    
    def _restore_main_pipeline(self):
        """คืนค่า main pipeline"""
        try:
            if not self.original_pipeline_state:
                logger.warning("No original pipeline state to restore")
                return
            
            # คืนค่า detection manager
            if self.original_pipeline_state.detection_running:
                logger.info("Restoring detection manager")
                if hasattr(self.detection_manager, 'resume'):
                    self.detection_manager.resume()
                elif hasattr(self.detection_manager, 'start'):
                    self.detection_manager.start()
                else:
                    logger.warning("Detection manager has no resume/start method")
            
            # รอให้ detection เริ่มทำงาน
            self._wait_for_detection_start()
            
            logger.info("Main pipeline restored successfully")
            
        except Exception as e:
            logger.error(f"Error restoring main pipeline: {e}")
            raise
    
    def _wait_for_detection_stop(self, timeout: float = 10.0):
        """รอให้ detection หยุดทำงาน"""
        start_time = time.time()
        while self._safe_check_detection_running():
            if time.time() - start_time > timeout:
                logger.warning("Timeout waiting for detection to stop")
                break
            time.sleep(0.1)
    
    def _wait_for_detection_start(self, timeout: float = 10.0):
        """รอให้ detection เริ่มทำงาน"""
        if not self.original_pipeline_state.detection_running:
            return
        
        start_time = time.time()
        while not self._safe_check_detection_running():
            if time.time() - start_time > timeout:
                logger.warning("Timeout waiting for detection to start")
                break
            time.sleep(0.1)
    
    def get_experiment_status(self) -> Dict[str, Any]:
        """ดึงสถานะการทำงานของ experiment mode"""
        with self.isolation_lock:
            return {
                'is_experiment_mode': self.is_experiment_mode,
                'experiment_duration': self._get_experiment_duration(),
                'pipeline_state': self.original_pipeline_state.__dict__ if self.original_pipeline_state else None,
                'isolation_locked': self.isolation_lock.locked()
            }
    
    def _get_experiment_duration(self) -> Optional[float]:
        """คำนวณเวลาที่ใช้ใน experiment mode"""
        if self.experiment_start_time and self.is_experiment_mode:
            return time.time() - self.experiment_start_time
        return None
    
    # Safe checking methods to avoid errors
    def _safe_check_detection_running(self) -> bool:
        """ตรวจสอบสถานะ detection แบบปลอดภัย"""
        try:
            if hasattr(self.detection_manager, 'is_running'):
                return self.detection_manager.is_running()
            elif hasattr(self.detection_manager, 'running'):
                return self.detection_manager.running
            return False
        except Exception:
            return False
    
    def _safe_check_camera_streaming(self) -> bool:
        """ตรวจสอบสถานะ camera streaming แบบปลอดภัย"""
        try:
            if hasattr(self.camera_manager, 'is_streaming'):
                return self.camera_manager.is_streaming()
            elif hasattr(self.camera_manager, 'streaming'):
                return self.camera_manager.streaming
            return False
        except Exception:
            return False
    
    def _safe_get_detection_interval(self) -> float:
        """ดึง detection interval แบบปลอดภัย"""
        try:
            if hasattr(self.detection_manager, 'get_detection_interval'):
                return self.detection_manager.get_detection_interval()
            elif hasattr(self.detection_manager, 'detection_interval'):
                return self.detection_manager.detection_interval
            return 0.1
        except Exception:
            return 0.1
    
    def _safe_check_detection_thread(self) -> bool:
        """ตรวจสอบสถานะ detection thread แบบปลอดภัย"""
        try:
            if hasattr(self.detection_manager, 'thread_alive'):
                return self.detection_manager.thread_alive
            elif hasattr(self.detection_manager, 'is_thread_alive'):
                return self.detection_manager.is_thread_alive()
            return False
        except Exception:
            return False
    
    def _safe_check_camera_initialized(self) -> bool:
        """ตรวจสอบสถานะ camera initialization แบบปลอดภัย"""
        try:
            if hasattr(self.camera_manager, 'is_initialized'):
                return self.camera_manager.is_initialized()
            elif hasattr(self.camera_manager, 'initialized'):
                return self.camera_manager.initialized
            return False
        except Exception:
            return False
    
    def cleanup(self):
        """ทำความสะอาด resources"""
        try:
            if self.is_experiment_mode:
                logger.warning("Cleaning up while in experiment mode - forcing exit")
                self.exit_experiment_mode()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")