import { Module } from '@nestjs/common';
import { ThrottlerModule } from '@nestjs/throttler';
import { rateLimitConfig } from '../config/rate-limit.config';
import { CustomRateLimitGuard } from '../guards/rate-limit.guard';

@Module({
  imports: [
    ThrottlerModule.forRoot(rateLimitConfig),
  ] as any,
  providers: [
    CustomRateLimitGuard,
  ],
  exports: [
    CustomRateLimitGuard,
  ],
})
export class RateLimitModule {}
