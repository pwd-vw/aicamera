<template>
  <div class="system-control">
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold mb-8 text-center">AI Camera System Control</h1>
      
      <!-- Status Section -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">System Status</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="font-medium">Backend Service:</span>
            <span :class="statusColors.backend" class="px-2 py-1 rounded text-sm font-medium">
              {{ systemStatus.backend || 'Unknown' }}
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="font-medium">Frontend Service:</span>
            <span :class="statusColors.frontend" class="px-2 py-1 rounded text-sm font-medium">
              {{ systemStatus.frontend || 'Unknown' }}
            </span>
          </div>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="font-medium">Backend Port (3000):</span>
            <span :class="portStatus.backend ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 rounded text-sm font-medium">
              {{ portStatus.backend ? 'In Use' : 'Not In Use' }}
            </span>
          </div>
          <div class="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span class="font-medium">Frontend Port (5173):</span>
            <span :class="portStatus.frontend ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 rounded text-sm font-medium">
              {{ portStatus.frontend ? 'In Use' : 'Not In Use' }}
            </span>
          </div>
        </div>
        <button 
          @click="refreshStatus" 
          :disabled="loading"
          class="mt-4 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
        >
          {{ loading ? 'Refreshing...' : 'Refresh Status' }}
        </button>
      </div>

      <!-- Control Buttons -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Service Control</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            @click="installServices" 
            :disabled="loading"
            class="bg-green-500 hover:bg-green-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
          >
            Install Services
          </button>
          <button 
            @click="startServices" 
            :disabled="loading"
            class="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
          >
            Start Services
          </button>
          <button 
            @click="stopServices" 
            :disabled="loading"
            class="bg-yellow-500 hover:bg-yellow-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
          >
            Stop Services
          </button>
          <button 
            @click="restartServices" 
            :disabled="loading"
            class="bg-purple-500 hover:bg-purple-600 disabled:bg-gray-400 text-white px-4 py-2 rounded transition-colors"
          >
            Restart Services
          </button>
        </div>
      </div>

      <!-- Build and Deploy -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 class="text-xl font-semibold mb-4">Build & Deploy</h2>
        <button 
          @click="buildAndDeploy" 
          :disabled="loading"
          class="bg-indigo-500 hover:bg-indigo-600 disabled:bg-gray-400 text-white px-6 py-2 rounded transition-colors"
        >
          {{ loading ? 'Building...' : 'Build & Deploy' }}
        </button>
      </div>

      <!-- Logs Section -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <h2 class="text-xl font-semibold mb-4">Recent Activity</h2>
        <div class="bg-gray-900 text-green-400 p-4 rounded font-mono text-sm h-64 overflow-y-auto">
          <div v-for="(log, index) in logs" :key="index" class="mb-1">
            <span class="text-gray-500">[{{ log.timestamp }}]</span> {{ log.message }}
          </div>
          <div v-if="logs.length === 0" class="text-gray-600">
            No activity logs yet...
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div v-if="toast.show" class="fixed top-4 right-4 z-50">
      <div :class="toastClasses" class="px-6 py-3 rounded shadow-lg">
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// Reactive data
const loading = ref(false)
const systemStatus = ref({
  backend: 'Unknown',
  frontend: 'Unknown'
})
const portStatus = ref({
  backend: false,
  frontend: false
})
const logs = ref<Array<{timestamp: string, message: string}>>([])
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// Computed properties
const statusColors = computed(() => ({
  backend: systemStatus.value.backend === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
  frontend: systemStatus.value.frontend === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
}))

const toastClasses = computed(() => {
  const base = 'px-6 py-3 rounded shadow-lg'
  switch (toast.value.type) {
    case 'success': return `${base} bg-green-500 text-white`
    case 'error': return `${base} bg-red-500 text-white`
    case 'warning': return `${base} bg-yellow-500 text-white`
    default: return `${base} bg-blue-500 text-white`
  }
})

// Methods
const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

const addLog = (message: string) => {
  logs.value.unshift({
    timestamp: new Date().toLocaleTimeString(),
    message
  })
  if (logs.value.length > 50) {
    logs.value = logs.value.slice(0, 50)
  }
}

