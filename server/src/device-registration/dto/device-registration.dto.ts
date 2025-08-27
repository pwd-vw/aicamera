import { IsString, IsOptional, IsEnum, IsDecimal, IsIP, IsMACAddress, IsObject, IsUUID, MinLength, MaxLength } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { DeviceRegistrationType, DeviceRegistrationStatus } from '../../../generated/prisma';

export class SelfRegisterDeviceDto {
  @ApiProperty({ description: 'Device serial number', example: 'CAM001-2024-001' })
  @IsString()
  @MinLength(5)
  @MaxLength(100)
  serialNumber: string;

  @ApiProperty({ description: 'Device model', example: 'AI-CAM-4K-V2' })
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  deviceModel: string;

  @ApiPropertyOptional({ description: 'Device type', example: 'camera', default: 'camera' })
  @IsOptional()
  @IsString()
  deviceType?: string;

  @ApiPropertyOptional({ description: 'Device IP address', example: '192.168.1.100' })
  @IsOptional()
  @IsIP()
  ipAddress?: string;

  @ApiPropertyOptional({ description: 'Device MAC address', example: '00:1B:44:11:3A:B7' })
  @IsOptional()
  @IsMACAddress()
  macAddress?: string;

  @ApiPropertyOptional({ description: 'Latitude', example: 13.7563 })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLat?: number;

  @ApiPropertyOptional({ description: 'Longitude', example: 100.5018 })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLng?: number;

  @ApiPropertyOptional({ description: 'Location address', example: 'Bangkok, Thailand' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  locationAddress?: string;

  @ApiPropertyOptional({ description: 'Additional device metadata' })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class PreProvisionDeviceDto extends SelfRegisterDeviceDto {
  @ApiProperty({ description: 'Device name', example: 'Main Entrance Camera' })
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  name: string;

  @ApiPropertyOptional({ description: 'Pre-generate API key' })
  @IsOptional()
  @IsString()
  generateApiKey?: boolean;

  @ApiPropertyOptional({ description: 'Pre-generate JWT secret' })
  @IsOptional()
  @IsString()
  generateJwtSecret?: boolean;
}

export class ApproveDeviceDto {
  @ApiProperty({ description: 'Device registration ID' })
  @IsUUID()
  deviceId: string;

  @ApiPropertyOptional({ description: 'Approval notes' })
  @IsOptional()
  @IsString()
  @MaxLength(500)
  notes?: string;

  @ApiPropertyOptional({ description: 'Camera name for approved device' })
  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  cameraName?: string;
}

export class RejectDeviceDto {
  @ApiProperty({ description: 'Device registration ID' })
  @IsUUID()
  deviceId: string;

  @ApiProperty({ description: 'Rejection reason' })
  @IsString()
  @MinLength(10)
  @MaxLength(500)
  reason: string;
}

export class UpdateDeviceRegistrationDto {
  @ApiPropertyOptional({ description: 'Device name' })
  @IsOptional()
  @IsString()
  @MinLength(3)
  @MaxLength(100)
  name?: string;

  @ApiPropertyOptional({ description: 'Location latitude' })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLat?: number;

  @ApiPropertyOptional({ description: 'Location longitude' })
  @IsOptional()
  @IsDecimal({ decimal_digits: '0,8' })
  locationLng?: number;

  @ApiPropertyOptional({ description: 'Location address' })
  @IsOptional()
  @IsString()
  @MaxLength(255)
  locationAddress?: string;

  @ApiPropertyOptional({ description: 'Registration status' })
  @IsOptional()
  @IsEnum(DeviceRegistrationStatus)
  registrationStatus?: DeviceRegistrationStatus;

  @ApiPropertyOptional({ description: 'Additional metadata' })
  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class DeviceHeartbeatDto {
  @ApiProperty({ description: 'Device serial number' })
  @IsString()
  serialNumber: string;

  @ApiPropertyOptional({ description: 'Current IP address' })
  @IsOptional()
  @IsIP()
  ipAddress?: string;

  @ApiPropertyOptional({ description: 'Device status information' })
  @IsOptional()
  @IsObject()
  statusData?: Record<string, any>;
}

export class DeviceRegistrationResponseDto {
  @ApiProperty({ description: 'Registration ID' })
  id: string;

  @ApiProperty({ description: 'Serial number' })
  serialNumber: string;

  @ApiProperty({ description: 'Registration status' })
  registrationStatus: DeviceRegistrationStatus;

  @ApiProperty({ description: 'Registration type' })
  registrationType: DeviceRegistrationType;

  @ApiPropertyOptional({ description: 'API key for device authentication' })
  apiKey?: string;

  @ApiPropertyOptional({ description: 'JWT secret for device authentication' })
  jwtSecret?: string;

  @ApiPropertyOptional({ description: 'Shared secret for device authentication' })
  sharedSecret?: string;

  @ApiProperty({ description: 'Registration timestamp' })
  createdAt: Date;

  @ApiPropertyOptional({ description: 'Approval timestamp' })
  approvedAt?: Date;

  @ApiProperty({ description: 'Success message' })
  message: string;
}