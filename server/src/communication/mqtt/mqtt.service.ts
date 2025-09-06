import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as mqtt from 'mqtt';
import { EventEmitter } from 'events';

export interface MqttMessage {
  topic: string;
  payload: Buffer;
  packet: mqtt.IPublishPacket;
}

export interface DetectionMessage {
  deviceId: string;
  timestamp: string;
  detectionData: any;
  imageInfo?: {
    filename: string;
    size: number;
    checksum: string;
  };
}

@Injectable()
export class MqttService extends EventEmitter implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(MqttService.name);
  private client: mqtt.MqttClient;
  private isConnected = false;

  // MQTT Topics
  private readonly TOPICS = {
    DEVICE_REGISTER: 'aicamera/device/register',
    DEVICE_HEARTBEAT: 'aicamera/device/heartbeat',
    DETECTION_DATA: 'aicamera/detection/+/data',
    DETECTION_RESPONSE: 'aicamera/detection/+/response',
    IMAGE_TRANSFER_REQUEST: 'aicamera/image/+/request',
    IMAGE_TRANSFER_STATUS: 'aicamera/image/+/status',
    SYSTEM_COMMAND: 'aicamera/system/+/command',
    SYSTEM_STATUS: 'aicamera/system/+/status',
  };

  constructor(private readonly configService: ConfigService) {
    super();
  }

  async onModuleInit() {
    await this.connect();
  }

  async onModuleDestroy() {
    await this.disconnect();
  }

  private async connect(): Promise<void> {
    try {
      const mqttUrl = this.configService.get<string>('MQTT_URL', 'mqtt://localhost:1883');
      const clientId = this.configService.get<string>('MQTT_CLIENT_ID', `aicamera-server-${Date.now()}`);
      const username = this.configService.get<string>('MQTT_USERNAME');
      const password = this.configService.get<string>('MQTT_PASSWORD');

      const options: mqtt.IClientOptions = {
        clientId,
        clean: true,
        connectTimeout: 60000,
        reconnectPeriod: 5000,
        keepalive: 60,
      };

      if (username && password) {
        options.username = username;
        options.password = password;
      }

      this.logger.log(`Connecting to MQTT broker at ${mqttUrl}`);
      this.client = mqtt.connect(mqttUrl, options);

      this.client.on('connect', () => {
        this.isConnected = true;
        this.logger.log('Connected to MQTT broker');
        this.setupSubscriptions();
        this.emit('connected');
      });

      this.client.on('disconnect', () => {
        this.isConnected = false;
        this.logger.warn('Disconnected from MQTT broker');
        this.emit('disconnected');
      });

      this.client.on('error', (error) => {
        this.logger.error(`MQTT connection error: ${error.message}`);
        this.emit('error', error);
      });

      this.client.on('message', (topic, payload, packet) => {
        this.handleMessage({ topic, payload, packet });
      });

      this.client.on('reconnect', () => {
        this.logger.log('Reconnecting to MQTT broker...');
      });

    } catch (error) {
      this.logger.error(`Failed to connect to MQTT broker: ${error.message}`);
      throw error;
    }
  }

  private async disconnect(): Promise<void> {
    if (this.client && this.isConnected) {
      this.logger.log('Disconnecting from MQTT broker');
      this.client.end();
      this.isConnected = false;
    }
  }

  private setupSubscriptions(): void {
    const topics = [
      this.TOPICS.DEVICE_REGISTER,
      this.TOPICS.DEVICE_HEARTBEAT,
      this.TOPICS.DETECTION_DATA,
      this.TOPICS.IMAGE_TRANSFER_REQUEST,
      this.TOPICS.SYSTEM_STATUS,
    ];

    topics.forEach(topic => {
      this.client.subscribe(topic, { qos: 1 }, (error) => {
        if (error) {
          this.logger.error(`Failed to subscribe to topic ${topic}: ${error.message}`);
        } else {
          this.logger.debug(`Subscribed to topic: ${topic}`);
        }
      });
    });
  }

  private handleMessage(message: MqttMessage): void {
    try {
      const topic = message.topic;
      const payload = message.payload.toString();

      this.logger.debug(`Received MQTT message on topic: ${topic}`);

      if (topic === this.TOPICS.DEVICE_REGISTER) {
        this.handleDeviceRegister(JSON.parse(payload));
      } else if (topic === this.TOPICS.DEVICE_HEARTBEAT) {
        this.handleDeviceHeartbeat(JSON.parse(payload));
      } else if (topic.startsWith('aicamera/detection/') && topic.endsWith('/data')) {
        const deviceId = this.extractDeviceId(topic, 'aicamera/detection/', '/data');
        this.handleDetectionData(deviceId, JSON.parse(payload));
      } else if (topic.startsWith('aicamera/image/') && topic.endsWith('/request')) {
        const deviceId = this.extractDeviceId(topic, 'aicamera/image/', '/request');
        this.handleImageTransferRequest(deviceId, JSON.parse(payload));
      } else if (topic.startsWith('aicamera/system/') && topic.endsWith('/status')) {
        const deviceId = this.extractDeviceId(topic, 'aicamera/system/', '/status');
        this.handleSystemStatus(deviceId, JSON.parse(payload));
      }

      // Emit generic message event for external handlers
      this.emit('message', { topic, payload: JSON.parse(payload) });

    } catch (error) {
      this.logger.error(`Error handling MQTT message: ${error.message}`);
    }
  }

  private extractDeviceId(topic: string, prefix: string, suffix: string): string {
    return topic.replace(prefix, '').replace(suffix, '');
  }

  private handleDeviceRegister(data: any): void {
    this.logger.log(`Device registration request: ${data.deviceId}`);
    this.emit('device-register', data);
  }

  private handleDeviceHeartbeat(data: any): void {
    this.logger.debug(`Device heartbeat: ${data.deviceId}`);
    this.emit('device-heartbeat', data);
  }

  private handleDetectionData(deviceId: string, data: DetectionMessage): void {
    this.logger.log(`Detection data received from device: ${deviceId}`);
    this.emit('detection-data', { deviceId, ...data });

    // Send acknowledgment
    this.publishDetectionResponse(deviceId, {
      timestamp: data.timestamp,
      status: 'received',
      message: 'Detection data processed successfully',
    });
  }

  private handleImageTransferRequest(deviceId: string, data: any): void {
    this.logger.log(`Image transfer request from device: ${deviceId}`);
    this.emit('image-transfer-request', { deviceId, ...data });
  }

  private handleSystemStatus(deviceId: string, data: any): void {
    this.logger.debug(`System status from device: ${deviceId}`);
    this.emit('system-status', { deviceId, ...data });
  }

  // Public methods for publishing messages

  async publishDetectionResponse(deviceId: string, response: any): Promise<void> {
    const topic = `aicamera/detection/${deviceId}/response`;
    await this.publish(topic, response);
  }

  async publishImageTransferStatus(deviceId: string, status: any): Promise<void> {
    const topic = `aicamera/image/${deviceId}/status`;
    await this.publish(topic, status);
  }

  async publishSystemCommand(deviceId: string, command: any): Promise<void> {
    const topic = `aicamera/system/${deviceId}/command`;
    await this.publish(topic, command);
  }

  async publish(topic: string, payload: any, options?: mqtt.IClientPublishOptions): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected) {
        reject(new Error('MQTT client is not connected'));
        return;
      }

      const message = typeof payload === 'string' ? payload : JSON.stringify(payload);
      const publishOptions: mqtt.IClientPublishOptions = {
        qos: 1,
        retain: false,
        ...options,
      };

      this.client.publish(topic, message, publishOptions, (error) => {
        if (error) {
          this.logger.error(`Failed to publish to topic ${topic}: ${error.message}`);
          reject(error);
        } else {
          this.logger.debug(`Published to topic: ${topic}`);
          resolve();
        }
      });
    });
  }

  async subscribe(topic: string, qos: 0 | 1 | 2 = 1): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected) {
        reject(new Error('MQTT client is not connected'));
        return;
      }

      this.client.subscribe(topic, { qos }, (error) => {
        if (error) {
          this.logger.error(`Failed to subscribe to topic ${topic}: ${error.message}`);
          reject(error);
        } else {
          this.logger.log(`Subscribed to topic: ${topic}`);
          resolve();
        }
      });
    });
  }

  async unsubscribe(topic: string): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isConnected) {
        reject(new Error('MQTT client is not connected'));
        return;
      }

      this.client.unsubscribe(topic, (error) => {
        if (error) {
          this.logger.error(`Failed to unsubscribe from topic ${topic}: ${error.message}`);
          reject(error);
        } else {
          this.logger.log(`Unsubscribed from topic: ${topic}`);
          resolve();
        }
      });
    });
  }

  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  getClient(): mqtt.MqttClient {
    return this.client;
  }

  getTopics() {
    return this.TOPICS;
  }
}