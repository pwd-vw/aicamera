import { Injectable } from '@nestjs/common';
import axios, { AxiosInstance } from 'axios';

const DEFAULT_BACKEND_URL = 'http://localhost:3000/server/api';

export interface CameraRegisterPayload {
  camera_id: string;
  checkpoint_id?: string;
  timestamp?: string;
}

export interface MqttHealthPayload {
  camera_id?: string;
  checkpoint_id?: string;
  status?: string;
  timestamp?: string;
  cpu_percent?: number;
  memory_percent?: number;
  disk_free_gb?: number;
  temperature_c?: number;
  uptime_seconds?: number;
  battery_percent?: number;
  network_connected?: boolean;
  location_lat?: number;
  location_lng?: number;
  [key: string]: unknown;
}

export interface CameraResponse {
  id: string;
  cameraId: string;
  name: string;
}

@Injectable()
export class BackendApiService {
  private readonly client: AxiosInstance;

  constructor() {
    const baseURL = process.env.BACKEND_API_URL || DEFAULT_BACKEND_URL;
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      maxRedirects: 5,
    });
  }

  async registerCamera(payload: CameraRegisterPayload): Promise<CameraResponse> {
    const { data } = await this.client.post<CameraResponse>('/cameras/register', {
      camera_id: payload.camera_id,
      checkpoint_id: payload.checkpoint_id || payload.camera_id,
      timestamp: payload.timestamp,
    });
    return data;
  }

  async createCameraHealth(
    cameraIdUuid: string,
    payload: MqttHealthPayload,
  ): Promise<{ id: string }> {
    const timestamp = payload.timestamp || new Date().toISOString();
    const status =
      payload.status ||
      (payload.cpu_percent != null && payload.cpu_percent > 90 ? 'degraded' : 'healthy');
    const metadata: Record<string, unknown> = { ...payload };
    delete metadata.camera_id;
    delete metadata.checkpoint_id;
    delete metadata.timestamp;
    delete metadata.status;
    delete metadata.cpu_percent;
    delete metadata.memory_percent;
    delete metadata.disk_free_gb;
    delete metadata.temperature_c;
    delete metadata.uptime_seconds;

    const body: Record<string, unknown> = {
      cameraId: cameraIdUuid,
      timestamp: timestamp,
      status: String(status).slice(0, 50),
      metadata,
    };
    if (payload.cpu_percent != null) body['cpuUsage'] = Number(payload.cpu_percent);
    if (payload.memory_percent != null) body['memoryUsage'] = Number(payload.memory_percent);
    if (payload.disk_free_gb != null) metadata['disk_free_gb'] = payload.disk_free_gb;
    if (payload.temperature_c != null) body['temperature'] = Number(payload.temperature_c);
    if (payload.uptime_seconds != null) body['uptimeSeconds'] = Number(payload.uptime_seconds);

    const { data } = await this.client.post<{ id: string }>('/camera-health', body);
    return data;
  }
}
