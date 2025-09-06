import { Controller, Get, Query } from '@nestjs/common';

@Controller('analytics')
export class AnalyticsController {
  @Get('summary')
  getSummary(@Query() query: any) {
    const { start_date, end_date } = query;
    const mockSummary = {
      total_detections: 1250,
      unique_plates: 342,
      detection_rate: 0.85,
      average_confidence: 0.92,
      top_cameras: [
        { camera_id: 'cam-001', detections: 450 },
        { camera_id: 'cam-002', detections: 380 },
        { camera_id: 'cam-003', detections: 420 },
      ],
      time_period: {
        start: start_date || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: end_date || new Date().toISOString(),
      },
    };
    return mockSummary;
  }

  @Get('trends')
  getTrends(@Query('period') period = 'daily', @Query() query: any) {
    const { start_date, end_date } = query;
    const mockTrends = [
      { date: '2024-01-01', detections: 45, unique_plates: 23 },
      { date: '2024-01-02', detections: 52, unique_plates: 28 },
      { date: '2024-01-03', detections: 38, unique_plates: 19 },
      { date: '2024-01-04', detections: 61, unique_plates: 31 },
      { date: '2024-01-05', detections: 48, unique_plates: 25 },
    ];
    return {
      period,
      trends: mockTrends,
      time_period: {
        start: start_date || new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
        end: end_date || new Date().toISOString(),
      },
    };
  }

  @Get('plates')
  getPlates(@Query('limit') limit = 20, @Query('offset') offset = 0, @Query('sort') _sort = 'frequency') {
    const mockPlates = [
      { license_plate: 'ABC123', frequency: 15, first_seen: '2024-01-01', last_seen: '2024-01-05' },
      { license_plate: 'XYZ789', frequency: 12, first_seen: '2024-01-02', last_seen: '2024-01-05' },
      { license_plate: 'DEF456', frequency: 8, first_seen: '2024-01-01', last_seen: '2024-01-04' },
    ];
    return {
      data: mockPlates,
      pagination: {
        limit: Number(limit),
        offset: Number(offset),
        total: mockPlates.length,
      },
    };
  }

  @Get('cameras')
  getCameras() {
    const mockCameraAnalytics = [
      {
        camera_id: 'cam-001',
        name: 'Main Entrance',
        total_detections: 450,
        unique_plates: 120,
        detection_rate: 0.88,
        average_confidence: 0.94,
        uptime_percentage: 99.5,
        last_activity: new Date().toISOString(),
      },
      {
        camera_id: 'cam-002',
        name: 'Side Entrance',
        total_detections: 380,
        unique_plates: 95,
        detection_rate: 0.82,
        average_confidence: 0.91,
        uptime_percentage: 98.8,
        last_activity: new Date().toISOString(),
      },
    ];
    return { data: mockCameraAnalytics };
  }
}

