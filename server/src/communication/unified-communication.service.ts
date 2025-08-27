import { Injectable, Logger, OnModuleInit } from '@nestjs/common';
import { EventEmitter } from 'events';
import { MqttService } from './mqtt/mqtt.service';
import { SftpService } from './sftp/sftp.service';
import { ImageStorageService, ImageMetadata } from './storage/image-storage.service';
import { DeviceRegistrationService } from '../device-registration/device-registration.service';

export interface CommunicationStats {
  mqtt: {
    connected: boolean;
    messagesSent: number;
    messagesReceived: number;
  };
  sftp: {
    running: boolean;
    activeConnections: number;
    filesTransferred: number;
  };
  storage: {
    totalFiles: number;
    totalSize: number;
    deviceCounts: Record<string, number>;
  };
  websocket: {
    connections: number;
    messagesSent: number;
  };
}

export interface DetectionData {
  deviceId: string;
  timestamp: string;
  vehicles_count: number;
  plates_count: number;
  ocr_results: any[];
  vehicle_detections: any[];
  plate_detections: any[];
  processing_time_ms: number;
  image_data?: string; // base64 encoded image
}

@Injectable()
export class UnifiedCommunicationService extends EventEmitter implements OnModuleInit {
  private readonly logger = new Logger(UnifiedCommunicationService.name);
  private stats: CommunicationStats = {
    mqtt: { connected: false, messagesSent: 0, messagesReceived: 0 },
    sftp: { running: false, activeConnections: 0, filesTransferred: 0 },
    storage: { totalFiles: 0, totalSize: 0, deviceCounts: {} },
    websocket: { connections: 0, messagesSent: 0 },
  };

  constructor(
    private readonly mqttService: MqttService,
    private readonly sftpService: SftpService,
    private readonly imageStorageService: ImageStorageService,
    private readonly deviceRegistrationService?: DeviceRegistrationService,
  ) {
    super();
  }

  async onModuleInit() {
    this.setupEventHandlers();
    this.updateStats();
    
    // Periodic stats update
    setInterval(() => {
      this.updateStats();
    }, 30000); // Update every 30 seconds
  }

  private setupEventHandlers(): void {
    // MQTT event handlers
    this.mqttService.on('connected', () => {
      this.logger.log('MQTT service connected');
      this.stats.mqtt.connected = true;
      this.emit('mqtt-connected');
    });

    this.mqttService.on('disconnected', () => {
      this.logger.log('MQTT service disconnected');
      this.stats.mqtt.connected = false;
      this.emit('mqtt-disconnected');
    });

    this.mqttService.on('device-register', (data) => {
      this.handleDeviceRegistration(data);
    });

    this.mqttService.on('device-heartbeat', (data) => {
      this.handleDeviceHeartbeat(data);
    });

    this.mqttService.on('detection-data', (data) => {
      this.handleDetectionData(data);
    });

    this.mqttService.on('image-transfer-request', (data) => {
      this.handleImageTransferRequest(data);
    });

    // SFTP event handlers
    this.sftpService.on('server-started', () => {
      this.logger.log('SFTP service started');
      this.stats.sftp.running = true;
      this.emit('sftp-started');
    });

    this.sftpService.on('transfer-complete', (transferInfo) => {
      this.handleImageTransferComplete(transferInfo);
    });

    // Storage event handlers
    this.imageStorageService.on('image-stored', (metadata: ImageMetadata) => {
      this.handleImageStored(metadata);
    });

    this.imageStorageService.on('rsync-complete', (result) => {
      this.logger.log('Rsync completed successfully');
      this.emit('sync-complete', result);
    });
  }

  private async updateStats(): Promise<void> {
    try {
      // Update MQTT stats
      this.stats.mqtt.connected = this.mqttService.getConnectionStatus();

      // Update SFTP stats
      const sftpStatus = this.sftpService.getServerStatus();
      this.stats.sftp.running = sftpStatus.running;
      this.stats.sftp.activeConnections = sftpStatus.activeConnections;

      // Update storage stats
      const storageStats = await this.imageStorageService.getStorageStats();
      this.stats.storage = storageStats;

    } catch (error) {
      this.logger.error(`Failed to update stats: ${error.message}`);
    }
  }

