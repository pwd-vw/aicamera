import { ThrottlerModuleOptions } from '@nestjs/throttler';

export const rateLimitConfig: ThrottlerModuleOptions = {
  throttlers: [
    // Global default limits
    {
      ttl: 60000, // 1 minute
      limit: 100, // 100 requests per minute
    },
  ],
  ignoreUserAgents: [
    // Ignore health check requests
    /health-check/i,
    // Ignore monitoring requests
    /monitoring/i,
  ],
  storage: undefined, // Use in-memory storage (can be changed to Redis for production)
};

// Rate limit constants for different user roles
export const RATE_LIMITS = {
  // Anonymous users (no authentication)
  ANONYMOUS: {
    LOGIN: { ttl: 60000, limit: 3 }, // 3 login attempts per minute
    REGISTER: { ttl: 300000, limit: 1 }, // 1 registration per 5 minutes
    API: { ttl: 60000, limit: 10 }, // 10 API calls per minute
    UPLOAD: { ttl: 60000, limit: 2 }, // 2 uploads per minute
  },
  // Authenticated users
  AUTHENTICATED: {
    API: { ttl: 60000, limit: 100 }, // 100 API calls per minute
    UPLOAD: { ttl: 60000, limit: 20 }, // 20 uploads per minute
    EXPORT: { ttl: 300000, limit: 5 }, // 5 exports per 5 minutes
  },
  // Admin users (higher limits)
  ADMIN: {
    API: { ttl: 60000, limit: 500 }, // 500 API calls per minute
    UPLOAD: { ttl: 60000, limit: 100 }, // 100 uploads per minute
    EXPORT: { ttl: 60000, limit: 20 }, // 20 exports per minute
    USER_MANAGEMENT: { ttl: 60000, limit: 50 }, // 50 user operations per minute
  },
};

// Rate limit decorators for different endpoints
export const RATE_LIMIT_DECORATORS = {
  // Authentication endpoints
  AUTH_LOGIN: { ttl: 60000, limit: 3 },
  AUTH_REGISTER: { ttl: 300000, limit: 1 },
  AUTH_REFRESH: { ttl: 60000, limit: 10 },
  
  // API endpoints
  API_READ: { ttl: 60000, limit: 100 },
  API_WRITE: { ttl: 60000, limit: 30 },
  API_DELETE: { ttl: 60000, limit: 10 },
  
  // File operations
  FILE_UPLOAD: { ttl: 60000, limit: 10 },
  FILE_DOWNLOAD: { ttl: 60000, limit: 50 },
  
  // Admin operations
  ADMIN_OPERATIONS: { ttl: 60000, limit: 50 },
  USER_MANAGEMENT: { ttl: 60000, limit: 20 },
  
  // Analytics and reporting
  ANALYTICS: { ttl: 60000, limit: 30 },
  EXPORT: { ttl: 300000, limit: 5 },
};
