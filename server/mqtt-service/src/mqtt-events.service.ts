import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

const LOG_FILE = process.env.MQTT_RECEIVE_LOG ?? path.join(process.cwd(), '..', 'mqtt_receive.log');

@Injectable()
export class MqttEventsService {
  logReceived(topic: string, data: unknown): void {
    const line = `[${new Date().toISOString()}] ${topic} ${JSON.stringify(data)}\n`;
    try {
      fs.appendFileSync(LOG_FILE, line);
    } catch (err) {
      console.error('mqtt-events: failed to write log', err);
    }
  }
}
