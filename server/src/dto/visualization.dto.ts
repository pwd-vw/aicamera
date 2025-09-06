import { IsString, IsOptional, IsEnum, IsNotEmpty, Length, IsObject, IsNumber, Min, Max, IsBoolean, IsArray } from 'class-validator';
import { VisualizationType } from '../../generated/prisma';

export class CreateVisualizationDto {
  @IsString()
  @IsNotEmpty({ message: 'Visualization name is required' })
  @Length(1, 100, { message: 'Name must be between 1 and 100 characters' })
  name: string;

  @IsOptional()
  @IsString()
  @Length(0, 500, { message: 'Description cannot exceed 500 characters' })
  description?: string;

  @IsEnum(VisualizationType)
  type: VisualizationType;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;

  @IsOptional()
  @IsString()
  dataSource?: string;

  @IsOptional()
  @IsNumber()
  @Min(10)
  @Max(86400)
  refreshInterval?: number;
}

export class UpdateVisualizationDto {
  @IsOptional()
  @IsString()
  @Length(1, 255, { message: 'Name must be between 1 and 255 characters' })
  name?: string;

  @IsOptional()
  @IsString()
  @Length(0, 1000, { message: 'Description must not exceed 1000 characters' })
  description?: string;

  @IsOptional()
  @IsEnum(VisualizationType, { message: 'Type must be one of: chart, graph, table, metric, map' })
  type?: VisualizationType;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Data source must be between 1 and 100 characters' })
  dataSource?: string;

  @IsOptional()
  @IsNumber()
  @Min(30, { message: 'Refresh interval must be at least 30 seconds' })
  @Max(86400, { message: 'Refresh interval cannot exceed 24 hours' })
  refreshInterval?: number;

  @IsOptional()
  @IsBoolean()
  isActive?: boolean;
}

export class VisualizationQueryDto {
  @IsOptional()
  @IsString()
  name?: string;

  @IsOptional()
  @IsEnum(VisualizationType, { message: 'Type must be one of: chart, graph, table, metric, map' })
  type?: VisualizationType;

  @IsOptional()
  @IsString()
  dataSource?: string;

  @IsOptional()
  @IsBoolean()
  isActive?: boolean;

  @IsOptional()
  @IsString()
  createdBy?: string;

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

export class VisualizationConfigDto {
  @IsString()
  @IsNotEmpty({ message: 'Chart type is required' })
  chartType: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  dimensions?: string[];

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  metrics?: string[];

  @IsOptional()
  @IsObject()
  options?: Record<string, any>;

  @IsOptional()
  @IsString()
  title?: string;

  @IsOptional()
  @IsString()
  subtitle?: string;

  @IsOptional()
  @IsObject()
  colors?: Record<string, string>;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Height must be at least 1' })
  @Max(1000, { message: 'Height cannot exceed 1000' })
  height?: number;

  @IsOptional()
  @IsNumber()
  @Min(1, { message: 'Width must be at least 1' })
  @Max(1000, { message: 'Width cannot exceed 1000' })
  width?: number;
}