  private async handleDeviceRegistration(data: any): Promise<void> {
    try {
      this.logger.log(`Processing device registration via MQTT: ${data.deviceId}`);
      
      // Forward to device registration service if available
      if (this.deviceRegistrationService) {
        // Convert MQTT format to REST API format
        const registrationData = {
          serialNumber: data.deviceId,
          deviceModel: data.deviceModel || 'Unknown',
          deviceType: data.deviceType || 'camera',
          ipAddress: data.ipAddress,
          macAddress: data.macAddress,
          locationLat: data.locationLat,
          locationLng: data.locationLng,
          locationAddress: data.locationAddress,
          metadata: {
            ...data.metadata,
            registrationMethod: 'mqtt',
            mqttTimestamp: data.timestamp,
          },
        };

        try {
          const result = await this.deviceRegistrationService.selfRegisterDevice(registrationData);
          
          // Send registration response via MQTT
          await this.mqttService.publish(`aicamera/device/${data.deviceId}/register/response`, {
            success: true,
            registrationId: result.id,
            status: result.registrationStatus,
            message: result.message,
          });

        } catch (error) {
          // Send error response via MQTT
          await this.mqttService.publish(`aicamera/device/${data.deviceId}/register/response`, {
            success: false,
            error: error.message,
          });
        }
      }

      this.emit('device-registered', data);
      
    } catch (error) {
      this.logger.error(`Error handling device registration: ${error.message}`);
    }
  }

  private async handleDeviceHeartbeat(data: any): Promise<void> {
    try {
      this.logger.debug(`Processing device heartbeat: ${data.deviceId}`);
      
      // Forward to device registration service for heartbeat update
      if (this.deviceRegistrationService) {
        const heartbeatData = {
          serialNumber: data.deviceId,
          ipAddress: data.ipAddress,
          statusData: data.statusData || data.metadata,
        };

        try {
          await this.deviceRegistrationService.updateHeartbeat(heartbeatData);
        } catch (error) {
          this.logger.warn(`Failed to update heartbeat for ${data.deviceId}: ${error.message}`);
        }
      }

      this.emit('device-heartbeat', data);
      
    } catch (error) {
      this.logger.error(`Error handling device heartbeat: ${error.message}`);
    }
  }

  private async handleDetectionData(data: DetectionData): Promise<void> {
    try {
      this.logger.log(`Processing detection data from device: ${data.deviceId}`);
      
      // Store image if provided
      let imageMetadata: ImageMetadata | null = null;
      if (data.image_data) {
        try {
          const imageBuffer = Buffer.from(data.image_data, 'base64');
          imageMetadata = await this.imageStorageService.storeImage(
            data.deviceId,
            imageBuffer,
            {
              originalName: `detection_${data.timestamp}.jpg`,
              processingTime: data.processing_time_ms,
            }
          );
        } catch (error) {
          this.logger.error(`Failed to store detection image: ${error.message}`);
        }
      }

      // Process detection data (save to database, analytics, etc.)
      const processedData = {
        ...data,
        imageMetadata,
        processedAt: new Date().toISOString(),
      };

      // Send acknowledgment via MQTT
      await this.mqttService.publishDetectionResponse(data.deviceId, {
        timestamp: data.timestamp,
        status: 'processed',
        message: 'Detection data processed successfully',
        imageStored: !!imageMetadata,
      });

      this.stats.mqtt.messagesReceived++;
      this.emit('detection-processed', processedData);
      
    } catch (error) {
      this.logger.error(`Error processing detection data: ${error.message}`);
      
      // Send error response
      try {
        await this.mqttService.publishDetectionResponse(data.deviceId, {
          timestamp: data.timestamp,
          status: 'error',
          message: error.message,
        });
      } catch (mqttError) {
        this.logger.error(`Failed to send error response: ${mqttError.message}`);
      }
    }
  }

