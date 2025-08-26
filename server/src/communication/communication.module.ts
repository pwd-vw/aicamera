import { Module } from '@nestjs/common';
import { EventsGateway } from '../events/events.gateway';
import { CommunicationOrchestratorService } from './communication-orchestrator.service';
import { CommunicationController } from './communication.controller';
import { WebSocketProtocol } from './protocols/websocket.protocol';
// import { RestProtocol } from './protocols/rest.protocol';
// import { MqttProtocol } from './protocols/mqtt.protocol';

@Module({
  providers: [EventsGateway],
  exports: [EventsGateway],
})
export class EventsModule {}

@Module({
  imports: [EventsModule],
  controllers: [CommunicationController],
  providers: [
    CommunicationOrchestratorService,
    WebSocketProtocol,
    // RestProtocol,
    // MqttProtocol,
  ],
  exports: [CommunicationOrchestratorService],
})
export class CommunicationModule {}
