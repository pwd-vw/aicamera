#!/usr/bin/env python3
"""
Enhanced Focus Controller for AI Camera v2.0

This module provides enhanced focus control with multiple modes:
- Auto mode: Single-shot autofocus with smart triggering
- Continuous mode: Continuous autofocus for moving objects
- Manual mode: Fixed focus with smart lock/unlock
- Hybrid mode: Adaptive focus based on detection results

Author: AI Camera Team
Version: 2.0
Date: December 2025
"""

import time
import threading
from typing import Dict, Any, Optional
from collections import deque
from datetime import datetime

from edge.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


class EnhancedFocusController:
    """
    Enhanced focus controller with multiple modes and adaptive behavior.
    
    Features:
    - Multiple focus modes (Auto, Continuous, Manual, Hybrid)
    - Adaptive focus adjustment based on quality metrics
    - Integration with detection results
    - Comprehensive focus quality monitoring
    - Smart focus lock/unlock mechanism
    """
    
    def __init__(self, camera_handler):
        """
        Initialize enhanced focus controller.
        
        Args:
            camera_handler: CameraHandler instance
        """
        self.camera = camera_handler
        self.logger = logger
        
        # Focus mode and state
        self.mode = "auto"  # auto, continuous, manual, hybrid
        self.focus_locked = False
        self.last_focus_action_time = 0.0
        
        # Focus quality tracking
        self.focus_history = deque(maxlen=100)
        self.detection_results_history = deque(maxlen=50)
        
        # Mode-specific parameters
        self.auto_mode_params = {
            'trigger_interval': 30.0,  # seconds
            'poor_threshold': 400,  # FocusFoM threshold
            'last_trigger_time': 0.0
        }
        
        self.continuous_mode_params = {
            'speed': 0,  # 0=Normal, 1=Fast
            'metering': 1,  # 0=Auto, 1=Center
            'range_mode': 0  # 0=Full, 1=Macro, 2=Normal
        }
        
        self.manual_mode_params = {
            'distance_m': 3.0,  # meters
            'unlock_interval': 60.0,  # seconds
            'last_unlock_time': 0.0,
            'poor_threshold': 300  # FocusFoM threshold for re-focus
        }
        
        self.hybrid_mode_params = {
            'base_distance': 3.0,  # meters
            'continuous_range': 2.0,  # meters
            'vehicle_detected_focus_threshold': 500  # FocusFoM threshold
        }
        
        # Statistics
        self.stats = {
            'focus_actions': 0,
            'focus_locks': 0,
            'focus_unlocks': 0,
            'focus_triggers': 0,
            'focus_hunting_events': 0
        }
        
        self.logger.info(f"EnhancedFocusController initialized with mode: {self.mode}")
    
    def set_focus_mode(self, mode: str, **kwargs):
        """
        Set focus mode with optional parameters.
        
        Args:
            mode: "auto", "continuous", "manual", "hybrid"
            **kwargs: Mode-specific parameters
        """
        if mode not in ["auto", "continuous", "manual", "hybrid"]:
            self.logger.error(f"Invalid focus mode: {mode}")
            return False
        
        old_mode = self.mode
        self.mode = mode
        
        try:
            if mode == "auto":
                self._setup_auto_mode(**kwargs)
            elif mode == "continuous":
                self._setup_continuous_mode(**kwargs)
            elif mode == "manual":
                self._setup_manual_mode(**kwargs)
            elif mode == "hybrid":
                self._setup_hybrid_mode(**kwargs)
            
            self.logger.info(f"Focus mode changed from {old_mode} to {mode}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set focus mode {mode}: {e}")
            self.mode = old_mode
            return False
    
    def _setup_auto_mode(self, trigger_interval: float = 30.0, poor_threshold: int = 400):
        """Setup auto focus mode."""
        if not self.camera or not self.camera.picam2:
            self.logger.error("Camera not available for auto mode setup")
            return
        
        controls = {
            "AfMode": 1,  # Auto
            "AfTrigger": 0,  # No trigger initially
            "AfMetering": 1,  # Center-weighted
            "AfRange": 0  # Full range
        }
        
        try:
            self.camera.picam2.set_controls(controls)
            self.auto_mode_params['trigger_interval'] = trigger_interval
            self.auto_mode_params['poor_threshold'] = poor_threshold
            self.auto_mode_params['last_trigger_time'] = 0.0
            self.logger.info(f"Auto focus mode setup: trigger_interval={trigger_interval}s, poor_threshold={poor_threshold}")
        except Exception as e:
            self.logger.error(f"Failed to setup auto mode: {e}")
            raise
    
    def _setup_continuous_mode(self, speed: int = 0, metering: int = 1, range_mode: int = 0):
        """Setup continuous focus mode."""
        if not self.camera or not self.camera.picam2:
            self.logger.error("Camera not available for continuous mode setup")
            return
        
        controls = {
            "AfMode": 2,  # Continuous
            "AfSpeed": speed,  # 0=Normal, 1=Fast
            "AfMetering": metering,  # 0=Auto, 1=Center
            "AfRange": range_mode  # 0=Full, 1=Macro, 2=Normal
        }
        
        try:
            self.camera.picam2.set_controls(controls)
            self.continuous_mode_params['speed'] = speed
            self.continuous_mode_params['metering'] = metering
            self.continuous_mode_params['range_mode'] = range_mode
            self.logger.info(f"Continuous focus mode setup: speed={speed}, metering={metering}, range={range_mode}")
        except Exception as e:
            self.logger.error(f"Failed to setup continuous mode: {e}")
            raise
    
    def _setup_manual_mode(self, distance_m: float = 3.0, unlock_interval: float = 60.0):
        """Setup manual focus mode with smart lock."""
        if not self.camera or not self.camera.picam2:
            self.logger.error("Camera not available for manual mode setup")
            return
        
        # Convert distance to diopters
        if distance_m <= 0:
            distance_m = 3.0
        diopters = 1.0 / distance_m
        diopters = max(0.1, min(10.0, diopters))  # Clamp to valid range
        
        controls = {
            "AfMode": 0,  # Manual
            "LensPosition": diopters,
            "AfMetering": 1  # Center-weighted
        }
        
        try:
            self.camera.picam2.set_controls(controls)
            self.manual_mode_params['distance_m'] = distance_m
            self.manual_mode_params['unlock_interval'] = unlock_interval
            self.manual_mode_params['last_unlock_time'] = time.time()
            self.focus_locked = True
            self.logger.info(f"Manual focus mode setup: distance={distance_m}m ({diopters:.3f} diopters), unlock_interval={unlock_interval}s")
        except Exception as e:
            self.logger.error(f"Failed to setup manual mode: {e}")
            raise
    
    def _setup_hybrid_mode(self, base_distance: float = 3.0, continuous_range: float = 2.0):
        """
        Hybrid mode: Continuous focus with range limitation.
        Focus continuously but limit range to reduce hunting.
        """
        if not self.camera or not self.camera.picam2:
            self.logger.error("Camera not available for hybrid mode setup")
            return
        
        # Start with continuous mode
        controls = {
            "AfMode": 2,  # Continuous
            "AfSpeed": 0,  # Normal speed
            "AfMetering": 1,  # Center-weighted
            "AfRange": 0  # Full range (libcamera may not support custom range)
        }
        
        try:
            self.camera.picam2.set_controls(controls)
            self.hybrid_mode_params['base_distance'] = base_distance
            self.hybrid_mode_params['continuous_range'] = continuous_range
            self.logger.info(f"Hybrid focus mode setup: base_distance={base_distance}m, range=±{continuous_range}m")
        except Exception as e:
            self.logger.error(f"Failed to setup hybrid mode: {e}")
            raise
    
    def update_focus_quality(self, metadata: Dict[str, Any], 
                            detection_result: Optional[Dict[str, Any]] = None):
        """
        Update focus quality assessment and adjust if needed.
        
        Args:
            metadata: Camera metadata with FocusFoM
            detection_result: Detection results (optional)
        """
        if not metadata:
            return
        
        focus_fom = metadata.get("FocusFoM", 0)
        current_time = time.time()
        
        # Record focus quality
        self.focus_history.append({
            'fom': focus_fom,
            'timestamp': current_time,
            'detection_success': detection_result is not None if detection_result else None,
            'vehicles_count': len(detection_result.get('vehicles', [])) if detection_result else 0
        })
        
        # Record detection results
        if detection_result:
            self.detection_results_history.append({
                'timestamp': current_time,
                'vehicles': detection_result.get('vehicles', []),
                'license_plates': detection_result.get('license_plates', []),
                'focus_fom': focus_fom
            })
        
        # Handle mode-specific updates
        try:
            if self.mode == "auto":
                self._handle_auto_mode(focus_fom, metadata, current_time)
            elif self.mode == "continuous":
                self._handle_continuous_mode(focus_fom, metadata, current_time)
            elif self.mode == "manual":
                self._handle_manual_mode(focus_fom, metadata, current_time)
            elif self.mode == "hybrid":
                self._handle_hybrid_mode(focus_fom, metadata, detection_result, current_time)
        except Exception as e:
            self.logger.warning(f"Error handling focus mode {self.mode}: {e}")
    
    def _handle_auto_mode(self, focus_fom: float, metadata: Dict[str, Any], current_time: float):
        """Handle auto focus mode updates."""
        params = self.auto_mode_params
        
        # Check if we need to trigger autofocus
        should_trigger = False
        
        # Trigger if quality is poor
        if focus_fom < params['poor_threshold']:
            should_trigger = True
            self.logger.debug(f"Auto mode: Poor focus quality ({focus_fom:.0f}), triggering AF")
        
        # Periodic trigger
        if current_time - params['last_trigger_time'] > params['trigger_interval']:
            should_trigger = True
            self.logger.debug(f"Auto mode: Periodic trigger (interval: {params['trigger_interval']}s)")
        
        if should_trigger:
            try:
                # Trigger autofocus
                self.camera.picam2.set_controls({"AfTrigger": 1})
                time.sleep(0.1)  # Wait for trigger
                self.camera.picam2.set_controls({"AfTrigger": 0})
                
                params['last_trigger_time'] = current_time
                self.stats['focus_triggers'] += 1
                self.stats['focus_actions'] += 1
                self.logger.info(f"Auto mode: Autofocus triggered (FocusFoM: {focus_fom:.0f})")
            except Exception as e:
                self.logger.error(f"Auto mode: Failed to trigger autofocus: {e}")
    
    def _handle_continuous_mode(self, focus_fom: float, metadata: Dict[str, Any], current_time: float):
        """Handle continuous focus mode updates."""
        # Continuous mode handles focus automatically
        # Just monitor for quality issues
        
        if focus_fom < 300:
            # Very poor quality - might need intervention
            self.logger.warning(f"Continuous mode: Very poor focus quality ({focus_fom:.0f})")
            
            # Check for focus hunting (rapid FOM changes)
            if len(self.focus_history) >= 10:
                recent_foms = [h['fom'] for h in list(self.focus_history)[-10:]]
                fom_variance = max(recent_foms) - min(recent_foms)
                
                if fom_variance > 500:  # Large variance indicates hunting
                    self.stats['focus_hunting_events'] += 1
                    self.logger.warning(f"Continuous mode: Possible focus hunting detected (variance: {fom_variance:.0f})")
    
    def _handle_manual_mode(self, focus_fom: float, metadata: Dict[str, Any], current_time: float):
        """Handle manual focus mode with smart lock/unlock."""
        params = self.manual_mode_params
        
        # Check if we need to unlock and re-focus
        if current_time - params['last_unlock_time'] > params['unlock_interval']:
            # Unlock and trigger AF
            self.logger.info(f"Manual mode: Unlocking for periodic re-focus (FocusFoM: {focus_fom:.0f})")
            
            try:
                # Switch to Auto mode temporarily
                self.camera.picam2.set_controls({
                    "AfMode": 1,  # Switch to Auto
                    "AfTrigger": 1
                })
                time.sleep(0.5)  # Wait for focus
                
                # Lock back to manual at target distance
                self._setup_manual_mode(params['distance_m'], params['unlock_interval'])
                
                params['last_unlock_time'] = current_time
                self.stats['focus_unlocks'] += 1
                self.stats['focus_locks'] += 1
                self.stats['focus_actions'] += 1
            except Exception as e:
                self.logger.error(f"Manual mode: Failed to unlock/re-lock: {e}")
        
        # If quality is very poor, trigger immediate re-focus
        elif focus_fom < params['poor_threshold']:
            self.logger.warning(f"Manual mode: Very poor focus quality ({focus_fom:.0f}), re-focusing")
            try:
                # Re-lock at target distance
                self._setup_manual_mode(params['distance_m'], params['unlock_interval'])
                self.stats['focus_actions'] += 1
            except Exception as e:
                self.logger.error(f"Manual mode: Failed to re-focus: {e}")
    
    def _handle_hybrid_mode(self, focus_fom: float, metadata: Dict[str, Any],
                           detection_result: Optional[Dict[str, Any]], current_time: float):
        """Handle hybrid focus mode."""
        params = self.hybrid_mode_params
        
        # Check if vehicle is detected
        has_vehicle = False
        if detection_result and detection_result.get('vehicles'):
            has_vehicle = True
        
        # If vehicle detected and focus quality is marginal, switch to auto for better focus
        if has_vehicle and focus_fom < params['vehicle_detected_focus_threshold']:
            self.logger.info(f"Hybrid mode: Vehicle detected with poor focus ({focus_fom:.0f}), switching to auto mode")
            
            try:
                # Temporarily switch to auto for better focus
                self.camera.picam2.set_controls({
                    "AfMode": 1,  # Auto
                    "AfTrigger": 1
                })
                time.sleep(0.3)  # Wait for focus
                
                # Switch back to continuous
                self._setup_continuous_mode(
                    self.continuous_mode_params['speed'],
                    self.continuous_mode_params['metering'],
                    self.continuous_mode_params['range_mode']
                )
                
                self.stats['focus_actions'] += 1
            except Exception as e:
                self.logger.error(f"Hybrid mode: Failed to switch to auto: {e}")
    
    def get_focus_statistics(self) -> Dict[str, Any]:
        """
        Get focus statistics and quality metrics.
        
        Returns:
            Dict with focus statistics
        """
        if not self.focus_history:
            return {
                'mode': self.mode,
                'focus_locked': self.focus_locked,
                'stats': self.stats,
                'quality': {
                    'mean_fom': 0,
                    'std_fom': 0,
                    'min_fom': 0,
                    'max_fom': 0
                }
            }
        
        fom_values = [h['fom'] for h in self.focus_history]
        
        import numpy as np
        return {
            'mode': self.mode,
            'focus_locked': self.focus_locked,
            'stats': self.stats.copy(),
            'quality': {
                'mean_fom': float(np.mean(fom_values)),
                'std_fom': float(np.std(fom_values)),
                'min_fom': float(np.min(fom_values)),
                'max_fom': float(np.max(fom_values)),
                'current_fom': float(fom_values[-1]) if fom_values else 0
            },
            'history_size': len(self.focus_history),
            'detection_history_size': len(self.detection_results_history)
        }
    
    def reset_statistics(self):
        """Reset focus statistics."""
        self.stats = {
            'focus_actions': 0,
            'focus_locks': 0,
            'focus_unlocks': 0,
            'focus_triggers': 0,
            'focus_hunting_events': 0
        }
        self.focus_history.clear()
        self.detection_results_history.clear()
        self.logger.info("Focus statistics reset")