const refreshStatus = async () => {
  loading.value = true
  try {
    const response = await axios.get('/system/status')
    if (response.data.success) {
      addLog('Status refreshed successfully')
      // Parse the status output to extract service and port status
      parseStatusOutput(response.data.status)
    } else {
      addLog(`Failed to refresh status: ${response.data.error}`)
      showToast('Failed to refresh status', 'error')
    }
  } catch (error) {
    addLog(`Error refreshing status: ${error}`)
    showToast('Error refreshing status', 'error')
  } finally {
    loading.value = false
  }
}

const parseStatusOutput = (output: string) => {
  // Parse the status output to extract service status
  const lines = output.split('\n')
  for (const line of lines) {
    if (line.includes('aicamera-backend:')) {
      systemStatus.value.backend = line.includes('ACTIVE') ? 'ACTIVE' : 'INACTIVE'
    }
    if (line.includes('aicamera-frontend:')) {
      systemStatus.value.frontend = line.includes('ACTIVE') ? 'ACTIVE' : 'INACTIVE'
    }
    if (line.includes('Port 3000')) {
      portStatus.value.backend = line.includes('is in use')
    }
    if (line.includes('Port 5173')) {
      portStatus.value.frontend = line.includes('is in use')
    }
  }
}

const installServices = async () => {
  loading.value = true
  try {
    const response = await axios.post('/system/install')
    if (response.data.success) {
      addLog('Services installed successfully')
      showToast('Services installed successfully', 'success')
    } else {
      addLog(`Failed to install services: ${response.data.error}`)
      showToast('Failed to install services', 'error')
    }
  } catch (error) {
    addLog(`Error installing services: ${error}`)
    showToast('Error installing services', 'error')
  } finally {
    loading.value = false
  }
}

const startServices = async () => {
  loading.value = true
  try {
    const response = await axios.post('/system/start')
    if (response.data.success) {
      addLog('Services started successfully')
      showToast('Services started successfully', 'success')
      setTimeout(refreshStatus, 2000)
    } else {
      addLog(`Failed to start services: ${response.data.error}`)
      showToast('Failed to start services', 'error')
    }
  } catch (error) {
    addLog(`Error starting services: ${error}`)
    showToast('Error starting services', 'error')
  } finally {
    loading.value = false
  }
}

const stopServices = async () => {
  loading.value = true
  try {
    const response = await axios.post('/system/stop')
    if (response.data.success) {
      addLog('Services stopped successfully')
      showToast('Services stopped successfully', 'success')
      setTimeout(refreshStatus, 2000)
    } else {
      addLog(`Failed to stop services: ${response.data.error}`)
      showToast('Failed to stop services', 'error')
    }
  } catch (error) {
    addLog(`Error stopping services: ${error}`)
    showToast('Error stopping services', 'error')
  } finally {
    loading.value = false
  }
}

const restartServices = async () => {
  loading.value = true
  try {
    const response = await axios.post('/system/restart')
    if (response.data.success) {
      addLog('Services restarted successfully')
      showToast('Services restarted successfully', 'success')
      setTimeout(refreshStatus, 2000)
    } else {
      addLog(`Failed to restart services: ${response.data.error}`)
      showToast('Failed to restart services', 'error')
    }
  } catch (error) {
    addLog(`Error restarting services: ${error}`)
    showToast('Error restarting services', 'error')
  } finally {
    loading.value = false
  }
}

const buildAndDeploy = async () => {
  loading.value = true
  try {
    const response = await axios.post('/system/build')
    if (response.data.success) {
      addLog('Build and deploy completed successfully')
      showToast('Build and deploy completed successfully', 'success')
      setTimeout(refreshStatus, 2000)
    } else {
      addLog(`Failed to build and deploy: ${response.data.error}`)
      showToast('Failed to build and deploy', 'error')
    }
  } catch (error) {
    addLog(`Error building and deploying: ${error}`)
    showToast('Error building and deploying', 'error')
  } finally {
    loading.value = false
  }
}

// Lifecycle
onMounted(() => {
  refreshStatus()
})
</script>

<style scoped>
.system-control {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}
</style>
