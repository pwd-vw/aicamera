<template>
  <div class="service-status">
    <h3>Service Status</h3>
    <div class="status-grid">
      <div class="status-item">
        <span class="label">API:</span>
        <span class="status" :class="{ connected: apiStatus }">
          {{ apiStatus ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
      <div class="status-item">
        <span class="label">WebSocket:</span>
        <span class="status" :class="{ connected: wsStatus }">
          {{ wsStatus ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
      <div class="status-item">
        <span class="label">MQTT:</span>
        <span class="status" :class="{ connected: mqttStatus }">
          {{ mqttStatus ? 'Connected' : 'Disconnected' }}
        </span>
      </div>
    </div>
    <button @click="testConnections" :disabled="testing">
      {{ testing ? 'Testing...' : 'Test Connections' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';
import { communicationService } from '../services';

const apiStatus = ref(false);
const wsStatus = ref(false);
const mqttStatus = ref(false);
const testing = ref(false);

const updateStatus = () => {
  const status = communicationService.getConnectionStatus();
  apiStatus.value = status.api;
  wsStatus.value = status.websocket;
  mqttStatus.value = status.mqtt;
};

const testConnections = async () => {
  testing.value = true;
  try {
    await communicationService.initialize();
    updateStatus();
  } catch (error) {
    console.error('Connection test failed:', error);
  } finally {
    testing.value = false;
  }
};

onMounted(async () => {
  await communicationService.initialize();
  updateStatus();
  
  // Update status every 5 seconds
  const interval = setInterval(updateStatus, 5000);
  
  onUnmounted(() => {
    clearInterval(interval);
    communicationService.disconnect();
  });
});
</script>

<style scoped>
.service-status {
  padding: 1rem;
  border: 1px solid #ccc;
  border-radius: 0.5rem;
  background: #f9f9f9;
}

.status-grid {
  display: grid;
  gap: 0.5rem;
  margin: 1rem 0;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label {
  font-weight: 600;
}

.status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  background: #ef4444;
  color: white;
}

.status.connected {
  background: #10b981;
}

button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