  private async handleImageTransferRequest(data: any): Promise<void> {
    try {
      this.logger.log(`Processing image transfer request from device: ${data.deviceId}`);
      
      // Create device directory for SFTP uploads
      await this.sftpService.createDeviceDirectory(data.deviceId);
      
      // Send transfer status via MQTT
      await this.mqttService.publishImageTransferStatus(data.deviceId, {
        requestId: data.requestId,
        status: 'ready',
        sftpPath: `/${data.deviceId}/images/`,
        message: 'Ready to receive images via SFTP',
      });

      this.emit('image-transfer-ready', data);
      
    } catch (error) {
      this.logger.error(`Error handling image transfer request: ${error.message}`);
      
      // Send error status
      await this.mqttService.publishImageTransferStatus(data.deviceId, {
        requestId: data.requestId,
        status: 'error',
        message: error.message,
      });
    }
  }

  private handleImageTransferComplete(transferInfo: any): void {
    this.logger.log(`Image transfer completed: ${transferInfo.filename} from ${transferInfo.deviceId}`);
    
    this.stats.sftp.filesTransferred++;
    this.emit('image-transferred', transferInfo);
  }

  private handleImageStored(metadata: ImageMetadata): void {
    this.logger.log(`Image stored: ${metadata.filename} from ${metadata.deviceId}`);
    this.emit('image-stored', metadata);
  }

  // Public API methods

  async sendSystemCommand(deviceId: string, command: any): Promise<void> {
    await this.mqttService.publishSystemCommand(deviceId, command);
    this.stats.mqtt.messagesSent++;
  }

  async requestImageSync(deviceId: string, syncOptions?: any): Promise<void> {
    const command = {
      type: 'sync_images',
      timestamp: new Date().toISOString(),
      options: syncOptions,
    };
    
    await this.sendSystemCommand(deviceId, command);
  }

  async broadcastMessage(message: any): Promise<void> {
    await this.mqttService.publish('aicamera/broadcast', message);
    this.stats.mqtt.messagesSent++;
  }

  getStats(): CommunicationStats {
    return { ...this.stats };
  }

  async getDeviceImages(deviceId: string, limit?: number, offset?: number): Promise<string[]> {
    return this.imageStorageService.listImages(deviceId, limit, offset);
  }

  async getDeviceImage(deviceId: string, filename: string): Promise<Buffer | null> {
    return this.imageStorageService.getImage(deviceId, filename);
  }

  async getDeviceThumbnail(deviceId: string, filename: string): Promise<Buffer | null> {
    return this.imageStorageService.getThumbnail(deviceId, filename);
  }

  async deleteDeviceImage(deviceId: string, filename: string): Promise<boolean> {
    return this.imageStorageService.deleteImage(deviceId, filename);
  }

  async cleanupDeviceImages(deviceId: string, retentionDays: number = 30): Promise<number> {
    return this.imageStorageService.cleanupOldImages(deviceId, retentionDays);
  }

  async syncImagesWithRsync(sourcePattern: string, destination: string): Promise<{ success: boolean; output: string }> {
    return this.imageStorageService.syncWithRsync({
      source: sourcePattern,
      destination,
      recursive: true,
      compress: true,
      excludePatterns: ['*.tmp', '*.temp'],
    });
  }

  isHealthy(): boolean {
    // Service is considered healthy if at least one communication method is working
    return this.stats.mqtt.connected || this.stats.sftp.running;
  }

  async getServiceStatus(): Promise<Record<string, any>> {
    return {
      mqtt: {
        connected: this.stats.mqtt.connected,
        topics: this.mqttService.getTopics(),
      },
      sftp: this.sftpService.getServerStatus(),
      storage: await this.imageStorageService.getStorageStats(),
      unified: {
        healthy: this.isHealthy(),
        uptime: process.uptime(),
        stats: this.stats,
      },
    };
  }
}