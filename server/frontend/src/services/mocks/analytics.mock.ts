import type { 
  EdgeStatusSummary,
  NetworkStats,
  DetectionTimeSeriesPoint,
  DetectionsByLocation,
  TopPlateItem,
  DetectionFilters,
} from '../analytics.service';

function seededRandom(seed: number) {
  let value = seed % 2147483647;
  return () => (value = (value * 48271) % 2147483647) / 2147483647;
}

const baseSeed = 123456;

export function mockEdgeStatusSummary(): EdgeStatusSummary {
  const rand = seededRandom(baseSeed);
  const total = 24;
  const active = 18;
  const error = 2;
  const inactive = total - active - error;
  const perCamera = Array.from({ length: total }).map((_, i) => {
    const status: 'active' | 'inactive' | 'error' = i < active ? 'active' : i < active + inactive ? 'inactive' : 'error';
    return {
      cameraId: `CAM-${String(100 + i)}`,
      name: `Intersection ${i + 1}`,
      status,
      cpuUtilization: Math.round((40 + rand() * 45) * 10) / 10,
      memoryUtilization: Math.round((35 + rand() * 50) * 10) / 10,
      droppedFramesRate: Math.round(rand() * (status === 'active' ? 2 : 5) * 10) / 10,
    };
  });
  const cpuAvg = perCamera.reduce((s, c) => s + c.cpuUtilization, 0) / total;
  const memAvg = perCamera.reduce((s, c) => s + c.memoryUtilization, 0) / total;
  return {
    totalCameras: total,
    activeCameras: active,
    inactiveCameras: inactive,
    errorCameras: error,
    cpuUtilizationAvg: Math.round(cpuAvg * 10) / 10,
    memoryUtilizationAvg: Math.round(memAvg * 10) / 10,
    perCamera,
  };
}

export function mockNetworkStats(): NetworkStats {
  return {
    api: { status: 'up', latencyMsAvg: 62, latencyMsP95: 140, requestRatePerMin: 180 },
    websocket: { status: 'up', latencyMsAvg: 35, msgRatePerMin: 420 },
    mqtt: { status: 'up', latencyMsAvg: 28, msgRatePerMin: 520 },
  };
}

export function mockDetectionTimeSeries(filters: DetectionFilters = {}): DetectionTimeSeriesPoint[] {
  const rand = seededRandom(baseSeed + 99);
  const end = filters.endDate ? new Date(filters.endDate) : new Date();
  const start = filters.startDate ? new Date(filters.startDate) : new Date(end);
  const bucket = filters.bucket || 'hour';
  if (!filters.startDate) {
    if (bucket === 'hour') start.setHours(end.getHours() - 24);
    else start.setDate(end.getDate() - 14);
  }
  const points: DetectionTimeSeriesPoint[] = [];
  const cursor = new Date(start);
  while (cursor <= end) {
    points.push({ timestamp: cursor.toISOString(), count: Math.floor(20 + rand() * 80) });
    if (bucket === 'hour') cursor.setHours(cursor.getHours() + 1);
    else cursor.setDate(cursor.getDate() + 1);
  }
  return points;
}

export function mockDetectionsByLocation(_filters: DetectionFilters = {}): DetectionsByLocation {
  // Clustered around SF
  const centers = [
    { lat: 37.7749, lng: -122.4194 },
    { lat: 37.784, lng: -122.409 },
    { lat: 37.764, lng: -122.431 },
  ];
  const buckets = centers.flatMap((c, idx) =>
    Array.from({ length: 8 }).map(() => ({
      lat: c.lat + (Math.random() - 0.5) * 0.02,
      lng: c.lng + (Math.random() - 0.5) * 0.02,
      count: Math.floor(10 + Math.random() * (idx === 0 ? 60 : 40)),
    }))
  );
  return { buckets };
}

export function mockTopPlates(_filters: DetectionFilters = {}): TopPlateItem[] {
  const now = new Date();
  const plates = [
    '7ABC123', '8XYZ456', '5LMN789', '4QRS012', '9TUV345',
    '3JKL678', '2MNO901', '6PQR234', '1STU567', '0VWX890',
  ];
  return plates.map((p, i) => {
    const first = new Date(now);
    first.setDate(now.getDate() - (10 - i));
    const last = new Date(now);
    last.setHours(now.getHours() - i);
    return {
      licensePlate: p,
      count: 20 + (10 - i) * 7,
      firstSeen: first.toISOString(),
      lastSeen: last.toISOString(),
      sampleImageUrl: '/assets/car_crop_results.png',
    };
  });
}

