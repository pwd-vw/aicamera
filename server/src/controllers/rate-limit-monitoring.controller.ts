import { Controller, Get, Query, UseGuards } from '@nestjs/common';
import { RateLimitMonitoringService } from '../services/rate-limit-monitoring.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { RateLimitApiRead } from '../decorators/rate-limit.decorators';
import { UserRole } from '../../generated/prisma';

@Controller('rate-limit-monitoring')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(UserRole.admin)
export class RateLimitMonitoringController {
  constructor(private readonly rateLimitMonitoringService: RateLimitMonitoringService) {}

  @Get('stats')
  @RateLimitApiRead()
  async getRateLimitStats(
    @Query('startDate') startDate?: string,
    @Query('endDate') endDate?: string,
  ) {
    const timeRange = startDate && endDate
      ? {
          startDate: new Date(startDate),
          endDate: new Date(endDate),
        }
      : undefined;

    return this.rateLimitMonitoringService.getRateLimitStats(timeRange);
  }

  @Get('alerts')
  @RateLimitApiRead()
  async getRateLimitAlerts() {
    return this.rateLimitMonitoringService.getRateLimitAlerts();
  }

  @Get('recent-events')
  @RateLimitApiRead()
  async getRecentEvents() {
    // This would typically fetch recent rate limit events
    // For now, return a placeholder
    return {
      message: 'Recent rate limit events endpoint',
      note: 'This endpoint would return recent rate limiting events for monitoring',
    };
  }
}
