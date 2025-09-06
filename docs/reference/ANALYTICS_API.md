## Analytics API Reference

This document maps frontend analytics views to backend endpoints and data contracts. All endpoints are versionless under `/api` by default; adjust prefixes as needed.

### Edge Status Summary

- Frontend method: `analyticsService.getEdgeStatusSummary()`
- Endpoint: `GET /analytics/edge-status`
- Response body:
```json
{
  "totalCameras": 24,
  "activeCameras": 18,
  "inactiveCameras": 4,
  "errorCameras": 2,
  "cpuUtilizationAvg": 57.3,
  "memoryUtilizationAvg": 61.2,
  "perCamera": [
    {
      "cameraId": "CAM-101",
      "name": "Intersection 1",
      "status": "active",
      "cpuUtilization": 55.1,
      "memoryUtilization": 60.4,
      "droppedFramesRate": 0.8
    }
  ]
}
```

### Unified Communication Network Stats

- Frontend method: `analyticsService.getNetworkStats()`
- Endpoint: `GET /analytics/network`
- Response body:
```json
{
  "api": { "status": "up", "latencyMsAvg": 62, "latencyMsP95": 140, "requestRatePerMin": 180 },
  "websocket": { "status": "up", "latencyMsAvg": 35, "msgRatePerMin": 420 },
  "mqtt": { "status": "up", "latencyMsAvg": 28, "msgRatePerMin": 520 }
}
```

### Detections Time Series

- Frontend method: `analyticsService.getDetectionTimeSeries(params)`
- Endpoint: `GET /analytics/detections/time-series`
- Query params:
  - `cameraId?`: string
  - `startDate?`: ISO string
  - `endDate?`: ISO string
  - `bucket?`: `hour | day` (default `hour`)
- Response body:
```json
[
  { "timestamp": "2025-01-01T00:00:00.000Z", "count": 42 },
  { "timestamp": "2025-01-01T01:00:00.000Z", "count": 37 }
]
```

### Detections by Location

- Frontend method: `analyticsService.getDetectionsByLocation(params)`
- Endpoint: `GET /analytics/detections/by-location`
- Query params: same as Time Series (minus `bucket`)
- Response body:
```json
{
  "buckets": [
    { "lat": 37.7749, "lng": -122.4194, "count": 64 },
    { "lat": 37.7840, "lng": -122.4090, "count": 28 }
  ]
}
```

### Top License Plates

- Frontend method: `analyticsService.getTopPlates(params)`
- Endpoint: `GET /analytics/detections/top-plates`
- Query params:
  - `cameraId?`, `startDate?`, `endDate?`, `limit?` (default 10)
- Response body:
```json
[
  {
    "licensePlate": "7ABC123",
    "count": 61,
    "firstSeen": "2025-01-01T03:12:00.000Z",
    "lastSeen": "2025-01-03T11:42:00.000Z",
    "sampleImageUrl": "/assets/car_crop_results.png"
  }
]
```

### Notes for Backend Developers

- Auth: Standard bearer token via `Authorization: Bearer <token>` is attached by the Axios instance.
- Error handling: Frontend falls back to mock data if endpoint is unreachable or returns an error. Return proper HTTP status codes on failures.
- Performance: Time series endpoints should support server-side aggregation by bucket and filtering by time range and camera id.
- CORS: Ensure CORS allows the frontend origin during local development.

### Frontend Integration Points

- View: `src/views/AnalyticsView.vue`
- Service: `src/services/analytics.service.ts`
- Router: route `GET /analytics` renders the analytics dashboard
- Mocks: `src/services/mocks/analytics.mock.ts` used automatically on error

