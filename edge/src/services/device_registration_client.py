#!/usr/bin/env python3
"""
Device Registration Client for Edge Devices

This module handles device registration with the server using different mechanisms:
1. Self-registration: Device registers itself with the server
2. Pre-provision: Device uses pre-configured credentials
3. Admin approval: Device waits for admin approval after registration

Author: AI Camera Team
Version: 2.0.0
"""

import os
import json
import time
import logging
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
import psutil
import socket

@dataclass
class DeviceInfo:
    """Device information for registration"""
    serial_number: str
    device_model: str
    device_type: str = "camera"
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None
    location_address: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class DeviceCredentials:
    """Device credentials received from server"""
    api_key: str
    jwt_secret: Optional[str] = None
    shared_secret: Optional[str] = None
    registration_id: str = None
    approved_at: Optional[str] = None

class DeviceRegistrationClient:
    """
    Client for handling device registration with the server
    """
    
    def __init__(self, server_url: str, config_file: str = None):
        self.server_url = server_url.rstrip('/')
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), '../../config/device_config.json')
        self.logger = logging.getLogger(__name__)
        self.credentials: Optional[DeviceCredentials] = None
        self.device_info: Optional[DeviceInfo] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.heartbeat_interval = 60  # seconds
        self.stop_heartbeat = threading.Event()
        
        # Load existing configuration
        self._load_config()
    
    def _load_config(self):
        """Load device configuration from file"""
        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Load device info
                if 'device_info' in config:
                    self.device_info = DeviceInfo(**config['device_info'])
                
                # Load credentials
                if 'credentials' in config:
                    self.credentials = DeviceCredentials(**config['credentials'])
                
                self.logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                self.logger.error(f"Error loading configuration: {e}")
    
    def _save_config(self):
        """Save device configuration to file"""
        config_path = Path(self.config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {}
        if self.device_info:
            config['device_info'] = asdict(self.device_info)
        if self.credentials:
            config['credentials'] = asdict(self.credentials)
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            self.logger.info(f"Configuration saved to {config_path}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def _get_device_info(self) -> DeviceInfo:
        """Get device information for registration"""
        if self.device_info:
            return self.device_info
        
        # Auto-detect device information
        hostname = socket.gethostname()
        ip_address = self._get_local_ip()
        mac_address = self._get_mac_address()
        
        # Get serial number from environment or generate one
        serial_number = os.getenv('DEVICE_SERIAL_NUMBER', f"{hostname}_{mac_address}")
        device_model = os.getenv('DEVICE_MODEL', 'AI-CAM-EDGE-V2')
        
        # Get location from environment if available
        location_lat = float(os.getenv('DEVICE_LAT', 0)) or None
        location_lng = float(os.getenv('DEVICE_LNG', 0)) or None
        location_address = os.getenv('DEVICE_LOCATION', None)
        
        # Additional metadata
        metadata = {
            'hostname': hostname,
            'os': f"{os.name} {os.uname().sysname if hasattr(os, 'uname') else 'unknown'}",
            'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            'registration_timestamp': datetime.now().isoformat(),
        }
        
        device_info = DeviceInfo(
            serial_number=serial_number,
            device_model=device_model,
            ip_address=ip_address,
            mac_address=mac_address,
            location_lat=location_lat,
            location_lng=location_lng,
            location_address=location_address,
            metadata=metadata
        )
        
        self.device_info = device_info
        return device_info
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            # Connect to a remote address to determine local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"
    
    def _get_mac_address(self) -> str:
        """Get MAC address"""
        try:
            import uuid
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 2*6, 2)][::-1])
            return mac
        except Exception:
            return "00:00:00:00:00:00"
    
    def self_register(self) -> Tuple[bool, str]:
        """
        Self-registration mechanism: Device registers itself with the server
        """
        device_info = self._get_device_info()
        
        try:
            response = requests.post(
                f"{self.server_url}/device-registration/register",
                json=asdict(device_info),
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                self.logger.info(f"Device registered successfully: {data['message']}")
                
                # Save registration info
                self.credentials = DeviceCredentials(
                    registration_id=data['id'],
                    api_key=data.get('apiKey'),
                    jwt_secret=data.get('jwtSecret'),
                    shared_secret=data.get('sharedSecret'),
                    approved_at=data.get('approvedAt')
                )
                
                self._save_config()
                return True, data['message']
            
            elif response.status_code == 409:
                error_msg = response.json().get('message', 'Device already exists')
                self.logger.warning(f"Registration conflict: {error_msg}")
                return False, error_msg
            
            else:
                error_msg = response.json().get('message', 'Registration failed')
                self.logger.error(f"Registration failed: {error_msg}")
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during registration: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error during registration: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def use_pre_provisioned_credentials(self, api_key: str, jwt_secret: str = None, 
                                      shared_secret: str = None) -> bool:
        """
        Use pre-provisioned credentials provided by admin
        """
        self.credentials = DeviceCredentials(
            api_key=api_key,
            jwt_secret=jwt_secret,
            shared_secret=shared_secret
        )
        
        self._save_config()
        self.logger.info("Pre-provisioned credentials configured")
        return True
    
    def check_approval_status(self) -> Tuple[bool, str, Optional[DeviceCredentials]]:
        """
        Check if device registration has been approved
        """
        if not self.device_info:
            return False, "Device not registered", None
        
        try:
            response = requests.get(
                f"{self.server_url}/device-registration/serial/{self.device_info.serial_number}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('registrationStatus')
                
                if status == 'approved':
                    # Update credentials
                    self.credentials = DeviceCredentials(
                        registration_id=data['id'],
                        api_key=data.get('apiKey'),
                        jwt_secret=data.get('jwtSecret'),
                        shared_secret=data.get('sharedSecret'),
                        approved_at=data.get('approvedAt')
                    )
                    self._save_config()
                    return True, "Device approved", self.credentials
                
                elif status == 'pending_approval':
                    return False, "Device pending approval", None
                
                elif status == 'rejected':
                    reason = data.get('rejectionReason', 'No reason provided')
                    return False, f"Device rejected: {reason}", None
                
                else:
                    return False, f"Unknown status: {status}", None
            
            elif response.status_code == 404:
                return False, "Device not found", None
            
            else:
                error_msg = response.json().get('message', 'Status check failed')
                return False, error_msg, None
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error during status check: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
        except Exception as e:
            error_msg = f"Unexpected error during status check: {e}"
            self.logger.error(error_msg)
            return False, error_msg, None
    
    def send_heartbeat(self) -> bool:
        """
        Send heartbeat to server to maintain active status
        """
        if not self.credentials or not self.credentials.api_key:
            self.logger.warning("No credentials available for heartbeat")
            return False
        
        if not self.device_info:
            self.logger.warning("No device info available for heartbeat")
            return False
        
        # Collect current device status
        status_data = {
            'cpu_usage': psutil.cpu_percent(interval=1),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - psutil.boot_time(),
        }
        
        heartbeat_data = {
            'serialNumber': self.device_info.serial_number,
            'ipAddress': self._get_local_ip(),
            'statusData': status_data
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/device-registration/heartbeat",
                json=heartbeat_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.credentials.api_key,
                    'X-Device-Serial': self.device_info.serial_number
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                error_msg = response.json().get('message', 'Heartbeat failed')
                self.logger.error(f"Heartbeat failed: {error_msg}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during heartbeat: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during heartbeat: {e}")
            return False
    
    def start_heartbeat(self, interval: int = 60):
        """
        Start sending periodic heartbeats
        """
        self.heartbeat_interval = interval
        self.stop_heartbeat.clear()
        
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.logger.warning("Heartbeat thread already running")
            return
        
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
        self.heartbeat_thread.start()
        self.logger.info(f"Heartbeat started with {interval}s interval")
    
    def stop_heartbeat_service(self):
        """
        Stop sending heartbeats
        """
        self.stop_heartbeat.set()
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
        self.logger.info("Heartbeat stopped")
    
    def _heartbeat_worker(self):
        """
        Worker thread for sending periodic heartbeats
        """
        while not self.stop_heartbeat.is_set():
            try:
                self.send_heartbeat()
                self.stop_heartbeat.wait(self.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Error in heartbeat worker: {e}")
                self.stop_heartbeat.wait(self.heartbeat_interval)
    
    def is_registered(self) -> bool:
        """
        Check if device is registered and has credentials
        """
        return (self.credentials is not None and 
                self.credentials.api_key is not None and 
                self.device_info is not None)
    
    def get_credentials(self) -> Optional[DeviceCredentials]:
        """
        Get current device credentials
        """
        return self.credentials
    
    def get_device_info(self) -> Optional[DeviceInfo]:
        """
        Get current device information
        """
        return self.device_info


def main():
    """
    Example usage of DeviceRegistrationClient
    """
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client
    server_url = os.getenv('SERVER_URL', 'http://localhost:3000')
    client = DeviceRegistrationClient(server_url)
    
    # Check if already registered
    if client.is_registered():
        print("Device already registered")
        client.start_heartbeat()
        
        # Keep running
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            client.stop_heartbeat_service()
            print("Stopped")
    else:
        print("Device not registered, attempting self-registration...")
        success, message = client.self_register()
        
        if success:
            print(f"Registration successful: {message}")
            
            # Wait for approval
            print("Waiting for admin approval...")
            while True:
                approved, status_msg, credentials = client.check_approval_status()
                print(f"Status: {status_msg}")
                
                if approved:
                    print("Device approved! Starting heartbeat...")
                    client.start_heartbeat()
                    break
                elif "rejected" in status_msg.lower():
                    print("Device registration rejected")
                    break
                
                time.sleep(30)  # Check every 30 seconds
        else:
            print(f"Registration failed: {message}")


if __name__ == "__main__":
    main()