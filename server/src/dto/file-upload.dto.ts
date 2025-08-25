import { IsString, IsOptional, IsNumber, IsNotEmpty, Length, IsArray, IsEnum, Min, Max } from 'class-validator';
import { IsFileSize, IsFileType } from '../decorators/validation.decorators';

export class FileUploadDto {
  @IsString()
  @IsNotEmpty({ message: 'File name is required' })
  @Length(1, 255, { message: 'File name must be between 1 and 255 characters' })
  filename: string;

  @IsString()
  @IsNotEmpty({ message: 'File type is required' })
  mimetype: string;

  @IsNumber()
  @IsNotEmpty({ message: 'File size is required' })
  size: number;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Description must be between 1 and 500 characters' })
  description?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Category must be between 1 and 100 characters' })
  category?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  detectionId?: string;
}

export class ImageUploadDto extends FileUploadDto {
  @IsFileType(['image/jpeg', 'image/png', 'image/gif', 'image/webp'], { message: 'File must be a valid image type (JPEG, PNG, GIF, WebP)' })
  mimetype: string;

  @IsFileSize(10, { message: 'Image file size must not exceed 10MB' })
  size: number;
}

export class VideoUploadDto extends FileUploadDto {
  @IsFileType(['video/mp4', 'video/avi', 'video/mov', 'video/wmv'], { message: 'File must be a valid video type (MP4, AVI, MOV, WMV)' })
  mimetype: string;

  @IsFileSize(100, { message: 'Video file size must not exceed 100MB' })
  size: number;
}

export class DocumentUploadDto extends FileUploadDto {
  @IsFileType(['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'], { message: 'File must be a valid document type (PDF, DOC, DOCX, TXT)' })
  mimetype: string;

  @IsFileSize(5, { message: 'Document file size must not exceed 5MB' })
  size: number;
}

export class FileQueryDto {
  @IsOptional()
  @IsString()
  filename?: string;

  @IsOptional()
  @IsString()
  category?: string;

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  detectionId?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @IsString()
  mimetype?: string;

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

export class FileUpdateDto {
  @IsOptional()
  @IsString()
  @Length(1, 255, { message: 'File name must be between 1 and 255 characters' })
  filename?: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Description must be between 1 and 500 characters' })
  description?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Category must be between 1 and 100 characters' })
  category?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];
}

export enum FileCategory {
  IMAGE = 'image',
  VIDEO = 'video',
  DOCUMENT = 'document',
  LOG = 'log',
  CONFIG = 'config',
  BACKUP = 'backup',
  OTHER = 'other',
}

export class FileMetadataDto {
  @IsString()
  @IsNotEmpty({ message: 'File ID is required' })
  fileId: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Description must be between 1 and 500 characters' })
  description?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Category must be between 1 and 100 characters' })
  category?: string;

  @IsOptional()
  @IsArray()
  @IsString({ each: true })
  tags?: string[];

  @IsOptional()
  @IsString()
  cameraId?: string;

  @IsOptional()
  @IsString()
  detectionId?: string;
}
