export interface DetectionData {
  licensePlate: string;
  timestamp: Date;
  imageUrl: string;
  latitude: number;
  longitude: number;
  edgeDeviceId: string;
  confidence: number;
}

export interface DeviceData {
  id: string;
  name: string;
  ipAddress: string;
  status: string;
  location?: string;
}

export interface CommunicationResponse {
  success: boolean;
  message: string;
  data?: any;
  timestamp: Date;
}

export interface CommunicationProtocol {
  name: string;
  isAvailable(): Promise<boolean>;
  sendDetection(data: DetectionData): Promise<CommunicationResponse>;
  sendDeviceUpdate(data: DeviceData): Promise<CommunicationResponse>;
  sendHealthCheck(): Promise<CommunicationResponse>;
  connect(): Promise<void>;
  disconnect(): Promise<void>;
}
