import { Injectable } from '@nestjs/common';
import axios, { AxiosInstance } from 'axios';

const DEFAULT_BACKEND_URL = 'http://localhost:3000/server/api';

export interface CameraRegisterPayload {
  camera_id: string;
  checkpoint_id: string;
  timestamp?: string;
}

export interface DetectionResultContent {
  type: string;
  aicamera_id: string;
  checkpoint_id: string;
  timestamp: string;
  vehicles_count: number;
  plates_count: number;
  ocr_results: Array<{ text: string; confidence: number }>;
  vehicle_detections?: Array<{ bbox: number[]; confidence: number }>;
  plate_detections?: Array<{ bbox: number[]; confidence: number }>;
  processing_time_ms?: number;
  created_at?: string;
}

export interface HealthStatusPayload {
  type: string;
  aicamera_id: string;
  checkpoint_id: string;
  timestamp?: string;
  component: string;
  status: string;
  message: string;
  details?: string;
  created_at?: string;
}

export interface CameraResponse {
  id: string;
  cameraId: string;
  name: string;
}

export interface DetectionResponse {
  id: string;
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
    const { data } = await this.client.post<CameraResponse>(
      '/cameras/register',
      payload,
    );
    return data;
  }

  async createDetections(
    cameraIdUuid: string,
    content: DetectionResultContent,
  ): Promise<DetectionResponse[]> {
    const timestamp = content.timestamp || content.created_at || new Date().toISOString();
    const results: DetectionResponse[] = [];
    const ocrResults = content.ocr_results ?? [];
    const metadata: Record<string, unknown> = {
      vehicles_count: content.vehicles_count,
      plates_count: content.plates_count,
      vehicle_detections: content.vehicle_detections ?? [],
      plate_detections: content.plate_detections ?? [],
      processing_time_ms: content.processing_time_ms,
    };
    for (const ocr of ocrResults) {
      const licensePlate = String(ocr.text).slice(0, 20);
      const confidence = Math.min(1, Math.max(0, Number(ocr.confidence)));
      const { data } = await this.client.post<DetectionResponse>('/detections', {
        cameraId: cameraIdUuid,
        timestamp,
        licensePlate,
        confidence,
        imagePath: null,
        metadata,
      });
      results.push(data);
    }
    return results;
  }

  async updateDetectionsImagePath(
    cameraIdUuid: string,
    timestampIso: string,
    imagePath: string,
  ): Promise<{ affected: number }> {
    const { data } = await this.client.patch<{ affected: number }>(
      '/detections/image-path',
      {
        cameraId: cameraIdUuid,
        timestamp: timestampIso,
        imagePath,
      },
    );
    return data;
  }

  async createCameraHealth(
    cameraIdUuid: string,
    payload: HealthStatusPayload,
  ): Promise<{ id: string }> {
    const timestamp = payload.timestamp || payload.created_at || new Date().toISOString();
    const metadata: Record<string, unknown> = {
      component: payload.component,
      message: payload.message,
      details: payload.details ?? {},
    };
    try {
      if (typeof metadata.details === 'string') {
        try {
          metadata.details = JSON.parse(metadata.details as string);
        } catch {
          // keep as string
        }
      }
    } catch {
      // ignore
    }
    const { data } = await this.client.post<{ id: string }>('/camera-health', {
      cameraId: cameraIdUuid,
      timestamp,
      status: payload.status,
      metadata,
    });
    return data;
  }
}
