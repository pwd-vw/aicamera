import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { DeviceController } from './device.controller';
import { DeviceService } from './device.service';
import {
  Camera,
  Detection,
  Analytics,
  CameraHealth,
  SystemEvent,
  Visualization,
  AnalyticsEvent,
} from '../entities';

@Module({
  imports: [
    TypeOrmModule.forFeature([
      Camera,
      Detection,
      Analytics,
      CameraHealth,
      SystemEvent,
      Visualization,
      AnalyticsEvent,
    ]),
  ],
  controllers: [DeviceController],
  providers: [DeviceService],
})
export class DeviceModule {}
