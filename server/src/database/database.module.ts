import { Module } from '@nestjs/common';
import { PrismaService } from './prisma.service';
import { VisualizationService } from '../services/visualization.service';
import { AnalyticsEventService } from '../services/analytics-event.service';
import { UserService } from '../services/user.service';
import { RateLimitMonitoringService } from '../services/rate-limit-monitoring.service';
import { VisualizationController } from '../controllers/visualization.controller';
import { AnalyticsEventController } from '../controllers/analytics-event.controller';
import { UserController } from '../controllers/user.controller';
import { RateLimitMonitoringController } from '../controllers/rate-limit-monitoring.controller';

@Module({
  providers: [
    PrismaService,
    VisualizationService,
    AnalyticsEventService,
    UserService,
    RateLimitMonitoringService,
  ],
  controllers: [
    VisualizationController,
    AnalyticsEventController,
    UserController,
    RateLimitMonitoringController,
  ],
  exports: [
    PrismaService,
    VisualizationService,
    AnalyticsEventService,
    UserService,
    RateLimitMonitoringService,
  ],
})
export class DatabaseModule {}
