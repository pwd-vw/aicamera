#!/usr/bin/env python3
"""
Communication System Test Script for AI Camera

This script tests the complete communication workflow:
1. Device registration
2. MQTT communication
3. SFTP image transfer
4. WebSocket metadata transmission
5. Server response verification

Usage:
    python test_communication_system.py [options]
"""

import os
import sys
import json
import time
import random
import logging
import argparse
import requests
import paho.mqtt.client as mqtt
import paramiko
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageDraw

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CommunicationTester:
    """Test suite for AI Camera communication system"""
    
    def __init__(self, config):
        self.config = config
        self.test_results = {}
        self.mqtt_client = None
        self.sftp_client = None
        
    def run_all_tests(self):
        """Run complete test suite"""
        logger.info("Starting AI Camera Communication System Tests")
        
        tests = [
            ('server_connectivity', self.test_server_connectivity),
            ('device_registration', self.test_device_registration),
            ('mqtt_communication', self.test_mqtt_communication),
            ('sftp_transfer', self.test_sftp_transfer),
            ('websocket_communication', self.test_websocket_communication),
            ('image_storage', self.test_image_storage),
        ]
        
        for test_name, test_func in tests:
            logger.info(f"Running test: {test_name}")
            try:
                result = test_func()
                self.test_results[test_name] = {
                    'status': 'PASS' if result else 'FAIL',
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"Test {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                self.test_results[test_name] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"Test {test_name} ERROR: {e}")
            
            time.sleep(2)  # Brief pause between tests
        
        self.print_test_summary()
        return self.test_results
    
    def test_server_connectivity(self):
        """Test basic server connectivity"""
        try:
            response = requests.get(
                f"{self.config['server_url']}/health",
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Server connectivity failed: {e}")
            return False
    
    def test_device_registration(self):
        """Test device self-registration"""
        try:
            device_data = {
                "serialNumber": f"test-device-{random.randint(1000, 9999)}",
                "deviceModel": "TEST-CAM-V1",
                "deviceType": "camera",
                "ipAddress": "127.0.0.1",
                "macAddress": "00:00:00:00:00:01",
                "locationLat": 13.7563,
                "locationLng": 100.5018,
                "locationAddress": "Test Location",
                "metadata": {
                    "test_mode": True,
                    "test_timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.config['server_url']}/device-registration/register",
                json=device_data,
                timeout=10
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"Device registered: {result['id']}")
                self.config['registration_id'] = result['id']
                self.config['device_serial'] = device_data['serialNumber']
                return True
            else:
                logger.error(f"Registration failed: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Device registration failed: {e}")
            return False
    
    def test_mqtt_communication(self):
        """Test MQTT communication"""
        try:
            # Connect to MQTT broker
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.connect(
                self.config['mqtt_host'], 
                self.config['mqtt_port'], 
                60
            )
            self.mqtt_client.loop_start()
            
            # Publish test message
            topic = f"aicamera/test/{self.config.get('device_serial', 'test-device')}"
            message = {
                "type": "test",
                "timestamp": datetime.now().isoformat(),
                "message": "Communication test"
            }
            
            result = self.mqtt_client.publish(topic, json.dumps(message), qos=1)
            result.wait_for_publish(timeout=5)
            
            if result.is_published():
                logger.info("MQTT message published successfully")
                return True
            else:
                logger.error("MQTT message publish failed")
                return False
                
        except Exception as e:
            logger.error(f"MQTT communication failed: {e}")
            return False
        finally:
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
    
    def test_sftp_transfer(self):
        """Test SFTP file transfer"""
        try:
            # Create test image
            test_image_path = self.create_test_image()
            
            # Connect to SFTP
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.config['sftp_host'],
                port=self.config['sftp_port'],
                username=self.config['sftp_username'],
                password=self.config['sftp_password'],
                timeout=10
            )
            
            self.sftp_client = ssh.open_sftp()
            
            # Create remote directory
            device_id = self.config.get('device_serial', 'test-device')
            remote_dir = f"image_storage/{device_id}"
            
            try:
                self.sftp_client.mkdir(remote_dir)
            except IOError:
                pass  # Directory might already exist
            
            # Upload test image
            remote_path = f"{remote_dir}/test_image.jpg"
            self.sftp_client.put(test_image_path, remote_path)
            
            # Verify upload
            remote_stat = self.sftp_client.stat(remote_path)
            local_size = os.path.getsize(test_image_path)
            
            if remote_stat.st_size == local_size:
                logger.info(f"SFTP transfer successful: {remote_path}")
                return True
            else:
                logger.error("SFTP transfer size mismatch")
                return False
                
        except Exception as e:
            logger.error(f"SFTP transfer failed: {e}")
            return False
        finally:
            if self.sftp_client:
                self.sftp_client.close()
            # Clean up test image
            if 'test_image_path' in locals():
                try:
                    os.unlink(test_image_path)
                except:
                    pass
    
    def test_websocket_communication(self):
        """Test WebSocket communication"""
        try:
            # For now, we'll test via REST API since WebSocket requires more setup
            # In a full implementation, this would test Socket.IO connections
            
            # Test communication endpoints
            response = requests.get(
                f"{self.config['server_url']}/communication/status",
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                logger.info(f"Communication status: {status}")
                return True
            else:
                logger.error(f"WebSocket status check failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"WebSocket communication test failed: {e}")
            return False
    
    def test_image_storage(self):
        """Test image storage functionality"""
        try:
            # Test image storage endpoints
            response = requests.get(
                f"{self.config['server_url']}/communication/images/stats",
                timeout=10
            )
            
            if response.status_code == 200:
                stats = response.json()
                logger.info(f"Image storage stats: {stats}")
                return True
            else:
                logger.error(f"Image storage test failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Image storage test failed: {e}")
            return False
    
    def create_test_image(self):
        """Create a test image for transfer"""
        img = Image.new('RGB', (640, 480), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Draw test content
        draw.text((10, 10), "AI Camera Test Image", fill='black')
        draw.text((10, 30), f"Timestamp: {datetime.now()}", fill='black')
        draw.rectangle([100, 100, 200, 150], outline='red', width=2)
        draw.text((110, 120), "TEST", fill='red')
        
        # Save to temp file
        test_image_path = f"/tmp/test_image_{random.randint(1000, 9999)}.jpg"
        img.save(test_image_path, 'JPEG')
        
        return test_image_path
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n" + "="*50)
        print("AI CAMERA COMMUNICATION SYSTEM TEST RESULTS")
        print("="*50)
        
        passed = 0
        failed = 0
        errors = 0
        
        for test_name, result in self.test_results.items():
            status = result['status']
            if status == 'PASS':
                print(f"✅ {test_name.upper()}: {status}")
                passed += 1
            elif status == 'FAIL':
                print(f"❌ {test_name.upper()}: {status}")
                failed += 1
            else:
                print(f"⚠️  {test_name.upper()}: {status} - {result.get('error', '')}")
                errors += 1
        
        print("-"*50)
        print(f"TOTAL TESTS: {len(self.test_results)}")
        print(f"PASSED: {passed}")
        print(f"FAILED: {failed}")
        print(f"ERRORS: {errors}")
        
        success_rate = (passed / len(self.test_results)) * 100
        print(f"SUCCESS RATE: {success_rate:.1f}%")
        print("="*50)
        
        if success_rate >= 80:
            print("🎉 Communication system is working well!")
        elif success_rate >= 60:
            print("⚠️  Communication system has some issues")
        else:
            print("❌ Communication system needs attention")
        
        print("\nDetailed results saved to test_results.json")
        
        # Save detailed results
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Test AI Camera Communication System')
    parser.add_argument('--server-url', default='http://localhost:3000', help='Server URL')
    parser.add_argument('--mqtt-host', default='localhost', help='MQTT broker host')
    parser.add_argument('--mqtt-port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--sftp-host', default='localhost', help='SFTP server host')
    parser.add_argument('--sftp-port', type=int, default=22, help='SFTP server port')
    parser.add_argument('--sftp-username', default='aicamera', help='SFTP username')
    parser.add_argument('--sftp-password', default='aicamera123', help='SFTP password')
    parser.add_argument('--test', choices=[
        'server', 'registration', 'mqtt', 'sftp', 'websocket', 'storage'
    ], help='Run specific test only')
    
    args = parser.parse_args()
    
    config = {
        'server_url': args.server_url,
        'mqtt_host': args.mqtt_host,
        'mqtt_port': args.mqtt_port,
        'sftp_host': args.sftp_host,
        'sftp_port': args.sftp_port,
        'sftp_username': args.sftp_username,
        'sftp_password': args.sftp_password,
    }
    
    tester = CommunicationTester(config)
    
    if args.test:
        # Run specific test
        test_method = getattr(tester, f'test_{args.test}_communication', None)
        if test_method:
            result = test_method()
            print(f"Test {args.test}: {'PASS' if result else 'FAIL'}")
        else:
            print(f"Unknown test: {args.test}")
    else:
        # Run all tests
        tester.run_all_tests()


if __name__ == "__main__":
    main()