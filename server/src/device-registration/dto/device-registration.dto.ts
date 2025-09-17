import { IsString, IsOptional, IsEnum, IsDecimal, IsIP, IsMACAddress, IsObject, IsUUID, MinLength, MaxLength } from 'class-validator';
// import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { DeviceRegistrationType, DeviceRegistrationStatus } from '../../../generated/prisma';

export class SelfRegisterDeviceDto {
  @IsString()
  @MinLength(5)
  @MaxLength(100)
  serialNumber: string;

({ description: 'Device model', example: 'AI-CAM-4K-V2' })
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  deviceModel: string;

Optional({ description: 'Device type', example: 'camera', default: 'camera' })
  @IsOptional()
  @IsString()
  deviceType?: string;

Optional({ description: 'Device IP address', example: '192.168.1.100' })
  @IsOptional()
  @IsIP()
  ipAddress?: string;

Optional({ description: 'Device MAC address', example: '00:1B:44:11:3A:B7' })
  @IsOptional()
  @IsMACAddress()
  macAddress?: string;

Optional({ description: 'Latitude', example: 13.7563 })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLat?: number;

Optional({ description: 'Longitude', example: 100.5018 })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLng?: number;

Optional({ description: 'Location address', example: 'Bangkok, Thailand' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  locationAddress?: string;

Optional({ description: 'Additional device metadata' })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class PreProvisionDeviceDto extends SelfRegisterDeviceDto {
({ description: 'Device name', example: 'Main Entrance Camera' })
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  name: string;

Optional({ description: 'Pre-generate API key' })
  @IsOptional()
  @IsString()
  generateApiKey?: boolean;

Optional({ description: 'Pre-generate JWT secret' })
  @IsOptional()
  @IsString()
  generateJwtSecret?: boolean;
}

export class ApproveDeviceDto {
({ description: 'Device registration ID' })
  @IsUUID()
  deviceId: string;

Optional({ description: 'Approval notes' })
  @IsOptional()
  @IsString()
  @MaxLength(500)
  notes?: string;

Optional({ description: 'Camera name for approved device' })
  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  cameraName?: string;
}

export class RejectDeviceDto {
({ description: 'Device registration ID' })
  @IsUUID()
  deviceId: string;

({ description: 'Rejection reason' })
  @IsString()
  @MinLength(10)
  @MaxLength(500)
  reason: string;
}

export class UpdateDeviceRegistrationDto {
Optional({ description: 'Device name' })
  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  name?: string;

Optional({ description: 'Location latitude' })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLat?: number;

Optional({ description: 'Location longitude' })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLng?: number;

Optional({ description: 'Location address' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  locationAddress?: string;

Optional({ description: 'Registration status' })
  @IsOptional()
  @IsEnum(DeviceRegistrationStatus)
  registrationStatus?: DeviceRegistrationStatus;

Optional({ description: 'Additional metadata' })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class DeviceHeartbeatDto {
({ description: 'Device serial number' })
  @IsString()
  serialNumber: string;

Optional({ description: 'Current IP address' })
  @IsOptional()
  @IsIP()
  ipAddress?: string;

Optional({ description: 'Device status information' })
  @IsOptional()
  @IsObject()
  statusData?: Record<string, any>;
}

export class DeviceRegistrationResponseDto {
({ description: 'Registration ID' })
  id: string;

({ description: 'Serial number' })
  serialNumber: string;

({ description: 'Registration status' })
  registrationStatus: DeviceRegistrationStatus;

({ description: 'Registration type' })
  registrationType: DeviceRegistrationType;

Optional({ description: 'API key for device authentication' })
  apiKey?: string;

Optional({ description: 'JWT secret for device authentication' })
  jwtSecret?: string;

Optional({ description: 'Shared secret for device authentication' })
  sharedSecret?: string;

({ description: 'Registration timestamp' })
  createdAt: Date;

Optional({ description: 'Approval timestamp' })
  approvedAt?: Date;

({ description: 'Success message' })
  message: string;
}