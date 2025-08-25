import { Module } from '@nestjs/common';
import { CommunicationOrchestratorService } from './communication-orchestrator.service';
import { CommunicationController } from './communication.controller';
import { WebSocketProtocol } from './protocols/websocket.protocol';
import { RestProtocol } from './protocols/rest.protocol';
import { MqttProtocol } from './protocols/mqtt.protocol';

@Module({
  controllers: [CommunicationController],
  providers: [
    CommunicationOrchestratorService,
    WebSocketProtocol,
    RestProtocol,
    MqttProtocol,
  ],
  exports: [CommunicationOrchestratorService],
})
export class CommunicationModule {}
