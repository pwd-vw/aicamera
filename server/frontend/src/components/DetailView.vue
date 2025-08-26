<template>
  <div class="detail-view-container">
    <div class="detail-header">
      <div class="header-content">
        <button @click="goBack" class="back-btn">
          ← Back
        </button>
        <h2>{{ title }}</h2>
      </div>
      
      <div class="header-actions">
        <slot name="header-actions"></slot>
        <button v-if="showEdit" @click="editItem" class="btn-primary">
          Edit
        </button>
        <button v-if="showDelete" @click="confirmDelete" class="btn-danger">
          Delete
        </button>
      </div>
    </div>

    <div class="detail-content">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Loading details...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="refresh" class="btn-secondary">Retry</button>
      </div>
      
      <div v-else-if="!item" class="empty-state">
        <p>No data available</p>
        <button @click="refresh" class="btn-secondary">Refresh</button>
      </div>
      
      <div v-else class="detail-sections">
        <!-- Main Information Section -->
        <section class="detail-section">
          <h3>Information</h3>
          <div class="info-grid">
            <slot name="main-info" :item="item">
              <div v-for="field in mainFields" :key="field.key" class="info-item">
                <label>{{ field.label }}:</label>
                <span :class="getFieldClass(field)">
                  <slot :name="`field-${field.key}`" :value="getFieldValue(item, field.key)">
                    {{ formatFieldValue(getFieldValue(item, field.key), field.type) }}
                  </slot>
                </span>
              </div>
            </slot>
          </div>
        </section>

        <!-- Additional Sections -->
        <slot name="additional-sections" :item="item"></slot>

        <!-- Related Data Section -->
        <section v-if="relatedData.length > 0" class="detail-section">
          <h3>Related Data</h3>
          <div class="related-data">
            <slot name="related-data" :item="item" :related-data="relatedData">
              <div v-for="data in relatedData" :key="data.key" class="related-item">
                <h4>{{ data.title }}</h4>
                <div class="related-content">
                  <slot :name="`related-${data.key}`" :data="data.data">
                    <DataTable 
                      :title="data.title"
                      :columns="data.columns"
                      :items="data.data"
                      :loading="data.loading"
                      :error="data.error"
                      @refresh="loadRelatedData(data.key)"
                    />
                  </slot>
                </div>
              </div>
            </slot>
          </div>
        </section>

        <!-- Metadata Section -->
        <section v-if="showMetadata" class="detail-section">
          <h3>Metadata</h3>
          <div class="metadata-grid">
            <div class="metadata-item">
              <label>Created:</label>
              <span>{{ formatDate(item.createdAt) }}</span>
            </div>
            <div class="metadata-item">
              <label>Updated:</label>
              <span>{{ formatDate(item.updatedAt) }}</span>
            </div>
            <div v-if="item.id" class="metadata-item">
              <label>ID:</label>
              <span class="id-value">{{ item.id }}</span>
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content" @click.stop>
        <h3>Confirm Delete</h3>
        <p>Are you sure you want to delete this item? This action cannot be undone.</p>
        <div class="modal-actions">
          <button @click="cancelDelete" class="btn-secondary">Cancel</button>
          <button @click="deleteItem" class="btn-danger">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import DataTable from './DataTable.vue';

export interface DetailField {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'status' | 'boolean' | 'json';
  class?: string;
}

export interface RelatedData {
  key: string;
  title: string;
  data: any[];
  columns: any[];
  loading: boolean;
  error: string;
}

interface Props {
  title: string;
  item: any;
  loading?: boolean;
  error?: string;
  mainFields?: DetailField[];
  relatedData?: RelatedData[];
  showEdit?: boolean;
  showDelete?: boolean;
  showMetadata?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: '',
  mainFields: () => [],
  relatedData: () => [],
  showEdit: true,
  showDelete: true,
  showMetadata: true
});

const emit = defineEmits<{
  back: [];
  refresh: [];
  edit: [item: any];
  delete: [item: any];
  'load-related': [key: string];
}>();

const showDeleteModal = ref(false);

const getFieldValue = (item: any, key: string) => {
  return key.split('.').reduce((obj, k) => obj?.[k], item);
};

const getFieldClass = (field: DetailField) => {
  const baseClass = 'field-value';
  return field.class ? `${baseClass} ${field.class}` : baseClass;
};

const formatFieldValue = (value: any, type?: string) => {
  if (value === null || value === undefined) return '-';
  
  switch (type) {
    case 'date':
      return new Date(value).toLocaleString();
    case 'boolean':
      return value ? 'Yes' : 'No';
    case 'json':
      return JSON.stringify(value, null, 2);
    case 'number':
      return new Intl.NumberFormat().format(value);
    default:
      return String(value);
  }
};

const formatDate = (dateString: string) => {
  if (!dateString) return '-';
  return new Date(dateString).toLocaleString();
};

const goBack = () => {
  emit('back');
};

const refresh = () => {
  emit('refresh');
};

const editItem = () => {
  emit('edit', props.item);
};

const confirmDelete = () => {
  showDeleteModal.value = true;
};

const cancelDelete = () => {
  showDeleteModal.value = false;
};

const deleteItem = () => {
  emit('delete', props.item);
  showDeleteModal.value = false;
};

const loadRelatedData = (key: string) => {
  emit('load-related', key);
};
</script>

<style scoped>
.detail-view-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.5rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.back-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.detail-content {
  position: relative;
  min-height: 400px;
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
  padding: 3rem;
  text-align: center;
}

.detail-sections {
  padding: 1.5rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h3 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.field-value {
  font-size: 1rem;
  color: #374151;
  word-break: break-word;
}

.related-data {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.related-item h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.metadata-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.metadata-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metadata-item label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #6b7280;
}

.id-value {
  font-family: monospace;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
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
  max-width: 400px;
  width: 90%;
}

.modal-content h3 {
  margin: 0 0 1rem 0;
  color: #374151;
}

.modal-content p {
  margin: 0 0 1.5rem 0;
  color: #6b7280;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
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

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

/* Status field styling */
.field-value.status-active {
  color: #10b981;
  font-weight: 500;
}

.field-value.status-inactive {
  color: #6b7280;
}

.field-value.status-error {
  color: #ef4444;
  font-weight: 500;
}

.field-value.status-pending {
  color: #f59e0b;
  font-weight: 500;
}

.field-value.status-completed {
  color: #3b82f6;
  font-weight: 500;
}

/* JSON field styling */
.field-value.json {
  background: #f9fafb;
  padding: 0.5rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.875rem;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
}
</style>
