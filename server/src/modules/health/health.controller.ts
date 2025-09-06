import { Controller, Get, HttpException, HttpStatus } from '@nestjs/common';
import { PrismaService } from '../../database/prisma.service';

@Controller('health')
export class HealthController {
  constructor(private readonly prisma: PrismaService) {}

  @Get()
  async basicHealth() {
    return {
      status: 'healthy',
      service: 'aicamera-server',
      version: process.env.npm_package_version || '1.0.0',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
    };
  }

  @Get('detailed')
  async detailedHealth() {
    const healthChecks: any = {
      server: {
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
      },
      database: { status: 'unknown' },
      redis: { status: process.env.REDIS_URL ? 'unknown' : 'not_configured' },
    };

    try {
      await (this.prisma as any).$queryRaw`SELECT 1`;
      healthChecks.database.status = 'healthy';
    } catch (error) {
      healthChecks.database.status = 'unhealthy';
      healthChecks.database.error = error instanceof Error ? error.message : 'Unknown error';
    }

    const overallStatus = Object.values(healthChecks).every((check: any) =>
      check.status === 'healthy' || check.status === 'unknown' || check.status === 'not_configured',
    ) ? 'healthy' : 'degraded';

    return {
      status: overallStatus,
      service: 'aicamera-server',
      timestamp: new Date().toISOString(),
      checks: healthChecks,
    };
  }

  @Get('ready')
  async readiness() {
    try {
      await (this.prisma as any).$queryRaw`SELECT 1`;
      return { status: 'ready', timestamp: new Date().toISOString() };
    } catch (error) {
      throw new HttpException({ status: 'not ready', reason: 'Database connection failed' }, HttpStatus.SERVICE_UNAVAILABLE);
    }
  }

  @Get('live')
  liveness() {
    return { status: 'alive', timestamp: new Date().toISOString(), uptime: process.uptime() };
  }
}

