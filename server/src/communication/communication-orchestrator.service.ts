import { Injectable, Logger } from '@nestjs/common';
import { CommunicationProtocol, DetectionData, DeviceData, CommunicationResponse } from './interfaces/communication.interface';
import { WebSocketProtocol } from './protocols/websocket.protocol';
import { RestProtocol } from './protocols/rest.protocol';
import { MqttProtocol } from './protocols/mqtt.protocol';

export interface CommunicationConfig {
  priority: 'websocket' | 'rest' | 'mqtt';
  fallbackOrder: ('websocket' | 'rest' | 'mqtt')[];
  retryAttempts: number;
  retryDelay: number;
}

@Injectable()
export class CommunicationOrchestratorService {
  private readonly logger = new Logger(CommunicationOrchestratorService.name);
  private protocols: Map<string, CommunicationProtocol> = new Map();
  private config: CommunicationConfig;

  constructor(
    private readonly webSocketProtocol: WebSocketProtocol,
    private readonly restProtocol: RestProtocol,
    private readonly mqttProtocol: MqttProtocol
  ) {
    this.config = {
      priority: 'websocket',
      fallbackOrder: ['websocket', 'rest', 'mqtt'],
      retryAttempts: 3,
      retryDelay: 1000
    };

    this.initializeProtocols();
  }

  private async initializeProtocols(): Promise<void> {
    this.protocols.set('websocket', this.webSocketProtocol);
    this.protocols.set('rest', this.restProtocol);
    this.protocols.set('mqtt', this.mqttProtocol);

    // Connect to all protocols
    for (const [name, protocol] of this.protocols) {
      try {
        await protocol.connect();
        this.logger.log(`Connected to ${name} protocol`);
      } catch (error) {
        this.logger.warn(`Failed to connect to ${name} protocol: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
  }

  async sendDetection(data: DetectionData): Promise<CommunicationResponse> {
    return this.sendWithFallback('sendDetection', data);
  }

  async sendDeviceUpdate(data: DeviceData): Promise<CommunicationResponse> {
    return this.sendWithFallback('sendDeviceUpdate', data);
  }

  async sendHealthCheck(): Promise<CommunicationResponse> {
    return this.sendWithFallback('sendHealthCheck');
  }

  private async sendWithFallback(
    method: 'sendDetection' | 'sendDeviceUpdate' | 'sendHealthCheck',
    data?: DetectionData | DeviceData
  ): Promise<CommunicationResponse> {
    let lastError: string = '';

    for (const protocolName of this.config.fallbackOrder) {
      const protocol = this.protocols.get(protocolName);
      if (!protocol) {
        this.logger.warn(`Protocol ${protocolName} not found`);
        continue;
      }

      // Check if protocol is available
      const isAvailable = await protocol.isAvailable();
      if (!isAvailable) {
        this.logger.debug(`Protocol ${protocolName} is not available`);
        continue;
      }

      // Try to send with retries
      for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
        try {
          let response: CommunicationResponse;

          switch (method) {
            case 'sendDetection':
              response = await protocol.sendDetection(data as DetectionData);
              break;
            case 'sendDeviceUpdate':
              response = await protocol.sendDeviceUpdate(data as DeviceData);
              break;
            case 'sendHealthCheck':
              response = await protocol.sendHealthCheck();
              break;
            default:
              throw new Error(`Unknown method: ${method}`);
          }

          if (response.success) {
            this.logger.log(`Successfully sent ${method} via ${protocolName}`);
            return response;
          } else {
            lastError = response.message;
            this.logger.warn(`Failed to send ${method} via ${protocolName}: ${response.message}`);
          }
        } catch (error) {
          lastError = error instanceof Error ? error.message : 'Unknown error';
          this.logger.warn(`Attempt ${attempt} failed for ${method} via ${protocolName}: ${lastError}`);
          
          if (attempt < this.config.retryAttempts) {
            await this.delay(this.config.retryDelay);
          }
        }
      }
    }

    // All protocols failed
    const errorMessage = `All communication protocols failed for ${method}. Last error: ${lastError}`;
    this.logger.error(errorMessage);
    
    return {
      success: false,
      message: errorMessage,
      timestamp: new Date()
    };
  }

  async getAvailableProtocols(): Promise<string[]> {
    const available: string[] = [];
    
    for (const [name, protocol] of this.protocols) {
      if (await protocol.isAvailable()) {
        available.push(name);
      }
    }
    
    return available;
  }

  async updateConfig(config: Partial<CommunicationConfig>): Promise<void> {
    this.config = { ...this.config, ...config };
    this.logger.log('Communication configuration updated');
  }

  async getProtocolStatus(): Promise<Record<string, boolean>> {
    const status: Record<string, boolean> = {};
    
    for (const [name, protocol] of this.protocols) {
      status[name] = await protocol.isAvailable();
    }
    
    return status;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  async onModuleDestroy(): Promise<void> {
    // Disconnect from all protocols
    for (const [name, protocol] of this.protocols) {
      try {
        await protocol.disconnect();
        this.logger.log(`Disconnected from ${name} protocol`);
      } catch (error) {
        this.logger.warn(`Failed to disconnect from ${name} protocol: ${error instanceof Error ? error.message : String(error)}`);
      }
    }
  }
}
