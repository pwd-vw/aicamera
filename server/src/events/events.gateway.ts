import { 
  SubscribeMessage, 
  WebSocketGateway, 
  WebSocketServer,
} from '@nestjs/websockets';
import { Server } from 'socket.io';
import { Socket } from 'socket.io';

@WebSocketGateway()
export class EventsGateway {
  @WebSocketServer()
  server: Server;

  @SubscribeMessage('detection')
  handleDetection(_client: Socket, payload: any): string {
    this.server.emit('detection', payload);
    return 'Detection received!';
  }
}