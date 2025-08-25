import { Controller, Get, Post, Body, Param, Query } from '@nestjs/common';
import { AnalyticsEventService } from '../services/analytics-event.service';
import { AnalyticsEventCategory } from '../../generated/prisma';

@Controller('analytics-events')
export class AnalyticsEventController {
  constructor(private readonly analyticsEventService: AnalyticsEventService) {}

  @Post()
  async create(@Body() data: {
    eventType: string;
    eventCategory: AnalyticsEventCategory;
    userId?: string;
    sessionId?: string;
    cameraId?: string;
    visualizationId?: string;
    eventData?: any;
    ipAddress?: string;
    userAgent?: string;
  }) {
    return this.analyticsEventService.create(data);
  }

  @Get()
  async findAll(
    @Query('eventType') eventType?: string,
    @Query('eventCategory') eventCategory?: AnalyticsEventCategory,
    @Query('userId') userId?: string,
    @Query('cameraId') cameraId?: string,
    @Query('visualizationId') visualizationId?: string,
  ) {
    const where: any = {};
    if (eventType) where.eventType = eventType;
    if (eventCategory) where.eventCategory = eventCategory;
    if (userId) where.userId = userId;
    if (cameraId) where.cameraId = cameraId;
    if (visualizationId) where.visualizationId = visualizationId;
    
    return this.analyticsEventService.findAll(where);
  }

  @Get('stats')
  async getEventStats(
    @Query('startDate') startDate?: string,
    @Query('endDate') endDate?: string,
  ) {
    const timeRange = startDate && endDate
      ? {
          startDate: new Date(startDate),
          endDate: new Date(endDate),
        }
      : undefined;
    
    return this.analyticsEventService.getEventStats(timeRange);
  }

  @Get('category/:category')
  async findByCategory(@Param('category') category: AnalyticsEventCategory) {
    return this.analyticsEventService.findByCategory(category);
  }

  @Get('user/:userId')
  async findByUser(@Param('userId') userId: string) {
    return this.analyticsEventService.findByUser(userId);
  }

  @Get('camera/:cameraId')
  async findByCamera(@Param('cameraId') cameraId: string) {
    return this.analyticsEventService.findByCamera(cameraId);
  }

  @Get('visualization/:visualizationId')
  async findByVisualization(@Param('visualizationId') visualizationId: string) {
    return this.analyticsEventService.findByVisualization(visualizationId);
  }

  @Get(':id')
  async findById(@Param('id') id: string) {
    return this.analyticsEventService.findById(id);
  }
}
