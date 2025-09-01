#!/usr/bin/env python3
"""
AI Camera Kiosk Browser Handler
รองรับทั้งการต่อจอ monitor และ headless mode
"""

import os
import sys
import time
import subprocess
import logging
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/kiosk_browser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class KioskBrowserHandler:
    """Handler สำหรับจัดการ kiosk browser ในสภาพแวดล้อมต่างๆ"""
    
    def __init__(self):
        self.config = self.load_config()
        self.browser_process = None
        self.current_mode = None
        self.is_running = False
        
    def load_config(self) -> Dict:
        """โหลดการตั้งค่าจาก environment variables"""
        return {
            'web_url': os.getenv('WEB_URL', 'http://localhost/'),
            'browser_path': os.getenv('BROWSER_PATH', '/usr/lib/chromium/chromium'),
            'user_data_dir': os.getenv('USER_DATA_DIR', '/tmp/chromium-kiosk'),
            'remote_debug_port': int(os.getenv('REMOTE_DEBUG_PORT', '9222')),
            'wait_timeout': int(os.getenv('WAIT_TIMEOUT', '120')),
            'check_interval': int(os.getenv('CHECK_INTERVAL', '30')),
            'max_retries': int(os.getenv('MAX_RETRIES', '3')),
            'headless_fallback': os.getenv('HEADLESS_FALLBACK', 'true').lower() == 'true'
        }
    
    def detect_environment(self) -> str:
        """ตรวจสอบสภาพแวดล้อมและเลือก browser mode ที่เหมาะสม"""
        logger.info("Detecting environment...")
        
        # ตรวจสอบ DISPLAY
        display = os.getenv('DISPLAY')
        if not display:
            logger.info("No DISPLAY environment variable - using headless mode")
            return 'headless'
        
        # ตรวจสอบ X server
        if not self.check_x_server():
            logger.info("X server not available - using headless mode")
            return 'headless'
        
        # ตรวจสอบ screen resolution
        if not self.check_screen_resolution():
            logger.info("No valid screen resolution - using headless mode")
            return 'headless'
        
        # ตรวจสอบว่าเป็น embedded system หรือไม่
        if self.is_embedded_system():
            logger.info("Embedded system detected - using headless mode")
            return 'headless'
        
        logger.info("Full display environment detected - using kiosk mode")
        return 'kiosk'
    
    def check_x_server(self) -> bool:
        """ตรวจสอบว่า X server ทำงานอยู่หรือไม่"""
        try:
            # ตรวจสอบ X server process
            result = subprocess.run(
                ['xset', 'q'], 
                capture_output=True, 
                timeout=5,
                env={'DISPLAY': os.getenv('DISPLAY', ':0')}
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def check_screen_resolution(self) -> bool:
        """ตรวจสอบ screen resolution"""
        try:
            result = subprocess.run(
                ['xrandr', '--current'], 
                capture_output=True, 
                timeout=5,
                env={'DISPLAY': os.getenv('DISPLAY', ':0')}
            )
            if result.returncode == 0:
                output = result.stdout.decode()
                # ตรวจสอบว่ามี screen ที่ใช้งานได้
                return 'connected' in output and 'x' in output
            return False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def is_embedded_system(self) -> bool:
        """ตรวจสอบว่าเป็น embedded system หรือไม่"""
        # ตรวจสอบ CPU architecture
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_info = f.read()
                if 'ARM' in cpu_info or 'aarch64' in cpu_info:
                    return True
        except:
            pass
        
        # ตรวจสอบ system memory
        try:
            mem_info = psutil.virtual_memory()
            if mem_info.total < 2 * 1024 * 1024 * 1024:  # < 2GB
                return True
        except:
            pass
        
        return False
    
    def get_browser_args(self, mode: str) -> List[str]:
        """สร้าง browser arguments ตาม mode ที่เลือก"""
        base_args = [
            self.config['browser_path'],
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-web-security',
            '--disable-features=VizDisplayCompositor',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-background-timer-throttling',
            '--disable-backgrounding-occluded-windows',
            '--disable-renderer-backgrounding',
            '--disable-features=TranslateUI',
            '--disable-ipc-flooding-protection',
            '--autoplay-policy=no-user-gesture-required',
            '--disable-session-crashed-bubble',
            '--disable-infobars',
            '--disable-notifications',
            '--new-window',
            '--allow-running-insecure-content'
        ]
        
        if mode == 'headless':
            # Headless mode arguments
            headless_args = [
                '--headless',
                '--disable-gpu',
                f'--user-data-dir={self.config["user_data_dir"]}-headless',
                f'--remote-debugging-port={self.config["remote_debug_port"]}',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--disable-java',
                '--disable-plugins-discovery',
                '--disable-default-apps'
            ]
            base_args.extend(headless_args)
        else:
            # Kiosk mode arguments
            kiosk_args = [
                '--kiosk',
                '--disable-gpu',
                f'--user-data-dir={self.config["user_data_dir"]}-kiosk',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-infobars',
                '--disable-session-crashed-bubble',
                '--disable-notifications',
                '--disable-web-security',
                '--allow-running-insecure-content',
                '--no-first-run',
                '--no-default-browser-check',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-ipc-flooding-protection',
                '--autoplay-policy=no-user-gesture-required'
            ]
            base_args.extend(kiosk_args)
        
        # เพิ่ม URL
        base_args.append(self.config['web_url'])
        
        return base_args
    
    def wait_for_services(self) -> bool:
        """รอให้ services พร้อมใช้งาน"""
        logger.info("Waiting for services to be ready...")
        
        # รอ nginx
        if not self.wait_for_service('nginx', 30):
            logger.error("Nginx service not ready")
            return False
        
        # รอ aicamera_lpr
        if not self.wait_for_service('aicamera_lpr', 60):
            logger.error("AICamera LPR service not ready")
            return False
        
        # รอ web service
        if not self.wait_for_web_service():
            logger.error("Web service not responding")
            return False
        
        logger.info("All services are ready!")
        return True
    
    def wait_for_service(self, service_name: str, timeout: int) -> bool:
        """รอให้ systemd service พร้อมใช้งาน"""
        logger.info(f"Waiting for {service_name} service...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = subprocess.run(
                    ['systemctl', 'is-active', '--quiet', service_name],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"{service_name} service is ready")
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            time.sleep(2)
        
        return False
    
    def wait_for_web_service(self) -> bool:
        """รอให้ web service ตอบสนอง"""
        logger.info("Waiting for web service to respond...")
        start_time = time.time()
        
        while time.time() - start_time < self.config['wait_timeout']:
            try:
                result = subprocess.run(
                    ['curl', '-s', '-f', self.config['web_url']],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info("Web service is responding")
                    return True
            except subprocess.TimeoutExpired:
                pass
            
            time.sleep(5)
        
        return False
    
    def start_browser(self, mode: str) -> bool:
        """เริ่มต้น browser ใน mode ที่กำหนด"""
        logger.info(f"Starting browser in {mode} mode...")
        
        try:
            # สร้าง user data directory
            user_data_dir = f"{self.config['user_data_dir']}-{mode}"
            os.makedirs(user_data_dir, exist_ok=True)
            
            # สร้าง browser arguments
            args = self.get_browser_args(mode)
            logger.info(f"Browser command: {' '.join(args)}")
            
            # เริ่มต้น browser process
            self.browser_process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            self.current_mode = mode
            self.is_running = True
            
            logger.info(f"Browser started successfully in {mode} mode (PID: {self.browser_process.pid})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def stop_browser(self):
        """หยุด browser"""
        if self.browser_process and self.is_running:
            logger.info("Stopping browser...")
            
            try:
                # ส่ง SIGTERM
                os.killpg(os.getpgid(self.browser_process.pid), signal.SIGTERM)
                
                # รอให้ process หยุด
                try:
                    self.browser_process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # ส่ง SIGKILL ถ้ายังไม่หยุด
                    os.killpg(os.getpgid(self.browser_process.pid), signal.SIGKILL)
                    self.browser_process.wait()
                
                logger.info("Browser stopped successfully")
                
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")
            
            finally:
                self.browser_process = None
                self.is_running = False
                self.current_mode = None
    
    def check_browser_health(self) -> bool:
        """ตรวจสอบสุขภาพของ browser process"""
        if not self.browser_process or not self.is_running:
            return False
        
        # ตรวจสอบว่า process ยังทำงานอยู่หรือไม่
        if self.browser_process.poll() is not None:
            logger.warning("Browser process has exited")
            self.is_running = False
            return False
        
        # ตรวจสอบ memory usage
        try:
            process = psutil.Process(self.browser_process.pid)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            if memory_mb > 1000:  # > 1GB
                logger.warning(f"High memory usage: {memory_mb:.1f} MB")
            
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logger.warning("Cannot access browser process info")
        
        return True
    
    def restart_browser(self, mode: str = None) -> bool:
        """รีสตาร์ท browser"""
        logger.info("Restarting browser...")
        
        # หยุด browser ปัจจุบัน
        self.stop_browser()
        
        # รอสักครู่
        time.sleep(2)
        
        # เริ่มต้น browser ใหม่
        if mode is None:
            mode = self.current_mode or self.detect_environment()
        
        return self.start_browser(mode)
    
    def run(self):
        """ทำงานหลักของ handler"""
        logger.info("Starting Kiosk Browser Handler...")
        
        # ตรวจสอบสภาพแวดล้อม
        mode = self.detect_environment()
        logger.info(f"Selected mode: {mode}")
        
        # รอให้ services พร้อม
        if not self.wait_for_services():
            logger.error("Services not ready, exiting")
            return 1
        
        # เริ่มต้น browser
        if not self.start_browser(mode):
            logger.error("Failed to start browser")
            return 1
        
        # Main loop
        try:
            while self.is_running:
                # ตรวจสอบสุขภาพของ browser
                if not self.check_browser_health():
                    logger.warning("Browser health check failed, restarting...")
                    if not self.restart_browser():
                        logger.error("Failed to restart browser")
                        break
                
                # รอสักครู่
                time.sleep(self.config['check_interval'])
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        finally:
            self.stop_browser()
            logger.info("Kiosk Browser Handler stopped")
        
        return 0

def main():
    """Main function"""
    handler = KioskBrowserHandler()
    return handler.run()

if __name__ == '__main__':
    sys.exit(main())
