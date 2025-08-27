import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { MqttService } from './mqtt/mqtt.service';
import { SftpService } from './sftp/sftp.service';
import { ImageStorageService } from './storage/image-storage.service';
import { UnifiedCommunicationService } from './unified-communication.service';

@Module({
  imports: [ConfigModule],
  providers: [
    MqttService,
    SftpService,
    ImageStorageService,
    UnifiedCommunicationService,
  ],
  exports: [
    MqttService,
    SftpService,
    ImageStorageService,
    UnifiedCommunicationService,
  ],
})
export class CommunicationModule {}