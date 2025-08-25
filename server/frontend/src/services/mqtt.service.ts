import mqtt, { MqttClient } from 'mqtt';
import type { IClientOptions, IClientPublishOptions } from 'mqtt';

export class MQTTService {
  private client: MqttClient | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private subscriptions: Map<string, (message: string) => void> = new Map();

  connect(url: string = import.meta.env.VITE_MQTT_URL || 'mqtt://localhost:1883', options?: IClientOptions) {
    if (this.client?.connected) {
      return this.client;
    }

    const defaultOptions: IClientOptions = {
      clientId: `aicamera_frontend_${Math.random().toString(16).slice(2, 8)}`,
      clean: true,
      reconnectPeriod: this.reconnectDelay,
      connectTimeout: 30 * 1000,
      ...options,
    };

    this.client = mqtt.connect(url, defaultOptions);
    this.setupEventHandlers();
    return this.client;
  }

  private setupEventHandlers() {
    if (!this.client) return;

    this.client.on('connect', () => {
      console.log('MQTT connected');
      this.reconnectAttempts = 0;
      // Resubscribe to topics after reconnection
      this.subscriptions.forEach((callback, topic) => {
        this.client?.subscribe(topic);
      });
    });

    this.client.on('disconnect', () => {
      console.log('MQTT disconnected');
    });

    this.client.on('error', (error) => {
      console.error('MQTT error:', error);
    });

    this.client.on('reconnect', () => {
      console.log('MQTT reconnecting...');
      this.reconnectAttempts++;
    });

    this.client.on('message', (topic: string, message: Buffer) => {
      const callback = this.subscriptions.get(topic);
      if (callback) {
        try {
          const messageStr = message.toString();
          const data = JSON.parse(messageStr);
          callback(data);
        } catch (error) {
          console.error('Error parsing MQTT message:', error);
          callback(message.toString());
        }
      }
    });
  }

  // Subscribe to topics
  subscribe(topic: string, callback: (message: any) => void) {
    if (!this.client) {
      console.error('MQTT client not connected');
      return;
    }

    this.subscriptions.set(topic, callback);
    this.client.subscribe(topic, (err) => {
      if (err) {
        console.error('MQTT subscribe error:', err);
      } else {
        console.log('Subscribed to:', topic);
      }
    });
  }

  // Unsubscribe from topics
  unsubscribe(topic: string) {
    if (!this.client) return;

    this.subscriptions.delete(topic);
    this.client.unsubscribe(topic, (err) => {
      if (err) {
        console.error('MQTT unsubscribe error:', err);
      } else {
        console.log('Unsubscribed from:', topic);
      }
    });
  }

  // Publish messages
  publish(topic: string, message: any, options?: IClientPublishOptions) {
    if (!this.client) {
      console.error('MQTT client not connected');
      return;
    }

    const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
    this.client.publish(topic, messageStr, options, (err) => {
      if (err) {
        console.error('MQTT publish error:', err);
      }
    });
  }

  // Camera control topics
  subscribeToCameraStatus(cameraId: string, callback: (status: any) => void) {
    this.subscribe(`camera/${cameraId}/status`, callback);
  }

  subscribeToCameraHealth(cameraId: string, callback: (health: any) => void) {
    this.subscribe(`camera/${cameraId}/health`, callback);
  }

  subscribeToDetections(cameraId: string, callback: (detection: any) => void) {
    this.subscribe(`camera/${cameraId}/detections`, callback);
  }

  // System topics
  subscribeToSystemEvents(callback: (event: any) => void) {
    this.subscribe('system/events', callback);
  }

  subscribeToSystemHealth(callback: (health: any) => void) {
    this.subscribe('system/health', callback);
  }

  // Control topics
  publishCameraControl(cameraId: string, command: string, params?: any) {
    this.publish(`camera/${cameraId}/control`, { command, params });
  }

  publishCameraConfig(cameraId: string, config: any) {
    this.publish(`camera/${cameraId}/config`, config);
  }

  // Connection management
  disconnect() {
    if (this.client) {
      this.client.end();
      this.client = null;
      this.subscriptions.clear();
    }
  }

  isConnected(): boolean {
    return this.client?.connected || false;
  }

  getClient(): MqttClient | null {
    return this.client;
  }

  // Get all active subscriptions
  getSubscriptions(): string[] {
    return Array.from(this.subscriptions.keys());
  }
}

// Create singleton instance
export const mqttService = new MQTTService();
