import {
  Controller,
  Get,
  Post,
  Put,
  Delete,
  Body,
  Param,
  Query,
  ParseUUIDPipe,
} from '@nestjs/common';
import { DeviceService } from './device.service';
import { Camera, Detection, CameraHealth } from '../entities';

@Controller()
export class DeviceController {
  constructor(private readonly deviceService: DeviceService) {}

  @Get('cameras')
  async getCameras() {
    return this.deviceService.findAllCameras();
  }

  @Get('cameras/summary')
  async getCameraSummary() {
    return this.deviceService.getCameraSummary();
  }

  @Get('cameras/analytics/run')
  async runDailyAnalytics() {
    await this.deviceService.runUpdateDailyAnalytics();
    return { ok: true };
  }

  @Get('cameras/:id')
  async getCamera(@Param('id', ParseUUIDPipe) id: string) {
    const camera = await this.deviceService.findCameraById(id);
    if (!camera) return { error: 'Not found' };
    return camera;
  }

  @Post('cameras')
  async createCamera(@Body() body: Partial<Camera>) {
    return this.deviceService.createCamera(body);
  }

  @Put('cameras/:id')
  async updateCamera(
    @Param('id', ParseUUIDPipe) id: string,
    @Body() body: Partial<Camera>,
  ) {
    return this.deviceService.updateCamera(id, body);
  }

  @Delete('cameras/:id')
  async deleteCamera(@Param('id', ParseUUIDPipe) id: string) {
    await this.deviceService.deleteCamera(id);
    return { ok: true };
  }

  @Get('detections')
  async getDetections(@Query('cameraId') cameraId?: string, @Query('limit') limit?: string) {
    return this.deviceService.findAllDetections(
      cameraId,
      limit ? parseInt(limit, 10) : 100,
    );
  }

  @Get('cameras/:id/detections')
  async getDetectionsByCamera(
    @Param('id', ParseUUIDPipe) id: string,
    @Query('limit') limit?: string,
  ) {
    return this.deviceService.findDetectionsByCameraId(
      id,
      limit ? parseInt(limit, 10) : 100,
    );
  }

  @Post('detections')
  async createDetection(@Body() body: Partial<Detection>) {
    return this.deviceService.createDetection(body);
  }

  @Get('camera-health')
  async getCameraHealth(
    @Query('cameraId') cameraId?: string,
    @Query('limit') limit?: string,
  ) {
    return this.deviceService.findAllCameraHealth(
      cameraId,
      limit ? parseInt(limit, 10) : 200,
    );
  }

  @Post('camera-health')
  async createCameraHealth(@Body() body: Partial<CameraHealth>) {
    return this.deviceService.createCameraHealth(body);
  }
}
