import { Controller, Get, Post, Put, Delete, Body, Param, Query, UseGuards, Request } from '@nestjs/common';
// import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth } from '@nestjs/swagger';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { UserRole } from '../../generated/prisma';
import { UnifiedCommunicationService } from './unified-communication.service';
import { ImageStorageService } from './storage/image-storage.service';
import { MqttService } from './mqtt/mqtt.service';
import { SftpService } from './sftp/sftp.service';

@ApiTags('Communication')
@Controller('communication')
@UseGuards(JwtAuthGuard, RolesGuard)
@ApiBearerAuth()
export class CommunicationController {
  constructor(
    private readonly communicationService: UnifiedCommunicationService,
    private readonly imageStorageService: ImageStorageService,
    private readonly mqttService: MqttService,
    private readonly sftpService: SftpService,
  ) {}

  @Get('status')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'Get communication system status' })
  @ApiResponse({ status: 200, description: 'Communication status retrieved' })
  async getStatus() {
    return this.communicationService.getServiceStatus();
  }

  @Get('stats')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'Get communication statistics' })
  @ApiResponse({ status: 200, description: 'Communication statistics retrieved' })
  async getStats() {
    return this.communicationService.getStats();
  }

  // MQTT endpoints
  @Post('mqtt/publish')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Publish MQTT message' })
  @ApiResponse({ status: 200, description: 'Message published successfully' })
  async publishMqttMessage(
    @Body() body: { topic: string; payload: any; options?: any }
  ) {
    await this.mqttService.publish(body.topic, body.payload, body.options);
    return { success: true, message: 'Message published' };
  }

  @Post('mqtt/subscribe')
  @Roles(UserRole.admin)
  @ApiOperation({ summary: 'Subscribe to MQTT topic' })
  @ApiResponse({ status: 200, description: 'Subscribed to topic' })
  async subscribeMqttTopic(
    @Body() body: { topic: string; qos?: number }
  ) {
    await this.mqttService.subscribe(body.topic, body.qos);
    return { success: true, message: 'Subscribed to topic' };
  }

  @Post('mqtt/unsubscribe')
  @Roles(UserRole.admin)
  @ApiOperation({ summary: 'Unsubscribe from MQTT topic' })
  @ApiResponse({ status: 200, description: 'Unsubscribed from topic' })
  async unsubscribeMqttTopic(
    @Body() body: { topic: string }
  ) {
    await this.mqttService.unsubscribe(body.topic);
    return { success: true, message: 'Unsubscribed from topic' };
  }

  // Device communication endpoints
  @Post('devices/:deviceId/command')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Send command to device' })
  @ApiResponse({ status: 200, description: 'Command sent to device' })
  async sendDeviceCommand(
    @Param('deviceId') deviceId: string,
    @Body() command: any
  ) {
    await this.communicationService.sendSystemCommand(deviceId, command);
    return { success: true, message: 'Command sent to device' };
  }

  @Post('devices/:deviceId/sync-images')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Request image sync from device' })
  @ApiResponse({ status: 200, description: 'Image sync requested' })
  async requestImageSync(
    @Param('deviceId') deviceId: string,
    @Body() options?: any
  ) {
    await this.communicationService.requestImageSync(deviceId, options);
    return { success: true, message: 'Image sync requested' };
  }

  @Post('broadcast')
  @Roles(UserRole.admin)
  @ApiOperation({ summary: 'Broadcast message to all devices' })
  @ApiResponse({ status: 200, description: 'Message broadcasted' })
  async broadcastMessage(@Body() message: any) {
    await this.communicationService.broadcastMessage(message);
    return { success: true, message: 'Message broadcasted' };
  }

  // Image storage endpoints
  @Get('images/stats')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'Get image storage statistics' })
  @ApiResponse({ status: 200, description: 'Image storage statistics' })
  async getImageStats() {
    return this.imageStorageService.getStorageStats();
  }

  @Get('images/:deviceId')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'List images for device' })
  @ApiResponse({ status: 200, description: 'Device images listed' })
  async listDeviceImages(
    @Param('deviceId') deviceId: string,
    @Query('limit') limit?: number,
    @Query('offset') offset?: number
  ) {
    const images = await this.communicationService.getDeviceImages(deviceId, limit, offset);
    return { deviceId, images, count: images.length };
  }

  @Get('images/:deviceId/:filename')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'Get device image' })
  @ApiResponse({ status: 200, description: 'Image retrieved' })
  async getDeviceImage(
    @Param('deviceId') deviceId: string,
    @Param('filename') filename: string
  ) {
    const image = await this.communicationService.getDeviceImage(deviceId, filename);
    if (!image) {
      return { error: 'Image not found' };
    }
    
    return {
      deviceId,
      filename,
      size: image.length,
      data: image.toString('base64'),
    };
  }

  @Get('images/:deviceId/:filename/thumbnail')
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiOperation({ summary: 'Get device image thumbnail' })
  @ApiResponse({ status: 200, description: 'Thumbnail retrieved' })
  async getDeviceImageThumbnail(
    @Param('deviceId') deviceId: string,
    @Param('filename') filename: string
  ) {
    const thumbnail = await this.communicationService.getDeviceThumbnail(deviceId, filename);
    if (!thumbnail) {
      return { error: 'Thumbnail not found' };
    }
    
    return {
      deviceId,
      filename,
      size: thumbnail.length,
      data: thumbnail.toString('base64'),
    };
  }

  @Delete('images/:deviceId/:filename')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Delete device image' })
  @ApiResponse({ status: 200, description: 'Image deleted' })
  async deleteDeviceImage(
    @Param('deviceId') deviceId: string,
    @Param('filename') filename: string
  ) {
    const success = await this.communicationService.deleteDeviceImage(deviceId, filename);
    return { success, message: success ? 'Image deleted' : 'Failed to delete image' };
  }

  @Post('images/:deviceId/cleanup')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Cleanup old device images' })
  @ApiResponse({ status: 200, description: 'Images cleaned up' })
  async cleanupDeviceImages(
    @Param('deviceId') deviceId: string,
    @Body() body: { retentionDays?: number }
  ) {
    const deletedCount = await this.communicationService.cleanupDeviceImages(
      deviceId, 
      body.retentionDays || 30
    );
    return { success: true, deletedCount, message: `Cleaned up ${deletedCount} old images` };
  }

  // SFTP server endpoints
  @Get('sftp/status')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Get SFTP server status' })
  @ApiResponse({ status: 200, description: 'SFTP server status' })
  async getSftpStatus() {
    return this.sftpService.getServerStatus();
  }

  @Get('sftp/transfers')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Get active SFTP transfers' })
  @ApiResponse({ status: 200, description: 'Active transfers listed' })
  async getActiveSftpTransfers() {
    return this.sftpService.getTransferStats();
  }

  @Post('sftp/create-device-directory')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Create device directory for SFTP uploads' })
  @ApiResponse({ status: 200, description: 'Device directory created' })
  async createDeviceDirectory(@Body() body: { deviceId: string }) {
    const devicePath = await this.sftpService.createDeviceDirectory(body.deviceId);
    return { success: true, devicePath, message: 'Device directory created' };
  }

  // Rsync endpoints
  @Post('rsync/sync')
  @Roles(UserRole.admin, UserRole.operator)
  @ApiOperation({ summary: 'Perform rsync synchronization' })
  @ApiResponse({ status: 200, description: 'Rsync operation completed' })
  async performRsync(
    @Body() body: { source: string; destination: string; options?: any }
  ) {
    const result = await this.communicationService.syncImagesWithRsync(
      body.source, 
      body.destination
    );
    return result;
  }

  // System health endpoint
  @Get('health')
  @ApiOperation({ summary: 'Get communication system health' })
  @ApiResponse({ status: 200, description: 'System health status' })
  async getHealth() {
    const healthy = this.communicationService.isHealthy();
    const status = await this.communicationService.getServiceStatus();
    
    return {
      healthy,
      status: healthy ? 'ok' : 'degraded',
      services: status,
      timestamp: new Date().toISOString(),
    };
  }
}