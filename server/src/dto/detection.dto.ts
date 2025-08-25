import { IsString, IsOptional, IsNumber, IsEnum, IsNotEmpty, Length, IsUrl, IsObject, IsDateString, Min, Max } from 'class-validator';
import { DetectionStatus } from '../../generated/prisma';
import { IsLicensePlate, IsCoordinate } from '../decorators/validation.decorators';

export class CreateDetectionDto {
  @IsString()
  @IsNotEmpty({ message: 'Camera ID is required' })
  cameraId: string;

  @IsDateString({}, { message: 'Timestamp must be a valid ISO date string' })
  @IsNotEmpty({ message: 'Timestamp is required' })
  timestamp: string;

  @IsString()
  @IsNotEmpty({ message: 'License plate is required' })
  @IsLicensePlate({ message: 'License plate must be in valid format' })
  licensePlate: string;

  @IsNumber()
  @Min(0, { message: 'Confidence must be between 0 and 1' })
  @Max(1, { message: 'Confidence must be between 0 and 1' })
  confidence: number;

  @IsOptional()
  @IsUrl({}, { message: 'Image URL must be a valid URL' })
  imageUrl?: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Image path must be between 1 and 500 characters' })
  imagePath?: string;

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
  @Length(1, 100, { message: 'Vehicle make must be between 1 and 100 characters' })
  vehicleMake?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Vehicle model must be between 1 and 100 characters' })
  vehicleModel?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle color must be between 1 and 50 characters' })
  vehicleColor?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle type must be between 1 and 50 characters' })
  vehicleType?: string;

  @IsOptional()
  @IsEnum(DetectionStatus, { message: 'Status must be one of: pending, processed, failed' })
  status?: DetectionStatus;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class UpdateDetectionDto {
  @IsOptional()
  @IsString()
  @IsLicensePlate({ message: 'License plate must be in valid format' })
  licensePlate?: string;

  @IsOptional()
  @IsNumber()
  @Min(0, { message: 'Confidence must be between 0 and 1' })
  @Max(1, { message: 'Confidence must be between 0 and 1' })
  confidence?: number;

  @IsOptional()
  @IsUrl({}, { message: 'Image URL must be a valid URL' })
  imageUrl?: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Image path must be between 1 and 500 characters' })
  imagePath?: string;

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
  @Length(1, 100, { message: 'Vehicle make must be between 1 and 100 characters' })
  vehicleMake?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Vehicle model must be between 1 and 100 characters' })
  vehicleModel?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle color must be between 1 and 50 characters' })
  vehicleColor?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle type must be between 1 and 50 characters' })
  vehicleType?: string;

  @IsOptional()
  @IsEnum(DetectionStatus, { message: 'Status must be one of: pending, processed, failed' })
  status?: DetectionStatus;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}

export class DetectionQueryDto {
  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  @IsLicensePlate({ message: 'License plate must be in valid format' })
  licensePlate?: string;

  @IsOptional()
  @IsEnum(DetectionStatus, { message: 'Status must be one of: pending, processed, failed' })
  status?: DetectionStatus;

  @IsOptional()
  @IsString()
  vehicleMake?: string;

  @IsOptional()
  @IsString()
  vehicleModel?: string;

  @IsOptional()
  @IsString()
  vehicleColor?: string;

  @IsOptional()
  @IsString()
  vehicleType?: string;

  @IsOptional()
  @IsDateString({}, { message: 'Start date must be a valid ISO date string' })
  startDate?: string;

  @IsOptional()
  @IsDateString({}, { message: 'End date must be a valid ISO date string' })
  endDate?: string;

  @IsOptional()
  @IsNumber()
  @Min(0, { message: 'Min confidence must be between 0 and 1' })
  @Max(1, { message: 'Min confidence must be between 0 and 1' })
  minConfidence?: number;

  @IsOptional()
  @IsNumber()
  @Min(0, { message: 'Max confidence must be between 0 and 1' })
  @Max(1, { message: 'Max confidence must be between 0 and 1' })
  maxConfidence?: number;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Page must be at least 1' })
  page?: number;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Limit must be at least 1' })
  @Max(100, { message: 'Limit cannot exceed 100' })
  limit?: number;
}

export class DetectionStatsDto {
  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsDateString({}, { message: 'Start date must be a valid ISO date string' })
  startDate?: string;

  @IsOptional()
  @IsDateString({}, { message: 'End date must be a valid ISO date string' })
  endDate?: string;

  @IsOptional()
  @IsString()
  groupBy?: 'day' | 'hour' | 'camera' | 'vehicle_make' | 'vehicle_color';
}
