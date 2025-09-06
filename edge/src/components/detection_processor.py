#!/usr/bin/env python3
"""
Detection Processor Component for AI Camera v1.3

This component provides AI detection operations using Hailo AI models:
- Vehicle detection using Hailo accelerator
- License plate detection 
- License plate OCR
- Image validation and enhancement
- Bounding box drawing and cropping
- Database integration for detection results

Author: AI Camera Team  
Version: 1.3
Date: August 2025
"""

import os
import cv2
import numpy as np
import logging
import sqlite3
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import (
    VEHICLE_DETECTION_MODEL, LICENSE_PLATE_DETECTION_MODEL, LICENSE_PLATE_OCR_MODEL,
    HEF_MODEL_PATH, MODEL_ZOO_URL, EASYOCR_LANGUAGES,
    IMAGE_SAVE_DIR, DATABASE_PATH, CONFIDENCE_THRESHOLD, PLATE_CONFIDENCE_THRESHOLD
)
from edge.src.components.async_ocr_loader import AsyncOCRLoader
from edge.src.components.parallel_ocr_processor import ParallelOCRProcessor

logger = get_logger(__name__)


class DetectionProcessor:
    """
    Detection Processor Component for AI model inference.
    
    This component handles:
    - Loading and managing Hailo AI models
    - Image frame validation and enhancement
    - Vehicle detection using Hailo accelerator
    - License plate detection and OCR
    - Result processing and storage
    - Bounding box visualization
    """
    
    def __init__(self, logger=None):
        """
        Initialize Detection Processor.
        
        Args:
            logger: Logger instance
        """
        self.logger = logger or get_logger(__name__)
        self.logger.info("🔍 [DETECTION_PROC] Starting Detection Processor initialization...")
        
        # Model instances
        self.logger.info("🔍 [DETECTION_PROC] Initializing model instances...")
        self.vehicle_model = None
        self.lp_detection_model = None
        self.lp_ocr_model = None
        self.ocr_reader = None  # Legacy - will be replaced by async_ocr_loader
        self.logger.info("🔍 [DETECTION_PROC] Model instances initialized")
        
        # Async OCR loader for non-blocking EasyOCR initialization
        self.logger.info("🔍 [DETECTION_PROC] Creating AsyncOCRLoader...")
        self.async_ocr_loader = AsyncOCRLoader(languages=EASYOCR_LANGUAGES, logger=self.logger)
        self.logger.info("🔍 [DETECTION_PROC] AsyncOCRLoader created successfully")
        
        # Parallel OCR processor for simultaneous Hailo + EasyOCR
        self.logger.info("🔍 [DETECTION_PROC] Initializing parallel OCR processor...")
        self.parallel_ocr_processor = None
        self.logger.info("🔍 [DETECTION_PROC] Parallel OCR processor initialized")
        
        # State tracking
        self.logger.info("🔍 [DETECTION_PROC] Setting up state tracking...")
        self.models_loaded = False
        self.processing_stats = {
            'total_processed': 0,
            'vehicles_detected': 0,
            'plates_detected': 0,
            'successful_ocr': 0,
            'last_detection': None
        }
        self.logger.info("🔍 [DETECTION_PROC] State tracking initialized")
        
        # Configuration
        from edge.src.core.config import LORES_RESOLUTION
        self.detection_resolution = LORES_RESOLUTION
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.plate_confidence_threshold = PLATE_CONFIDENCE_THRESHOLD
        self.logger.info("DetectionProcessor initialized")
    
    def load_models(self) -> bool:
        """
        Load all detection and OCR models using configuration parameters.
        
        Returns:
            bool: True if models loaded successfully, False otherwise
        """
        self.logger.info("🔧 [DETECTION_PROC] Starting model loading process...")
        try:
            self.logger.info("🔧 [DETECTION_PROC] Loading detection models...")
            
            # Check if required model parameters are available
            self.logger.info("🔧 [DETECTION_PROC] Checking model configuration...")
            if not VEHICLE_DETECTION_MODEL:
                self.logger.warning("🔧 [DETECTION_PROC] VEHICLE_DETECTION_MODEL not configured")
                return False
            
            if not LICENSE_PLATE_DETECTION_MODEL:
                self.logger.warning("🔧 [DETECTION_PROC] LICENSE_PLATE_DETECTION_MODEL not configured")
                return False
            
            self.logger.info("🔧 [DETECTION_PROC] Model configuration validated")
            
            # Import degirum for Hailo model loading
            # Configure HailoRT logging before importing degirum
            self.logger.info("🔧 [DETECTION_PROC] Configuring HailoRT logging...")
            from edge.config.hailort_logging import configure_hailort_logging
            configure_hailort_logging()
            self.logger.info("🔧 [DETECTION_PROC] HailoRT logging configured")
            
            self.logger.info("🔧 [DETECTION_PROC] Importing degirum...")
            try:
                import degirum as dg
                self.logger.info("🔧 [DETECTION_PROC] ✅ Degirum available for Hailo AI model loading")
            except ImportError:
                self.logger.error("🔧 [DETECTION_PROC] degirum not available - cannot load Hailo models")
                return False
            
            models_loaded = 0
            
            # Load vehicle detection model
            self.logger.info("🔧 [DETECTION_PROC] Loading vehicle detection model...")
            try:
                self.logger.info(f"🔧 [DETECTION_PROC] Loading vehicle detection model: {VEHICLE_DETECTION_MODEL}")
                self.vehicle_model = dg.load_model(
                    model_name=VEHICLE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                self.logger.info("🔧 [DETECTION_PROC] ✅ Vehicle detection model loaded successfully")
                models_loaded += 1
            except Exception as e:
                self.logger.error(f"🔧 [DETECTION_PROC] Failed to load vehicle detection model: {e}")
                return False
            
            # Load license plate detection model
            self.logger.info("🔧 [DETECTION_PROC] Loading license plate detection model...")
            try:
                self.logger.info(f"🔧 [DETECTION_PROC] Loading license plate detection model: {LICENSE_PLATE_DETECTION_MODEL}")
                self.lp_detection_model = dg.load_model(
                    model_name=LICENSE_PLATE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL,
                    overlay_color=[(255, 255, 0), (0, 255, 0)]
                )
                self.logger.info("🔧 [DETECTION_PROC] ✅ License plate detection model loaded successfully")
                models_loaded += 1
            except Exception as e:
                self.logger.error(f"🔧 [DETECTION_PROC] Failed to load license plate detection model: {e}")
                return False
            
            # Load license plate OCR model (optional)
            self.logger.info("🔧 [DETECTION_PROC] Checking for optional OCR model...")
            if LICENSE_PLATE_OCR_MODEL:
                self.logger.info("🔧 [DETECTION_PROC] Loading license plate OCR model...")
                try:
                    self.logger.info(f"🔧 [DETECTION_PROC] Loading license plate OCR model: {LICENSE_PLATE_OCR_MODEL}")
                    self.lp_ocr_model = dg.load_model(
                        model_name=LICENSE_PLATE_OCR_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL,
                        output_use_regular_nms=False,
                        output_confidence_threshold=0.1
                    )
                    self.logger.info("🔧 [DETECTION_PROC] ✅ License plate OCR model loaded successfully")
                    models_loaded += 1
                except Exception as e:
                    self.logger.warning(f"🔧 [DETECTION_PROC] Failed to load OCR model (optional): {e}")
            else:
                self.logger.info("🔧 [DETECTION_PROC] No OCR model configured - skipping")
            
            # Start asynchronous EasyOCR loading (non-blocking)
            self.logger.info("🔧 [DETECTION_PROC] Starting asynchronous EasyOCR loading...")
            try:
                self.logger.info("🔧 [DETECTION_PROC] 🚀 Starting asynchronous EasyOCR loading...")
                if self.async_ocr_loader.start_loading():
                    self.logger.info("🔧 [DETECTION_PROC] ✅ EasyOCR loading started in background")
                    # Don't increment models_loaded here - OCR will be available later
                else:
                    self.logger.warning("🔧 [DETECTION_PROC] EasyOCR loading already in progress or failed to start")
            except Exception as e:
                self.logger.warning(f"🔧 [DETECTION_PROC] Failed to start EasyOCR loading: {e}")
            
            # Initialize parallel OCR processor
            self.logger.info("🔧 [DETECTION_PROC] Initializing parallel OCR processor...")
            try:
                from edge.src.components.parallel_ocr_processor import ParallelOCRProcessor
                self.parallel_ocr_processor = ParallelOCRProcessor(
                    hailo_ocr_model=self.lp_ocr_model,
                    async_ocr_loader=self.async_ocr_loader,
                    logger=self.logger
                )
                self.logger.info("🔧 [DETECTION_PROC] ✅ Parallel OCR processor initialized")
            except Exception as e:
                self.logger.warning(f"🔧 [DETECTION_PROC] Failed to initialize parallel OCR processor: {e}")
                self.parallel_ocr_processor = None
            
            self.models_loaded = models_loaded >= 2  # At least vehicle + LP detection
            self.logger.info(f"🔧 [DETECTION_PROC] Models loaded: {models_loaded}, Ready: {self.models_loaded}")
            
            self.logger.info("🔧 [DETECTION_PROC] Model loading process completed successfully")
            return self.models_loaded
            
        except Exception as e:
            self.logger.error(f"🔧 [DETECTION_PROC] Error loading models: {e}")
            return False
    
    def get_ocr_status(self) -> Dict[str, Any]:
        """
        Get current OCR loading and usage status.
        
        Returns:
            Dict containing OCR status information
        """
        status = self.async_ocr_loader.get_loading_status()
        # Include model names for frontend display
        status.update({
            'vehicle_model_name': VEHICLE_DETECTION_MODEL,
            'lp_detection_model_name': LICENSE_PLATE_DETECTION_MODEL,
            'lp_ocr_model_name': LICENSE_PLATE_OCR_MODEL or '',
            'easyocr_available': bool(status.get('is_ready', False)),
            'easyocr_ready': bool(status.get('is_ready', False))
        })
        return status
    
    def wait_for_ocr_ready(self, timeout: float = 30.0) -> bool:
        """
        Wait for OCR to be ready with timeout.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            bool: True if OCR is ready within timeout
        """
        return self.async_ocr_loader.wait_for_ready(timeout)
    
    def cleanup(self):
        """
        Clean up all resources including async OCR loader, parallel processor, and models.
        Safe to call multiple times (idempotent).
        """
        try:
            self.logger.info("Cleaning up DetectionProcessor...")
            
            # Step 1: Clean up parallel OCR processor if present
            if hasattr(self, 'parallel_ocr_processor') and self.parallel_ocr_processor:
                try:
                    self.parallel_ocr_processor.cleanup()
                    self.logger.debug("Parallel OCR processor cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up parallel OCR processor: {e}")
            
            # Step 2: Clean up async OCR loader if present
            if hasattr(self, 'async_ocr_loader'):
                try:
                    self.async_ocr_loader.cleanup()
                    self.logger.debug("Async OCR loader cleaned up")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up async OCR loader: {e}")
            
            # Step 3: Clean up model references
            try:
                self.vehicle_model = None
                self.lp_detection_model = None  
                self.lp_ocr_model = None
                self.ocr_reader = None
                self.models_loaded = False
                self.logger.debug("Model references cleaned up")
            except Exception as e:
                self.logger.warning(f"Error cleaning up model references: {e}")
            
            self.logger.info("DetectionProcessor cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during DetectionProcessor cleanup: {e}")
    
    def validate_and_enhance_frame(self, frame: np.ndarray) -> Optional[np.ndarray]:
        """
        Validate and enhance image frame for vehicle detection.
        
        Args:
            frame: Input image frame as numpy array

        Returns:
            Optional[np.ndarray]: Enhanced frame or None if validation fails
        """
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame called with frame type: {type(frame)}")
        
        if frame is None:
            self.logger.warning(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: frame is None")
            return None
        
        # Check if frame is a dict (should be numpy array)
        if isinstance(frame, dict):
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: received dict, extracting frame")
            if 'frame' in frame:
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: extracting frame from dict")
                frame = frame['frame']
                if frame is None:
                    self.logger.warning(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: extracted frame is None")
                    return None
            else:
                self.logger.error(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: dict does not contain 'frame' key")
                return None
        
        # Check if frame is numpy array
        if not isinstance(frame, np.ndarray):
            self.logger.error(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: expected numpy array, got {type(frame)}")
            return None
        
        # Check frame size
        if frame.size == 0:
            self.logger.warning(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: empty array")
            return None
        
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: frame shape: {frame.shape}, dtype: {frame.dtype}")
        
        try:
            # Ensure frame is in BGR format for detection models
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # BGRA
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: converting BGRA to BGR")
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 3:  # RGB from camera - convert to BGR for OpenCV
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: converting RGB to BGR")
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            elif len(frame.shape) == 2:  # Grayscale
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: converting grayscale to BGR")
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                self.logger.warning(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame failed: unsupported frame shape: {frame.shape}")
                return None
            
            # Resize frame to detection resolution if needed
            if frame.shape[:2] != self.detection_resolution:
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: resizing frame from {frame.shape[:2]} to {self.detection_resolution}")
                frame = cv2.resize(frame, self.detection_resolution)
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: frame resized successfully")
            
            # Basic enhancement - can be extended
            # Optional: histogram equalization, noise reduction, etc.
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame: returning enhanced frame with shape: {frame.shape}")
            return frame
            
        except Exception as e:
            self.logger.error(f"🔧 [DETECTION_PROCESSOR] validate_and_enhance_frame error: {e}")
            return None
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform vehicle detection on image frame.
        
        Args:
            frame: Input image frame (validated and enhanced)
            
        Returns:
            List[Dict[str, Any]]: List of detected vehicle objects
        """
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles called with frame shape: {frame.shape if frame is not None else 'None'}")
        
        if not self.models_loaded or not self.vehicle_model:
            self.logger.warning(f"🔧 [DETECTION_PROCESSOR] detect_vehicles failed: models_loaded={self.models_loaded}, vehicle_model={self.vehicle_model is not None}")
            return []
        
        try:
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: performing vehicle detection with confidence threshold: {self.confidence_threshold}")
            
            # Perform detection
            results = self.vehicle_model(frame)
            vehicle_boxes = getattr(results, "results", [])
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: raw detection results: {len(vehicle_boxes)} vehicles found")
            
            # Filter by confidence threshold
            filtered_boxes = []
            for i, box in enumerate(vehicle_boxes):
                confidence = box.get('score', 0)
                if confidence >= self.confidence_threshold:
                    filtered_boxes.append(box)
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: vehicle {i} passed filter (confidence: {confidence:.3f})")
                else:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: vehicle {i} filtered out (confidence: {confidence:.3f} < {self.confidence_threshold})")
            
            self.logger.info(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: 🚗 Vehicles detected: {len(filtered_boxes)} (filtered from {len(vehicle_boxes)})")
            self.processing_stats['vehicles_detected'] += len(filtered_boxes)
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_vehicles: returning {len(filtered_boxes)} filtered vehicle boxes")
            return filtered_boxes
            
        except Exception as e:
            self.logger.error(f"🔧 [DETECTION_PROCESSOR] detect_vehicles error: {e}")
            return []
    
    def detect_license_plates(self, frame: np.ndarray, vehicle_boxes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detect license plates within detected vehicles.
        
        Args:
            frame: Original image frame
            vehicle_boxes: List of detected vehicle bounding boxes
            
        Returns:
            List[Dict[str, Any]]: List of detected license plates
        """
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates called with frame shape: {frame.shape if frame is not None else 'None'}, vehicle_boxes: {len(vehicle_boxes)}")
        
        if not self.models_loaded or not self.lp_detection_model:
            self.logger.warning(f"🔧 [DETECTION_PROCESSOR] detect_license_plates failed: models_loaded={self.models_loaded}, lp_detection_model={self.lp_detection_model is not None}")
            return []
        
        detected_plates = []
        
        for i, vehicle_box in enumerate(vehicle_boxes):
            try:
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: processing vehicle {i}")
                
                # Extract vehicle region
                if 'bbox' not in vehicle_box:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} has no bbox, skipping")
                    continue
                    
                x1, y1, x2, y2 = vehicle_box['bbox']
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} bbox: [{x1}, {y1}, {x2}, {y2}]")
                
                vehicle_region = frame[int(y1):int(y2), int(x1):int(x2)]
                
                if vehicle_region.size == 0:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} region is empty, skipping")
                    continue
                
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} region shape: {vehicle_region.shape}")
                
                # Perform license plate detection on vehicle region
                lp_results = self.lp_detection_model(vehicle_region)
                lp_boxes = getattr(lp_results, "results", [])
                
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} raw LP detection results: {len(lp_boxes)} plates found")
                
                # Filter by confidence and convert coordinates back to full frame
                for j, lp_box in enumerate(lp_boxes):
                    confidence = lp_box.get('score', 0)
                    if confidence >= self.plate_confidence_threshold:
                        # Convert coordinates back to full frame
                        lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                        full_x1 = x1 + lp_x1
                        full_y1 = y1 + lp_y1
                        full_x2 = x1 + lp_x2
                        full_y2 = y1 + lp_y2
                        
                        plate_data = {
                            'bbox': [full_x1, full_y1, full_x2, full_y2],
                            'score': confidence,
                            'vehicle_idx': i,
                            'vehicle_bbox': vehicle_box['bbox']
                        }
                        
                        detected_plates.append(plate_data)
                        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} plate {j} passed filter (confidence: {confidence:.3f})")
                    else:
                        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: vehicle {i} plate {j} filtered out (confidence: {confidence:.3f} < {self.plate_confidence_threshold})")
                
            except Exception as e:
                self.logger.warning(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: error detecting plates in vehicle {i}: {e}")
                continue
        
        self.logger.info(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: 🔢 License plates detected: {len(detected_plates)} from {len(vehicle_boxes)} vehicles")
        self.processing_stats['plates_detected'] += len(detected_plates)
        
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] detect_license_plates: returning {len(detected_plates)} detected plates")
        return detected_plates
    
    def perform_ocr(self, frame: np.ndarray, plate_boxes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Perform OCR on detected license plates.
        
        Args:
            frame: Original image frame
            plate_boxes: List of detected license plate bounding boxes
            
        Returns:
            List[Dict[str, Any]]: OCR results with text and confidence
        """
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr called with frame shape: {frame.shape if frame is not None else 'None'}, plate_boxes: {len(plate_boxes)}")
        
        ocr_results = []
        
        for i, plate_box in enumerate(plate_boxes):
            try:
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: processing plate {i}")
                
                # Extract license plate region
                x1, y1, x2, y2 = plate_box['bbox']
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: plate {i} bbox: [{x1}, {y1}, {x2}, {y2}]")
                
                plate_region = frame[int(y1):int(y2), int(x1):int(x2)]
                
                if plate_region.size == 0:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: plate {i} region is empty, skipping")
                    continue
                
                self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: plate {i} region shape: {plate_region.shape}")
                
                # Try Hailo OCR model first (if available)
                hailo_ocr_text = ""
                hailo_ocr_confidence = 0.0
                hailo_ocr_success = False
                
                if self.lp_ocr_model:
                    try:
                        ocr_result = self.lp_ocr_model(plate_region)
                        # Extract text from Hailo OCR result
                        hailo_ocr_text = str(ocr_result)  # Adapt based on actual model output format
                        hailo_ocr_confidence = 0.8  # Placeholder - extract actual confidence
                        hailo_ocr_success = True
                    except Exception as e:
                        self.logger.debug(f"Hailo OCR failed for plate {i}: {e}")
                
                # Use parallel OCR processing (Hailo + EasyOCR simultaneously)
                parallel_results = None
                if self.parallel_ocr_processor:
                    try:
                        parallel_results = self.parallel_ocr_processor.process_plate_parallel(
                            plate_region, i, timeout=10.0
                        )
                    except Exception as e:
                        self.logger.warning(f"Parallel OCR failed for plate {i}: {e}")
                
                # Extract results from parallel processing
                if parallel_results:
                    # Get best result
                    best_result = parallel_results.get('best_result', {})
                    if best_result and best_result.get('success'):
                        final_ocr_text = best_result['text']
                        final_ocr_confidence = best_result['confidence']
                        ocr_method = best_result['method']
                    
                    # Extract individual results for database storage
                    hailo_result = parallel_results.get('hailo', {})
                    easyocr_result = parallel_results.get('easyocr', {})
                    
                    hailo_ocr_text = hailo_result.get('text', '') if hailo_result.get('success') else ''
                    hailo_ocr_confidence = hailo_result.get('confidence', 0.0)
                    hailo_ocr_success = hailo_result.get('success', False)
                    
                    easyocr_text = easyocr_result.get('text', '') if easyocr_result.get('success') else ''
                    easyocr_confidence = easyocr_result.get('confidence', 0.0)
                    easyocr_success = easyocr_result.get('success', False)
                    
                else:
                    # Fallback to individual OCR methods if parallel processing failed
                    easyocr_text = ""
                    easyocr_confidence = 0.0
                    easyocr_success = False
                    
                    if self.async_ocr_loader.is_ready():
                        try:
                            easyocr_results = self.async_ocr_loader.read_text(plate_region)
                            if easyocr_results:
                                # Take the result with highest confidence
                                best_result = max(easyocr_results, key=lambda x: x[2])
                                easyocr_text = best_result[1]
                                easyocr_confidence = best_result[2]
                                easyocr_success = True
                        except Exception as e:
                            self.logger.debug(f"Async EasyOCR failed for plate {i}: {e}")
                    elif self.async_ocr_loader.is_loading():
                        self.logger.debug(f"EasyOCR still loading - skipping OCR for plate {i}")
                    else:
                        self.logger.debug(f"EasyOCR not available - skipping OCR for plate {i}")
                
                # Determine final OCR result (prefer Hailo OCR if available)
                final_ocr_text = hailo_ocr_text if hailo_ocr_success else easyocr_text
                final_ocr_confidence = hailo_ocr_confidence if hailo_ocr_success else easyocr_confidence
                ocr_method = "hailo" if hailo_ocr_success else "easyocr" if easyocr_success else "none"
                
                if final_ocr_text:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: plate {i} OCR successful with method: {ocr_method}, text: '{final_ocr_text.strip()}', confidence: {final_ocr_confidence:.3f}")
                    
                    # Enhanced OCR result with parallel processing metadata
                    ocr_result = {
                        'plate_idx': i,
                        'bbox': plate_box['bbox'],
                        'text': final_ocr_text.strip(),
                        'confidence': final_ocr_confidence,
                        'vehicle_idx': plate_box.get('vehicle_idx', -1),
                        'detection_confidence': plate_box.get('score', 0),
                        'ocr_method': ocr_method,
                        'hailo_ocr': {
                            'text': hailo_ocr_text.strip() if hailo_ocr_success else "",
                            'confidence': hailo_ocr_confidence,
                            'success': hailo_ocr_success
                        },
                        'easyocr': {
                            'text': easyocr_text.strip() if easyocr_success else "",
                            'confidence': easyocr_confidence,
                            'success': easyocr_success
                        }
                    }
                    
                    # Add parallel processing metadata if available
                    if parallel_results:
                        ocr_result['parallel_processing'] = {
                            'parallel_success': parallel_results.get('parallel_success', False),
                            'processing_time': parallel_results.get('processing_time', 0.0),
                            'hailo_time': parallel_results.get('hailo', {}).get('processing_time', 0.0),
                            'easyocr_time': parallel_results.get('easyocr', {}).get('processing_time', 0.0),
                            'selection_reason': parallel_results.get('best_result', {}).get('selection_reason', '')
                        }
                    
                    ocr_results.append(ocr_result)
                    self.processing_stats['successful_ocr'] += 1
                else:
                    self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: plate {i} OCR failed - no text extracted")
                
            except Exception as e:
                self.logger.warning(f"🔧 [DETECTION_PROCESSOR] perform_ocr: error performing OCR on plate {i}: {e}")
                continue
        
        self.logger.info(f"🔧 [DETECTION_PROCESSOR] perform_ocr: 📝 OCR successful: {len(ocr_results)} from {len(plate_boxes)} plates")
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] perform_ocr: returning {len(ocr_results)} OCR results")
        return ocr_results
    
    def save_detection_results(self, original_frame: np.ndarray, vehicle_boxes: List[Dict], 
                             plate_boxes: List[Dict], ocr_results: List[Dict]) -> Tuple[str, str, str, List[str]]:
        """
        Save only original image for performance optimization.
        Detection bounding boxes will be drawn dynamically in showDetail.
        
        Args:
            original_frame: Original image frame
            vehicle_boxes: Detected vehicles
            plate_boxes: Detected license plates
            ocr_results: OCR results
            
        Returns:
            Tuple[str, str, str, List[str]]: Path to original image, empty strings for compatibility
        """
        try:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]

            # Ensure directory exists and is writable
            Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
            if not os.access(IMAGE_SAVE_DIR, os.W_OK):
                self.logger.error(f"Image save directory not writable: {IMAGE_SAVE_DIR}")
                return "", "", "", []

            # Step 1: Save only original image with datetime format filename
            original_filename = f"detection_{timestamp}.jpg"
            original_path = os.path.join(IMAGE_SAVE_DIR, original_filename)

            # Ensure frame is uint8 for imwrite
            frame_to_save = original_frame
            if frame_to_save is None or not isinstance(frame_to_save, np.ndarray) or frame_to_save.size == 0:
                self.logger.error("Invalid frame provided to save_detection_results")
                return "", "", "", []
            if frame_to_save.dtype != np.uint8:
                try:
                    frame_to_save = np.clip(frame_to_save, 0, 255).astype(np.uint8)
                except Exception:
                    self.logger.error("Failed to convert frame to uint8 for saving")
                    return "", "", "", []

            success = cv2.imwrite(original_path, frame_to_save)
            if not success or (not os.path.exists(original_path)):
                self.logger.error(f"cv2.imwrite failed or file missing after write: {original_path}")
                return "", "", "", []
            try:
                if os.path.getsize(original_path) <= 0:
                    self.logger.error(f"Saved image file is empty: {original_path}")
                    return "", "", "", []
            except OSError as e:
                self.logger.error(f"Error verifying saved image file: {e}")
                return "", "", "", []

            # Return empty strings for other image paths to maintain database schema compatibility
            # Detection bounding boxes will be drawn dynamically in showDetail for better performance
            vehicle_detected_path = ""
            plate_detected_path = ""
            cropped_paths = []

            self.logger.info(f"Saved original image only: {original_path} (optimized for performance)")
            return original_path, vehicle_detected_path, plate_detected_path, cropped_paths

        except Exception as e:
            self.logger.error(f"Error saving detection results: {e}")
            return "", "", "", []
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of the detection processor including model availability.
        
        Returns:
            Dict containing detection processor status information
        """
        self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status called")
        
        try:
            # Check model availability
            vehicle_model_available = self.vehicle_model is not None
            lp_detection_model_available = self.lp_detection_model is not None
            lp_ocr_model_available = self.lp_ocr_model is not None
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status: model availability - vehicle: {vehicle_model_available}, lp_detection: {lp_detection_model_available}, lp_ocr: {lp_ocr_model_available}")
            
            # Get OCR status
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status: getting OCR status")
            ocr_status = self.get_ocr_status()
            easyocr_available = ocr_status.get('easyocr_ready', False)
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status: OCR status - easyocr_available: {easyocr_available}")
            
            status = {
                'models_loaded': self.models_loaded,
                'vehicle_model_available': vehicle_model_available,
                'lp_detection_model_available': lp_detection_model_available,
                'lp_ocr_model_available': lp_ocr_model_available,
                'easyocr_available': easyocr_available,
                'detection_resolution': self.detection_resolution,
                'confidence_threshold': self.confidence_threshold,
                'plate_confidence_threshold': self.plate_confidence_threshold,
                'processing_stats': self.processing_stats.copy(),
                'last_update': datetime.now().isoformat()
            }
            
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status: returning status: {status}")
            return status
            
        except Exception as e:
            self.logger.error(f"🔧 [DETECTION_PROCESSOR] Error getting detection processor status: {e}")
            error_status = {
                'models_loaded': False,
                'vehicle_model_available': False,
                'lp_detection_model_available': False,
                'lp_ocr_model_available': False,
                'easyocr_available': False,
                'detection_resolution': self.detection_resolution,
                'confidence_threshold': self.confidence_threshold,
                'plate_confidence_threshold': self.plate_confidence_threshold,
                'processing_stats': {},
                'last_update': datetime.now().isoformat(),
                'error': str(e)
            }
            self.logger.debug(f"🔧 [DETECTION_PROCESSOR] get_status: returning error status: {error_status}")
            return error_status
    
    def _create_high_quality_detection_pipeline(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create high-quality frame for storage and detection-optimized frame for AI models.
        
        Returns:
            Tuple of (high_quality_frame, detection_frame)
        """
        try:
            # Keep original high-quality frame for storage
            high_quality_frame = frame.copy()
            
            # Create detection-optimized frame
            detection_frame = self._optimize_for_detection(frame)
            
            return high_quality_frame, detection_frame
            
        except Exception as e:
            self.logger.error(f"Failed to create detection pipeline: {e}")
            return frame, frame

    def _optimize_for_detection(self, frame: np.ndarray) -> np.ndarray:
        """Optimize frame specifically for detection models."""
        try:
            # Step 1: Apply quality enhancements before resizing
            enhanced_frame = self._enhance_frame_quality(frame)
            
            # Step 2: Smart resizing with letterboxing for aspect ratio preservation
            detection_frame = self._resize_with_letterbox(enhanced_frame, self.detection_resolution)
            
            # Step 3: Apply final detection-specific optimizations
            detection_frame = self._apply_detection_optimizations(detection_frame)
            
            return detection_frame
            
        except Exception as e:
            self.logger.error(f"Detection optimization failed: {e}")
            return cv2.resize(frame, self.detection_resolution)

    def _resize_with_letterbox(self, frame: np.ndarray, target_size: Tuple[int, int], 
                            padding_color: Tuple[int, int, int] = (114, 114, 114)) -> np.ndarray:
        """
        Resize frame to target size while preserving aspect ratio using letterboxing.
        
        Args:
            frame: Input frame
            target_size: Target (width, height)
            padding_color: BGR color for padding
            
        Returns:
            Resized frame with letterboxing
        """
        try:
            target_w, target_h = target_size
            frame_h, frame_w = frame.shape[:2]
            
            # Calculate scaling factor
            scale = min(target_w / frame_w, target_h / frame_h)
            
            # Calculate new dimensions
            new_w = int(frame_w * scale)
            new_h = int(frame_h * scale)
            
            # Resize frame
            resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
            
            # Create target canvas with padding color
            canvas = np.full((target_h, target_w, 3), padding_color, dtype=np.uint8)
            
            # Calculate padding
            pad_x = (target_w - new_w) // 2
            pad_y = (target_h - new_h) // 2
            
            # Place resized frame on canvas
            canvas[pad_y:pad_y + new_h, pad_x:pad_x + new_w] = resized
            
            return canvas
            
        except Exception as e:
            self.logger.error(f"Letterbox resizing failed: {e}")
            return cv2.resize(frame, target_size)

            # Add to DetectionProcessor
   
    def _enhance_frame_quality(self, frame: np.ndarray) -> np.ndarray:
        """Apply advanced image enhancement for better detection quality."""
        try:
            enhanced_frame = frame.copy()
            
            # Step 1: Noise reduction
            enhanced_frame = cv2.fastNlMeansDenoisingColored(enhanced_frame, None, 10, 10, 7, 21)
            
            # Step 2: Sharpening using unsharp masking
            enhanced_frame = self._apply_unsharp_masking(enhanced_frame, amount=1.5, radius=1.0, threshold=0)
            
            # Step 3: Contrast enhancement using CLAHE
            enhanced_frame = self._apply_clahe_enhancement(enhanced_frame)
            
            # Step 4: Brightness normalization
            enhanced_frame = self._normalize_brightness(enhanced_frame)
            
            return enhanced_frame
            
        except Exception as e:
            self.logger.warning(f"Frame enhancement failed: {e}")
            return frame

    def _apply_unsharp_masking(self, frame: np.ndarray, amount: float = 1.5, 
                          radius: float = 1.0, threshold: int = 0) -> np.ndarray:
        """Apply unsharp masking for image sharpening."""
        try:
            # Convert to float for processing
            frame_float = frame.astype(np.float32) / 255.0
            
            # Create Gaussian blur
            blurred = cv2.GaussianBlur(frame_float, (0, 0), radius)
            
            # Apply unsharp masking
            sharpened = frame_float + amount * (frame_float - blurred)
            
            # Clip values and convert back to uint8
            sharpened = np.clip(sharpened, 0, 1)
            return (sharpened * 255).astype(np.uint8)
            
        except Exception as e:
            self.logger.warning(f"Unsharp masking failed: {e}")
            return frame

            # Add to DetectionProcessor
   
    def _assess_frame_quality(self, frame: np.ndarray) -> Dict[str, Any]:
        """Assess overall frame quality for detection."""
        try:
            # Convert to grayscale for analysis
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance for sharpness
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate brightness and contrast
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Calculate noise level using local variance
            noise_level = self._estimate_noise_level(gray)
            
            # Determine overall quality score
            quality_score = self._calculate_quality_score(laplacian_var, brightness, contrast, noise_level)
            
            return {
                'sharpness_score': laplacian_var,
                'brightness': brightness,
                'contrast': contrast,
                'noise_level': noise_level,
                'quality_score': quality_score,
                'overall_quality': 'excellent' if quality_score > 80 else 'good' if quality_score > 60 else 'fair' if quality_score > 40 else 'poor'
            }
            
        except Exception as e:
            self.logger.warning(f"Quality assessment failed: {e}")
            return {}

    def _calculate_quality_score(self, sharpness: float, brightness: float, 
                            contrast: float, noise: float) -> float:
        """Calculate overall quality score (0-100)."""
        try:
            # Normalize values to 0-100 scale
            sharpness_score = min(sharpness / 10.0, 100)  # Normalize sharpness
            brightness_score = 100 - abs(brightness - 128) / 1.28  # Optimal around 128
            contrast_score = min(contrast / 2.0, 100)  # Normalize contrast
            noise_score = max(100 - noise, 0)  # Lower noise = higher score
            
            # Weighted average
            weights = [0.4, 0.2, 0.2, 0.2]  # Sharpness is most important
            scores = [sharpness_score, brightness_score, contrast_score, noise_score]
            
            quality_score = sum(w * s for w, s in zip(weights, scores))
            return max(0, min(100, quality_score))
            
        except Exception as e:
            self.logger.warning(f"Quality score calculation failed: {e}")
            return 50.0  # Default middle score

    def _log_quality_metrics(self, frame: np.ndarray, detection_results: List[Dict[str, Any]]):
        """Log quality metrics for analytics and monitoring."""
        try:
            quality_metrics = self._assess_frame_quality(frame)
            
            # Add detection performance metrics
            quality_metrics.update({
                'detection_count': len(detection_results),
                'detection_confidence_avg': np.mean([d.get('confidence', 0) for d in detection_results]) if detection_results else 0,
                'timestamp': time.time(),
                'frame_shape': frame.shape
            })
            
            # Log to database or analytics system
            self._store_quality_metrics(quality_metrics)
            
            # Alert if quality is consistently poor
            if quality_metrics['overall_quality'] == 'poor':
                self._alert_poor_quality(quality_metrics)
                
        except Exception as e:
            self.logger.warning(f"Quality metrics logging failed: {e}")

    def _monitor_processing_performance(self):
        """Monitor detection processing performance."""
        try:
            current_time = time.time()
            
            # Calculate processing time
            if hasattr(self, '_last_processing_time'):
                processing_time = current_time - self._last_processing_time
                self._processing_times.append(processing_time)
                
                # Keep only last 100 measurements
                if len(self._processing_times) > 100:
                    self._processing_times.pop(0)
                    
                # Calculate average processing time
                avg_processing_time = np.mean(self._processing_times)
                
                # Alert if processing is too slow
                if avg_processing_time > 0.1:  # More than 100ms
                    self.logger.warning(f"Slow processing detected: {avg_processing_time:.3f}s average")
                    
            self._last_processing_time = current_time
            
        except Exception as e:
            self.logger.warning(f"Performance monitoring failed: {e}")