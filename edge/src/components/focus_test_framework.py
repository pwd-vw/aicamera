#!/usr/bin/env python3
"""
Focus Test Framework for AI Camera v2.0

This module provides a comprehensive testing framework for evaluating
different focus modes and their impact on detection and OCR accuracy.

Author: AI Camera Team
Version: 2.0
Date: December 2025
"""

import time
import json
import os
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path

from edge.src.core.utils.logging_config import get_logger
from edge.src.components.enhanced_focus_controller import EnhancedFocusController

logger = get_logger(__name__)


class FocusTestFramework:
    """
    Framework for testing different focus modes and evaluating performance.
    
    Features:
    - Test multiple focus modes
    - Collect comprehensive metrics
    - Compare results across modes
    - Export test results
    """
    
    def __init__(self, camera_handler, detection_manager=None):
        """
        Initialize focus test framework.
        
        Args:
            camera_handler: CameraHandler instance
            detection_manager: DetectionManager instance (optional)
        """
        self.camera = camera_handler
        self.detection = detection_manager
        self.logger = logger
        
        # Test results storage
        self.results: List[Dict[str, Any]] = []
        
        # Enhanced focus controller
        self.focus_controller = EnhancedFocusController(camera_handler)
        
        # Test configuration
        self.test_config = {
            'frame_rate': 30.0,  # Target FPS
            'warmup_frames': 30,  # Frames to skip at start
            'min_test_duration': 60.0,  # Minimum test duration in seconds
            'max_test_duration': 600.0,  # Maximum test duration in seconds
        }
        
        self.logger.info("FocusTestFramework initialized")
    
    def run_test(self, mode: str, duration: int = 300, **kwargs) -> Dict[str, Any]:
        """
        Run focus test for specified mode and duration.
        
        Args:
            mode: Focus mode to test ("auto", "continuous", "manual", "hybrid")
            duration: Test duration in seconds
            **kwargs: Mode-specific parameters
            
        Returns:
            Dict with test results and metrics
        """
        if duration < self.test_config['min_test_duration']:
            self.logger.warning(f"Test duration too short, using minimum: {self.test_config['min_test_duration']}s")
            duration = int(self.test_config['min_test_duration'])
        
        if duration > self.test_config['max_test_duration']:
            self.logger.warning(f"Test duration too long, using maximum: {self.test_config['max_test_duration']}s")
            duration = int(self.test_config['max_test_duration'])
        
        self.logger.info(f"Starting focus test: mode={mode}, duration={duration}s")
        
        # Setup focus mode
        if not self.focus_controller.set_focus_mode(mode, **kwargs):
            self.logger.error(f"Failed to setup focus mode: {mode}")
            return None
        
        # Reset statistics
        self.focus_controller.reset_statistics()
        
        # Initialize metrics
        metrics = {
            'mode': mode,
            'mode_params': kwargs,
            'start_time': time.time(),
            'end_time': None,
            'duration': duration,
            'focus_fom_values': [],
            'focus_fom_timestamps': [],
            'detection_results': [],
            'focus_actions': [],
            'metadata_samples': []
        }
        
        # Run test
        end_time = time.time() + duration
        frame_count = 0
        last_frame_time = time.time()
        frame_interval = 1.0 / self.test_config['frame_rate']
        
        # Warmup period
        warmup_frames = 0
        while warmup_frames < self.test_config['warmup_frames']:
            frame = self.camera.capture_frame(source="buffer", stream_type="main")
            if frame is not None:
                warmup_frames += 1
            time.sleep(0.033)
        
        self.logger.info(f"Warmup complete, starting test data collection")
        
        # Main test loop
        while time.time() < end_time:
            current_time = time.time()
            
            # Rate limiting
            if current_time - last_frame_time < frame_interval:
                time.sleep(0.001)
                continue
            
            try:
                # Capture frame with metadata
                frame_data = self.camera.capture_frame(
                    source="buffer", 
                    stream_type="main", 
                    include_metadata=True
                )
                
                if frame_data is None:
                    continue
                
                # Extract metadata
                if isinstance(frame_data, dict):
                    metadata = frame_data.get('metadata', {})
                    frame = frame_data.get('frame')
                else:
                    metadata = {}
                    frame = frame_data
                
                # Record FocusFoM
                focus_fom = metadata.get("FocusFoM", 0)
                if focus_fom > 0:  # Only record valid FocusFoM
                    metrics['focus_fom_values'].append(focus_fom)
                    metrics['focus_fom_timestamps'].append(current_time)
                
                # Sample metadata periodically (every 10 frames)
                if frame_count % 10 == 0:
                    metrics['metadata_samples'].append({
                        'timestamp': current_time,
                        'metadata': metadata
                    })
                
                # Run detection if available
                detection_result = None
                if self.detection and frame is not None:
                    try:
                        detection_result = self.detection.process_frame_from_camera(
                            self.camera.camera_manager
                        )
                        
                        if detection_result:
                            metrics['detection_results'].append({
                                'timestamp': current_time,
                                'frame_count': frame_count,
                                'vehicles_detected': len(detection_result.get('vehicles', [])),
                                'license_plates_detected': len(detection_result.get('license_plates', [])),
                                'ocr_results': detection_result.get('ocr_results', []),
                                'focus_fom': focus_fom
                            })
                    except Exception as e:
                        self.logger.debug(f"Detection failed: {e}")
                
                # Update focus controller
                self.focus_controller.update_focus_quality(metadata, detection_result)
                
                # Record focus actions
                focus_stats = self.focus_controller.get_focus_statistics()
                if focus_stats['stats']['focus_actions'] > len(metrics['focus_actions']):
                    metrics['focus_actions'].append({
                        'timestamp': current_time,
                        'action': 'focus_trigger',
                        'stats': focus_stats['stats'].copy()
                    })
                
                frame_count += 1
                last_frame_time = current_time
                
            except Exception as e:
                self.logger.error(f"Error in test loop: {e}")
                continue
        
        # Calculate final metrics
        metrics['end_time'] = time.time()
        metrics['actual_duration'] = metrics['end_time'] - metrics['start_time']
        metrics['total_frames'] = frame_count
        metrics['actual_frame_rate'] = frame_count / metrics['actual_duration'] if metrics['actual_duration'] > 0 else 0
        
        # Focus quality metrics
        if metrics['focus_fom_values']:
            metrics['focus_quality'] = {
                'mean': float(np.mean(metrics['focus_fom_values'])),
                'std': float(np.std(metrics['focus_fom_values'])),
                'min': float(np.min(metrics['focus_fom_values'])),
                'max': float(np.max(metrics['focus_fom_values'])),
                'median': float(np.median(metrics['focus_fom_values'])),
                'q25': float(np.percentile(metrics['focus_fom_values'], 25)),
                'q75': float(np.percentile(metrics['focus_fom_values'], 75))
            }
            
            # Focus quality distribution
            fom_values = np.array(metrics['focus_fom_values'])
            metrics['focus_quality_distribution'] = {
                'excellent': int(np.sum(fom_values > 1000)),  # FocusFoM > 1000
                'good': int(np.sum((fom_values > 700) & (fom_values <= 1000))),  # 700-1000
                'fair': int(np.sum((fom_values > 400) & (fom_values <= 700))),  # 400-700
                'poor': int(np.sum(fom_values <= 400))  # <= 400
            }
        else:
            metrics['focus_quality'] = None
            metrics['focus_quality_distribution'] = None
        
        # Detection metrics
        if metrics['detection_results']:
            total_detections = len(metrics['detection_results'])
            metrics['detection_metrics'] = {
                'total_detections': total_detections,
                'detection_rate': total_detections / frame_count if frame_count > 0 else 0,
                'avg_vehicles_per_detection': float(np.mean([
                    r['vehicles_detected'] for r in metrics['detection_results']
                ])) if metrics['detection_results'] else 0,
                'avg_license_plates_per_detection': float(np.mean([
                    r['license_plates_detected'] for r in metrics['detection_results']
                ])) if metrics['detection_results'] else 0,
                'total_vehicles_detected': sum([
                    r['vehicles_detected'] for r in metrics['detection_results']
                ]),
                'total_license_plates_detected': sum([
                    r['license_plates_detected'] for r in metrics['detection_results']
                ])
            }
            
            # OCR metrics (if available)
            ocr_results = []
            for r in metrics['detection_results']:
                ocr_results.extend(r.get('ocr_results', []))
            
            if ocr_results:
                ocr_confidences = [r.get('confidence', 0) for r in ocr_results if 'confidence' in r]
                if ocr_confidences:
                    metrics['ocr_metrics'] = {
                        'total_ocr_attempts': len(ocr_results),
                        'avg_confidence': float(np.mean(ocr_confidences)),
                        'min_confidence': float(np.min(ocr_confidences)),
                        'max_confidence': float(np.max(ocr_confidences))
                    }
                else:
                    metrics['ocr_metrics'] = None
            else:
                metrics['ocr_metrics'] = None
        else:
            metrics['detection_metrics'] = {
                'total_detections': 0,
                'detection_rate': 0,
                'avg_vehicles_per_detection': 0,
                'avg_license_plates_per_detection': 0,
                'total_vehicles_detected': 0,
                'total_license_plates_detected': 0
            }
            metrics['ocr_metrics'] = None
        
        # Focus controller statistics
        focus_stats = self.focus_controller.get_focus_statistics()
        metrics['focus_controller_stats'] = focus_stats
        
        # Store results
        self.results.append(metrics)
        
        self.logger.info(f"Test completed: mode={mode}, frames={frame_count}, duration={metrics['actual_duration']:.1f}s")
        
        return metrics
    
    def compare_results(self) -> Optional[Dict[str, Any]]:
        """
        Compare results from all test modes.
        
        Returns:
            Dict with comparison results, or None if no results
        """
        if not self.results:
            self.logger.warning("No test results to compare")
            return None
        
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(self.results),
            'modes': [],
            'focus_quality_comparison': {},
            'detection_comparison': {},
            'overall_scores': {},
            'best_mode': None,
            'recommendations': []
        }
        
        # Collect data for each mode
        for result in self.results:
            mode = result['mode']
            comparison['modes'].append(mode)
            
            # Focus quality comparison
            if result.get('focus_quality'):
                comparison['focus_quality_comparison'][mode] = {
                    'mean': result['focus_quality']['mean'],
                    'std': result['focus_quality']['std'],
                    'min': result['focus_quality']['min'],
                    'max': result['focus_quality']['max'],
                    'excellent_percent': (
                        result['focus_quality_distribution']['excellent'] / 
                        len(result['focus_fom_values']) * 100
                        if result['focus_fom_values'] else 0
                    ),
                    'poor_percent': (
                        result['focus_quality_distribution']['poor'] / 
                        len(result['focus_fom_values']) * 100
                        if result['focus_fom_values'] else 0
                    )
                }
            
            # Detection comparison
            if result.get('detection_metrics'):
                comparison['detection_comparison'][mode] = {
                    'detection_rate': result['detection_metrics']['detection_rate'],
                    'avg_vehicles': result['detection_metrics']['avg_vehicles_per_detection'],
                    'total_vehicles': result['detection_metrics']['total_vehicles_detected'],
                    'total_plates': result['detection_metrics']['total_license_plates_detected']
                }
        
        # Calculate overall scores
        for mode in comparison['modes']:
            score = 0.0
            factors = []
            
            # Focus quality score (0-1, weight: 0.6)
            if mode in comparison['focus_quality_comparison']:
                fq = comparison['focus_quality_comparison'][mode]
                fom_score = min(fq['mean'] / 1000.0, 1.0)  # Normalize to 0-1
                excellent_score = fq['excellent_percent'] / 100.0
                poor_penalty = fq['poor_percent'] / 100.0
                focus_score = (fom_score * 0.5) + (excellent_score * 0.3) - (poor_penalty * 0.2)
                focus_score = max(0.0, min(1.0, focus_score))  # Clamp to 0-1
                score += focus_score * 0.6
                factors.append(f"focus_quality: {focus_score:.3f}")
            
            # Detection score (0-1, weight: 0.4)
            if mode in comparison['detection_comparison']:
                dc = comparison['detection_comparison'][mode]
                detection_score = min(dc['detection_rate'], 1.0)
                score += detection_score * 0.4
                factors.append(f"detection_rate: {detection_score:.3f}")
            
            comparison['overall_scores'][mode] = {
                'score': score,
                'factors': factors
            }
        
        # Find best mode
        if comparison['overall_scores']:
            best_mode = max(comparison['overall_scores'].items(), key=lambda x: x[1]['score'])
            comparison['best_mode'] = {
                'mode': best_mode[0],
                'score': best_mode[1]['score']
            }
            
            # Generate recommendations
            if comparison['best_mode']['score'] > 0.7:
                comparison['recommendations'].append(
                    f"✅ {comparison['best_mode']['mode']} mode shows excellent performance "
                    f"(score: {comparison['best_mode']['score']:.3f})"
                )
            elif comparison['best_mode']['score'] > 0.5:
                comparison['recommendations'].append(
                    f"⚠️ {comparison['best_mode']['mode']} mode shows good performance "
                    f"(score: {comparison['best_mode']['score']:.3f}), but may need optimization"
                )
            else:
                comparison['recommendations'].append(
                    f"❌ All modes show poor performance. Consider adjusting parameters or "
                    f"environmental conditions."
                )
        
        return comparison
    
    def export_results(self, output_path: Optional[str] = None) -> str:
        """
        Export test results to JSON file.
        
        Args:
            output_path: Output file path (optional)
            
        Returns:
            Path to exported file
        """
        if not output_path:
            # Use project directory instead of /tmp/ to avoid permission issues
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Try to find project root
            project_root = Path(__file__).resolve()
            for _ in range(5):  # Go up max 5 levels
                project_root = project_root.parent
                if (project_root / 'edge').exists() and (project_root / 'edge' / 'src').exists():
                    break
            
            # Create results directory in project
            results_dir = project_root / 'edge' / 'tests' / 'results'
            results_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(results_dir / f"focus_test_results_{timestamp}.json")
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure parent directory is writable
        if not os.access(output_path.parent, os.W_OK):
            # Fallback to user home if project directory not writable
            fallback_dir = Path.home() / 'aicamera_test_results'
            fallback_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = fallback_dir / f"focus_test_results_{timestamp}.json"
        
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'test_results': self.results,
            'comparison': self.compare_results()
        }
        
        # Convert numpy types to native Python types for JSON serialization
        def convert_numpy(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        export_data = convert_numpy(export_data)
        
        try:
            with open(output_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            # Verify file was written
            if output_path.exists():
                file_size = output_path.stat().st_size
                self.logger.info(f"Test results exported to: {output_path} ({file_size} bytes)")
            else:
                self.logger.error(f"File was not created: {output_path}")
                raise IOError(f"Failed to create output file: {output_path}")
            
            return str(output_path)
        except (IOError, OSError, PermissionError) as e:
            self.logger.error(f"Failed to write results to {output_path}: {e}")
            # Try fallback location
            fallback_dir = Path.home() / 'aicamera_test_results'
            fallback_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            fallback_path = fallback_dir / f"focus_test_results_{timestamp}.json"
            try:
                with open(fallback_path, 'w') as f:
                    json.dump(export_data, f, indent=2, default=str)
                self.logger.info(f"Results saved to fallback location: {fallback_path}")
                return str(fallback_path)
            except Exception as e2:
                self.logger.error(f"Failed to write to fallback location: {e2}")
                raise
    
    def clear_results(self):
        """Clear all test results."""
        self.results.clear()
        self.logger.info("Test results cleared")

