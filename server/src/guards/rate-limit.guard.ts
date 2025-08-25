import { Injectable, ExecutionContext } from '@nestjs/common';
import { ThrottlerGuard } from '@nestjs/throttler';
import { RATE_LIMITS } from '../config/rate-limit.config';

@Injectable()
export class CustomRateLimitGuard extends ThrottlerGuard {
  protected getThrottleOptions(context: ExecutionContext) {
    const request = context.switchToHttp().getRequest();
    const user = request.user; // From JWT authentication
    const url = request.url;
    const method = request.method;

    // Get user role (default to anonymous if not authenticated)
    const userRole = user?.role || 'anonymous';
    
    // Determine the appropriate rate limit based on endpoint and user role
    let limit = 100; // Default limit
    let ttl = 60000; // Default TTL (1 minute)

    // Authentication endpoints
    if (url.includes('/auth/login')) {
      if (userRole === 'anonymous') {
        limit = RATE_LIMITS.ANONYMOUS.LOGIN.limit;
        ttl = RATE_LIMITS.ANONYMOUS.LOGIN.ttl;
      } else {
        limit = 10; // Higher limit for authenticated users
        ttl = 60000;
      }
    } else if (url.includes('/auth/register')) {
      limit = RATE_LIMITS.ANONYMOUS.REGISTER.limit;
      ttl = RATE_LIMITS.ANONYMOUS.REGISTER.ttl;
    } else if (url.includes('/auth/refresh')) {
      limit = 10;
      ttl = 60000;
    }
    // File upload endpoints
    else if (url.includes('/upload') || url.includes('/images')) {
      if (userRole === 'admin') {
        limit = RATE_LIMITS.ADMIN.UPLOAD.limit;
        ttl = RATE_LIMITS.ADMIN.UPLOAD.ttl;
      } else if (userRole === 'anonymous') {
        limit = RATE_LIMITS.ANONYMOUS.UPLOAD.limit;
        ttl = RATE_LIMITS.ANONYMOUS.UPLOAD.ttl;
      } else {
        limit = RATE_LIMITS.AUTHENTICATED.UPLOAD.limit;
        ttl = RATE_LIMITS.AUTHENTICATED.UPLOAD.ttl;
      }
    }
    // User management endpoints (admin only)
    else if (url.includes('/users') && method !== 'GET') {
      if (userRole === 'admin') {
        limit = RATE_LIMITS.ADMIN.USER_MANAGEMENT.limit;
        ttl = RATE_LIMITS.ADMIN.USER_MANAGEMENT.ttl;
      } else {
        limit = 0; // Block non-admin users
        ttl = 60000;
      }
    }
    // Export endpoints
    else if (url.includes('/export')) {
      if (userRole === 'admin') {
        limit = RATE_LIMITS.ADMIN.EXPORT.limit;
        ttl = RATE_LIMITS.ADMIN.EXPORT.ttl;
      } else if (userRole === 'anonymous') {
        limit = 0; // Block anonymous users
        ttl = 60000;
      } else {
        limit = RATE_LIMITS.AUTHENTICATED.EXPORT.limit;
        ttl = RATE_LIMITS.AUTHENTICATED.EXPORT.ttl;
      }
    }
    // General API endpoints
    else {
      if (userRole === 'admin') {
        limit = RATE_LIMITS.ADMIN.API.limit;
        ttl = RATE_LIMITS.ADMIN.API.ttl;
      } else if (userRole === 'anonymous') {
        limit = RATE_LIMITS.ANONYMOUS.API.limit;
        ttl = RATE_LIMITS.ANONYMOUS.API.ttl;
      } else {
        limit = RATE_LIMITS.AUTHENTICATED.API.limit;
        ttl = RATE_LIMITS.AUTHENTICATED.API.ttl;
      }
    }

    return {
      limit,
      ttl,
    };
  }

  protected async getTracker(req: Record<string, any>): Promise<string> {
    // Use IP address and user ID (if authenticated) as tracker
    const ip = req.ip || req.connection.remoteAddress;
    const userId = req.user?.id || 'anonymous';
    return `${ip}-${userId}`;
  }
}
