#!/usr/bin/env python3
"""
Storage Manager for AI Camera Edge Device

This module handles image storage and transfer to the server using multiple protocols:
1. SFTP transfer for images
2. MQTT communication for metadata and status
3. Local database tracking for unsent files
4. Rsync synchronization support

Features:
- Automatic image transfer when network is available
- Retry mechanism for failed transfers
- Database tracking of transfer status
- Multiple transfer protocols (SFTP, rsync)
- Image compression and optimization
- Transfer queue management

Author: AI Camera Team
Version: 2.0.0
"""

import os
import json
import time
import sqlite3
import logging
import threading
import hashlib
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
import paramiko
from PIL import Image
import io

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import (
    DATABASE_PATH, CAPTURED_IMAGES_PATH, 
    SERVER_SFTP_HOST, SERVER_SFTP_PORT, SERVER_SFTP_USERNAME, SERVER_SFTP_PASSWORD,
    STORAGE_MANAGER_ENABLED, TRANSFER_RETRY_INTERVAL, MAX_TRANSFER_RETRIES,
    IMAGE_COMPRESSION_ENABLED, IMAGE_COMPRESSION_QUALITY
)

logger = get_logger(__name__)


@dataclass
class ImageTransferRecord:
    """Record for tracking image transfer status"""
    id: Optional[int] = None
    filename: str = ""
    filepath: str = ""
    checksum: str = ""
    size: int = 0
    compressed_size: int = 0
    detection_id: Optional[int] = None
    transfer_status: str = "pending"  # pending, uploading, completed, failed
    transfer_method: str = "sftp"  # sftp, rsync, mqtt
    retry_count: int = 0
    last_attempt: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    server_path: Optional[str] = None
    created_at: Optional[str] = None

@dataclass
class TransferStats:
    """Statistics for transfer operations"""
    total_files: int = 0
    pending_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    total_size: int = 0
    transferred_size: int = 0
    last_transfer: Optional[str] = None
    average_speed: float = 0.0  # bytes per second


