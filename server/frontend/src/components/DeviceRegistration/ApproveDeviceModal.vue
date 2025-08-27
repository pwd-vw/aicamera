<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Approve Device Registration</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>
      
      <div class="modal-body">
        <div class="device-info">
          <h4>Device Information</h4>
          <div class="info-grid">
            <div class="info-item">
              <label>Serial Number:</label>
              <span>{{ device.serialNumber }}</span>
            </div>
            <div class="info-item">
              <label>Device Model:</label>
              <span>{{ device.deviceModel }}</span>
            </div>
            <div class="info-item">
              <label>Device Type:</label>
              <span>{{ device.deviceType }}</span>
            </div>
            <div class="info-item">
              <label>IP Address:</label>
              <span>{{ device.ipAddress || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <label>MAC Address:</label>
              <span>{{ device.macAddress || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <label>Location:</label>
              <span>{{ formatLocation(device) }}</span>
            </div>
            <div class="info-item">
              <label>Registration Type:</label>
              <span>{{ formatRegistrationType(device.registrationType) }}</span>
            </div>
            <div class="info-item">
              <label>Registered:</label>
              <span>{{ formatDate(device.createdAt) }}</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="submitApproval" class="approval-form">
          <div class="form-group">
            <label for="cameraName">Camera Name *</label>
            <input
              id="cameraName"
              v-model="formData.cameraName"
              type="text"
              required
              :placeholder="`Camera ${device.serialNumber}`"
              class="form-control"
            />
          </div>

          <div class="form-group">
            <label for="notes">Approval Notes</label>
            <textarea
              id="notes"
              v-model="formData.notes"
              rows="3"
              placeholder="Optional notes about the approval..."
              class="form-control"
            ></textarea>
          </div>

          <div class="warning-box">
            <strong>⚠️ Important:</strong> Approving this device will generate API credentials and create a camera entity in the system. Make sure you have verified the device information above.
          </div>

          <div class="modal-footer">
            <button type="button" @click="$emit('close')" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="loading" class="btn btn-success">
              <span v-if="loading">Approving...</span>
              <span v-else>Approve Device</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { deviceRegistrationService } from '../../services/deviceRegistrationService'

interface Device {
  id: string
  serialNumber: string
  deviceModel: string
  deviceType: string
  ipAddress?: string
  macAddress?: string
  locationLat?: number
  locationLng?: number
  locationAddress?: string
  registrationStatus: string
  registrationType: string
  createdAt: string
}

const props = defineProps<{
  device: Device
}>()

const emit = defineEmits(['close', 'success'])

const loading = ref(false)

const formData = ref({
  cameraName: '',
  notes: ''
})

const formatLocation = (device: Device) => {
  if (device.locationAddress) return device.locationAddress
  if (device.locationLat && device.locationLng) {
    return `${device.locationLat.toFixed(4)}, ${device.locationLng.toFixed(4)}`
  }
  return 'N/A'
}

const formatRegistrationType = (type: string) => {
  return type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString()
}

const submitApproval = async () => {
  loading.value = true
  
  try {
    const payload = {
      deviceId: props.device.id,
      cameraName: formData.value.cameraName,
      notes: formData.value.notes || undefined
    }

    const result = await deviceRegistrationService.approveDevice(payload)
    
    console.log('Device approved successfully:', result)
    
    // Show generated credentials to admin
    alert(`Device approved successfully!\n\nGenerated Credentials:\nAPI Key: ${result.apiKey}\nJWT Secret: ${result.jwtSecret}\nShared Secret: ${result.sharedSecret}\n\nThe device can now connect using these credentials.`)
    
    emit('success', result)
  } catch (error: any) {
    console.error('Approval failed:', error)
    
    const errorMessage = error.response?.data?.message || error.message || 'Failed to approve device'
    alert(`Approval failed: ${errorMessage}`)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  // Set default camera name
  formData.value.cameraName = `Camera ${props.device.serialNumber}`
})
</script>

<style scoped>
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
  border-radius: 8px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #000;
}

.modal-body {
  padding: 20px;
}

.device-info {
  margin-bottom: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.device-info h4 {
  margin: 0 0 16px 0;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-item label {
  font-weight: 600;
  color: #666;
  font-size: 0.9em;
  margin-bottom: 2px;
}

.info-item span {
  color: #333;
}

.approval-form {
  margin-top: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 600;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-control:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.warning-box {
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 12px;
  margin: 20px 0;
  color: #856404;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #eee;
  margin-top: 20px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #545b62;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #1e7e34;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>