<template>
  <div class="cameras-view">
    <div class="view-header">
      <h1>Cameras</h1>
      <button @click="showAddModal = true" class="btn-primary">
        Add Camera
      </button>
    </div>

    <div class="view-content">
      <DataTable
        title="Cameras"
        :columns="columns"
        :items="cameras"
        :loading="loading"
        :error="error"
        @refresh="loadCameras"
        @view-item="viewCamera"
        @edit-item="editCamera"
        @delete-item="confirmDeleteCamera"
      >
        <template #filters>
          <select v-model="statusFilter" class="select">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
            <option value="error">Error</option>
          </select>
        </template>

        <template #cell-status="{ value }">
          <span :class="getStatusClass(value)">{{ value }}</span>
        </template>

        <template #cell-detectionEnabled="{ value }">
          <span :class="value ? 'status-active' : 'status-inactive'">
            {{ value ? 'Enabled' : 'Disabled' }}
          </span>
        </template>

        <template #row-actions="{ item }">
          <button @click.stop="viewCamera(item)" class="btn-link">View</button>
          <button @click.stop="editCamera(item)" class="btn-link">Edit</button>
          <button @click.stop="viewDetections(item)" class="btn-link">Detections</button>
          <button @click.stop="confirmDeleteCamera(item)" class="btn-link delete">Delete</button>
        </template>
      </DataTable>
    </div>

    <!-- Add/Edit Camera Modal -->
    <div v-if="showAddModal || showEditModal" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <h3>{{ showEditModal ? 'Edit Camera' : 'Add Camera' }}</h3>
        
        <form @submit.prevent="saveCamera" class="camera-form">
          <div class="form-group">
            <label>Camera ID:</label>
            <input v-model="cameraForm.cameraId" type="text" required />
          </div>
          
          <div class="form-group">
            <label>Name:</label>
            <input v-model="cameraForm.name" type="text" required />
          </div>
          
          <div class="form-group">
            <label>Location Address:</label>
            <input v-model="cameraForm.locationAddress" type="text" />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Latitude:</label>
              <input v-model.number="cameraForm.locationLat" type="number" step="any" />
            </div>
            
            <div class="form-group">
              <label>Longitude:</label>
              <input v-model.number="cameraForm.locationLng" type="number" step="any" />
            </div>
          </div>
          
          <div class="form-group">
            <label>Image Quality:</label>
            <select v-model="cameraForm.imageQuality">
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Upload Interval (seconds):</label>
            <input v-model.number="cameraForm.uploadInterval" type="number" min="1" />
          </div>
          
          <div class="form-group">
            <label>
              <input v-model="cameraForm.detectionEnabled" type="checkbox" />
              Enable Detection
            </label>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-secondary">Cancel</button>
            <button type="submit" :disabled="saving" class="btn-primary">
              {{ saving ? 'Saving...' : (showEditModal ? 'Update' : 'Create') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content" @click.stop>
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete camera "{{ cameraToDelete?.name }}"? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn-secondary">Cancel</button>
          <button @click="deleteCamera" :disabled="deleting" class="btn-danger">
            {{ deleting ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable, { type TableColumn } from '../components/DataTable.vue';
import { communicationService } from '../services';
import type { Camera } from '../services';

const router = useRouter();

const loading = ref(false);
const error = ref('');
const cameras = ref<Camera[]>([]);
const statusFilter = ref('');

const showAddModal = ref(false);
const showEditModal = ref(false);
const showDeleteModal = ref(false);
const saving = ref(false);
const deleting = ref(false);
const cameraToDelete = ref<Camera | null>(null);

const cameraForm = ref({
  cameraId: '',
  name: '',
  locationAddress: '',
  locationLat: null as number | null,
  locationLng: null as number | null,
  imageQuality: 'medium',
  uploadInterval: 30,
  detectionEnabled: true
});

const columns: TableColumn[] = [
  { key: 'cameraId', label: 'Camera ID', sortable: true },
  { key: 'name', label: 'Name', sortable: true },
  { key: 'status', label: 'Status', type: 'status', sortable: true },
  { key: 'detectionEnabled', label: 'Detection', type: 'status' },
  { key: 'imageQuality', label: 'Quality', sortable: true },
  { key: 'locationAddress', label: 'Location' },
  { key: 'createdAt', label: 'Created', type: 'date', sortable: true }
];

const filteredCameras = computed(() => {
  if (!statusFilter.value) return cameras.value;
  return cameras.value.filter(camera => camera.status === statusFilter.value);
});

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'status-active',
    inactive: 'status-inactive',
    error: 'status-error'
  };
  return statusMap[status] || '';
};

const loadCameras = async () => {
  loading.value = true;
  error.value = '';
  
  try {
    cameras.value = await communicationService.getCameras();
  } catch (err) {
    error.value = 'Failed to load cameras';
    console.error('Load cameras error:', err);
  } finally {
    loading.value = false;
  }
};

const viewCamera = (camera: Camera) => {
  router.push(`/cameras/${camera.id}`);
};

const editCamera = (camera: Camera) => {
  cameraForm.value = {
    cameraId: camera.cameraId,
    name: camera.name,
    locationAddress: camera.locationAddress || '',
    locationLat: camera.locationLat || null,
    locationLng: camera.locationLng || null,
    imageQuality: camera.imageQuality,
    uploadInterval: camera.uploadInterval || 30,
    detectionEnabled: camera.detectionEnabled
  };
  showEditModal.value = true;
};

const viewDetections = (camera: Camera) => {
  router.push(`/detections?cameraId=${camera.cameraId}`);
};

const confirmDeleteCamera = (camera: Camera) => {
  cameraToDelete.value = camera;
  showDeleteModal.value = true;
};

const saveCamera = async () => {
  saving.value = true;
  
  try {
    if (showEditModal.value && cameraToDelete.value) {
      await communicationService.updateCamera(cameraToDelete.value.id, cameraForm.value);
    } else {
      await communicationService.createCamera(cameraForm.value);
    }
    
    closeModal();
    loadCameras();
  } catch (err) {
    console.error('Save camera error:', err);
  } finally {
    saving.value = false;
  }
};

const deleteCamera = async () => {
  if (!cameraToDelete.value) return;
  
  deleting.value = true;
  
  try {
    await communicationService.deleteCamera(cameraToDelete.value.id);
    cancelDelete();
    loadCameras();
  } catch (err) {
    console.error('Delete camera error:', err);
  } finally {
    deleting.value = false;
  }
};

const closeModal = () => {
  showAddModal.value = false;
  showEditModal.value = false;
  cameraForm.value = {
    cameraId: '',
    name: '',
    locationAddress: '',
    locationLat: null,
    locationLng: null,
    imageQuality: 'medium',
    uploadInterval: 30,
    detectionEnabled: true
  };
};

const cancelDelete = () => {
  showDeleteModal.value = false;
  cameraToDelete.value = null;
};

onMounted(() => {
  loadCameras();
});
</script>

<style scoped>
.cameras-view {
  padding: 1.5rem;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.view-content {
  background: white;
  border-radius: 0.5rem;
  overflow: hidden;
}

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
  padding: 2rem;
  border-radius: 0.5rem;
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.camera-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group label {
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.form-group input[type="checkbox"] {
  width: auto;
  margin-right: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}

.select {
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  background: white;
  font-size: 0.875rem;
}

.btn-primary, .btn-secondary, .btn-danger {
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

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.btn-link:hover {
  background: #f3f4f6;
}

.btn-link.delete {
  color: #ef4444;
}

.btn-link.delete:hover {
  background: #fef2f2;
}

.status-active {
  color: #10b981;
  font-weight: 500;
}

.status-inactive {
  color: #6b7280;
}

.status-error {
  color: #ef4444;
  font-weight: 500;
}
</style>
