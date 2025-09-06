import { Body, Controller, Delete, Get, Param, Post, Put, Query } from '@nestjs/common';
import { CameraConfigDto, CreateCameraDto, UpdateCameraDto } from '../../dto/camera.dto';

@Controller('camera')
export class CameraController {
  @Post()
  create(@Body() cameraData: CreateCameraDto) {
    const mockCamera = {
      id: 'cam-' + Date.now(),
      ...cameraData,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return {
      message: 'Camera registered successfully',
      data: mockCamera,
    };
  }

  @Get()
  list(@Query('status') _status?: string, @Query('limit') limit = 50, @Query('offset') offset = 0) {
    const mockCameras = [
      {
        id: 'cam-001',
        name: 'Main Entrance Camera',
        location: {
          latitude: 40.7128,
          longitude: -74.0060,
          address: '123 Main St, New York, NY',
        },
        status: 'active',
        configuration: {
          detection_enabled: true,
          image_quality: 'high',
          upload_interval: 30,
        },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];
    return {
      data: mockCameras,
      pagination: { limit: Number(limit), offset: Number(offset), total: mockCameras.length },
    };
  }

  @Get(':id')
  getById(@Param('id') id: string) {
    const mockCamera = {
      id,
      name: 'Main Entrance Camera',
      location: {
        latitude: 40.7128,
        longitude: -74.0060,
        address: '123 Main St, New York, NY',
      },
      status: 'active',
      configuration: {
        detection_enabled: true,
        image_quality: 'high',
        upload_interval: 30,
      },
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    };
    return mockCamera;
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() updateData: UpdateCameraDto | CameraConfigDto) {
    const mockUpdatedCamera = {
      id,
      ...updateData,
      updated_at: new Date().toISOString(),
    };
    return {
      message: 'Camera updated successfully',
      data: mockUpdatedCamera,
    };
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    return { message: 'Camera deactivated successfully', id };
  }
}

