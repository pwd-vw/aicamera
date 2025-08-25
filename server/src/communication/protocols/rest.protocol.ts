import { Injectable } from '@nestjs/common';
import { CommunicationProtocol, DetectionData, DeviceData, CommunicationResponse } from '../interfaces/communication.interface';

@Injectable()
export class RestProtocol implements CommunicationProtocol {
  name = 'REST API';
  private baseUrl: string;
  private isConnected = false;

  constructor(baseUrl: string = 'http://localhost:3000') {
    this.baseUrl = baseUrl;
  }

  async isAvailable(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      this.isConnected = response.ok;
      return this.isConnected;
    } catch {
      this.isConnected = false;
      return false;
    }
  }

  async sendDetection(data: DetectionData): Promise<CommunicationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/detections`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      return {
        success: true,
        message: 'Detection sent via REST API',
        data: result,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `REST API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async sendDeviceUpdate(data: DeviceData): Promise<CommunicationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/devices`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();

      return {
        success: true,
        message: 'Device update sent via REST API',
        data: result,
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `REST API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async sendHealthCheck(): Promise<CommunicationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return {
        success: true,
        message: 'Health check sent via REST API',
        timestamp: new Date()
      };
    } catch (error) {
      return {
        success: false,
        message: `REST API error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date()
      };
    }
  }

  async connect(): Promise<void> {
    this.isConnected = await this.isAvailable();
  }

  async disconnect(): Promise<void> {
    this.isConnected = false;
  }
}
