<template>
  <div class="data-table-container">
    <div class="table-header">
      <div class="table-title">
        <h3>{{ title }}</h3>
        <span v-if="totalItems" class="item-count">
          {{ totalItems }} items
        </span>
      </div>
      
      <div class="table-controls">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            :placeholder="searchPlaceholder"
            class="search-input"
          />
        </div>
        
        <div class="filters">
          <slot name="filters"></slot>
        </div>
        
        <div class="actions">
          <button 
            v-if="showRefresh" 
            @click="refresh" 
            :disabled="loading" 
            class="btn-secondary"
          >
            {{ loading ? 'Loading...' : 'Refresh' }}
          </button>
          <slot name="actions"></slot>
        </div>
      </div>
    </div>

    <div class="table-content">
      <div v-if="loading" class="loading-overlay">
        <div class="spinner"></div>
        <p>Loading data...</p>
      </div>
      
      <div v-else-if="error" class="error-message">
        <p>{{ error }}</p>
        <button @click="refresh" class="btn-secondary">Retry</button>
      </div>
      
      <div v-else-if="!items.length" class="empty-state">
        <p>{{ emptyMessage }}</p>
        <button v-if="showRefresh" @click="refresh" class="btn-secondary">Refresh</button>
      </div>
      
      <table v-else class="data-table">
        <thead>
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              :class="{ sortable: column.sortable }"
              @click="column.sortable ? sortBy(column.key) : null"
            >
              <div class="th-content">
                {{ column.label }}
                <span v-if="column.sortable" class="sort-icon">
                  {{ getSortIcon(column.key) }}
                </span>
              </div>
            </th>
            <th v-if="showActions" class="actions-column">Actions</th>
          </tr>
        </thead>
        
        <tbody>
          <tr 
            v-for="item in paginatedItems" 
            :key="getItemKey(item)"
            class="table-row"
            :class="{ selected: selectedItems.includes(getItemKey(item)) }"
            @click="handleRowClick(item)"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              :class="column.class"
            >
              <slot 
                :name="`cell-${column.key}`" 
                :item="item" 
                :value="getItemValue(item, column.key)"
              >
                <span v-if="column.type === 'date'">
                  {{ formatDate(getItemValue(item, column.key)) }}
                </span>
                <span v-else-if="column.type === 'status'" :class="getStatusClass(getItemValue(item, column.key))">
                  {{ getItemValue(item, column.key) }}
                </span>
                <span v-else-if="column.type === 'number'">
                  {{ formatNumber(getItemValue(item, column.key)) }}
                </span>
                <span v-else>
                  {{ getItemValue(item, column.key) }}
                </span>
              </slot>
            </td>
            <td v-if="showActions" class="actions-cell">
              <slot name="row-actions" :item="item">
                <button @click.stop="viewItem(item)" class="btn-link">View</button>
                <button @click.stop="editItem(item)" class="btn-link">Edit</button>
                <button @click.stop="deleteItem(item)" class="btn-link delete">Delete</button>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showPagination && totalPages > 1" class="pagination">
      <button 
        @click="goToPage(currentPage - 1)" 
        :disabled="currentPage === 1"
        class="btn-secondary"
      >
        Previous
      </button>
      
      <div class="page-numbers">
        <button 
          v-for="page in visiblePages" 
          :key="page"
          @click="goToPage(page)"
          :class="{ active: page === currentPage }"
          class="page-btn"
        >
          {{ page }}
        </button>
      </div>
      
      <button 
        @click="goToPage(currentPage + 1)" 
        :disabled="currentPage === totalPages"
        class="btn-secondary"
      >
        Next
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';

export interface TableColumn {
  key: string;
  label: string;
  type?: 'text' | 'number' | 'date' | 'status';
  sortable?: boolean;
  class?: string;
}

interface Props {
  title: string;
  columns: TableColumn[];
  items: any[];
  loading?: boolean;
  error?: string;
  searchPlaceholder?: string;
  emptyMessage?: string;
  showActions?: boolean;
  showRefresh?: boolean;
  showPagination?: boolean;
  itemsPerPage?: number;
  selectable?: boolean;
  itemKey?: string;
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  error: '',
  searchPlaceholder: 'Search...',
  emptyMessage: 'No data available',
  showActions: true,
  showRefresh: true,
  showPagination: true,
  itemsPerPage: 10,
  selectable: false,
  itemKey: 'id'
});

const emit = defineEmits<{
  refresh: [];
  'row-click': [item: any];
  'view-item': [item: any];
  'edit-item': [item: any];
  'delete-item': [item: any];
  'selection-change': [items: any[]];
}>();

