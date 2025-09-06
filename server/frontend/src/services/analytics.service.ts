import api from '../utils/api';

// Types for analytics domain
export interface EdgeStatusSummary {
  totalCameras: number;
  activeCameras: number;
  inactiveCameras: number;
  errorCameras: number;
  cpuUtilizationAvg: number; // percent
  memoryUtilizationAvg: number; // percent
  perCamera?: Array<{
    cameraId: string;
    name: string;
    status: 'active' | 'inactive' | 'error';
    cpuUtilization: number;
    memoryUtilization: number;
    droppedFramesRate: number; // fps
  }>;
}

export interface NetworkStats {
  api: { status: 'up' | 'down'; latencyMsAvg: number; latencyMsP95: number; requestRatePerMin: number };
  websocket: { status: 'up' | 'down'; latencyMsAvg: number; msgRatePerMin: number };
  mqtt: { status: 'up' | 'down'; latencyMsAvg: number; msgRatePerMin: number };
}

export interface DetectionTimeSeriesPoint {
  timestamp: string; // ISO string bucket start
  count: number;
}

export interface DetectionsByLocation {
  buckets: Array<{
    lat: number;
    lng: number;
    count: number;
  }>;
}

export interface TopPlateItem {
  licensePlate: string;
  count: number;
  firstSeen: string;
  lastSeen: string;
  sampleImageUrl?: string;
}

export interface DetectionFilters {
  cameraId?: string;
  startDate?: string; // ISO
  endDate?: string; // ISO
  bucket?: 'hour' | 'day';
  limit?: number;
}

// Import mocks as fallback
import { 
  mockEdgeStatusSummary,
  mockNetworkStats,
  mockDetectionTimeSeries,
  mockDetectionsByLocation,
  mockTopPlates,
} from './mocks/analytics.mock';

export class AnalyticsService {
  async getEdgeStatusSummary(): Promise<EdgeStatusSummary> {
    try {
      const res = await api.get('/analytics/edge-status');
      return res.data;
    } catch (error) {
      console.warn('Using mock edge status summary due to API error:', error);
      return mockEdgeStatusSummary();
    }
  }

  async getNetworkStats(): Promise<NetworkStats> {
    try {
      const res = await api.get('/analytics/network');
      return res.data;
    } catch (error) {
      console.warn('Using mock network stats due to API error:', error);
      return mockNetworkStats();
    }
  }

  async getDetectionTimeSeries(filters: DetectionFilters = {}): Promise<DetectionTimeSeriesPoint[]> {
    try {
      const res = await api.get('/analytics/detections/time-series', { params: filters });
      return res.data;
    } catch (error) {
      console.warn('Using mock detection time series due to API error:', error);
      return mockDetectionTimeSeries(filters);
    }
  }

  async getDetectionsByLocation(filters: DetectionFilters = {}): Promise<DetectionsByLocation> {
    try {
      const res = await api.get('/analytics/detections/by-location', { params: filters });
      return res.data;
    } catch (error) {
      console.warn('Using mock detections by location due to API error:', error);
      return mockDetectionsByLocation(filters);
    }
  }

  async getTopPlates(filters: DetectionFilters = {}): Promise<TopPlateItem[]> {
    try {
      const res = await api.get('/analytics/detections/top-plates', { params: filters });
      return res.data;
    } catch (error) {
      console.warn('Using mock top plates due to API error:', error);
      return mockTopPlates(filters);
    }
  }
}

export const analyticsService = new AnalyticsService();

