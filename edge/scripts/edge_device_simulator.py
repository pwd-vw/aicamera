#!/usr/bin/env python3
"""
Edge Device Simulator for AI Camera Server Development

This simulator mimics edge device behavior for server testing without real hardware:
1. Device self-registration with server
2. Waiting for admin approval
3. Sending detection metadata via websocket
4. Image transfer via SFTP/rsync
5. Health monitoring and heartbeat

Usage:
    python edge_device_simulator.py --server-url http://localhost:3000 --device-id sim-001
"""

import os
import json
import time
import random
import logging
import sqlite3
import argparse
import threading
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import socketio
from PIL import Image, ImageDraw, ImageFont
import base64
import io

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SimulationConfig:
    """Configuration for edge device simulation"""
    server_url: str
    device_id: str
    device_model: str = "AI-CAM-SIMULATOR-V1"
    location_lat: float = 13.7563  # Bangkok coordinates
    location_lng: float = 100.5018
    location_address: str = "Simulator Device - Bangkok, Thailand"
    
    # Simulation parameters
    detection_interval: int = 10  # seconds between detections
    health_interval: int = 30     # seconds between health checks
    heartbeat_interval: int = 60  # seconds between heartbeats
    
    # Image simulation
    simulate_images: bool = True
    image_width: int = 640
    image_height: int = 480


class MockDatabase:
    """Mock SQLite database for simulator"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize mock database tables"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Mock detection_results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detection_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                vehicles_count INTEGER DEFAULT 0,
                plates_count INTEGER DEFAULT 0,
                ocr_results TEXT,
                original_image_path TEXT,
                vehicle_detections TEXT,
                plate_detections TEXT,
                processing_time_ms REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_to_server BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                server_response TEXT
            )
        """)
        
        # Mock health_checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS health_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                component TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                details TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_to_server BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                server_response TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info(f"Mock database initialized at {self.db_path}")
    
    def insert_detection_result(self, detection_data: Dict[str, Any]) -> int:
        """Insert mock detection result"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO detection_results (
                timestamp, vehicles_count, plates_count, ocr_results,
                original_image_path, vehicle_detections, plate_detections,
                processing_time_ms
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            detection_data['timestamp'],
            detection_data['vehicles_count'],
            detection_data['plates_count'],
            json.dumps(detection_data['ocr_results']),
            detection_data['original_image_path'],
            json.dumps(detection_data['vehicle_detections']),
            json.dumps(detection_data['plate_detections']),
            detection_data['processing_time_ms']
        ))
        
        detection_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return detection_id
    
    def insert_health_check(self, component: str, status: str, message: str, details: str = None) -> int:
        """Insert mock health check"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO health_checks (timestamp, component, status, message, details)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, component, status, message, details))
        
        health_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return health_id
    
    def get_unsent_detections(self) -> List[Dict]:
        """Get unsent detection results"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM detection_results 
            WHERE sent_to_server = 0 
            ORDER BY created_at ASC 
            LIMIT 10
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_unsent_health_checks(self) -> List[Dict]:
        """Get unsent health check results"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM health_checks 
            WHERE sent_to_server = 0 
            ORDER BY created_at ASC 
            LIMIT 10
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def mark_detection_sent(self, detection_id: int, response: str = None):
        """Mark detection as sent"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE detection_results 
            SET sent_to_server = 1, sent_at = ?, server_response = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), response, detection_id))
        
        conn.commit()
        conn.close()
    
    def mark_health_check_sent(self, health_id: int, response: str = None):
        """Mark health check as sent"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE health_checks 
            SET sent_to_server = 1, sent_at = ?, server_response = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), response, health_id))
        
        conn.commit()
        conn.close()


