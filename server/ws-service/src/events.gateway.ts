import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
} from '@nestjs/websockets';
import { Server } from 'socket.io';
import { Logger } from '@nestjs/common';
import { StorageService } from './storage.service';

@WebSocketGateway({ cors: { origin: '*' }, path: '/ws/' })
export class EventsGateway implements OnGatewayConnection, OnGatewayDisconnect {
  @WebSocketServer()
  server: Server;

  private readonly logger = new Logger(EventsGateway.name);

  constructor(private readonly storageService: StorageService) {}

  handleConnection(client: any) {
    this.logger.log(`Client connected: ${client.id}`);
  }

  handleDisconnect(client: any) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('image')
  async handleImage(
    @MessageBody() data: { data: string; filename?: string; camera_id?: string },
    @ConnectedSocket() client: any,
  ) {
    try {
      const filePath = await this.storageService.saveImage(
        data.data,
        data.filename,
        data.camera_id,
      );
      this.logger.log(`Image saved: ${filePath}`);
      return { event: 'image_saved', data: { path: filePath, success: true } };
    } catch (error) {
      this.logger.error(`Failed to save image: ${error.message}`);
      return { event: 'image_error', data: { success: false, error: error.message } };
    }
  }

  @SubscribeMessage('message')
  async handleMessage(
    @MessageBody() data: string | Record<string, any>,
    @ConnectedSocket() client: any,
  ) {
    try {
      const content =
        typeof data === 'string' ? data : (data?.content ?? JSON.stringify(data));
      await this.storageService.saveMessage(content);
      this.logger.log(`Message saved from client ${client.id}`);
      return { event: 'message_saved', data: { success: true } };
    } catch (error) {
      this.logger.error(`Failed to save message: ${error.message}`);
      return { event: 'message_error', data: { success: false, error: error.message } };
    }
  }
}
