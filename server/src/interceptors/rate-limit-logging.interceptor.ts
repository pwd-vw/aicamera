import { Injectable, NestInterceptor, ExecutionContext, CallHandler } from '@nestjs/common';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class RateLimitLoggingInterceptor implements NestInterceptor {
  intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
    const request = context.switchToHttp().getRequest();
    const response = context.switchToHttp().getResponse();
    const user = request.user;
    const ip = request.ip || request.connection.remoteAddress;
    const url = request.url;
    const method = request.method;
    const userAgent = request.headers['user-agent'];

    const startTime = Date.now();

    return next.handle().pipe(
      tap(() => {
        const duration = Date.now() - startTime;
        const statusCode = response.statusCode;
        
        // Log rate limiting information
        this.logRateLimitInfo({
          timestamp: new Date().toISOString(),
          ip,
          userId: user?.id || 'anonymous',
          userRole: user?.role || 'anonymous',
          method,
          url,
          statusCode,
          duration,
          userAgent,
          rateLimitRemaining: response.headers['x-ratelimit-remaining'],
          rateLimitReset: response.headers['x-ratelimit-reset'],
        });
      }),
    );
  }

  private logRateLimitInfo(info: {
    timestamp: string;
    ip: string;
    userId: string;
    userRole: string;
    method: string;
    url: string;
    statusCode: number;
    duration: number;
    userAgent: string;
    rateLimitRemaining: string;
    rateLimitReset: string;
  }) {
    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Rate Limit] ${info.method} ${info.url} - ${info.statusCode} - ${info.duration}ms - User: ${info.userRole} (${info.userId}) - IP: ${info.ip}`);
    }

    // TODO: In production, send to logging service or database
    // This could be sent to a monitoring service like DataDog, New Relic, or stored in the database
  }
}