class ImageSimulator:
    """Simulate camera images with license plates"""
    
    def __init__(self, config: SimulationConfig, output_dir: str):
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sample license plate patterns
        self.plate_patterns = [
            "ABC-1234", "XYZ-5678", "DEF-9012", "GHI-3456",
            "JKL-7890", "MNO-2468", "PQR-1357", "STU-9753"
        ]
    
    def generate_mock_image(self, detection_data: Dict[str, Any]) -> str:
        """Generate mock camera image with license plate overlay"""
        if not self.config.simulate_images:
            return None
        
        # Create base image
        img = Image.new('RGB', (self.config.image_width, self.config.image_height), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Try to load a font (fallback to default if not available)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            small_font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # Draw timestamp
        timestamp_text = f"Simulation {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        draw.text((10, 10), timestamp_text, fill='black', font=small_font)
        
        # Draw mock vehicles and license plates
        for i, ocr_result in enumerate(detection_data['ocr_results']):
            # Draw vehicle rectangle
            x1, y1 = 50 + i * 200, 100
            x2, y2 = x1 + 180, y1 + 120
            draw.rectangle([x1, y1, x2, y2], outline='blue', width=2)
            
            # Draw license plate rectangle
            plate_x1, plate_y1 = x1 + 50, y1 + 80
            plate_x2, plate_y2 = plate_x1 + 80, plate_y1 + 30
            draw.rectangle([plate_x1, plate_y1, plate_x2, plate_y2], fill='white', outline='red', width=2)
            
            # Draw license plate text
            plate_text = ocr_result['text']
            text_bbox = draw.textbbox((0, 0), plate_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = plate_x1 + (80 - text_width) // 2
            text_y = plate_y1 + (30 - text_height) // 2
            draw.text((text_x, text_y), plate_text, fill='black', font=font)
            
            # Draw confidence score
            conf_text = f"Conf: {ocr_result['confidence']:.2f}"
            draw.text((x1, y2 + 5), conf_text, fill='green', font=small_font)
        
        # Save image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"detection_{timestamp}_{random.randint(1000, 9999)}.jpg"
        image_path = self.output_dir / image_filename
        
        img.save(image_path, 'JPEG', quality=85)
        logger.info(f"Generated mock image: {image_path}")
        
        return str(image_path)


class EdgeDeviceSimulator:
    """Main edge device simulator class"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.logger = logger
        
        # Setup directories
        self.sim_dir = Path(f"simulator_data/{config.device_id}")
        self.sim_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.database = MockDatabase(str(self.sim_dir / "sim_database.db"))
        self.image_simulator = ImageSimulator(config, str(self.sim_dir / "captured_images"))
        
        # Device registration state
        self.credentials = None
        self.registration_id = None
        self.approved = False
        
        # Communication
        self.socketio_client = None
        self.connected = False
        
        # Threading
        self.running = False
        self.threads = []
        self.stop_event = threading.Event()
        
        self.logger.info(f"Edge Device Simulator initialized for {config.device_id}")
    
    def register_device(self) -> bool:
        """Register device with server"""
        self.logger.info("Starting device registration...")
        
        registration_data = {
            "serialNumber": self.config.device_id,
            "deviceModel": self.config.device_model,
            "deviceType": "camera",
            "ipAddress": self._get_local_ip(),
            "macAddress": self._generate_mac_address(),
            "locationLat": self.config.location_lat,
            "locationLng": self.config.location_lng,
            "locationAddress": self.config.location_address,
            "metadata": {
                "simulator": True,
                "version": "1.0.0",
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                "registration_timestamp": datetime.now().isoformat()
            }
        }
        
        try:
            response = requests.post(
                f"{self.config.server_url}/device-registration/register",
                json=registration_data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 201:
                data = response.json()
                self.registration_id = data['id']
                self.logger.info(f"Device registered successfully: {data['message']}")
                
                # If already has credentials (unlikely for first registration)
                if data.get('apiKey'):
                    self.credentials = {
                        'api_key': data['apiKey'],
                        'jwt_secret': data.get('jwtSecret'),
                        'shared_secret': data.get('sharedSecret')
                    }
                    self.approved = True
                
                return True
            else:
                error_msg = response.json().get('message', 'Registration failed')
                self.logger.error(f"Registration failed: {error_msg}")
                return False
                
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def wait_for_approval(self) -> bool:
        """Wait for device approval from admin"""
        self.logger.info("Waiting for admin approval...")
        
        max_wait_time = 300  # 5 minutes
        check_interval = 10  # 10 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(
                    f"{self.config.server_url}/device-registration/serial/{self.config.device_id}",
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status = data.get('registrationStatus')
                    
                    if status == 'approved':
                        self.credentials = {
                            'api_key': data.get('apiKey'),
                            'jwt_secret': data.get('jwtSecret'),
                            'shared_secret': data.get('sharedSecret')
                        }
                        self.approved = True
                        self.logger.info("Device approved! Credentials received.")
                        return True
                    
                    elif status == 'rejected':
                        reason = data.get('rejectionReason', 'No reason provided')
                        self.logger.error(f"Device rejected: {reason}")
                        return False
                    
                    else:
                        self.logger.info(f"Still pending approval... (status: {status})")
                
                time.sleep(check_interval)
                
            except Exception as e:
                self.logger.error(f"Error checking approval status: {e}")
                time.sleep(check_interval)
        
        self.logger.error("Approval timeout - device was not approved within the time limit")
        return False
    
    def connect_websocket(self) -> bool:
        """Connect to server websocket"""
        if not self.credentials:
            self.logger.error("No credentials available for websocket connection")
            return False
        
        try:
            self.socketio_client = socketio.Client()
            
            @self.socketio_client.on('connect')
            def on_connect():
                self.logger.info("WebSocket connected")
                self.connected = True
                
                # Register with server
                self.socketio_client.emit('camera_register', {
                    'camera_id': self.config.device_id,
                    'api_key': self.credentials['api_key'],
                    'timestamp': datetime.now().isoformat()
                })
            
            @self.socketio_client.on('disconnect')
            def on_disconnect():
                self.logger.info("WebSocket disconnected")
                self.connected = False
            
            @self.socketio_client.on('lpr_response')
            def on_lpr_response(data):
                self.logger.info(f"LPR response received: {data}")
            
            # Connect to server
            ws_url = self.config.server_url
            if ws_url.startswith('http://'):
                ws_url = ws_url.replace('http://', 'ws://')
            elif ws_url.startswith('https://'):
                ws_url = ws_url.replace('https://', 'wss://')
            
            self.socketio_client.connect(ws_url, timeout=10)
            
            if self.socketio_client.connected:
                self.logger.info("WebSocket connection established")
                return True
            else:
                self.logger.error("WebSocket connection failed")
                return False
                
        except Exception as e:
            self.logger.error(f"WebSocket connection error: {e}")
            return False
    
    def generate_mock_detection(self) -> Dict[str, Any]:
        """Generate mock detection data"""
        # Random number of vehicles and plates
        vehicles_count = random.randint(1, 3)
        plates_count = random.randint(1, vehicles_count)
        
        # Generate mock OCR results
        ocr_results = []
        vehicle_detections = []
        plate_detections = []
        
        for i in range(plates_count):
            plate_text = random.choice(self.image_simulator.plate_patterns)
            confidence = random.uniform(0.75, 0.95)
            
            ocr_results.append({
                'text': plate_text,
                'confidence': confidence,
                'method': 'simulator'
            })
            
            # Mock bounding boxes
            vehicle_detections.append({
                'bbox': [50 + i * 200, 100, 230 + i * 200, 220],
                'confidence': random.uniform(0.8, 0.95),
                'class': 'vehicle'
            })
            
            plate_detections.append({
                'bbox': [100 + i * 200, 180, 180 + i * 200, 210],
                'confidence': confidence,
                'class': 'license_plate',
                'text': plate_text
            })
        
        processing_time = random.uniform(50, 200)  # milliseconds
        
        detection_data = {
            'timestamp': datetime.now().isoformat(),
            'vehicles_count': vehicles_count,
            'plates_count': plates_count,
            'ocr_results': ocr_results,
            'vehicle_detections': vehicle_detections,
            'plate_detections': plate_detections,
            'processing_time_ms': processing_time,
            'original_image_path': None  # Will be set by image simulator
        }
        
        # Generate mock image
        image_path = self.image_simulator.generate_mock_image(detection_data)
        detection_data['original_image_path'] = image_path
        
        return detection_data
    
    def send_detection_to_server(self, detection_data: Dict[str, Any]) -> bool:
        """Send detection data to server via websocket"""
        if not self.connected or not self.socketio_client:
            self.logger.warning("Not connected to server - cannot send detection")
            return False
        
        try:
            # Prepare data for server
            server_data = {
                'type': 'detection_result',
                'aicamera_id': self.config.device_id,
                'timestamp': detection_data['timestamp'],
                'vehicles_count': detection_data['vehicles_count'],
                'plates_count': detection_data['plates_count'],
                'ocr_results': detection_data['ocr_results'],
                'vehicle_detections': detection_data['vehicle_detections'],
                'plate_detections': detection_data['plate_detections'],
                'processing_time_ms': detection_data['processing_time_ms']
            }
            
            # Add image data if available
            if detection_data['original_image_path'] and os.path.exists(detection_data['original_image_path']):
                try:
                    with open(detection_data['original_image_path'], 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode('utf-8')
                        server_data['annotated_image'] = image_data
                except Exception as e:
                    self.logger.warning(f"Failed to encode image: {e}")
            
            # Send via websocket
            self.socketio_client.emit('lpr_data', server_data)
            self.logger.info(f"Sent detection with {detection_data['plates_count']} plates to server")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send detection to server: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to server"""
        if not self.credentials:
            return False
        
        try:
            # Collect mock system status
            status_data = {
                'cpu_usage': random.uniform(20, 80),
                'memory_usage': random.uniform(30, 70),
                'disk_usage': random.uniform(10, 50),
                'temperature': random.uniform(35, 65),
                'uptime': random.uniform(3600, 86400),  # 1 hour to 1 day
                'timestamp': datetime.now().isoformat()
            }
            
            heartbeat_data = {
                'serialNumber': self.config.device_id,
                'ipAddress': self._get_local_ip(),
                'statusData': status_data
            }
            
            response = requests.post(
                f"{self.config.server_url}/device-registration/heartbeat",
                json=heartbeat_data,
                headers={
                    'Content-Type': 'application/json',
                    'X-API-Key': self.credentials['api_key'],
                    'X-Device-Serial': self.config.device_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                self.logger.debug("Heartbeat sent successfully")
                return True
            else:
                self.logger.error(f"Heartbeat failed: {response.text}")
                return False
                
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
            return False
    
    def detection_loop(self):
        """Main detection simulation loop"""
        self.logger.info(f"Detection loop started (interval: {self.config.detection_interval}s)")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Generate mock detection
                detection_data = self.generate_mock_detection()
                
                # Store in database
                detection_id = self.database.insert_detection_result(detection_data)
                detection_data['id'] = detection_id
                
                # Send to server if connected
                if self.connected:
                    success = self.send_detection_to_server(detection_data)
                    if success:
                        self.database.mark_detection_sent(detection_id, "Sent successfully")
                
                # Wait for next detection
                if self.stop_event.wait(self.config.detection_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in detection loop: {e}")
                if self.stop_event.wait(self.config.detection_interval):
                    break
        
        self.logger.info("Detection loop stopped")
    
    def health_loop(self):
        """Health monitoring loop"""
        self.logger.info(f"Health loop started (interval: {self.config.health_interval}s)")
        
        components = ['camera', 'ai_processor', 'storage', 'network']
        
        while self.running and not self.stop_event.is_set():
            try:
                # Generate mock health checks
                for component in components:
                    status = random.choice(['healthy', 'healthy', 'healthy', 'warning'])  # Mostly healthy
                    message = f"{component.title()} operating normally" if status == 'healthy' else f"{component.title()} performance degraded"
                    
                    details = json.dumps({
                        'component': component,
                        'metrics': {
                            'response_time_ms': random.uniform(10, 100),
                            'success_rate': random.uniform(0.95, 1.0),
                            'error_count': random.randint(0, 5)
                        }
                    })
                    
                    health_id = self.database.insert_health_check(component, status, message, details)
                
                # Wait for next health check
                if self.stop_event.wait(self.config.health_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in health loop: {e}")
                if self.stop_event.wait(self.config.health_interval):
                    break
        
        self.logger.info("Health loop stopped")
    
    def heartbeat_loop(self):
        """Heartbeat loop"""
        self.logger.info(f"Heartbeat loop started (interval: {self.config.heartbeat_interval}s)")
        
        while self.running and not self.stop_event.is_set():
            try:
                self.send_heartbeat()
                
                # Wait for next heartbeat
                if self.stop_event.wait(self.config.heartbeat_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                if self.stop_event.wait(self.config.heartbeat_interval):
                    break
        
        self.logger.info("Heartbeat loop stopped")
    
    def start_simulation(self):
        """Start the complete device simulation"""
        self.logger.info("Starting edge device simulation...")
        
        # Step 1: Register device
        if not self.register_device():
            self.logger.error("Device registration failed - aborting simulation")
            return False
        
        # Step 2: Wait for approval
        if not self.wait_for_approval():
            self.logger.error("Device approval failed - aborting simulation")
            return False
        
        # Step 3: Connect websocket
        if not self.connect_websocket():
            self.logger.error("WebSocket connection failed - aborting simulation")
            return False
        
        # Step 4: Start simulation loops
        self.running = True
        self.stop_event.clear()
        
        # Start threads
        detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        health_thread = threading.Thread(target=self.health_loop, daemon=True)
        heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
        
        self.threads = [detection_thread, health_thread, heartbeat_thread]
        
        for thread in self.threads:
            thread.start()
        
        self.logger.info("Edge device simulation is running!")
        self.logger.info(f"- Device ID: {self.config.device_id}")
        self.logger.info(f"- Server URL: {self.config.server_url}")
        self.logger.info(f"- Detection Interval: {self.config.detection_interval}s")
        self.logger.info(f"- Health Check Interval: {self.config.health_interval}s")
        self.logger.info(f"- Heartbeat Interval: {self.config.heartbeat_interval}s")
        self.logger.info("Press Ctrl+C to stop simulation")
        
        return True
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.logger.info("Stopping edge device simulation...")
        
        self.running = False
        self.stop_event.set()
        
        # Disconnect websocket
        if self.socketio_client and self.connected:
            try:
                self.socketio_client.disconnect()
            except Exception as e:
                self.logger.error(f"Error disconnecting websocket: {e}")
        
        # Wait for threads to finish
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=5)
        
        self.logger.info("Edge device simulation stopped")
    
    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    def _generate_mac_address(self) -> str:
        """Generate a random MAC address"""
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                       for elements in range(0, 2*6, 2)][::-1])
        return mac


def main():
    parser = argparse.ArgumentParser(description='Edge Device Simulator for AI Camera Server')
    parser.add_argument('--server-url', default='http://localhost:3000', help='Server URL')
    parser.add_argument('--device-id', default=f'sim-{random.randint(100, 999)}', help='Device ID')
    parser.add_argument('--device-model', default='AI-CAM-SIMULATOR-V1', help='Device model')
    parser.add_argument('--detection-interval', type=int, default=10, help='Detection interval (seconds)')
    parser.add_argument('--health-interval', type=int, default=30, help='Health check interval (seconds)')
    parser.add_argument('--heartbeat-interval', type=int, default=60, help='Heartbeat interval (seconds)')
    parser.add_argument('--no-images', action='store_true', help='Disable image generation')
    
    args = parser.parse_args()
    
    # Create configuration
    config = SimulationConfig(
        server_url=args.server_url,
        device_id=args.device_id,
        device_model=args.device_model,
        detection_interval=args.detection_interval,
        health_interval=args.health_interval,
        heartbeat_interval=args.heartbeat_interval,
        simulate_images=not args.no_images
    )
    
    # Create and start simulator
    simulator = EdgeDeviceSimulator(config)
    
    try:
        if simulator.start_simulation():
            # Keep running until interrupted
            while simulator.running:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    finally:
        simulator.stop_simulation()


if __name__ == "__main__":
    main()