const searchQuery = ref('');
const currentPage = ref(1);
const sortKey = ref('');
const sortDirection = ref<'asc' | 'desc'>('asc');
const selectedItems = ref<string[]>([]);

const filteredItems = computed(() => {
  let filtered = props.items;
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase();
    filtered = filtered.filter(item => 
      Object.values(item).some(value => 
        String(value).toLowerCase().includes(query)
      )
    );
  }
  
  if (sortKey.value) {
    filtered = [...filtered].sort((a, b) => {
      const aVal = getItemValue(a, sortKey.value);
      const bVal = getItemValue(b, sortKey.value);
      
      if (aVal < bVal) return sortDirection.value === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection.value === 'asc' ? 1 : -1;
      return 0;
    });
  }
  
  return filtered;
});

const totalItems = computed(() => filteredItems.value.length);
const totalPages = computed(() => Math.ceil(totalItems.value / props.itemsPerPage));

const paginatedItems = computed(() => {
  const start = (currentPage.value - 1) * props.itemsPerPage;
  const end = start + props.itemsPerPage;
  return filteredItems.value.slice(start, end);
});

const visiblePages = computed(() => {
  const pages = [];
  const maxVisible = 5;
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2));
  let end = Math.min(totalPages.value, start + maxVisible - 1);
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1);
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i);
  }
  
  return pages;
});

const getItemKey = (item: any) => {
  return item[props.itemKey] || item.id || JSON.stringify(item);
};

const getItemValue = (item: any, key: string) => {
  return key.split('.').reduce((obj, k) => obj?.[k], item);
};

const getSortIcon = (key: string) => {
  if (sortKey.value !== key) return '↕';
  return sortDirection.value === 'asc' ? '↑' : '↓';
};

const getStatusClass = (status: string) => {
  const statusMap: Record<string, string> = {
    active: 'status-active',
    inactive: 'status-inactive',
    error: 'status-error',
    pending: 'status-pending',
    completed: 'status-completed'
  };
  return statusMap[status?.toLowerCase()] || '';
};

const formatDate = (date: any) => {
  if (!date) return '';
  return new Date(date).toLocaleString();
};

const formatNumber = (num: any) => {
  if (num === null || num === undefined) return '';
  return new Intl.NumberFormat().format(num);
};

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    sortKey.value = key;
    sortDirection.value = 'asc';
  }
};

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page;
  }
};

const refresh = () => {
  emit('refresh');
};

const handleRowClick = (item: any) => {
  if (props.selectable) {
    const key = getItemKey(item);
    const index = selectedItems.value.indexOf(key);
    
    if (index > -1) {
      selectedItems.value.splice(index, 1);
    } else {
      selectedItems.value.push(key);
    }
    
    const selectedData = props.items.filter(item => 
      selectedItems.value.includes(getItemKey(item))
    );
    emit('selection-change', selectedData);
  }
  
  emit('row-click', item);
};

const viewItem = (item: any) => {
  emit('view-item', item);
};

const editItem = (item: any) => {
  emit('edit-item', item);
};

const deleteItem = (item: any) => {
  emit('delete-item', item);
};

watch(searchQuery, () => {
  currentPage.value = 1;
});

watch(() => props.items, () => {
  currentPage.value = 1;
  selectedItems.value = [];
});
</script>

<style scoped>
.data-table-container {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: white;
}

.table-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.table-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.item-count {
  font-size: 0.875rem;
  color: #6b7280;
}

.table-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 200px;
}

.search-input {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  font-size: 0.875rem;
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.table-content {
  position: relative;
  min-height: 200px;
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
  padding: 2rem;
  text-align: center;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: #f9fafb;
  padding: 0.75rem;
  text-align: left;
  font-weight: 600;
  font-size: 0.875rem;
  color: #374151;
  border-bottom: 1px solid #e5e7eb;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #f3f4f6;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.sort-icon {
  font-size: 0.75rem;
  color: #6b7280;
}

.data-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.875rem;
}

.table-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.table-row:hover {
  background: #f9fafb;
}

.table-row.selected {
  background: #eff6ff;
}

.actions-column {
  width: 120px;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
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

.btn-secondary {
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.25rem;
  background: white;
  color: #374151;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.page-numbers {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  background: white;
  color: #374151;
  cursor: pointer;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.page-btn:hover {
  background: #f3f4f6;
}

.page-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
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

.status-pending {
  color: #f59e0b;
  font-weight: 500;
}

.status-completed {
  color: #3b82f6;
  font-weight: 500;
}
</style>
