import { Injectable, Logger } from '@nestjs/common';
import { CommunicationOrchestratorService } from '../communication/communication-orchestrator.service';
import { DetectionData, DeviceData } from '../communication/interfaces/communication.interface';

@Injectable()
export class DeviceService {
  private readonly logger = new Logger(DeviceService.name);

  constructor(
    private readonly communicationOrchestrator: CommunicationOrchestratorService
  ) {}

  async createDevice(deviceData: DeviceData): Promise<any> {
    try {
      // Store device data (placeholder for database operation)
      this.logger.log(`Creating device: ${deviceData.name}`);

      // Send device update via communication orchestrator
      const response = await this.communicationOrchestrator.sendDeviceUpdate(deviceData);
      
      if (!response.success) {
        this.logger.warn(`Failed to send device update: ${response.message}`);
      }

      return {
        success: true,
        message: 'Device created successfully',
        data: deviceData,
        communicationResponse: response
      };
    } catch (error) {
      this.logger.error(`Error creating device: ${error instanceof Error ? error.message : 'Unknown error'}`);
      throw error;
    }
  }

  async createDetection(detectionData: DetectionData): Promise<any> {
    try {
      // Store detection data (placeholder for database operation)
      this.logger.log(`Creating detection: ${detectionData.licensePlate}`);

      // Send detection via communication orchestrator
      const response = await this.communicationOrchestrator.sendDetection(detectionData);
      
      if (!response.success) {
        this.logger.warn(`Failed to send detection: ${response.message}`);
      }

      return {
        success: true,
        message: 'Detection created successfully',
        data: detectionData,
        communicationResponse: response
      };
    } catch (error) {
      this.logger.error(`Error creating detection: ${error instanceof Error ? error.message : 'Unknown error'}`);
      throw error;
    }
  }

  async sendHealthCheck(): Promise<any> {
    try {
      const response = await this.communicationOrchestrator.sendHealthCheck();
      
      return {
        success: response.success,
        message: response.message,
        timestamp: response.timestamp
      };
    } catch (error) {
      this.logger.error(`Error sending health check: ${error instanceof Error ? error.message : 'Unknown error'}`);
      throw error;
    }
  }

  async getCommunicationStatus(): Promise<any> {
    try {
      const availableProtocols = await this.communicationOrchestrator.getAvailableProtocols();
      const protocolStatus = await this.communicationOrchestrator.getProtocolStatus();

      return {
        availableProtocols,
        protocolStatus,
        timestamp: new Date()
      };
    } catch (error) {
      this.logger.error(`Error getting communication status: ${error instanceof Error ? error.message : 'Unknown error'}`);
      throw error;
    }
  }
}