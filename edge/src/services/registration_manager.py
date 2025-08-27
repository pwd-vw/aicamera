#!/usr/bin/env python3
"""
Registration Manager for Edge Application

This module integrates device registration with the main edge application,
providing a high-level interface for registration management.

Author: AI Camera Team
Version: 2.0.0
"""

import os
import logging
import time
import threading
from typing import Optional, Dict, Any, Callable
from enum import Enum
from datetime import datetime

from .device_registration_client import DeviceRegistrationClient, DeviceCredentials, DeviceInfo

class RegistrationState(Enum):
    """Device registration states"""
    NOT_REGISTERED = "not_registered"
    REGISTERING = "registering"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    ERROR = "error"

class RegistrationManager:
    """
    High-level registration manager that integrates with the edge application
    """
    
    def __init__(self, server_url: str, config_file: str = None):
        self.logger = logging.getLogger(__name__)
        self.client = DeviceRegistrationClient(server_url, config_file)
        self.state = RegistrationState.NOT_REGISTERED
        self.last_error: Optional[str] = None
        self.registration_callbacks: Dict[str, Callable] = {}
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitoring = threading.Event()
        
        # Check initial state
        self._check_initial_state()
    
    def _check_initial_state(self):
        """Check initial registration state"""
        if self.client.is_registered():
            credentials = self.client.get_credentials()
            if credentials and credentials.approved_at:
                self.state = RegistrationState.APPROVED
                self.logger.info("Device is already registered and approved")
            else:
                self.state = RegistrationState.PENDING_APPROVAL
                self.logger.info("Device is registered but pending approval")
        else:
            self.state = RegistrationState.NOT_REGISTERED
            self.logger.info("Device is not registered")
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register callback for registration events
        
        Events:
        - on_registration_success
        - on_approval
        - on_rejection
        - on_error
        - on_active
        """
        self.registration_callbacks[event] = callback
    
    def _trigger_callback(self, event: str, *args, **kwargs):
        """Trigger registered callback"""
        if event in self.registration_callbacks:
            try:
                self.registration_callbacks[event](*args, **kwargs)
            except Exception as e:
                self.logger.error(f"Error in callback {event}: {e}")
    
    def start_registration_process(self, registration_type: str = "self") -> bool:
        """
        Start the registration process
        
        Args:
            registration_type: "self", "pre_provision", or "manual"
        """
        if self.state == RegistrationState.APPROVED:
            self.logger.info("Device already approved, starting heartbeat")
            self._start_heartbeat()
            return True
        
        if registration_type == "self":
            return self._self_register()
        elif registration_type == "pre_provision":
            return self._use_pre_provision()
        else:
            self.logger.warning(f"Unknown registration type: {registration_type}")
            return False
    
    def _self_register(self) -> bool:
        """Handle self-registration process"""
        self.state = RegistrationState.REGISTERING
        self.logger.info("Starting self-registration process")
        
        success, message = self.client.self_register()
        
        if success:
            self.state = RegistrationState.PENDING_APPROVAL
            self.logger.info(f"Self-registration successful: {message}")
            self._trigger_callback('on_registration_success', message)
            
            # Start monitoring for approval
            self._start_approval_monitoring()
            return True
        else:
            self.state = RegistrationState.ERROR
            self.last_error = message
            self.logger.error(f"Self-registration failed: {message}")
            self._trigger_callback('on_error', message)
            return False
    
    def _use_pre_provision(self) -> bool:
        """Handle pre-provisioned credentials"""
        # Check environment variables for pre-provisioned credentials
        api_key = os.getenv('DEVICE_API_KEY')
        jwt_secret = os.getenv('DEVICE_JWT_SECRET')
        shared_secret = os.getenv('DEVICE_SHARED_SECRET')
        
        if not api_key:
            error_msg = "No pre-provisioned API key found in environment"
            self.logger.error(error_msg)
            self.state = RegistrationState.ERROR
            self.last_error = error_msg
            self._trigger_callback('on_error', error_msg)
            return False
        
        success = self.client.use_pre_provisioned_credentials(api_key, jwt_secret, shared_secret)
        
        if success:
            self.state = RegistrationState.APPROVED
            self.logger.info("Pre-provisioned credentials configured successfully")
            self._trigger_callback('on_approval', "Pre-provisioned device approved")
            
            # Start heartbeat
            self._start_heartbeat()
            return True
        else:
            error_msg = "Failed to configure pre-provisioned credentials"
            self.logger.error(error_msg)
            self.state = RegistrationState.ERROR
            self.last_error = error_msg
            self._trigger_callback('on_error', error_msg)
            return False
    
    def _start_approval_monitoring(self):
        """Start monitoring for approval status"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        
        self.stop_monitoring.clear()
        self.monitor_thread = threading.Thread(target=self._approval_monitor_worker, daemon=True)
        self.monitor_thread.start()
        self.logger.info("Started approval monitoring")
    
    def _approval_monitor_worker(self):
        """Worker thread for monitoring approval status"""
        check_interval = int(os.getenv('APPROVAL_CHECK_INTERVAL', '30'))  # seconds
        max_wait_time = int(os.getenv('MAX_APPROVAL_WAIT_TIME', '3600'))  # 1 hour
        start_time = time.time()
        
        while not self.stop_monitoring.is_set():
            try:
                # Check if we've been waiting too long
                if time.time() - start_time > max_wait_time:
                    error_msg = f"Approval timeout after {max_wait_time} seconds"
                    self.logger.error(error_msg)
                    self.state = RegistrationState.ERROR
                    self.last_error = error_msg
                    self._trigger_callback('on_error', error_msg)
                    break
                
                # Check approval status
                approved, status_msg, credentials = self.client.check_approval_status()
                
                if approved:
                    self.state = RegistrationState.APPROVED
                    self.logger.info(f"Device approved: {status_msg}")
                    self._trigger_callback('on_approval', status_msg)
                    
                    # Start heartbeat
                    self._start_heartbeat()
                    break
                
                elif "rejected" in status_msg.lower():
                    self.state = RegistrationState.REJECTED
                    self.last_error = status_msg
                    self.logger.error(f"Device rejected: {status_msg}")
                    self._trigger_callback('on_rejection', status_msg)
                    break
                
                else:
                    # Still pending
                    self.logger.debug(f"Still pending approval: {status_msg}")
                
                # Wait before next check
                self.stop_monitoring.wait(check_interval)
                
            except Exception as e:
                error_msg = f"Error during approval monitoring: {e}"
                self.logger.error(error_msg)
                self.state = RegistrationState.ERROR
                self.last_error = error_msg
                self._trigger_callback('on_error', error_msg)
                break
    
    def _start_heartbeat(self):
        """Start heartbeat service"""
        heartbeat_interval = int(os.getenv('HEARTBEAT_INTERVAL', '60'))
        self.client.start_heartbeat(heartbeat_interval)
        self.state = RegistrationState.ACTIVE
        self.logger.info("Device is now active with heartbeat service")
        self._trigger_callback('on_active', "Device is active")
    
    def stop(self):
        """Stop all registration services"""
        self.logger.info("Stopping registration manager")
        
        # Stop monitoring
        self.stop_monitoring.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        # Stop heartbeat
        self.client.stop_heartbeat_service()
        
        self.logger.info("Registration manager stopped")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current registration status"""
        device_info = self.client.get_device_info()
        credentials = self.client.get_credentials()
        
        return {
            'state': self.state.value,
            'is_registered': self.client.is_registered(),
            'last_error': self.last_error,
            'device_info': {
                'serial_number': device_info.serial_number if device_info else None,
                'device_model': device_info.device_model if device_info else None,
                'ip_address': device_info.ip_address if device_info else None,
                'location_address': device_info.location_address if device_info else None,
            } if device_info else None,
            'credentials': {
                'has_api_key': bool(credentials and credentials.api_key),
                'registration_id': credentials.registration_id if credentials else None,
                'approved_at': credentials.approved_at if credentials else None,
            } if credentials else None,
            'timestamp': datetime.now().isoformat()
        }
    
    def force_re_registration(self):
        """Force device to re-register (useful for testing or recovery)"""
        self.logger.info("Forcing device re-registration")
        
        # Stop current services
        self.stop()
        
        # Clear credentials
        self.client.credentials = None
        self.client._save_config()
        
        # Reset state
        self.state = RegistrationState.NOT_REGISTERED
        self.last_error = None
        
        self.logger.info("Device reset for re-registration")
    
    def get_credentials(self) -> Optional[DeviceCredentials]:
        """Get device credentials for API calls"""
        return self.client.get_credentials()
    
    def is_ready(self) -> bool:
        """Check if device is ready for operation"""
        return self.state == RegistrationState.ACTIVE


# Global registration manager instance
_registration_manager: Optional[RegistrationManager] = None

def get_registration_manager(server_url: str = None, config_file: str = None) -> RegistrationManager:
    """Get global registration manager instance"""
    global _registration_manager
    
    if _registration_manager is None:
        if not server_url:
            server_url = os.getenv('SERVER_URL', 'http://localhost:3000')
        
        _registration_manager = RegistrationManager(server_url, config_file)
    
    return _registration_manager

def initialize_registration(server_url: str = None, config_file: str = None) -> RegistrationManager:
    """Initialize registration manager"""
    return get_registration_manager(server_url, config_file)