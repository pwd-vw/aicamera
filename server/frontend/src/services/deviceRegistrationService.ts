import axios from 'axios'

const API_BASE = '/api'

export interface DeviceRegistration {
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
  apiKey?: string
  jwtSecret?: string
  sharedSecret?: string
  metadata: Record<string, any>
  lastHeartbeat?: string
  createdAt: string
  updatedAt: string
  approvedAt?: string
  rejectedAt?: string
  rejectionReason?: string
  camera?: {
    id: string
    name: string
    cameraId: string
    status: string
  }
  approvedByUser?: {
    id: string
    username: string
    firstName?: string
    lastName?: string
  }
  rejectedByUser?: {
    id: string
    username: string
    firstName?: string
    lastName?: string
  }
}

export interface DeviceRegistrationFilters {
  status?: string
  type?: string
  limit?: number
  offset?: number
}

export interface PreProvisionDeviceData {
  serialNumber: string
  deviceModel: string
  name: string
  deviceType?: string
  ipAddress?: string
  macAddress?: string
  locationLat?: number
  locationLng?: number
  locationAddress?: string
  metadata?: Record<string, any>
}

export interface ApproveDeviceData {
  deviceId: string
  notes?: string
  cameraName?: string
}

export interface RejectDeviceData {
  deviceId: string
  reason: string
}

class DeviceRegistrationService {
  private getAuthHeaders() {
    const token = localStorage.getItem('auth_token')
    return token ? { Authorization: `Bearer ${token}` } : {}
  }

  async getAllDevices(filters: DeviceRegistrationFilters = {}) {
    const params = new URLSearchParams()
    if (filters.status) params.append('status', filters.status)
    if (filters.type) params.append('type', filters.type)
    if (filters.limit) params.append('limit', filters.limit.toString())
    if (filters.offset) params.append('offset', filters.offset.toString())

    const response = await axios.get(`${API_BASE}/device-registration?${params}`, {
      headers: this.getAuthHeaders()
    })
    
    return response.data
  }

  async getDeviceBySerialNumber(serialNumber: string): Promise<DeviceRegistration> {
    const response = await axios.get(`${API_BASE}/device-registration/serial/${serialNumber}`, {
      headers: this.getAuthHeaders()
    })
    
    return response.data
  }

  async getDeviceById(id: string): Promise<DeviceRegistration> {
    const response = await axios.get(`${API_BASE}/device-registration/${id}`, {
      headers: this.getAuthHeaders()
    })
    
    return response.data
  }

  async getPendingApprovals() {
    const response = await axios.get(`${API_BASE}/device-registration/pending/approvals`, {
      headers: this.getAuthHeaders()
    })
    
    return response.data
  }

  async preProvisionDevice(data: PreProvisionDeviceData) {
    const response = await axios.post(`${API_BASE}/device-registration/pre-provision`, data, {
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json'
      }
    })
    
    return response.data
  }

  async approveDevice(data: ApproveDeviceData) {
    const response = await axios.post(`${API_BASE}/device-registration/approve`, data, {
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json'
      }
    })
    
    return response.data
  }

  async rejectDevice(data: RejectDeviceData) {
    const response = await axios.post(`${API_BASE}/device-registration/reject`, data, {
      headers: {
        ...this.getAuthHeaders(),
        'Content-Type': 'application/json'
      }
    })
    
    return response.data
  }

  async getDeviceStatus(serialNumber: string) {
    const response = await axios.get(`${API_BASE}/device-registration/status/${serialNumber}`, {
      headers: {
        'X-API-Key': 'your-device-api-key', // This would come from device credentials
        'X-Device-Serial': serialNumber
      }
    })
    
    return response.data
  }

  // Statistics and monitoring
  async getRegistrationStats() {
    try {
      const [allDevices, pendingDevices] = await Promise.all([
        this.getAllDevices(),
        this.getPendingApprovals()
      ])

      const devices = allDevices.devices || []
      const pending = pendingDevices.devices || []

      const stats = {
        total: devices.length,
        pending: pending.length,
        approved: devices.filter((d: DeviceRegistration) => d.registrationStatus === 'approved').length,
        active: devices.filter((d: DeviceRegistration) => d.registrationStatus === 'active').length,
        rejected: devices.filter((d: DeviceRegistration) => d.registrationStatus === 'rejected').length,
        provisioned: devices.filter((d: DeviceRegistration) => d.registrationStatus === 'provisioned').length,
        byType: {
          self_registration: devices.filter((d: DeviceRegistration) => d.registrationType === 'self_registration').length,
          pre_provision: devices.filter((d: DeviceRegistration) => d.registrationType === 'pre_provision').length,
          admin_approval: devices.filter((d: DeviceRegistration) => d.registrationType === 'admin_approval').length,
        },
        onlineDevices: devices.filter((d: DeviceRegistration) => {
          if (!d.lastHeartbeat) return false
          const now = new Date()
          const heartbeat = new Date(d.lastHeartbeat)
          const diffMinutes = (now.getTime() - heartbeat.getTime()) / (1000 * 60)
          return diffMinutes < 5 // Consider online if heartbeat within 5 minutes
        }).length
      }

      return stats
    } catch (error) {
      console.error('Failed to get registration stats:', error)
      throw error
    }
  }
}

export const deviceRegistrationService = new DeviceRegistrationService()
export default deviceRegistrationService