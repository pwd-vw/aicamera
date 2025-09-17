<template>
  <div class="map-view">
    <header class="flex items-center justify-between mb-6">
      <h1 class="text-2xl font-semibold">Camera Map</h1>
      <div class="flex items-center gap-3">
        <router-link to="/dashboard" class="btn-secondary">← Back to Dashboard</router-link>
        <router-link to="/cameras" class="btn-secondary">Manage Cameras</router-link>
      </div>
    </header>
    
    <div class="map-container">
      <div class="map-header">
        <h3>Camera Locations & Detections</h3>
        <div class="map-controls">
          <button @click="refreshMap" :disabled="loading" class="btn-secondary">
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
          <select v-model="selectedFilter" class="select" @change="updateMapMarkers">
            <option value="all">All Cameras</option>
            <option value="active">Active Only</option>
            <option value="detections">With Detections</option>
          </select>
          <select v-model="selectedMapLayer" class="select" @change="changeMapLayer">
            <option value="street">Street Map</option>
            <option value="satellite">Satellite</option>
            <option value="terrain">Terrain</option>
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
        
        <!-- Map will be rendered here by Leaflet -->
      </div>
    </div>
    
    <!-- Camera Details Modal -->
    <div v-if="selectedCamera" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ selectedCamera.name }}</h3>
          <button @click="closeModal" class="close-btn">&times;</button>
        </div>
        <div class="modal-body">
          <div class="camera-details">
            <div class="detail-row">
              <span class="label">Location:</span>
              <span class="value">{{ selectedCamera.locationAddress || 'No address' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Status:</span>
              <span class="value status" :class="selectedCamera.status">{{ selectedCamera.status }}</span>
            </div>
            <div class="detail-row">
              <span class="label">IP Address:</span>
              <span class="value">{{ selectedCamera.ipAddress || 'N/A' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Last Detection:</span>
              <span class="value">{{ selectedCamera.lastDetection || 'None' }}</span>
            </div>
            <div class="detail-row">
              <span class="label">Total Detections:</span>
              <span class="value">{{ (selectedCamera as any).detectionCount || 0 }}</span>
            </div>
          </div>
          
          <div class="camera-actions">
            <button @click="viewCameraDetails" class="btn-primary">View Details</button>
            <button @click="viewDetections" class="btn-secondary">View Detections</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { communicationService } from '../services';

// Fix for default markers in Leaflet with Vite
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const router = useRouter();

// Reactive data
const mapContainer = ref<HTMLElement>();
const loading = ref(false);
const error = ref<string | null>(null);
const cameras = ref<any[]>([]);
const selectedCamera = ref<any>(null);
const selectedFilter = ref('all');
const selectedMapLayer = ref('street');

// Map instance
let map: L.Map | null = null;
let markers: L.Marker[] = [];
let currentLayer: L.TileLayer | null = null;

// Computed properties
const filteredCameras = computed(() => {
  if (selectedFilter.value === 'all') return cameras.value;
  if (selectedFilter.value === 'active') return cameras.value.filter(c => c.status === 'active');
  if (selectedFilter.value === 'detections') return cameras.value.filter(c => (c as any).detectionCount > 0);
  return cameras.value;
});

// Map layer configurations
const mapLayers = {
  street: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
  }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: '© Esri'
  }),
  terrain: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenTopoMap'
  })
};

// Initialize map
const initializeMap = () => {
  if (!mapContainer.value) return;

  // Create map centered on a default location (you can change this)
  map = L.map(mapContainer.value).setView([13.7563, 100.5018], 13); // Bangkok coordinates

  // Add default layer
  currentLayer = mapLayers[selectedMapLayer.value as keyof typeof mapLayers];
  currentLayer.addTo(map);

  // Add map controls
  L.control.scale().addTo(map);
};

// Create custom camera markers
const createCameraMarker = (camera: any) => {
  // Generate coordinates if not available (for demo purposes)
  const lat = camera.latitude || (13.7563 + (Math.random() - 0.5) * 0.1);
  const lng = camera.longitude || (100.5018 + (Math.random() - 0.5) * 0.1);

  // Create custom icon based on camera status
  const getMarkerColor = (status: string) => {
    switch (status) {
      case 'active': return '#10b981'; // green
      case 'inactive': return '#6b7280'; // gray
      case 'error': return '#ef4444'; // red
      default: return '#3b82f6'; // blue
    }
  };

  const customIcon = L.divIcon({
    className: 'custom-camera-marker',
    html: `
      <div style="
        background-color: ${getMarkerColor(camera.status)};
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        color: white;
        cursor: pointer;
      ">
        📹
      </div>
    `,
    iconSize: [30, 30],
    iconAnchor: [15, 15]
  });

  const marker = L.marker([lat, lng], { icon: customIcon }).addTo(map!);
  
  // Add popup with camera information
  const popupContent = `
    <div style="min-width: 200px;">
      <h4 style="margin: 0 0 8px 0; color: #374151;">${camera.name}</h4>
      <p style="margin: 4px 0; color: #6b7280;"><strong>Status:</strong> <span style="color: ${getMarkerColor(camera.status)};">${camera.status}</span></p>
      <p style="margin: 4px 0; color: #6b7280;"><strong>Location:</strong> ${camera.locationAddress || 'No address'}</p>
      <p style="margin: 4px 0; color: #6b7280;"><strong>Detections:</strong> ${(camera as any).detectionCount || 0}</p>
      <button onclick="window.selectCameraFromMap('${camera.id}')" style="
        background: #3b82f6;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        margin-top: 8px;
      ">View Details</button>
    </div>
  `;
  
  marker.bindPopup(popupContent);
  
  // Add click event
  marker.on('click', () => {
    selectCamera(camera);
  });

  return marker;
};

