import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AnalyticsEvent, AnalyticsEventCategory } from '../../generated/prisma';

@Injectable()
export class AnalyticsEventService {
  constructor(private prisma: PrismaService) {}

  async create(data: {
    eventType: string;
    eventCategory: AnalyticsEventCategory;
    userId?: string;
    sessionId?: string;
    cameraId?: string;
    visualizationId?: string;
    eventData?: any;
    ipAddress?: string;
    userAgent?: string;
  }): Promise<AnalyticsEvent> {
    return this.prisma.analyticsEvent.create({
      data: {
        eventType: data.eventType,
        eventCategory: data.eventCategory,
        userId: data.userId,
        sessionId: data.sessionId,
        cameraId: data.cameraId,
        visualizationId: data.visualizationId,
        eventData: data.eventData || {},
        ipAddress: data.ipAddress,
        userAgent: data.userAgent,
      },
    });
  }

  async findAll(where?: {
    eventType?: string;
    eventCategory?: AnalyticsEventCategory;
    userId?: string;
    cameraId?: string;
    visualizationId?: string;
  }): Promise<AnalyticsEvent[]> {
    return this.prisma.analyticsEvent.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async findById(id: string): Promise<AnalyticsEvent | null> {
    return this.prisma.analyticsEvent.findUnique({
      where: { id },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async findByCategory(category: AnalyticsEventCategory): Promise<AnalyticsEvent[]> {
    return this.prisma.analyticsEvent.findMany({
      where: { eventCategory: category },
      orderBy: { createdAt: 'desc' },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async findByUser(userId: string): Promise<AnalyticsEvent[]> {
    return this.prisma.analyticsEvent.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async findByCamera(cameraId: string): Promise<AnalyticsEvent[]> {
    return this.prisma.analyticsEvent.findMany({
      where: { cameraId },
      orderBy: { createdAt: 'desc' },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async findByVisualization(visualizationId: string): Promise<AnalyticsEvent[]> {
    return this.prisma.analyticsEvent.findMany({
      where: { visualizationId },
      orderBy: { createdAt: 'desc' },
      include: {
        camera: true,
        visualization: true,
      },
    });
  }

  async getEventStats(timeRange?: {
    startDate: Date;
    endDate: Date;
  }): Promise<{
    totalEvents: number;
    eventsByCategory: Record<AnalyticsEventCategory, number>;
    eventsByType: Record<string, number>;
  }> {
    const whereClause = timeRange
      ? {
          createdAt: {
            gte: timeRange.startDate,
            lte: timeRange.endDate,
          },
        }
      : {};

    const events = await this.prisma.analyticsEvent.findMany({
      where: whereClause,
      select: {
        eventCategory: true,
        eventType: true,
      },
    });

    const totalEvents = events.length;
    const eventsByCategory: Record<AnalyticsEventCategory, number> = {
      user_interaction: 0,
      system_event: 0,
      performance: 0,
      error: 0,
      security: 0,
    };
    const eventsByType: Record<string, number> = {};

    events.forEach((event) => {
      eventsByCategory[event.eventCategory]++;
      eventsByType[event.eventType] = (eventsByType[event.eventType] || 0) + 1;
    });

    return {
      totalEvents,
      eventsByCategory,
      eventsByType,
    };
  }

  async deleteOldEvents(olderThan: Date): Promise<number> {
    const result = await this.prisma.analyticsEvent.deleteMany({
      where: {
        createdAt: {
          lt: olderThan,
        },
      },
    });
    return result.count;
  }
}
