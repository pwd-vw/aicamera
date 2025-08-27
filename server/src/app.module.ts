import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { CommunicationModule } from './communication/communication.module';
import { SystemModule } from './system/system.module';
import { AuthModule } from './auth/auth.module';
import { DeviceRegistrationModule } from './device-registration/device-registration.module';
import { DeviceService } from './device/device.service';
import { SftpService } from './sftp/sftp.service';

const GlobalConfigModule = ConfigModule.forRoot({ isGlobal: true }) as unknown as import('@nestjs/common').DynamicModule;

@Module({
  imports: [GlobalConfigModule, CommunicationModule, SystemModule, AuthModule, DeviceRegistrationModule],
  controllers: [],
  providers: [DeviceService, SftpService],
})
export class AppModule {}