class StorageManager:
    """
    Storage Manager for handling image storage and transfer operations
    """
    
    def __init__(self, database_manager=None):
        self.logger = logger
        self.database_manager = database_manager
        
        # Configuration
        self.enabled = STORAGE_MANAGER_ENABLED
        self.captured_images_path = Path(CAPTURED_IMAGES_PATH)
        self.database_path = DATABASE_PATH
        
        # Server connection settings
        self.sftp_host = SERVER_SFTP_HOST
        self.sftp_port = SERVER_SFTP_PORT
        self.sftp_username = SERVER_SFTP_USERNAME
        self.sftp_password = SERVER_SFTP_PASSWORD
        
        # Transfer settings
        self.retry_interval = TRANSFER_RETRY_INTERVAL
        self.max_retries = MAX_TRANSFER_RETRIES
        self.compression_enabled = IMAGE_COMPRESSION_ENABLED
        self.compression_quality = IMAGE_COMPRESSION_QUALITY
        
        # Threading
        self.running = False
        self.transfer_thread = None
        self.stop_event = threading.Event()
        
        # SFTP connection
        self.sftp_client = None
        self.sftp_connected = False
        
        # Statistics
        self.stats = TransferStats()
        
        # Initialize database
        self._init_database()
        
        self.logger.info("Storage Manager initialized")
    
    def _init_database(self):
        """Initialize the storage database tables"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Image transfer records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS image_transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    checksum TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    compressed_size INTEGER DEFAULT 0,
                    detection_id INTEGER,
                    transfer_status TEXT DEFAULT 'pending',
                    transfer_method TEXT DEFAULT 'sftp',
                    retry_count INTEGER DEFAULT 0,
                    last_attempt DATETIME,
                    completed_at DATETIME,
                    error_message TEXT,
                    server_path TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Transfer statistics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transfer_statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    files_transferred INTEGER DEFAULT 0,
                    bytes_transferred INTEGER DEFAULT 0,
                    transfer_time_seconds INTEGER DEFAULT 0,
                    average_speed REAL DEFAULT 0.0,
                    errors_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(date)
                )
            """)
            
            # Indexes for better performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transfer_status ON image_transfers(transfer_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_transfer_created_at ON image_transfers(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_detection_id ON image_transfers(detection_id)")
            
            conn.commit()
            conn.close()
            
            self.logger.info("Storage database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage database: {e}")
            raise
    
    def initialize(self) -> bool:
        """Initialize the storage manager"""
        try:
            if not self.enabled:
                self.logger.info("Storage Manager is disabled")
                return False
            
            # Ensure directories exist
            self.captured_images_path.mkdir(parents=True, exist_ok=True)
            
            # Update statistics
            self._update_stats()
            
            self.logger.info("Storage Manager initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Storage Manager: {e}")
            return False
    
    def start(self) -> bool:
        """Start the storage manager service"""
        try:
            if not self.initialize():
                return False
            
            self.running = True
            self.stop_event.clear()
            
            # Start transfer thread
            self.transfer_thread = threading.Thread(
                target=self._transfer_loop,
                name="Storage-Transfer-Thread",
                daemon=True
            )
            self.transfer_thread.start()
            
            self.logger.info("Storage Manager started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start Storage Manager: {e}")
            return False
    
    def stop(self):
        """Stop the storage manager service"""
        try:
            self.logger.info("Stopping Storage Manager...")
            
            self.running = False
            self.stop_event.set()
            
            # Disconnect SFTP
            self._disconnect_sftp()
            
            # Wait for threads to finish
            if self.transfer_thread and self.transfer_thread.is_alive():
                self.transfer_thread.join(timeout=10.0)
            
            self.logger.info("Storage Manager stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping Storage Manager: {e}")
    
    def add_image_for_transfer(self, filepath: str, detection_id: Optional[int] = None, 
                             transfer_method: str = "sftp") -> Optional[int]:
        """
        Add an image file to the transfer queue
        
        Args:
            filepath: Path to the image file
            detection_id: Associated detection ID
            transfer_method: Transfer method (sftp, rsync, mqtt)
            
        Returns:
            Transfer record ID or None if failed
        """
        try:
            file_path = Path(filepath)
            if not file_path.exists():
                self.logger.error(f"Image file does not exist: {filepath}")
                return None
            
            # Calculate file checksum
            checksum = self._calculate_file_checksum(filepath)
            file_size = file_path.stat().st_size
            
            # Check if already exists in queue
            if self._transfer_record_exists(checksum):
                self.logger.debug(f"Image already in transfer queue: {filepath}")
                return None
            
            # Compress image if enabled
            compressed_size = file_size
            if self.compression_enabled and self._is_image_file(filepath):
                compressed_size = self._compress_image(filepath)
            
            # Create transfer record
            record = ImageTransferRecord(
                filename=file_path.name,
                filepath=str(file_path),
                checksum=checksum,
                size=file_size,
                compressed_size=compressed_size,
                detection_id=detection_id,
                transfer_method=transfer_method,
                created_at=datetime.now().isoformat()
            )
            
            # Insert into database
            record_id = self._insert_transfer_record(record)
            
            if record_id:
                self.logger.info(f"Added image to transfer queue: {file_path.name} (ID: {record_id})")
                self._update_stats()
                return record_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to add image to transfer queue: {e}")
            return None
    
    def get_pending_transfers(self, limit: int = 10) -> List[ImageTransferRecord]:
        """Get pending transfer records"""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM image_transfers 
                WHERE transfer_status IN ('pending', 'failed')
                AND retry_count < ?
                ORDER BY created_at ASC
                LIMIT ?
            """, (self.max_retries, limit))
            
            records = []
            for row in cursor.fetchall():
                records.append(ImageTransferRecord(**dict(row)))
            
            conn.close()
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get pending transfers: {e}")
            return []
    
    def _transfer_loop(self):
        """Main transfer loop"""
        self.logger.info("Storage transfer loop started")
        
        while self.running and not self.stop_event.is_set():
            try:
                # Get pending transfers
                pending_transfers = self.get_pending_transfers()
                
                if not pending_transfers:
                    # No pending transfers, wait longer
                    if self.stop_event.wait(30):  # Wait 30 seconds
                        break
                    continue
                
                # Process transfers
                for record in pending_transfers:
                    if not self.running or self.stop_event.is_set():
                        break
                    
                    success = self._process_transfer(record)
                    
                    if success:
                        self.logger.info(f"Successfully transferred: {record.filename}")
                    else:
                        self.logger.warning(f"Failed to transfer: {record.filename}")
                    
                    # Brief pause between transfers
                    if self.stop_event.wait(1):
                        break
                
                # Update statistics
                self._update_stats()
                
                # Wait before next batch
                if self.stop_event.wait(self.retry_interval):
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in transfer loop: {e}")
                if self.stop_event.wait(self.retry_interval):
                    break
        
        self.logger.info("Storage transfer loop stopped")
    
    def _process_transfer(self, record: ImageTransferRecord) -> bool:
        """Process a single transfer record"""
        try:
            # Check if file still exists
            if not os.path.exists(record.filepath):
                self.logger.warning(f"File no longer exists: {record.filepath}")
                self._update_transfer_status(record.id, "failed", "File not found")
                return False
            
            # Update attempt
            self._update_transfer_attempt(record.id)
            
            # Choose transfer method
            if record.transfer_method == "sftp":
                success = self._transfer_via_sftp(record)
            elif record.transfer_method == "rsync":
                success = self._transfer_via_rsync(record)
            else:
                self.logger.error(f"Unsupported transfer method: {record.transfer_method}")
                success = False
            
            # Update record status
            if success:
                self._update_transfer_status(record.id, "completed")
                
                # Delete local file if configured to do so
                if self._should_delete_after_transfer():
                    self._delete_transferred_file(record.filepath)
            else:
                retry_count = record.retry_count + 1
                if retry_count >= self.max_retries:
                    self._update_transfer_status(record.id, "failed", f"Max retries exceeded ({self.max_retries})")
                else:
                    self._update_transfer_status(record.id, "pending", f"Retry {retry_count}/{self.max_retries}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error processing transfer: {e}")
            self._update_transfer_status(record.id, "failed", str(e))
            return False
    
    def _transfer_via_sftp(self, record: ImageTransferRecord) -> bool:
        """Transfer file via SFTP"""
        try:
            # Connect to SFTP server
            if not self._connect_sftp():
                return False
            
            # Prepare remote path
            remote_dir = f"/aicamera/{self._get_device_id()}/images"
            remote_path = f"{remote_dir}/{record.filename}"
            
            # Create remote directory
            self._ensure_remote_directory(remote_dir)
            
            # Upload file
            start_time = time.time()
            self.sftp_client.put(record.filepath, remote_path)
            transfer_time = time.time() - start_time
            
            # Verify upload
            remote_stat = self.sftp_client.stat(remote_path)
            local_size = os.path.getsize(record.filepath)
            
            if remote_stat.st_size != local_size:
                raise Exception(f"File size mismatch: local={local_size}, remote={remote_stat.st_size}")
            
            # Update record with server path
            self._update_transfer_server_path(record.id, remote_path)
            
            # Update daily statistics
            self._update_daily_stats(1, local_size, transfer_time)
            
            return True
            
        except Exception as e:
            self.logger.error(f"SFTP transfer failed for {record.filename}: {e}")
            return False
    
    def _transfer_via_rsync(self, record: ImageTransferRecord) -> bool:
        """Transfer file via rsync"""
        try:
            # Prepare rsync command
            local_path = record.filepath
            remote_path = f"{self.sftp_username}@{self.sftp_host}:/aicamera/{self._get_device_id()}/images/{record.filename}"
            
            cmd = [
                "rsync", "-avz", "--progress",
                local_path, remote_path
            ]
            
            import subprocess
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info(f"Rsync transfer successful: {record.filename}")
                return True
            else:
                self.logger.error(f"Rsync transfer failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Rsync transfer failed for {record.filename}: {e}")
            return False
    
    def _connect_sftp(self) -> bool:
        """Connect to SFTP server"""
        if self.sftp_connected and self.sftp_client:
            return True
        
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            ssh.connect(
                hostname=self.sftp_host,
                port=self.sftp_port,
                username=self.sftp_username,
                password=self.sftp_password,
                timeout=30
            )
            
            self.sftp_client = ssh.open_sftp()
            self.sftp_connected = True
            
            self.logger.info(f"Connected to SFTP server: {self.sftp_host}:{self.sftp_port}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to SFTP server: {e}")
            return False
    
    def _disconnect_sftp(self):
        """Disconnect from SFTP server"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            self.sftp_connected = False
            self.sftp_client = None
            
        except Exception as e:
            self.logger.error(f"Error disconnecting SFTP: {e}")
    
    def _ensure_remote_directory(self, remote_dir: str):
        """Ensure remote directory exists"""
        try:
            if self.sftp_client:
                # Try to create directory structure
                dirs = remote_dir.strip('/').split('/')
                path = ''
                for dir_name in dirs:
                    path += f'/{dir_name}'
                    try:
                        self.sftp_client.mkdir(path)
                    except IOError:
                        pass  # Directory might already exist
                        
        except Exception as e:
            self.logger.warning(f"Could not ensure remote directory: {e}")
    
    def _calculate_file_checksum(self, filepath: str) -> str:
        """Calculate SHA256 checksum of file"""
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _compress_image(self, filepath: str) -> int:
        """Compress image and return compressed size"""
        try:
            if not self._is_image_file(filepath):
                return os.path.getsize(filepath)
            
            with Image.open(filepath) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                
                # Create compressed version
                compressed_path = f"{filepath}.compressed"
                img.save(
                    compressed_path,
                    'JPEG',
                    quality=self.compression_quality,
                    optimize=True
                )
                
                compressed_size = os.path.getsize(compressed_path)
                
                # Replace original with compressed version
                shutil.move(compressed_path, filepath)
                
                return compressed_size
                
        except Exception as e:
            self.logger.warning(f"Failed to compress image {filepath}: {e}")
            return os.path.getsize(filepath)
    
    def _is_image_file(self, filepath: str) -> bool:
        """Check if file is an image"""
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        return Path(filepath).suffix.lower() in image_extensions
    
    def _transfer_record_exists(self, checksum: str) -> bool:
        """Check if transfer record already exists"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM image_transfers WHERE checksum = ?", (checksum,))
            count = cursor.fetchone()[0]
            
            conn.close()
            return count > 0
            
        except Exception as e:
            self.logger.error(f"Failed to check transfer record existence: {e}")
            return False
    
    def _insert_transfer_record(self, record: ImageTransferRecord) -> Optional[int]:
        """Insert transfer record into database"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO image_transfers (
                    filename, filepath, checksum, size, compressed_size,
                    detection_id, transfer_method, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.filename, record.filepath, record.checksum,
                record.size, record.compressed_size, record.detection_id,
                record.transfer_method, record.created_at
            ))
            
            record_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return record_id
            
        except Exception as e:
            self.logger.error(f"Failed to insert transfer record: {e}")
            return None
    
    def _update_transfer_status(self, record_id: int, status: str, error_message: str = None):
        """Update transfer record status"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            completed_at = datetime.now().isoformat() if status == "completed" else None
            
            cursor.execute("""
                UPDATE image_transfers 
                SET transfer_status = ?, error_message = ?, completed_at = ?
                WHERE id = ?
            """, (status, error_message, completed_at, record_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update transfer status: {e}")
    
    def _update_transfer_attempt(self, record_id: int):
        """Update transfer attempt count and timestamp"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE image_transfers 
                SET retry_count = retry_count + 1, last_attempt = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), record_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update transfer attempt: {e}")
    
    def _update_transfer_server_path(self, record_id: int, server_path: str):
        """Update server path for transfer record"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE image_transfers 
                SET server_path = ?
                WHERE id = ?
            """, (server_path, record_id))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update server path: {e}")
    
    def _update_stats(self):
        """Update transfer statistics"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get counts by status
            cursor.execute("""
                SELECT transfer_status, COUNT(*), COALESCE(SUM(size), 0)
                FROM image_transfers 
                GROUP BY transfer_status
            """)
            
            stats_data = cursor.fetchall()
            
            self.stats = TransferStats()
            
            for status, count, total_size in stats_data:
                self.stats.total_files += count
                
                if status == 'pending':
                    self.stats.pending_files = count
                elif status == 'completed':
                    self.stats.completed_files = count
                    self.stats.transferred_size = total_size
                elif status == 'failed':
                    self.stats.failed_files = count
                
                self.stats.total_size += total_size
            
            # Get last transfer time
            cursor.execute("""
                SELECT completed_at FROM image_transfers 
                WHERE transfer_status = 'completed'
                ORDER BY completed_at DESC LIMIT 1
            """)
            
            result = cursor.fetchone()
            if result:
                self.stats.last_transfer = result[0]
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update statistics: {e}")
    
    def _update_daily_stats(self, files_count: int, bytes_transferred: int, transfer_time: float):
        """Update daily transfer statistics"""
        try:
            today = datetime.now().date().isoformat()
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO transfer_statistics (
                    date, files_transferred, bytes_transferred, 
                    transfer_time_seconds, average_speed
                ) VALUES (
                    ?, 
                    COALESCE((SELECT files_transferred FROM transfer_statistics WHERE date = ?), 0) + ?,
                    COALESCE((SELECT bytes_transferred FROM transfer_statistics WHERE date = ?), 0) + ?,
                    COALESCE((SELECT transfer_time_seconds FROM transfer_statistics WHERE date = ?), 0) + ?,
                    CASE WHEN ? > 0 THEN ? / ? ELSE 0 END
                )
            """, (
                today, today, files_count, today, bytes_transferred, 
                today, int(transfer_time), transfer_time, bytes_transferred, transfer_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to update daily statistics: {e}")
    
    def _should_delete_after_transfer(self) -> bool:
        """Check if files should be deleted after successful transfer"""
        # This should be configurable - for now, don't delete
        return False
    
    def _delete_transferred_file(self, filepath: str):
        """Delete file after successful transfer"""
        try:
            if os.path.exists(filepath):
                os.unlink(filepath)
                self.logger.info(f"Deleted transferred file: {filepath}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete transferred file: {e}")
    
    def _get_device_id(self) -> str:
        """Get device ID from configuration or environment"""
        # This should get the actual device ID from registration
        import socket
        return os.getenv('DEVICE_ID', socket.gethostname())
    
    # Public API methods
    
    def get_status(self) -> Dict[str, Any]:
        """Get storage manager status"""
        return {
            'enabled': self.enabled,
            'running': self.running,
            'sftp_connected': self.sftp_connected,
            'stats': asdict(self.stats),
            'configuration': {
                'sftp_host': self.sftp_host,
                'sftp_port': self.sftp_port,
                'compression_enabled': self.compression_enabled,
                'max_retries': self.max_retries,
            }
        }
    
    def get_transfer_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get transfer history"""
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM image_transfers 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return records
            
        except Exception as e:
            self.logger.error(f"Failed to get transfer history: {e}")
            return []
    
    def retry_failed_transfers(self) -> int:
        """Retry all failed transfers"""
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE image_transfers 
                SET transfer_status = 'pending', retry_count = 0, error_message = NULL
                WHERE transfer_status = 'failed'
                AND retry_count < ?
            """, (self.max_retries,))
            
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Reset {updated_count} failed transfers to pending")
            self._update_stats()
            
            return updated_count
            
        except Exception as e:
            self.logger.error(f"Failed to retry failed transfers: {e}")
            return 0
    
    def cleanup_completed_records(self, days_old: int = 7) -> int:
        """Clean up old completed transfer records"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days_old)).isoformat()
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM image_transfers 
                WHERE transfer_status = 'completed' 
                AND completed_at < ?
            """, (cutoff_date,))
            
            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            self.logger.info(f"Cleaned up {deleted_count} old transfer records")
            self._update_stats()
            
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup completed records: {e}")
            return 0


def create_storage_manager(database_manager=None) -> StorageManager:
    """
    Factory function for Storage Manager
    
    Args:
        database_manager: Database manager instance
        
    Returns:
        StorageManager: Configured storage manager instance
    """
    return StorageManager(database_manager)