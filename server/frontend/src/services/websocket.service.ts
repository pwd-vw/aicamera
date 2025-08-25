import { io, Socket } from 'socket.io-client';

export class WebSocketService {
  private socket: Socket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(url: string = import.meta.env.VITE_WS_URL || 'ws://localhost:3000') {
    if (this.socket?.connected) {
      return this.socket;
    }

    this.socket = io(url, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventHandlers();
    return this.socket;
  }

  private setupEventHandlers() {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
    });

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      this.reconnectAttempts++;
    });

    this.socket.on('reconnect', (attemptNumber) => {
      console.log('WebSocket reconnected after', attemptNumber, 'attempts');
    });

    this.socket.on('reconnect_failed', () => {
      console.error('WebSocket reconnection failed');
    });
  }

  // Camera events
  onCameraStatus(callback: (data: any) => void) {
    this.socket?.on('camera_status_update', callback);
  }

  onCameraConnected(callback: (data: any) => void) {
    this.socket?.on('camera_connected', callback);
  }

  onCameraDisconnected(callback: (data: any) => void) {
    this.socket?.on('camera_disconnected', callback);
  }

  // Detection events
  onDetectionUpdate(callback: (data: any) => void) {
    this.socket?.on('detection_update', callback);
  }

  onNewDetection(callback: (data: any) => void) {
    this.socket?.on('new_detection', callback);
  }

  // System events
  onSystemEvent(callback: (data: any) => void) {
    this.socket?.on('system_event', callback);
  }

  onHealthUpdate(callback: (data: any) => void) {
    this.socket?.on('health_update', callback);
  }

  // Client events
  requestCameraStatus() {
    this.socket?.emit('camera_status_request');
  }

  requestCameraConfig() {
    this.socket?.emit('camera_config_request');
  }

  updateCameraConfig(config: any) {
    this.socket?.emit('camera_config_update', config);
  }

  sendCameraControl(command: string, params?: any) {
    this.socket?.emit('camera_control', { command, params });
  }

  // Generic event handling
  on(event: string, callback: (data: any) => void) {
    this.socket?.on(event, callback);
  }

  emit(event: string, data?: any) {
    this.socket?.emit(event, data);
  }

  // Connection management
  disconnect() {
    this.socket?.disconnect();
    this.socket = null;
  }

  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  getSocket(): Socket | null {
    return this.socket;
  }
}

// Create singleton instance
export const websocketService = new WebSocketService();
