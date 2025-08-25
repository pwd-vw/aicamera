import { Module } from '@nestjs/common';
import { EventsGateway } from './events/events.gateway';
import { CommunicationModule } from './communication/communication.module';
import { DeviceService } from './device/device.service';
import { SftpService } from './sftp/sftp.service';

@Module({
  imports: [CommunicationModule],
  controllers: [],
  providers: [EventsGateway, DeviceService, SftpService],
})
export class AppModule {}
