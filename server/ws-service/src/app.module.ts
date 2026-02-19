import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { EventsGateway } from './events.gateway';
import { StorageService } from './storage.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService, EventsGateway, StorageService],
})
export class AppModule {}
