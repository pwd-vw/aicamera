import { Module } from '@nestjs/common';
import { JwtModule } from '@nestjs/jwt';
import { DeviceRegistrationController } from './device-registration.controller';
import { DeviceRegistrationService } from './device-registration.service';
import { DeviceApiKeyGuard } from './guards/device-api-key.guard';
import { PrismaService } from '../database/prisma.service';

@Module({
  imports: [
    JwtModule.register({
      secret: process.env.JWT_SECRET || 'your-secret-key',
      signOptions: { expiresIn: '1h' },
    }),
  ],
  controllers: [DeviceRegistrationController],
  providers: [
    DeviceRegistrationService,
    DeviceApiKeyGuard,
    PrismaService,
  ],
  exports: [DeviceRegistrationService],
})
export class DeviceRegistrationModule {}