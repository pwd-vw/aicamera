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
        
        # Model instances
        self.vehicle_model = None
        self.lp_detection_model = None
        self.lp_ocr_model = None
        self.ocr_reader = None  # Legacy - will be replaced by async_ocr_loader
        
        # Async OCR loader for non-blocking EasyOCR initialization
        self.async_ocr_loader = AsyncOCRLoader(languages=EASYOCR_LANGUAGES, logger=self.logger)
        
        # Parallel OCR processor for simultaneous Hailo + EasyOCR
        self.parallel_ocr_processor = None
        
        # State tracking
        self.models_loaded = False
        self.processing_stats = {
            'total_processed': 0,
            'vehicles_detected': 0,
            'plates_detected': 0,
            'successful_ocr': 0,
            'last_detection': None
        }
        
        # Configuration
        self.detection_resolution = (640, 640)
        self.confidence_threshold = CONFIDENCE_THRESHOLD
        self.plate_confidence_threshold = PLATE_CONFIDENCE_THRESHOLD
        self.logger.info("DetectionProcessor initialized")
    
    def load_models(self) -> bool:
        """
        Load all detection and OCR models using configuration parameters.
        
        Returns:
            bool: True if models loaded successfully, False otherwise
        """
        try:
            self.logger.info("🔧 Loading detection models...")
            
            # Check if required model parameters are available
            if not VEHICLE_DETECTION_MODEL:
                self.logger.warning("VEHICLE_DETECTION_MODEL not configured")
                return False
            
            if not LICENSE_PLATE_DETECTION_MODEL:
                self.logger.warning("LICENSE_PLATE_DETECTION_MODEL not configured")
                return False
            
            # Import degirum for Hailo model loading
            # Configure HailoRT logging before importing degirum
            from edge.config.hailort_logging import configure_hailort_logging
            configure_hailort_logging()
            
            try:
                import degirum as dg
                self.logger.info("✅ Degirum available for Hailo AI model loading")
            except ImportError:
                self.logger.error("degirum not available - cannot load Hailo models")
                return False
            
            models_loaded = 0
            
            # Load vehicle detection model
            try:
                self.logger.info(f"Loading vehicle detection model: {VEHICLE_DETECTION_MODEL}")
                self.vehicle_model = dg.load_model(
                    model_name=VEHICLE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL
                )
                self.logger.info("✅ Vehicle detection model loaded successfully")
                models_loaded += 1
            except Exception as e:
                self.logger.error(f"Failed to load vehicle detection model: {e}")
                return False
            
            # Load license plate detection model
            try:
                self.logger.info(f"Loading license plate detection model: {LICENSE_PLATE_DETECTION_MODEL}")
                self.lp_detection_model = dg.load_model(
                    model_name=LICENSE_PLATE_DETECTION_MODEL,
                    inference_host_address=HEF_MODEL_PATH,
                    zoo_url=MODEL_ZOO_URL,
                    overlay_color=[(255, 255, 0), (0, 255, 0)]
                )
                self.logger.info("✅ License plate detection model loaded successfully")
                models_loaded += 1
            except Exception as e:
                self.logger.error(f"Failed to load license plate detection model: {e}")
                return False
            
            # Load license plate OCR model (optional)
            if LICENSE_PLATE_OCR_MODEL:
                try:
                    self.logger.info(f"Loading license plate OCR model: {LICENSE_PLATE_OCR_MODEL}")
                    self.lp_ocr_model = dg.load_model(
                        model_name=LICENSE_PLATE_OCR_MODEL,
                        inference_host_address=HEF_MODEL_PATH,
                        zoo_url=MODEL_ZOO_URL,
                        output_use_regular_nms=False,
                        output_confidence_threshold=0.1
                    )
                    self.logger.info("✅ License plate OCR model loaded successfully")
                    models_loaded += 1
                except Exception as e:
                    self.logger.warning(f"Failed to load OCR model (optional): {e}")
            
            # Start asynchronous EasyOCR loading (non-blocking)
            try:
                self.logger.info("🚀 Starting asynchronous EasyOCR loading...")
                if self.async_ocr_loader.start_loading():
                    self.logger.info("✅ EasyOCR loading started in background")
                    # Don't increment models_loaded here - OCR will be available later
                else:
                    self.logger.warning("EasyOCR loading already in progress or failed to start")
            except Exception as e:
                self.logger.warning(f"Failed to start EasyOCR loading: {e}")
            
            # Initialize parallel OCR processor
            try:
                from edge.src.components.parallel_ocr_processor import ParallelOCRProcessor
                self.parallel_ocr_processor = ParallelOCRProcessor(
                    hailo_ocr_model=self.lp_ocr_model,
                    async_ocr_loader=self.async_ocr_loader,
                    logger=self.logger
                )
                self.logger.info("✅ Parallel OCR processor initialized")
            except Exception as e:
                self.logger.warning(f"Failed to initialize parallel OCR processor: {e}")
                self.parallel_ocr_processor = None
            
            self.models_loaded = models_loaded >= 2  # At least vehicle + LP detection
            self.logger.info(f"Models loaded: {models_loaded}, Ready: {self.models_loaded}")
            
            return self.models_loaded
            
        except Exception as e:
            self.logger.error(f"Error loading models: {e}")
            return False
    
    def get_ocr_status(self) -> Dict[str, Any]:
        """
        Get current OCR loading and usage status.
        
        Returns:
            Dict containing OCR status information
        """
        return self.async_ocr_loader.get_loading_status()
    
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
        Clean up resources including async OCR loader.
        """
        try:
            if hasattr(self, 'async_ocr_loader'):
                self.async_ocr_loader.cleanup()
            
            if hasattr(self, 'parallel_ocr_processor') and self.parallel_ocr_processor:
                self.parallel_ocr_processor.cleanup()
                
            self.logger.info("DetectionProcessor cleaned up")
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
        if frame is None:
            self.logger.warning("Invalid frame: frame is None")
            return None
        
        # Check if frame is a dict (should be numpy array)
        if isinstance(frame, dict):
            self.logger.error("Invalid frame: received dict instead of numpy array")
            if 'frame' in frame:
                self.logger.info("Extracting frame from dict")
                frame = frame['frame']
                if frame is None:
                    self.logger.warning("Extracted frame is None")
                    return None
            else:
                self.logger.error("Dict does not contain 'frame' key")
                return None
        
        # Check if frame is numpy array
        if not isinstance(frame, np.ndarray):
            self.logger.error(f"Invalid frame: expected numpy array, got {type(frame)}")
            return None
        
        # Check frame size
        if frame.size == 0:
            self.logger.warning("Invalid frame: empty array")
            return None
        
        try:
            # Ensure frame is in BGR format for detection models
            if len(frame.shape) == 3:
                if frame.shape[2] == 4:  # BGRA
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                elif frame.shape[2] == 3:  # Already BGR/RGB - assume BGR
                    pass  # Keep as-is
            elif len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            else:
                self.logger.warning(f"Unsupported frame shape: {frame.shape}")
                return None
            
            # Resize frame to detection resolution if needed
            if frame.shape[:2] != self.detection_resolution:
                frame = cv2.resize(frame, self.detection_resolution)
                self.logger.debug(f"Resized frame to {self.detection_resolution}")
            
            # Basic enhancement - can be extended
            # Optional: histogram equalization, noise reduction, etc.
            
            return frame
            
        except Exception as e:
            self.logger.error(f"Error validating/enhancing frame: {e}")
            return None
    
    def detect_vehicles(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Perform vehicle detection on image frame.
        
        Args:
            frame: Input image frame (validated and enhanced)
            
        Returns:
            List[Dict[str, Any]]: List of detected vehicle objects
        """
        if not self.models_loaded or not self.vehicle_model:
            self.logger.warning("Vehicle detection model not available")
            return []
        
        try:
            self.logger.debug("Performing vehicle detection...")
            
            # Perform detection
            results = self.vehicle_model(frame)
            vehicle_boxes = getattr(results, "results", [])
            
            # Filter by confidence threshold
            filtered_boxes = []
            for box in vehicle_boxes:
                if box.get('score', 0) >= self.confidence_threshold:
                    filtered_boxes.append(box)
            
            self.logger.info(f"🚗 Vehicles detected: {len(filtered_boxes)}")
            self.processing_stats['vehicles_detected'] += len(filtered_boxes)
            
            return filtered_boxes
            
        except Exception as e:
            self.logger.error(f"Error in vehicle detection: {e}")
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
        if not self.models_loaded or not self.lp_detection_model:
            self.logger.warning("License plate detection model not available")
            return []
        
        detected_plates = []
        
        for i, vehicle_box in enumerate(vehicle_boxes):
            try:
                # Extract vehicle region
                if 'bbox' not in vehicle_box:
                    continue
                    
                x1, y1, x2, y2 = vehicle_box['bbox']
                vehicle_region = frame[int(y1):int(y2), int(x1):int(x2)]
                
                if vehicle_region.size == 0:
                    continue
                
                # Perform license plate detection on vehicle region
                lp_results = self.lp_detection_model(vehicle_region)
                lp_boxes = getattr(lp_results, "results", [])
                
                # Filter by confidence and convert coordinates back to full frame
                for lp_box in lp_boxes:
                    if lp_box.get('score', 0) >= self.plate_confidence_threshold:
                        # Convert coordinates back to full frame
                        lp_x1, lp_y1, lp_x2, lp_y2 = lp_box['bbox']
                        full_x1 = x1 + lp_x1
                        full_y1 = y1 + lp_y1
                        full_x2 = x1 + lp_x2
                        full_y2 = y1 + lp_y2
                        
                        detected_plates.append({
                            'bbox': [full_x1, full_y1, full_x2, full_y2],
                            'score': lp_box.get('score', 0),
                            'vehicle_idx': i,
                            'vehicle_bbox': vehicle_box['bbox']
                        })
                
            except Exception as e:
                self.logger.warning(f"Error detecting plates in vehicle {i}: {e}")
                continue
        
        self.logger.info(f"🔢 License plates detected: {len(detected_plates)}")
        self.processing_stats['plates_detected'] += len(detected_plates)
        
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
        ocr_results = []
        
        for i, plate_box in enumerate(plate_boxes):
            try:
                # Extract license plate region
                x1, y1, x2, y2 = plate_box['bbox']
                plate_region = frame[int(y1):int(y2), int(x1):int(x2)]
                
                if plate_region.size == 0:
                    continue
                
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
                
            except Exception as e:
                self.logger.warning(f"Error performing OCR on plate {i}: {e}")
                continue
        
        self.logger.info(f"📝 OCR successful: {len(ocr_results)}")
        return ocr_results
    
    def save_detection_results(self, original_frame: np.ndarray, vehicle_boxes: List[Dict], 
                             plate_boxes: List[Dict], ocr_results: List[Dict]) -> Tuple[str, str, str, List[str]]:
        """
        Save original image, vehicle detection image, and license plate detection image with cropped plates.
        
        Args:
            original_frame: Original image frame
            vehicle_boxes: Detected vehicles
            plate_boxes: Detected license plates
            ocr_results: OCR results
            
        Returns:
            Tuple[str, str, str, List[str]]: Path to original image, vehicle detection image, plate detection image, list of cropped plate paths
        """
        try:
            # Generate timestamp for filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            
            # Create directories if they don't exist
            Path(IMAGE_SAVE_DIR).mkdir(parents=True, exist_ok=True)
            
            # Step 1: Save original image with datetime format filename
            original_filename = f"detection_{timestamp}.jpg"
            original_path = os.path.join(IMAGE_SAVE_DIR, original_filename)
            cv2.imwrite(original_path, original_frame)
            
            # Step 2: Create vehicle detection image (original + vehicle bounding boxes only)
            vehicle_detected_frame = original_frame.copy()
            
            # Draw vehicle boxes (green) only
            for vehicle_box in vehicle_boxes:
                if 'bbox' in vehicle_box:
                    x1, y1, x2, y2 = vehicle_box['bbox']
                    cv2.rectangle(vehicle_detected_frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                                (0, 255, 0), 2)
                    
                    # Add vehicle label
                    label = vehicle_box.get('label', 'Vehicle')
                    confidence = vehicle_box.get('score', 0)
                    cv2.putText(vehicle_detected_frame, f"{label} {confidence:.2f}", 
                              (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.5, (0, 255, 0), 2)
            
            # Step 3: Create license plate detection image (original + plate bounding boxes only)
            plate_detected_frame = original_frame.copy()
            
            # Draw license plate boxes (blue) and add OCR text
            for plate_box in plate_boxes:
                x1, y1, x2, y2 = plate_box['bbox']
                cv2.rectangle(plate_detected_frame, (int(x1), int(y1)), (int(x2), int(y2)), 
                            (255, 0, 0), 2)
                
                # Add plate confidence score
                plate_confidence = plate_box.get('score', 0)
                cv2.putText(plate_detected_frame, f"LP {plate_confidence:.2f}", 
                          (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                          0.5, (255, 0, 0), 2)
                
                # Add OCR text if available
                plate_idx = plate_boxes.index(plate_box)
                ocr_text = ""
                ocr_confidence = 0.0
                for ocr_result in ocr_results:
                    if ocr_result.get('plate_idx') == plate_idx:
                        ocr_text = ocr_result['text']
                        ocr_confidence = ocr_result.get('confidence', 0)
                        break
                
                if ocr_text:
                    # Display OCR text with confidence
                    cv2.putText(plate_detected_frame, f"{ocr_text} ({ocr_confidence:.2f})", 
                              (int(x1), int(y2) + 20), cv2.FONT_HERSHEY_SIMPLEX, 
                              0.6, (255, 0, 0), 2)
            
            # Step 4: Save vehicle detection image
            vehicle_detected_filename = f"vehicle_detected_{timestamp}.jpg"
            vehicle_detected_path = os.path.join(IMAGE_SAVE_DIR, vehicle_detected_filename)
            cv2.imwrite(vehicle_detected_path, vehicle_detected_frame)
            
            # Step 5: Save license plate detection image
            plate_detected_filename = f"plate_detected_{timestamp}.jpg"
            plate_detected_path = os.path.join(IMAGE_SAVE_DIR, plate_detected_filename)
            cv2.imwrite(plate_detected_path, plate_detected_frame)
            
            # Step 6: Save cropped license plates
            cropped_paths = []
            for i, plate_box in enumerate(plate_boxes):
                try:
                    x1, y1, x2, y2 = plate_box['bbox']
                    plate_crop = original_frame[int(y1):int(y2), int(x1):int(x2)]
                    
                    if plate_crop.size > 0:
                        crop_path = os.path.join(IMAGE_SAVE_DIR, f"plate_{timestamp}_{i}.jpg")
                        cv2.imwrite(crop_path, plate_crop)
                        cropped_paths.append(crop_path)
                        
                except Exception as e:
                    self.logger.warning(f"Failed to save cropped plate {i}: {e}")
            
            self.logger.info(f"Saved detection results: original={original_path}, vehicle={vehicle_detected_path}, plate={plate_detected_path}, {len(cropped_paths)} plates")
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
        try:
            # Check model availability
            vehicle_model_available = self.vehicle_model is not None
            lp_detection_model_available = self.lp_detection_model is not None
            lp_ocr_model_available = self.lp_ocr_model is not None
            
            # Get OCR status
            ocr_status = self.get_ocr_status()
            easyocr_available = ocr_status.get('easyocr_ready', False)
            
            return {
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
        except Exception as e:
            self.logger.error(f"Error getting detection processor status: {e}")
            return {
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
    
    def cleanup(self):
        """Clean up resources and models."""
        try:
            self.logger.info("Cleaning up DetectionProcessor...")
            
            # Clean up model references
            self.vehicle_model = None
            self.lp_detection_model = None  
            self.lp_ocr_model = None
            self.ocr_reader = None
            
            self.models_loaded = False
            
            self.logger.info("DetectionProcessor cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during DetectionProcessor cleanup: {e}")
