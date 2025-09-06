import { IsString, IsOptional, IsNumber, IsEnum, IsNotEmpty, Length, IsObject, IsDateString, Min, Max } from 'class-validator';
import { AnalyticsEventCategory } from '../../generated/prisma';
import { IsIPAddress } from '../decorators/validation.decorators';

export class CreateAnalyticsEventDto {
  @IsString()
  @IsNotEmpty({ message: 'Event type is required' })
  @Length(1, 100, { message: 'Event type must be between 1 and 100 characters' })
  eventType: string;

  @IsEnum(AnalyticsEventCategory, { message: 'Event category must be one of: user_interaction, system_event, performance, error, security' })
  @IsNotEmpty({ message: 'Event category is required' })
  eventCategory: AnalyticsEventCategory;

  @IsOptional()
  @IsString()
  userId?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Session ID must be between 1 and 100 characters' })
  sessionId?: string;

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  visualizationId?: string;

  @IsOptional()
  @IsObject()
  eventData?: Record<string, any>;

  @IsOptional()
  @IsIPAddress({ message: 'IP address must be a valid IP address' })
  ipAddress?: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'User agent must be between 1 and 500 characters' })
  userAgent?: string;
}

export class AnalyticsEventQueryDto {
  @IsOptional()
  @IsString()
  eventType?: string;

  @IsOptional()
  @IsEnum(AnalyticsEventCategory, { message: 'Event category must be one of: user_interaction, system_event, performance, error, security' })
  eventCategory?: AnalyticsEventCategory;

  @IsOptional()
  @IsString()
  userId?: string;

  @IsOptional()
  @IsString()
  sessionId?: string;

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  visualizationId?: string;

  @IsOptional()
  @IsIPAddress({ message: 'IP address must be a valid IP address' })
  ipAddress?: string;

  @IsOptional()
  @IsDateString({}, { message: 'Start date must be a valid ISO date string' })
  startDate?: string;

  @IsOptional()
  @IsDateString({}, { message: 'End date must be a valid ISO date string' })
  endDate?: string;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Page must be at least 1' })
  page?: number;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Limit must be at least 1' })
  @Max(1000, { message: 'Limit cannot exceed 1000' })
  limit?: number;
}

export class AnalyticsStatsQueryDto {
  @IsOptional()
  @IsString()
  eventType?: string;

  @IsOptional()
  @IsEnum(AnalyticsEventCategory, { message: 'Event category must be one of: user_interaction, system_event, performance, error, security' })
  eventCategory?: AnalyticsEventCategory;

  @IsOptional()
  @IsString()
  userId?: string;

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  visualizationId?: string;

  @IsOptional()
  @IsIPAddress({ message: 'IP address must be a valid IP address' })
  ipAddress?: string;

  @IsOptional()
  @IsDateString({}, { message: 'Start date must be a valid ISO date string' })
  startDate?: string;

  @IsOptional()
  @IsDateString({}, { message: 'End date must be a valid ISO date string' })
  endDate?: string;

  @IsOptional()
  @IsString()
  groupBy?: 'hour' | 'day' | 'week' | 'month' | 'event_type' | 'event_category' | 'user_id' | 'camera_id' | 'ip_address';
}

export class AnalyticsExportDto {
  @IsOptional()
  @IsString()
  eventType?: string;

  @IsOptional()
  @IsEnum(AnalyticsEventCategory, { message: 'Event category must be one of: user_interaction, system_event, performance, error, security' })
  eventCategory?: AnalyticsEventCategory;

  @IsOptional()
  @IsString()
  userId?: string;

  @IsOptional()
  @IsDateString({}, { message: 'Start date must be a valid ISO date string' })
  startDate?: string;

  @IsOptional()
  @IsDateString({}, { message: 'End date must be a valid ISO date string' })
  endDate?: string;

  @IsOptional()
  @IsString()
  format?: 'csv' | 'json' | 'xlsx';

  @IsOptional()
  @IsString()
  @Length(1, 255, { message: 'Filename must be between 1 and 255 characters' })
  filename?: string;
}
