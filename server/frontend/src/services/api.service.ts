import api from '../utils/api';

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  firstName?: string;
  lastName?: string;
  role?: string;
}

export interface Camera {
  id: string;
  cameraId: string;
  name: string;
  locationLat?: number;
  locationLng?: number;
  locationAddress?: string;
  status: string;
  detectionEnabled: boolean;
  imageQuality: string;
  uploadInterval?: number;
  configuration?: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export interface Detection {
  id: string;
  cameraId: string;
  timestamp: string;
  licensePlate: string;
  confidence: number;
  imageUrl?: string;
  imagePath?: string;
  locationLat?: number;
  locationLng?: number;
  vehicleMake?: string;
  vehicleModel?: string;
  vehicleColor?: string;
  vehicleType?: string;
  status: string;
  metadata?: Record<string, any>;
  createdAt: string;
}

export interface AnalyticsEvent {
  id: string;
  eventType: string;
  eventCategory: string;
  userId?: string;
  sessionId?: string;
  cameraId?: string;
  visualizationId?: string;
  eventData?: Record<string, any>;
  ipAddress?: string;
  userAgent?: string;
  createdAt: string;
}

export interface Visualization {
  id: string;
  name: string;
  description?: string;
  type: string;
  configuration: Record<string, any>;
  dataSource: string;
  refreshInterval?: number;
  isActive: boolean;
  createdBy?: string;
  createdAt: string;
  updatedAt: string;
}

export class ApiService {
  // Authentication
  async login(data: LoginRequest) {
    const response = await api.post('/auth/login', data);
    return response.data;
  }

  async register(data: RegisterRequest) {
    const response = await api.post('/auth/register', data);
    return response.data;
  }

  async refreshToken() {
    const response = await api.post('/auth/refresh');
    return response.data;
  }

  async getProfile() {
    const response = await api.get('/auth/profile');
    return response.data;
  }

  async updateProfile(data: Partial<RegisterRequest>) {
    const response = await api.put('/auth/profile', data);
    return response.data;
  }

  async changePassword(currentPassword: string, newPassword: string) {
    const response = await api.put('/auth/change-password', {
      currentPassword,
      newPassword,
    });
    return response.data;
  }

  async logout() {
    const response = await api.post('/auth/logout');
    return response.data;
  }

  // Cameras
  async getCameras() {
    const response = await api.get('/cameras');
    return response.data;
  }

  async getCamera(id: string) {
    const response = await api.get(`/cameras/${id}`);
    return response.data;
  }

  async createCamera(data: Partial<Camera>) {
    const response = await api.post('/cameras', data);
    return response.data;
  }

  async updateCamera(id: string, data: Partial<Camera>) {
    const response = await api.put(`/cameras/${id}`, data);
    return response.data;
  }

  async deleteCamera(id: string) {
    const response = await api.delete(`/cameras/${id}`);
    return response.data;
  }

  async getCameraHealth(id: string) {
    const response = await api.get(`/cameras/${id}/health`);
    return response.data;
  }

  async getCameraConfig(id: string) {
    const response = await api.get(`/cameras/${id}/config`);
    return response.data;
  }

  async updateCameraConfig(id: string, config: any) {
    const response = await api.put(`/cameras/${id}/config`, config);
    return response.data;
  }

  // Detections
  async getDetections(params?: {
    cameraId?: string;
    licensePlate?: string;
    status?: string;
    startDate?: string;
    endDate?: string;
    minConfidence?: number;
    maxConfidence?: number;
    page?: number;
    limit?: number;
  }) {
    const response = await api.get('/detections', { params });
    return response.data;
  }

  async getDetection(id: string) {
    const response = await api.get(`/detections/${id}`);
    return response.data;
  }

  async createDetection(data: Partial<Detection>) {
    const response = await api.post('/detections', data);
    return response.data;
  }

  async updateDetection(id: string, data: Partial<Detection>) {
    const response = await api.put(`/detections/${id}`, data);
    return response.data;
  }

  async deleteDetection(id: string) {
    const response = await api.delete(`/detections/${id}`);
    return response.data;
  }

  async getDetectionStats(params?: {
    cameraId?: string;
    startDate?: string;
    endDate?: string;
    groupBy?: string;
  }) {
    const response = await api.get('/detections/stats', { params });
    return response.data;
  }

  // Analytics Events
  async getAnalyticsEvents(params?: {
    eventType?: string;
    eventCategory?: string;
    userId?: string;
    cameraId?: string;
    startDate?: string;
    endDate?: string;
    page?: number;
    limit?: number;
  }) {
    const response = await api.get('/analytics-events', { params });
    return response.data;
  }

  async createAnalyticsEvent(data: Partial<AnalyticsEvent>) {
    const response = await api.post('/analytics-events', data);
    return response.data;
  }

  async getAnalyticsStats(params?: {
    eventType?: string;
    eventCategory?: string;
    userId?: string;
    cameraId?: string;
    startDate?: string;
    endDate?: string;
    groupBy?: string;
  }) {
    const response = await api.get('/analytics-events/stats', { params });
    return response.data;
  }

  // Visualizations
  async getVisualizations(params?: {
    name?: string;
    type?: string;
    dataSource?: string;
    isActive?: boolean;
    createdBy?: string;
    page?: number;
    limit?: number;
  }) {
    const response = await api.get('/visualizations', { params });
    return response.data;
  }

  async getVisualization(id: string) {
    const response = await api.get(`/visualizations/${id}`);
    return response.data;
  }

  async createVisualization(data: Partial<Visualization>) {
    const response = await api.post('/visualizations', data);
    return response.data;
  }

  async updateVisualization(id: string, data: Partial<Visualization>) {
    const response = await api.put(`/visualizations/${id}`, data);
    return response.data;
  }

  async deleteVisualization(id: string) {
    const response = await api.delete(`/visualizations/${id}`);
    return response.data;
  }

  async getActiveVisualizations() {
    const response = await api.get('/visualizations/active');
    return response.data;
  }

  // Users (Admin only)
  async getUsers() {
    const response = await api.get('/users');
    return response.data;
  }

  async getUser(id: string) {
    const response = await api.get(`/users/${id}`);
    return response.data;
  }

  async updateUser(id: string, data: any) {
    const response = await api.put(`/users/${id}`, data);
    return response.data;
  }

  async deleteUser(id: string) {
    const response = await api.delete(`/users/${id}`);
    return response.data;
  }

  async getUserStats() {
    const response = await api.get('/users/stats');
    return response.data;
  }

  // Rate Limiting Monitoring (Admin only)
  async getRateLimitStats(params?: {
    startDate?: string;
    endDate?: string;
  }) {
    const response = await api.get('/rate-limit-monitoring/stats', { params });
    return response.data;
  }

  async getRateLimitAlerts() {
    const response = await api.get('/rate-limit-monitoring/alerts');
    return response.data;
  }

  // File Upload
  async uploadFile(file: File, metadata?: any) {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async uploadImage(file: File, metadata?: any) {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }

    const response = await api.post('/upload/image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // System Health
  async getSystemHealth() {
    const response = await api.get('/health');
    return response.data;
  }

  async getSystemStatus() {
    const response = await api.get('/status');
    return response.data;
  }
}

// Create singleton instance
export const apiService = new ApiService();
