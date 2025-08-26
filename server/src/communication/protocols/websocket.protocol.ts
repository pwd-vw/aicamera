import { Injectable } from '@nestjs/common';
import { Server } from 'socket.io';
import { EventsGateway } from '../../events/events.gateway';
import { CommunicationProtocol, DetectionData, DeviceData, CommunicationResponse } from '../interfaces/communication.interface';

@Injectable()
export class WebSocketProtocol implements CommunicationProtocol {
  name = 'WebSocket';
  private isConnected = false;

  constructor(private eventsGateway: EventsGateway) {}

  private get server(): Server {
    return this.eventsGateway.server;
  }

  async isAvailable(): Promise<boolean> {
    return this.isConnected && this.server !== null;
  }

  async sendDetection(data: DetectionData): Promise<CommunicationResponse> {
    try {
      if (!this.isConnected) {
        throw new Error('WebSocket not connected');
      }

      this.server.emit('detection', {
        ...data,
        protocol: 'websocket',
        timestamp: new Date()
      });

      return {
        success: true,
        message: 'Detection sent via WebSocket',
        data: data,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `WebSocket error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async sendDeviceUpdate(data: DeviceData): Promise<CommunicationResponse> {
    try {
      if (!this.isConnected) {
        throw new Error('WebSocket not connected');
      }

      this.server.emit('device_update', {
        ...data,
        protocol: 'websocket',
        timestamp: new Date()
      });

      return {
        success: true,
        message: 'Device update sent via WebSocket',
        data: data,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `WebSocket error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async sendHealthCheck(): Promise<CommunicationResponse> {
    try {
      if (!this.isConnected) {
        throw new Error('WebSocket not connected');
      }

      this.server.emit('health_check', {
        status: 'healthy',
        protocol: 'websocket',
        timestamp: new Date()
      });

      return {
        success: true,
        message: 'Health check sent via WebSocket',
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `WebSocket error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async connect(): Promise<void> {
    this.isConnected = true;
  }

  async disconnect(): Promise<void> {
    this.isConnected = false;
  }
}
