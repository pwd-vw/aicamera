import websocket
import json
import logging
import threading
import time
from typing import Optional, Callable

class WebSocketClient:
    def __init__(self, server_url: str):
        self.server_url = server_url
        self.ws = None
        self.connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5
        
    def connect(self) -> bool:
        try:
            self.ws = websocket.WebSocketApp(
                self.server_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            
            # Run in separate thread
            wst = threading.Thread(target=self.ws.run_forever)
            wst.daemon = True
            wst.start()
            
            # Wait for connection
            timeout = 10
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
                
            return self.connected
        except Exception as e:
            logging.getLogger('communication').error(f"WebSocket connection failed: {e}")
            return False
            
    def on_open(self, ws):
        self.connected = True
        self.reconnect_attempts = 0
        logging.getLogger('communication').info(f"WebSocket connected to {self.server_url}")
        
    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            logging.getLogger('communication').info(f"Received WebSocket message: {data}")
        except json.JSONDecodeError:
            logging.getLogger('communication').warning(f"Received non-JSON WebSocket message: {message}")
            
    def on_error(self, ws, error):
        logging.getLogger('communication').error(f"WebSocket error: {error}")
        
    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False
        logging.getLogger('communication').info("WebSocket connection closed")
        
        # Attempt reconnection
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            logging.getLogger('communication').info(f"Attempting reconnection {self.reconnect_attempts}/{self.max_reconnect_attempts}")
            time.sleep(self.reconnect_delay)
            self.connect()
            
    def send_metadata(self, metadata: dict) -> bool:
        if self.connected and self.ws:
            try:
                self.ws.send(json.dumps(metadata))
                return True
            except Exception as e:
                logging.getLogger('communication').error(f"Failed to send metadata: {e}")
                return False
        return False
        
    def disconnect(self):
        if self.ws:
            self.ws.close()
