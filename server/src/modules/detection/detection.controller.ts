import { Body, Controller, Get, Param, Post, Query } from '@nestjs/common';
import { CreateDetectionDto, DetectionQueryDto } from '../../dto/detection.dto';

@Controller('detection')
export class DetectionController {
  @Post()
  create(@Body() detectionData: CreateDetectionDto) {
    return {
      message: 'Detection data received successfully',
      id: 'temp-id-' + Date.now(),
      received: detectionData,
    };
  }

  @Get()
  list(@Query() _query: DetectionQueryDto) {
    const mockData = [
      {
        id: '1',
        camera_id: 'cam-001',
        timestamp: new Date().toISOString(),
        license_plate: 'ABC123',
        confidence: 0.95,
        image_url: 'https://example.com/image1.jpg',
      },
    ];
    return {
      data: mockData,
      pagination: { limit: 50, offset: 0, total: mockData.length },
    };
  }

  @Get(':id')
  getById(@Param('id') id: string) {
    const mockData = {
      id,
      camera_id: 'cam-001',
      timestamp: new Date().toISOString(),
      license_plate: 'ABC123',
      confidence: 0.95,
      image_url: 'https://example.com/image1.jpg',
    };
    return mockData;
  }
}

