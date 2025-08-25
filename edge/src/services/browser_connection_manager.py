#!/usr/bin/env python3
"""
Browser Connection Manager Service for AI Camera v2.0.0

This service tracks browser connections and manages resource allocation
based on active browser sessions.

Features:
- Browser connection tracking
- Resource allocation management
- Connection statistics
- Automatic resource cleanup
- Integration with camera manager

Author: AI Camera Team
Version: 2.0.0
Date: August 25, 2025
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import (
    BROWSER_CONNECTION_TIMEOUT, 
    BROWSER_CLEANUP_INTERVAL
)

logger = get_logger(__name__)


@dataclass
class BrowserConnection:
    """Browser connection information."""
    session_id: str
    connected_at: datetime
    last_activity: datetime
    user_agent: str
    ip_address: str
    resources_allocated: List[str]
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'connected_at': self.connected_at.isoformat(),
            'last_activity': self.last_activity.isoformat(),
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'resources_allocated': self.resources_allocated,
            'is_active': self.is_active,
            'duration_seconds': (datetime.now() - self.connected_at).total_seconds()
        }


class BrowserConnectionManager:
    """
    Browser Connection Manager for tracking and managing browser sessions.
    
    This service provides:
    - Real-time browser connection tracking
    - Resource allocation management
    - Connection statistics and monitoring
    - Automatic cleanup of stale connections
    - Integration with camera and streaming services
    """
    
    def __init__(self):
        """
        Initialize Browser Connection Manager.
        """
        self.logger = logger
        
        # Connection tracking
        self.active_connections: Dict[str, BrowserConnection] = {}
        self.connection_history: List[BrowserConnection] = []
        
        # Resource management
        self.resource_allocation_enabled = True
        self.conditional_resource_allocation = True
        
        # Statistics
        self.total_connections = 0
        self.current_connections = 0
        self.max_concurrent_connections = 0
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Cleanup thread
        self.cleanup_thread = None
        self.stop_cleanup = threading.Event()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        self.logger.info("BrowserConnectionManager initialized")
    
    def on_browser_connect(self, session_id: str, browser_info: Dict[str, Any]) -> bool:
        """
        Handle new browser connection.
        
        Args:
            session_id: WebSocket session ID
            browser_info: Browser information (user_agent, ip_address, etc.)
            
        Returns:
            bool: True if connection tracked successfully
        """
        try:
            with self.lock:
                # Create connection record
                connection = BrowserConnection(
                    session_id=session_id,
                    connected_at=datetime.now(),
                    last_activity=datetime.now(),
                    user_agent=browser_info.get('user_agent', 'Unknown'),
                    ip_address=browser_info.get('ip_address', 'Unknown'),
                    resources_allocated=[]
                )
                
                # Add to active connections
                self.active_connections[session_id] = connection
                
                # Update statistics
                self.total_connections += 1
                self.current_connections = len(self.active_connections)
                self.max_concurrent_connections = max(
                    self.max_concurrent_connections, 
                    self.current_connections
                )
                
                self.logger.info(f"Browser connected: {session_id} from {connection.ip_address}")
                self.logger.info(f"Active connections: {self.current_connections}")
                
                # Trigger resource allocation if needed
                if self.conditional_resource_allocation:
                    self._trigger_resource_allocation()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error tracking browser connection {session_id}: {e}")
            return False
    
    def on_browser_disconnect(self, session_id: str) -> bool:
        """
        Handle browser disconnection.
        
        Args:
            session_id: WebSocket session ID
            
        Returns:
            bool: True if disconnection handled successfully
        """
        try:
            with self.lock:
                if session_id in self.active_connections:
                    # Get connection info
                    connection = self.active_connections[session_id]
                    connection.is_active = False
                    
                    # Move to history
                    self.connection_history.append(connection)
                    
                    # Remove from active connections
                    del self.active_connections[session_id]
                    
                    # Update statistics
                    self.current_connections = len(self.active_connections)
                    
                    self.logger.info(f"Browser disconnected: {session_id}")
                    self.logger.info(f"Active connections: {self.current_connections}")
                    
                    # Trigger resource cleanup if needed
                    if self.conditional_resource_allocation:
                        self._trigger_resource_cleanup()
                    
                    return True
                else:
                    self.logger.warning(f"Unknown session disconnected: {session_id}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error handling browser disconnection {session_id}: {e}")
            return False
    
    def update_activity(self, session_id: str) -> bool:
        """
        Update last activity time for a connection.
        
        Args:
            session_id: WebSocket session ID
            
        Returns:
            bool: True if activity updated successfully
        """
        try:
            with self.lock:
                if session_id in self.active_connections:
                    self.active_connections[session_id].last_activity = datetime.now()
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Error updating activity for {session_id}: {e}")
            return False
    
    def get_connection_status(self) -> Dict[str, Any]:
        """
        Get current connection status and statistics.
        
        Returns:
            Dict containing connection status information
        """
        try:
            with self.lock:
                # Calculate connection durations
                active_connections = []
                for conn in self.active_connections.values():
                    active_connections.append(conn.to_dict())
                
                # Calculate average duration
                total_duration = sum(
                    (datetime.now() - conn.connected_at).total_seconds() 
                    for conn in self.active_connections.values()
                )
                avg_duration = total_duration / len(self.active_connections) if self.active_connections else 0
                
                return {
                    'active_connections': active_connections,
                    'current_connections': self.current_connections,
                    'total_connections': self.total_connections,
                    'max_concurrent_connections': self.max_concurrent_connections,
                    'average_connection_duration': round(avg_duration, 2),
                    'resource_allocation_enabled': self.resource_allocation_enabled,
                    'conditional_resource_allocation': self.conditional_resource_allocation,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"Error getting connection status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def should_allocate_resources(self) -> bool:
        """
        Check if resources should be allocated based on active connections.
        
        Returns:
            bool: True if resources should be allocated
        """
        try:
            with self.lock:
                if not self.conditional_resource_allocation:
                    return True  # Always allocate if conditional allocation is disabled
                
                has_active_connections = len(self.active_connections) > 0
                
                if has_active_connections:
                    self.logger.debug(f"Active connections detected: {len(self.active_connections)} - resources should be allocated")
                else:
                    self.logger.debug("No active connections - resources can be deallocated")
                
                return has_active_connections
                
        except Exception as e:
            self.logger.error(f"Error checking resource allocation: {e}")
            return True  # Default to allocating resources on error
    
    def _trigger_resource_allocation(self):
        """Trigger resource allocation when connections are established."""
        try:
            if self.should_allocate_resources():
                self.logger.info("Triggering resource allocation for active connections")
                # Note: Camera manager handles its own resource allocation
                # This is just for tracking purposes
        except Exception as e:
            self.logger.error(f"Error triggering resource allocation: {e}")
    
    def _trigger_resource_cleanup(self):
        """Trigger resource cleanup when no connections are active."""
        try:
            if not self.should_allocate_resources():
                self.logger.info("No active connections - resources can be deallocated")
                # Note: Camera manager handles its own resource cleanup
                # This is just for tracking purposes
        except Exception as e:
            self.logger.error(f"Error triggering resource cleanup: {e}")
    
    def _start_cleanup_thread(self):
        """Start background thread for cleaning up stale connections."""
        try:
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_worker,
                daemon=True,
                name="BrowserConnectionCleanup"
            )
            self.cleanup_thread.start()
            self.logger.info("Browser connection cleanup thread started")
        except Exception as e:
            self.logger.error(f"Error starting cleanup thread: {e}")
    
    def _cleanup_worker(self):
        """Background worker for cleaning up stale connections."""
        while not self.stop_cleanup.is_set():
            try:
                self._cleanup_stale_connections()
                time.sleep(BROWSER_CLEANUP_INTERVAL)
            except Exception as e:
                self.logger.error(f"Error in cleanup worker: {e}")
                time.sleep(5)  # Wait before retrying
    
    def _cleanup_stale_connections(self):
        """Clean up connections that have been inactive for too long."""
        try:
            with self.lock:
                current_time = datetime.now()
                stale_sessions = []
                
                for session_id, connection in self.active_connections.items():
                    time_since_activity = (current_time - connection.last_activity).total_seconds()
                    
                    if time_since_activity > BROWSER_CONNECTION_TIMEOUT:
                        stale_sessions.append(session_id)
                        self.logger.warning(f"Stale connection detected: {session_id} (inactive for {time_since_activity:.1f}s)")
                
                # Remove stale connections
                for session_id in stale_sessions:
                    self.on_browser_disconnect(session_id)
                
                if stale_sessions:
                    self.logger.info(f"Cleaned up {len(stale_sessions)} stale connections")
                    
        except Exception as e:
            self.logger.error(f"Error cleaning up stale connections: {e}")
    
    def cleanup(self):
        """Cleanup resources."""
        try:
            self.logger.info("Cleaning up BrowserConnectionManager...")
            
            # Stop cleanup thread
            self.stop_cleanup.set()
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            # Clear connections
            with self.lock:
                self.active_connections.clear()
                self.connection_history.clear()
            
            self.logger.info("BrowserConnectionManager cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


def create_browser_connection_manager() -> BrowserConnectionManager:
    """
    Factory function for BrowserConnectionManager.
    
    Returns:
        BrowserConnectionManager instance
    """
    return BrowserConnectionManager()
