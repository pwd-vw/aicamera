import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MqttEventsController } from './mqtt-events.controller';
import { MqttEventsService } from './mqtt-events.service';

@Module({
  imports: [],
  controllers: [AppController, MqttEventsController],
  providers: [AppService, MqttEventsService],
})
export class AppModule {}