// Update map markers based on filter
const updateMapMarkers = () => {
  if (!map) return;

  // Clear existing markers
  markers.forEach(marker => map!.removeLayer(marker));
  markers = [];

  // Add filtered markers
  filteredCameras.value.forEach(camera => {
    const marker = createCameraMarker(camera);
    markers.push(marker);
  });
};

// Change map layer
const changeMapLayer = () => {
  if (!map || !currentLayer) return;

  // Remove current layer
  map.removeLayer(currentLayer);

  // Add new layer
  currentLayer = mapLayers[selectedMapLayer.value as keyof typeof mapLayers];
  currentLayer.addTo(map);
};

// Load cameras data
const loadCameras = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    cameras.value = await communicationService.getCameras();
    
    // Add some mock data for demonstration if no cameras exist
    if (cameras.value.length === 0) {
      cameras.value = [
        {
          id: '1',
          name: 'Main Entrance Camera',
          status: 'active',
          locationAddress: 'Main Building Entrance',
          ipAddress: '192.168.1.100',
          detectionCount: 15,
          lastDetection: '2 hours ago'
        },
        {
          id: '2',
          name: 'Parking Lot Camera',
          status: 'active',
          locationAddress: 'Parking Lot A',
          ipAddress: '192.168.1.101',
          detectionCount: 8,
          lastDetection: '1 hour ago'
        },
        {
          id: '3',
          name: 'Back Door Camera',
          status: 'inactive',
          locationAddress: 'Back Door',
          ipAddress: '192.168.1.102',
          detectionCount: 0,
          lastDetection: 'Never'
        }
      ];
    }
    
    // Update map markers after data is loaded
    if (map) {
      updateMapMarkers();
    }
  } catch (err: any) {
    error.value = err.message || 'Failed to load cameras';
    console.error('Error loading cameras:', err);
  } finally {
    loading.value = false;
  }
};

// Refresh map data
const refreshMap = () => {
  loadCameras();
};

// Select camera
const selectCamera = (camera: any) => {
  selectedCamera.value = camera;
};

// Close modal
const closeModal = () => {
  selectedCamera.value = null;
};

// View camera details
const viewCameraDetails = () => {
  if (selectedCamera.value) {
    router.push(`/cameras/${selectedCamera.value.id}`);
  }
};

// View detections
const viewDetections = () => {
  if (selectedCamera.value) {
    router.push(`/detections?camera=${selectedCamera.value.id}`);
  }
};

// Format date
const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString();
};

// Lifecycle hooks
onMounted(async () => {
  // Initialize map
  setTimeout(() => {
    initializeMap();
    loadCameras();
  }, 100);
});

onUnmounted(() => {
  if (map) {
    map.remove();
  }
});

// Make selectCameraFromMap available globally for popup buttons
(window as any).selectCameraFromMap = (cameraId: string) => {
  const camera = cameras.value.find(c => c.id === cameraId);
  if (camera) {
    selectCamera(camera);
  }
};
</script>

<style scoped>
.map-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.map-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.map-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.map-controls {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.map-content {
  flex: 1;
  position: relative;
  min-height: 500px;
}

.loading-overlay,
.error-message,
.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 1000;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background: white;
  font-size: 0.875rem;
}

.btn-secondary {
  background: #6b7280;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 0.5rem;
  max-width: 500px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
}

.modal-body {
  padding: 1rem;
}

.camera-details {
  margin-bottom: 1rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.label {
  font-weight: 600;
  color: #374151;
}

.value {
  color: #6b7280;
}

.value.status {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.value.status.active {
  background: #d1fae5;
  color: #065f46;
}

.value.status.inactive {
  background: #f3f4f6;
  color: #374151;
}

.value.status.error {
  background: #fee2e2;
  color: #991b1b;
}

.camera-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-primary:hover {
  background: #2563eb;
}

/* Leaflet map styles */
:deep(.leaflet-container) {
  height: 100%;
  width: 100%;
}

:deep(.custom-camera-marker) {
  background: transparent !important;
  border: none !important;
}
</style>