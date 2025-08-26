# Communication Services Documentation

## Overview

The Vue.js frontend includes comprehensive communication services for interacting with the AI Camera backend through multiple protocols:

- **REST API** (Primary) - HTTP requests for CRUD operations
- **WebSocket** (Real-time) - Bidirectional communication for live updates
- **MQTT** (Lightweight) - Publish/subscribe messaging for IoT-style communication

## Services Architecture

### 1. API Service (`api.service.ts`)

**Purpose**: Handles all HTTP REST API communication with the backend.

**Features**:
- Authentication (login, register, refresh, logout)
- Camera management (CRUD operations, health checks, configuration)
- Detection management (CRUD operations, statistics)
- Analytics events (create, query, statistics)
- Visualizations (CRUD operations)
- User management (admin only)
- Rate limiting monitoring (admin only)
- File uploads
- System health checks

**Usage**:
```typescript
import { apiService } from '../services';

// Authentication
const result = await apiService.login({ username: 'admin', password: 'password' });

// Get cameras
const cameras = await apiService.getCameras();

// Get detections
const detections = await apiService.getDetections({ cameraId: 'camera1' });
```

### 2. WebSocket Service (`websocket.service.ts`)

**Purpose**: Provides real-time bidirectional communication with the backend.

**Features**:
- Automatic reconnection with exponential backoff
- Event-based communication
- Camera status updates
- Detection notifications
- System health monitoring
- Camera control commands

**Events**:
- `camera_status_update` - Real-time camera status
- `camera_connected` / `camera_disconnected` - Connection events
- `detection_update` / `new_detection` - Detection events
- `system_event` - System notifications
- `health_update` - Health monitoring

**Usage**:
```typescript
import { websocketService } from '../services';

// Connect to WebSocket
websocketService.connect('ws://localhost:3000');

// Subscribe to camera status
websocketService.onCameraStatus((status) => {
  console.log('Camera status:', status);
});

// Send camera control
websocketService.sendCameraControl('restart', { force: true });
```

### 3. MQTT Service (`mqtt.service.ts`)

**Purpose**: Lightweight publish/subscribe messaging for IoT-style communication.

**Features**:
- Topic-based messaging
- QoS levels support
- Automatic reconnection
- Message persistence
- Camera-specific topics
- System-wide topics

**Topics**:
- `camera/{id}/status` - Camera status updates
- `camera/{id}/health` - Camera health monitoring
- `camera/{id}/detections` - Detection events
- `camera/{id}/control` - Camera control commands
- `camera/{id}/config` - Configuration updates
- `system/events` - System events
- `system/health` - System health

**Usage**:
```typescript
import { mqttService } from '../services';

// Connect to MQTT broker
mqttService.connect('mqtt://localhost:1883');

// Subscribe to camera status
mqttService.subscribeToCameraStatus('camera1', (status) => {
  console.log('Camera status:', status);
});

// Publish camera control
mqttService.publishCameraControl('camera1', 'restart', { force: true });
```

### 4. Communication Service (`communication.service.ts`)

**Purpose**: Unified service that manages all communication protocols with automatic fallback.

**Features**:
- Protocol prioritization (WebSocket → MQTT → API)
- Automatic fallback mechanisms
- Connection status monitoring
- Configuration management
- Unified API for all protocols

**Fallback Strategy**:
1. **WebSocket** (Primary) - Real-time bidirectional communication
2. **MQTT** (Secondary) - Lightweight messaging
3. **REST API** (Fallback) - Polling-based updates

**Usage**:
```typescript
import { communicationService } from '../services';

// Initialize all services
await communicationService.initialize();

// Subscribe to camera status (automatic protocol selection)
communicationService.subscribeToCameraStatus('camera1', (status) => {
  console.log('Camera status:', status);
});

// Get connection status
const status = communicationService.getConnectionStatus();
console.log('API:', status.api);
console.log('WebSocket:', status.websocket);
console.log('MQTT:', status.mqtt);
```

## Configuration

### Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000
VITE_MQTT_URL=mqtt://localhost:1883
```

### Service Configuration

```typescript
import { communicationService } from '../services';

// Update configuration
communicationService.updateConfig({
  enableWebSocket: true,
  enableMQTT: true,
  fallbackToAPI: true,
});
```

## Service Status Component

The `ServiceStatus.vue` component provides a visual interface for monitoring service connections:

```vue
<template>
  <ServiceStatus />
</template>

<script setup>
import ServiceStatus from '../components/ServiceStatus.vue';
</script>
```

## Error Handling

All services include comprehensive error handling:

```typescript
try {
  const cameras = await apiService.getCameras();
} catch (error) {
  console.error('Failed to get cameras:', error);
  // Handle error appropriately
}
```

## Best Practices

1. **Initialize Early**: Initialize communication services when the app starts
2. **Handle Disconnections**: Implement proper error handling for network issues
3. **Use Fallbacks**: Leverage the automatic fallback mechanisms
4. **Monitor Status**: Use the connection status monitoring for UI feedback
5. **Clean Up**: Disconnect services when the app unmounts

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check if the backend WebSocket server is running
   - Verify the WebSocket URL in environment variables
   - Check browser console for CORS issues

2. **MQTT Connection Failed**
   - Ensure MQTT broker is running on the specified port
   - Check firewall settings
   - Verify MQTT URL configuration

3. **API Requests Failing**
   - Verify backend server is running
   - Check API base URL configuration
   - Ensure proper authentication

### Debug Mode

Enable debug logging:

```typescript
// In browser console
localStorage.setItem('debug', 'true');
```

## Integration with Vue Components

```vue
<template>
  <div>
    <div v-if="cameras.length > 0">
      <div v-for="camera in cameras" :key="camera.id">
        {{ camera.name }} - {{ camera.status }}
      </div>
    </div>
    <div v-else>Loading cameras...</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { communicationService } from '../services';

const cameras = ref([]);

onMounted(async () => {
  // Initialize communication
  await communicationService.initialize();
  
  // Load cameras
  cameras.value = await communicationService.getCameras();
  
  // Subscribe to real-time updates
  communicationService.subscribeToCameraStatus('all', (status) => {
    // Update camera status in real-time
    const camera = cameras.value.find(c => c.id === status.cameraId);
    if (camera) {
      camera.status = status.status;
    }
  });
});

onUnmounted(() => {
  communicationService.disconnect();
});
</script>
```

This comprehensive communication system ensures reliable, real-time interaction with the AI Camera backend across multiple protocols with automatic fallback mechanisms.
