import { IsString, IsOptional, IsNumber, IsBoolean, IsEnum, IsNotEmpty, Length, IsUrl, IsObject } from 'class-validator';
import { CameraStatus, ImageQuality } from '../../generated/prisma';
import { IsCameraId, IsCoordinate } from '../decorators/validation.decorators';

export class CreateCameraDto {
  @IsString()
  @IsNotEmpty({ message: 'Camera ID is required' })
  @IsCameraId({ message: 'Camera ID must be in format cam-XXX' })
  cameraId: string;

  @IsString()
  @IsNotEmpty({ message: 'Camera name is required' })
  @Length(1, 255, { message: 'Camera name must be between 1 and 255 characters' })
  name: string;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Latitude must be between -90 and 90' })
  locationLat?: number;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Longitude must be between -180 and 180' })
  locationLng?: number;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Location address must be between 1 and 500 characters' })
  locationAddress?: string;

  @IsOptional()
  @IsEnum(CameraStatus, { message: 'Status must be one of: active, inactive, maintenance' })
  status?: CameraStatus;

  @IsOptional()
  @IsBoolean()
  detectionEnabled?: boolean;

  @IsOptional()
  @IsEnum(ImageQuality, { message: 'Image quality must be one of: low, medium, high' })
  imageQuality?: ImageQuality;

  @IsOptional()
  @IsNumber()
  uploadInterval?: number;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;
}

export class UpdateCameraDto {
  @IsOptional()
  @IsString()
  @Length(1, 255, { message: 'Camera name must be between 1 and 255 characters' })
  name?: string;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Latitude must be between -90 and 90' })
  locationLat?: number;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Longitude must be between -180 and 180' })
  locationLng?: number;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Location address must be between 1 and 500 characters' })
  locationAddress?: string;

  @IsOptional()
  @IsEnum(CameraStatus, { message: 'Status must be one of: active, inactive, maintenance' })
  status?: CameraStatus;

  @IsOptional()
  @IsBoolean()
  detectionEnabled?: boolean;

  @IsOptional()
  @IsEnum(ImageQuality, { message: 'Image quality must be one of: low, medium, high' })
  imageQuality?: ImageQuality;

  @IsOptional()
  @IsNumber()
  uploadInterval?: number;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;
}

export class CameraConfigDto {
  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Latitude must be between -90 and 90' })
  locationLat?: number;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Longitude must be between -180 and 180' })
  locationLng?: number;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Location address must be between 1 and 500 characters' })
  locationAddress?: string;

  @IsOptional()
  @IsEnum(ImageQuality, { message: 'Image quality must be one of: low, medium, high' })
  imageQuality?: ImageQuality;

  @IsOptional()
  @IsNumber()
  uploadInterval?: number;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;
}

export class CameraHealthDto {
  @IsString()
  @IsNotEmpty({ message: 'Status is required' })
  status: string;

  @IsOptional()
  @IsNumber()
  cpuUsage?: number;

  @IsOptional()
  @IsNumber()
  memoryUsage?: number;

  @IsOptional()
  @IsNumber()
  diskUsage?: number;

  @IsOptional()
  @IsNumber()
  temperature?: number;

  @IsOptional()
  @IsNumber()
  uptimeSeconds?: number;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}
