import { SetMetadata } from '@nestjs/common';
import { RATE_LIMIT_DECORATORS } from '../config/rate-limit.config';

export const RATE_LIMIT_KEY = 'rateLimit';

export interface RateLimitOptions {
  ttl: number;
  limit: number;
  skipIf?: (req: any) => boolean;
}

// Authentication rate limit decorators
export const RateLimitAuthLogin = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.AUTH_LOGIN);

export const RateLimitAuthRegister = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.AUTH_REGISTER);

export const RateLimitAuthRefresh = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.AUTH_REFRESH);

// API rate limit decorators
export const RateLimitApiRead = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.API_READ);

export const RateLimitApiWrite = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.API_WRITE);

export const RateLimitApiDelete = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.API_DELETE);

// File operation rate limit decorators
export const RateLimitFileUpload = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.FILE_UPLOAD);

export const RateLimitFileDownload = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.FILE_DOWNLOAD);

// Admin operation rate limit decorators
export const RateLimitAdminOperations = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.ADMIN_OPERATIONS);

export const RateLimitUserManagement = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.USER_MANAGEMENT);

// Analytics and export rate limit decorators
export const RateLimitAnalytics = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.ANALYTICS);

export const RateLimitExport = () => 
  SetMetadata(RATE_LIMIT_KEY, RATE_LIMIT_DECORATORS.EXPORT);

// Custom rate limit decorator
export const RateLimit = (options: RateLimitOptions) => 
  SetMetadata(RATE_LIMIT_KEY, options);

// Skip rate limiting decorator
export const SkipRateLimit = () => 
  SetMetadata(RATE_LIMIT_KEY, { skip: true });
