import { apiService } from './api.service';
import { websocketService } from './websocket.service';
import { mqttService } from './mqtt.service';
import type { Camera, Detection, AnalyticsEvent } from './api.service';

export interface CommunicationConfig {
  apiUrl: string;
  wsUrl: string;
  mqttUrl: string;
  enableWebSocket: boolean;
  enableMQTT: boolean;
  fallbackToAPI: boolean;
}

export class CommunicationService {
  private config: CommunicationConfig;
  private isInitialized = false;

  constructor(config: Partial<CommunicationConfig> = {}) {
    this.config = {
      apiUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000',
      wsUrl: import.meta.env.VITE_WS_URL || 'ws://localhost:3000',
      mqttUrl: import.meta.env.VITE_MQTT_URL || 'mqtt://localhost:1883',
      enableWebSocket: true,
      enableMQTT: true,
      fallbackToAPI: true,
      ...config,
    };
  }

  async initialize() {
    if (this.isInitialized) return;

    try {
      // Initialize WebSocket if enabled
      if (this.config.enableWebSocket) {
        websocketService.connect(this.config.wsUrl);
      }

      // Initialize MQTT if enabled
      if (this.config.enableMQTT) {
        mqttService.connect(this.config.mqttUrl);
      }

      this.isInitialized = true;
      console.log('Communication service initialized');
    } catch (error) {
      console.error('Failed to initialize communication service:', error);
      if (this.config.fallbackToAPI) {
        console.log('Falling back to API-only mode');
      }
    }
  }

  // Camera operations
  async getCameras(): Promise<Camera[]> {
    try {
      return await apiService.getCameras();
    } catch (error) {
      console.error('Failed to get cameras:', error);
      throw error;
    }
  }

  async getCamera(id: string): Promise<Camera> {
    try {
      return await apiService.getCamera(id);
    } catch (error) {
      console.error('Failed to get camera:', error);
      throw error;
    }
  }

  // Real-time camera status
  subscribeToCameraStatus(cameraId: string, callback: (status: any) => void) {
    // Try WebSocket first
    if (this.config.enableWebSocket && websocketService.isConnected()) {
      websocketService.onCameraStatus(callback);
      websocketService.requestCameraStatus();
      return;
    }

    // Fallback to MQTT
    if (this.config.enableMQTT && mqttService.isConnected()) {
      mqttService.subscribeToCameraStatus(cameraId, callback);
      return;
    }

    // Fallback to polling via API
    if (this.config.fallbackToAPI) {
      this.pollCameraStatus(cameraId, callback);
    }
  }

  private async pollCameraStatus(cameraId: string, callback: (status: any) => void) {
    const poll = async () => {
      try {
        const health = await apiService.getCameraHealth(cameraId);
        callback(health);
      } catch (error) {
        console.error('Failed to poll camera status:', error);
      }
    };

    // Initial call
    await poll();

    // Poll every 5 seconds
    setInterval(poll, 5000);
  }

  // Detection operations
  async getDetections(params?: any): Promise<Detection[]> {
    try {
      return await apiService.getDetections(params);
    } catch (error) {
      console.error('Failed to get detections:', error);
      throw error;
    }
  }

  subscribeToDetections(cameraId: string, callback: (detection: Detection) => void) {
    // Try WebSocket first
    if (this.config.enableWebSocket && websocketService.isConnected()) {
      websocketService.onNewDetection(callback);
      return;
    }

    // Fallback to MQTT
    if (this.config.enableMQTT && mqttService.isConnected()) {
      mqttService.subscribeToDetections(cameraId, callback);
      return;
    }

    // Fallback to polling via API
    if (this.config.fallbackToAPI) {
      this.pollDetections(cameraId, callback);
    }
  }

  private async pollDetections(cameraId: string, callback: (detection: Detection) => void) {
    let lastTimestamp = new Date().toISOString();

    const poll = async () => {
      try {
        const detections = await apiService.getDetections({
          cameraId,
          startDate: lastTimestamp,
          limit: 10,
        });

        detections.forEach((detection: Detection) => {
          callback(detection);
          if (detection.createdAt > lastTimestamp) {
            lastTimestamp = detection.createdAt;
          }
        });
      } catch (error) {
        console.error('Failed to poll detections:', error);
      }
    };

    // Poll every 10 seconds
    setInterval(poll, 10000);
  }

  // Analytics events
  async createAnalyticsEvent(event: Partial<AnalyticsEvent>) {
    try {
      return await apiService.createAnalyticsEvent(event);
    } catch (error) {
      console.error('Failed to create analytics event:', error);
      throw error;
    }
  }

  subscribeToSystemEvents(callback: (event: any) => void) {
    // Try WebSocket first
    if (this.config.enableWebSocket && websocketService.isConnected()) {
      websocketService.onSystemEvent(callback);
      return;
    }

    // Fallback to MQTT
    if (this.config.enableMQTT && mqttService.isConnected()) {
      mqttService.subscribeToSystemEvents(callback);
      return;
    }
  }

  // Camera control
  async sendCameraControl(cameraId: string, command: string, params?: any) {
    // Try WebSocket first
    if (this.config.enableWebSocket && websocketService.isConnected()) {
      websocketService.sendCameraControl(command, params);
      return;
    }

    // Fallback to MQTT
    if (this.config.enableMQTT && mqttService.isConnected()) {
      mqttService.publishCameraControl(cameraId, command, params);
      return;
    }

    // Fallback to API
    if (this.config.fallbackToAPI) {
      // This would need to be implemented in the API
      console.warn('Camera control via API not implemented');
    }
  }

  // Connection status
  getConnectionStatus() {
    return {
      api: true, // API is always available
      websocket: this.config.enableWebSocket ? websocketService.isConnected() : false,
      mqtt: this.config.enableMQTT ? mqttService.isConnected() : false,
    };
  }

  // Cleanup
  disconnect() {
    if (this.config.enableWebSocket) {
      websocketService.disconnect();
    }

    if (this.config.enableMQTT) {
      mqttService.disconnect();
    }

    this.isInitialized = false;
  }

  // Configuration
  updateConfig(newConfig: Partial<CommunicationConfig>) {
    this.config = { ...this.config, ...newConfig };
  }

  getConfig(): CommunicationConfig {
    return { ...this.config };
  }
}

// Create singleton instance
export const communicationService = new CommunicationService();
