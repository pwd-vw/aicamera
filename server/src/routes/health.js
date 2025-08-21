const express = require('express');
const router = express.Router();
const logger = require('../utils/logger');
const { testConnection } = require('../database/connection');

/**
 * GET /api/v1/health
 * Basic health check
 */
router.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'aicamera-server',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: process.env.npm_package_version || '1.0.0'
  });
});

/**
 * GET /api/v1/health/detailed
 * Detailed health check with dependencies
 */
router.get('/detailed', async (req, res) => {
  try {
    const healthChecks = {
      server: {
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        cpu: process.cpuUsage()
      },
      database: {
        status: 'unknown'
      },
      redis: {
        status: 'unknown'
      }
    };

    // Check database connection
    try {
      const dbHealthy = await testConnection();
      healthChecks.database.status = dbHealthy ? 'healthy' : 'unhealthy';
    } catch (error) {
      healthChecks.database.status = 'unhealthy';
      healthChecks.database.error = error.message;
    }

    // Check Redis connection (if configured)
    if (process.env.REDIS_URL) {
      try {
        const Redis = require('redis');
        const redis = Redis.createClient({ url: process.env.REDIS_URL });
        await redis.connect();
        await redis.ping();
        await redis.disconnect();
        healthChecks.redis.status = 'healthy';
      } catch (error) {
        healthChecks.redis.status = 'unhealthy';
        healthChecks.redis.error = error.message;
      }
    }

    // Determine overall status
    const overallStatus = Object.values(healthChecks).every(check => 
      check.status === 'healthy' || check.status === 'unknown'
    ) ? 'healthy' : 'degraded';

    res.json({
      status: overallStatus,
      service: 'aicamera-server',
      timestamp: new Date().toISOString(),
      checks: healthChecks
    });
  } catch (error) {
    logger.error('Error in detailed health check:', error);
    res.status(500).json({
      status: 'unhealthy',
      service: 'aicamera-server',
      error: 'Health check failed',
      timestamp: new Date().toISOString()
    });
  }
});

/**
 * GET /api/v1/health/ready
 * Readiness probe for Kubernetes
 */
router.get('/ready', async (req, res) => {
  try {
    // Check if database is ready
    const dbHealthy = await testConnection();
    
    if (!dbHealthy) {
      return res.status(503).json({
        status: 'not ready',
        reason: 'Database connection failed'
      });
    }

    res.json({
      status: 'ready',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    logger.error('Readiness check failed:', error);
    res.status(503).json({
      status: 'not ready',
      reason: 'Service not ready',
      error: error.message
    });
  }
});

/**
 * GET /api/v1/health/live
 * Liveness probe for Kubernetes
 */
router.get('/live', (req, res) => {
  res.json({
    status: 'alive',
    timestamp: new Date().toISOString(),
    uptime: process.uptime()
  });
});

module.exports = router;
