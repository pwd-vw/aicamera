import { Controller, Post, Get, Body, Logger } from '@nestjs/common';
import { CommunicationOrchestratorService } from './communication-orchestrator.service';
import { DetectionData, DeviceData } from './interfaces/communication.interface';

@Controller('communication')
export class CommunicationController {
  private readonly logger = new Logger(CommunicationController.name);

  constructor(
    private readonly communicationOrchestrator: CommunicationOrchestratorService
  ) {}

  @Post('detection')
  async sendDetection(@Body() detectionData: DetectionData) {
    this.logger.log(`Received detection request: ${detectionData.licensePlate}`);
    return await this.communicationOrchestrator.sendDetection(detectionData);
  }

  @Post('device')
  async sendDeviceUpdate(@Body() deviceData: DeviceData) {
    this.logger.log(`Received device update request: ${deviceData.name}`);
    return await this.communicationOrchestrator.sendDeviceUpdate(deviceData);
  }

  @Post('health')
  async sendHealthCheck() {
    this.logger.log('Received health check request');
    return await this.communicationOrchestrator.sendHealthCheck();
  }

  @Get('status')
  async getStatus() {
    const availableProtocols = await this.communicationOrchestrator.getAvailableProtocols();
    const protocolStatus = await this.communicationOrchestrator.getProtocolStatus();

    return {
      availableProtocols,
      protocolStatus,
      timestamp: new Date()
    };
  }
}
