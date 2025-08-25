import { Injectable } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { AnalyticsEventService } from './analytics-event.service';
import { AnalyticsEventCategory } from '../../generated/prisma';

@Injectable()
export class RateLimitMonitoringService {
  constructor(
    private prisma: PrismaService,
    private analyticsEventService: AnalyticsEventService,
  ) {}

  async logRateLimitEvent(data: {
    ip: string;
    userId?: string;
    userRole: string;
    method: string;
    url: string;
    statusCode: number;
    duration: number;
    userAgent: string;
    rateLimitRemaining?: string;
    rateLimitReset?: string;
    isBlocked: boolean;
  }) {
    try {
      // Log to analytics events
      await this.analyticsEventService.create({
        eventType: data.isBlocked ? 'rate_limit_exceeded' : 'rate_limit_check',
        eventCategory: 'security',
        userId: data.userId,
        ipAddress: data.ip,
        userAgent: data.userAgent,
        eventData: {
          method: data.method,
          url: data.url,
          statusCode: data.statusCode,
          duration: data.duration,
          userRole: data.userRole,
          rateLimitRemaining: data.rateLimitRemaining,
          rateLimitReset: data.rateLimitReset,
          isBlocked: data.isBlocked,
          timestamp: new Date().toISOString(),
        },
      });
    } catch (error) {
      console.error('Failed to log rate limit event:', error);
    }
  }

  async getRateLimitStats(timeRange?: {
    startDate: Date;
    endDate: Date;
  }) {
    const whereClause = timeRange
      ? {
          createdAt: {
            gte: timeRange.startDate,
            lte: timeRange.endDate,
          },
          eventType: {
            in: ['rate_limit_exceeded', 'rate_limit_check'],
          },
        }
      : {
          eventType: {
            in: ['rate_limit_exceeded', 'rate_limit_check'],
          },
        };

    const events = await this.prisma.analyticsEvent.findMany({
      where: whereClause,
      select: {
        eventType: true,
        eventData: true,
        ipAddress: true,
        userAgent: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    const stats = {
      totalEvents: events.length,
      blockedRequests: events.filter(e => e.eventType === 'rate_limit_exceeded').length,
      allowedRequests: events.filter(e => e.eventType === 'rate_limit_check').length,
      topBlockedIPs: this.getTopIPs(events.filter(e => e.eventType === 'rate_limit_exceeded')),
      topBlockedEndpoints: this.getTopEndpoints(events.filter(e => e.eventType === 'rate_limit_exceeded')),
      eventsByHour: this.groupEventsByHour(events),
    };

    return stats;
  }

  private getTopIPs(events: any[]) {
    const ipCounts: Record<string, number> = {};
    events.forEach(event => {
      const ip = event.ipAddress || 'unknown';
      ipCounts[ip] = (ipCounts[ip] || 0) + 1;
    });

    return Object.entries(ipCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([ip, count]) => ({ ip, count }));
  }

  private getTopEndpoints(events: any[]) {
    const endpointCounts: Record<string, number> = {};
    events.forEach(event => {
      const eventData = event.eventData as any;
      const endpoint = eventData?.url || 'unknown';
      endpointCounts[endpoint] = (endpointCounts[endpoint] || 0) + 1;
    });

    return Object.entries(endpointCounts)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 10)
      .map(([endpoint, count]) => ({ endpoint, count }));
  }

  private groupEventsByHour(events: any[]) {
    const hourlyCounts: Record<string, number> = {};
    events.forEach(event => {
      const hour = new Date(event.createdAt).toISOString().slice(0, 13) + ':00:00Z';
      hourlyCounts[hour] = (hourlyCounts[hour] || 0) + 1;
    });

    return Object.entries(hourlyCounts)
      .sort(([a], [b]) => a.localeCompare(b))
      .map(([hour, count]) => ({ hour, count }));
  }

  async getRateLimitAlerts() {
    // Get recent rate limit exceeded events
    const recentBlockedEvents = await this.prisma.analyticsEvent.findMany({
      where: {
        eventType: 'rate_limit_exceeded',
        createdAt: {
          gte: new Date(Date.now() - 60 * 60 * 1000), // Last hour
        },
      },
      select: {
        ipAddress: true,
        eventData: true,
        createdAt: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    const alerts = [];

    // Check for suspicious patterns
    const ipCounts: Record<string, number> = {};
    recentBlockedEvents.forEach(event => {
      const ip = event.ipAddress || 'unknown';
      ipCounts[ip] = (ipCounts[ip] || 0) + 1;
    });

    // Alert for IPs with many blocked requests
    Object.entries(ipCounts).forEach(([ip, count]) => {
      if (count >= 10) {
        alerts.push({
          type: 'high_blocked_requests',
          severity: 'warning',
          message: `IP ${ip} has ${count} blocked requests in the last hour`,
          ip,
          count,
          timestamp: new Date().toISOString(),
        });
      }
    });

    return alerts;
  }
}
