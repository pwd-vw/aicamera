<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>Reject Device Registration</h3>
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
              <label>IP Address:</label>
              <span>{{ device.ipAddress || 'N/A' }}</span>
            </div>
            <div class="info-item">
              <label>Location:</label>
              <span>{{ formatLocation(device) }}</span>
            </div>
          </div>
        </div>

        <form @submit.prevent="submitRejection" class="rejection-form">
          <div class="form-group">
            <label for="reason">Rejection Reason *</label>
            <textarea
              id="reason"
              v-model="formData.reason"
              rows="4"
              required
              placeholder="Please provide a detailed reason for rejecting this device registration..."
              class="form-control"
            ></textarea>
            <div class="help-text">
              This reason will be logged and may be communicated to the device owner.
            </div>
          </div>

          <div class="warning-box">
            <strong>⚠️ Warning:</strong> Rejecting this device will permanently deny its registration. The device will need to re-register to be reconsidered.
          </div>

          <div class="modal-footer">
            <button type="button" @click="$emit('close')" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" :disabled="loading || !formData.reason.trim()" class="btn btn-danger">
              <span v-if="loading">Rejecting...</span>
              <span v-else>Reject Device</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
  reason: ''
})

const formatLocation = (device: Device) => {
  if (device.locationAddress) return device.locationAddress
  if (device.locationLat && device.locationLng) {
    return `${device.locationLat.toFixed(4)}, ${device.locationLng.toFixed(4)}`
  }
  return 'N/A'
}

const submitRejection = async () => {
  if (!formData.value.reason.trim()) {
    alert('Please provide a rejection reason')
    return
  }

  loading.value = true
  
  try {
    const payload = {
      deviceId: props.device.id,
      reason: formData.value.reason.trim()
    }

    const result = await deviceRegistrationService.rejectDevice(payload)
    
    console.log('Device rejected successfully:', result)
    
    alert(`Device registration rejected successfully.\n\nReason: ${formData.value.reason}`)
    
    emit('success', result)
  } catch (error: any) {
    console.error('Rejection failed:', error)
    
    const errorMessage = error.response?.data?.message || error.message || 'Failed to reject device'
    alert(`Rejection failed: ${errorMessage}`)
  } finally {
    loading.value = false
  }
}
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
  max-width: 600px;
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

.rejection-form {
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
  font-family: inherit;
  resize: vertical;
}

.form-control:focus {
  outline: none;
  border-color: #dc3545;
  box-shadow: 0 0 0 2px rgba(220, 53, 69, 0.25);
}

.help-text {
  font-size: 0.85em;
  color: #6c757d;
  margin-top: 4px;
}

.warning-box {
  background: #f8d7da;
  border: 1px solid #f5c6cb;
  border-radius: 4px;
  padding: 12px;
  margin: 20px 0;
  color: #721c24;
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

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c82333;
}

@media (max-width: 768px) {
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>