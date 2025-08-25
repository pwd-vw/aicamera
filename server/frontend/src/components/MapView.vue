<template>
  <div class="map-container">
    <div class="map-header">
      <h3>Camera Locations & Detections</h3>
      <div class="map-controls">
        <button @click="refreshMap" :disabled="loading" class="btn-secondary">
          {{ loading ? 'Loading...' : 'Refresh' }}
        </button>
        <select v-model="selectedFilter" class="select">
          <option value="all">All Cameras</option>
          <option value="active">Active Only</option>
          <option value="detections">With Detections</option>
        </select>
      </div>
    </div>
    
    <div ref="mapContainer" class="map-content">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Loading map data...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="refreshMap" class="btn-secondary">Retry</button>
      </div>
      
      <div v-else-if="!cameras.length" class="empty-state">
        <p>No cameras found</p>
        <button @click="refreshMap" class="btn-secondary">Refresh</button>
      </div>
      
      <div v-else class="map-placeholder">
        <div class="map-grid">
          <div 
            v-for="camera in filteredCameras" 
            :key="camera.id"
            class="camera-marker"
            :class="{ 
              'active': camera.status === 'active',
              'inactive': camera.status === 'inactive',
              'error': camera.status === 'error'
            }"
            @click="selectCamera(camera)"
          >
            <div class="marker-icon">
              <span class="icon">📹</span>
            </div>
            <div class="marker-info">
              <strong>{{ camera.name }}</strong>
              <span class="status">{{ camera.status }}</span>
              <span v-if="camera.detectionCount" class="detections">
                {{ camera.detectionCount }} detections
              </span>
            </div>
          </div>
        </div>
        
        <div v-if="selectedCamera" class="camera-details">
          <h4>{{ selectedCamera.name }}</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>Status:</label>
              <span :class="selectedCamera.status">{{ selectedCamera.status }}</span>
            </div>
            <div class="detail-item">
              <label>Location:</label>
              <span>{{ selectedCamera.locationAddress || 'No address' }}</span>
            </div>
            <div class="detail-item">
              <label>Detections:</label>
              <span>{{ selectedCamera.detectionCount || 0 }}</span>
            </div>
            <div class="detail-item">
              <label>Last Update:</label>
              <span>{{ formatDate(selectedCamera.updatedAt) }}</span>
            </div>
          </div>
          <div class="camera-actions">
            <button @click="viewCameraDetails(selectedCamera)" class="btn-primary">
              View Details
            </button>
            <button @click="viewDetections(selectedCamera)" class="btn-secondary">
              View Detections
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { communicationService } from '../services';
import type { Camera } from '../services';

const mapContainer = ref<HTMLElement>();
const loading = ref(false);
const error = ref('');
const cameras = ref<Camera[]>([]);
const selectedCamera = ref<Camera | null>(null);
const selectedFilter = ref('all');

const filteredCameras = computed(() => {
  switch (selectedFilter.value) {
    case 'active':
      return cameras.value.filter(c => c.status === 'active');
    case 'detections':
      return cameras.value.filter(c => (c as any).detectionCount > 0);
    default:
      return cameras.value;
  }
});

const refreshMap = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    cameras.value = await communicationService.getCameras();
    
    // Get detection counts for each camera
    for (const camera of cameras.value) {
      try {
        const detections = await communicationService.getDetections({ 
          cameraId: camera.cameraId,
          limit: 1 
        });
        (camera as any).detectionCount = detections.length;
      } catch (err) {
        (camera as any).detectionCount = 0;
      }
    }
  } catch (err) {
    error.value = 'Failed to load camera data';
    console.error('Map refresh error:', err);
  } finally {
    loading.value = false;
  }
};

const selectCamera = (camera: Camera) => {
  selectedCamera.value = camera;
};

const viewCameraDetails = (camera: Camera) => {
  // Emit event or navigate to camera details
  console.log('View camera details:', camera.id);
};

const viewDetections = (camera: Camera) => {
  // Emit event or navigate to detections
  console.log('View detections for camera:', camera.id);
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString();
};

onMounted(() => {
  refreshMap();
});

watch(selectedFilter, () => {
  selectedCamera.value = null;
});
</script>

<style scoped>
.map-container {
  height: 600px;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f9fafb;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.map-controls {
  display: flex;
  gap: 0.5rem;
}

.map-content {
  height: calc(100% - 70px);
  position: relative;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 10;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-grid {
  flex: 1;
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  overflow-y: auto;
}

.camera-marker {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.camera-marker:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.camera-marker.active {
  border-color: #10b981;
}

.camera-marker.inactive {
  border-color: #6b7280;
  opacity: 0.7;
}

.camera-marker.error {
  border-color: #ef4444;
}

.marker-icon {
  font-size: 1.5rem;
}

.marker-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.status {
  font-size: 0.875rem;
  color: #6b7280;
}

.detections {
  font-size: 0.75rem;
  color: #3b82f6;
}

.camera-details {
  padding: 1rem;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin: 1rem 0;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-item label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

.camera-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-primary, .btn-secondary {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  background: white;
  font-size: 0.875rem;
}
</style>
