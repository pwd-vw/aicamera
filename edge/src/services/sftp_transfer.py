import paramiko
import os
import logging
import time
from pathlib import Path
from typing import Optional

class SFTPTransfer:
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.transport = None
        self.sftp = None
        
    def connect(self) -> bool:
        try:
            self.transport = paramiko.Transport((self.host, self.port))
            self.transport.connect(username=self.username, password=self.password)
            self.sftp = paramiko.SFTPClient.from_transport(self.transport)
            logging.info(f"Connected to SFTP server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to SFTP server: {e}")
            return False
            
    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.transport:
            self.transport.close()
            
    def transfer_image(self, local_path: str, remote_path: str) -> bool:
        if not self.sftp:
            if not self.connect():
                return False
                
        try:
            # Ensure remote directory exists
            remote_dir = os.path.dirname(remote_path)
            try:
                self.sftp.stat(remote_dir)
            except FileNotFoundError:
                self.sftp.mkdir(remote_dir)
                
            # Transfer file
            self.sftp.put(local_path, remote_path)
            logging.info(f"Image transferred successfully: {remote_path}")
            return True
        except Exception as e:
            logging.error(f"SFTP transfer failed: {e}")
            return False
