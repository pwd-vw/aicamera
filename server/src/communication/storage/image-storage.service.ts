import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as fs from 'fs';
import * as path from 'path';
import * as crypto from 'crypto';
import { promisify } from 'util';
import { spawn } from 'child_process';
import { EventEmitter } from 'events';
import * as sharp from 'sharp';

export interface ImageMetadata {
  filename: string;
  originalName?: string;
  deviceId: string;
  timestamp: string;
  size: number;
  checksum: string;
  mimeType: string;
  width?: number;
  height?: number;
  processingTime?: number;
}

export interface RsyncOptions {
  source: string;
  destination: string;
  excludePatterns?: string[];
  includePatterns?: string[];
  dryRun?: boolean;
  deleteExtraneous?: boolean;
  compress?: boolean;
  preservePermissions?: boolean;
  recursive?: boolean;
}

export interface StorageStats {
  totalFiles: number;
  totalSize: number;
  deviceCounts: Record<string, number>;
  recentFiles: string[];
}

@Injectable()
export class ImageStorageService extends EventEmitter {
  private readonly logger = new Logger(ImageStorageService.name);
  private readonly storagePath: string;
  private readonly thumbnailPath: string;
  private readonly tempPath: string;

  constructor(private readonly configService: ConfigService) {
    super();
    
    this.storagePath = this.configService.get<string>('IMAGE_STORAGE_PATH', './image_storage');
    this.thumbnailPath = path.join(this.storagePath, '_thumbnails');
    this.tempPath = path.join(this.storagePath, '_temp');
    
    this.initializeStorage();
  }

  private async initializeStorage(): Promise<void> {
    try {
      // Create main directories
      await this.ensureDirectoryExists(this.storagePath);
      await this.ensureDirectoryExists(this.thumbnailPath);
      await this.ensureDirectoryExists(this.tempPath);

      this.logger.log(`Image storage initialized at: ${this.storagePath}`);
    } catch (error) {
      this.logger.error(`Failed to initialize image storage: ${error.message}`);
      throw error;
    }
  }

  async storeImage(deviceId: string, imageBuffer: Buffer, metadata?: Partial<ImageMetadata>): Promise<ImageMetadata> {
    try {
      const timestamp = new Date().toISOString();
      const checksum = crypto.createHash('sha256').update(imageBuffer).digest('hex');
      
      // Generate filename
      const filename = this.generateFilename(deviceId, timestamp, checksum);
      const devicePath = await this.ensureDeviceDirectory(deviceId);
      const fullPath = path.join(devicePath, filename);

      // Get image info
      let imageInfo: { width?: number; height?: number; format?: string } = {};
      try {
        const sharpImage = sharp(imageBuffer);
        const sharpMetadata = await sharpImage.metadata();
        imageInfo = {
          width: sharpMetadata.width,
          height: sharpMetadata.height,
          format: sharpMetadata.format,
        };
      } catch (error) {
        this.logger.warn(`Could not extract image metadata: ${error.message}`);
      }

      // Write image file
      await promisify(fs.writeFile)(fullPath, imageBuffer);

      // Create metadata object
      const imageMetadata: ImageMetadata = {
        filename,
        originalName: metadata?.originalName,
        deviceId,
        timestamp,
        size: imageBuffer.length,
        checksum,
        mimeType: this.getMimeTypeFromBuffer(imageBuffer),
        width: imageInfo.width,
        height: imageInfo.height,
        processingTime: metadata?.processingTime,
      };

      // Generate thumbnail
      await this.generateThumbnail(fullPath, deviceId, filename);

      // Save metadata
      await this.saveImageMetadata(imageMetadata);

      this.logger.log(`Image stored: ${filename} (${imageBuffer.length} bytes)`);
      this.emit('image-stored', imageMetadata);

      return imageMetadata;

    } catch (error) {
      this.logger.error(`Failed to store image: ${error.message}`);
      throw error;
    }
  }

  async getImage(deviceId: string, filename: string): Promise<Buffer | null> {
    try {
      const imagePath = path.join(this.storagePath, deviceId, filename);
      
      if (!fs.existsSync(imagePath)) {
        return null;
      }

      return await promisify(fs.readFile)(imagePath);
    } catch (error) {
      this.logger.error(`Failed to get image ${filename}: ${error.message}`);
      return null;
    }
  }

  async getThumbnail(deviceId: string, filename: string): Promise<Buffer | null> {
    try {
      const thumbnailFilename = this.getThumbnailFilename(filename);
      const thumbnailPath = path.join(this.thumbnailPath, deviceId, thumbnailFilename);
      
      if (!fs.existsSync(thumbnailPath)) {
        return null;
      }

      return await promisify(fs.readFile)(thumbnailPath);
    } catch (error) {
      this.logger.error(`Failed to get thumbnail ${filename}: ${error.message}`);
      return null;
    }
  }

  async deleteImage(deviceId: string, filename: string): Promise<boolean> {
    try {
      const imagePath = path.join(this.storagePath, deviceId, filename);
      const thumbnailFilename = this.getThumbnailFilename(filename);
      const thumbnailPath = path.join(this.thumbnailPath, deviceId, thumbnailFilename);

      // Delete main image
      if (fs.existsSync(imagePath)) {
        await promisify(fs.unlink)(imagePath);
      }

      // Delete thumbnail
      if (fs.existsSync(thumbnailPath)) {
        await promisify(fs.unlink)(thumbnailPath);
      }

      this.logger.log(`Image deleted: ${filename}`);
      this.emit('image-deleted', { deviceId, filename });
      
      return true;
    } catch (error) {
      this.logger.error(`Failed to delete image ${filename}: ${error.message}`);
      return false;
    }
  }

  async listImages(deviceId: string, limit?: number, offset?: number): Promise<string[]> {
    try {
      const devicePath = path.join(this.storagePath, deviceId);
      
      if (!fs.existsSync(devicePath)) {
        return [];
      }

      const files = await promisify(fs.readdir)(devicePath);
      const imageFiles = files
        .filter(file => this.isImageFile(file))
        .sort((a, b) => b.localeCompare(a)) // Sort by name (descending = newest first)
        .slice(offset || 0, (offset || 0) + (limit || 100));

      return imageFiles;
    } catch (error) {
      this.logger.error(`Failed to list images for device ${deviceId}: ${error.message}`);
      return [];
    }
  }

  async getStorageStats(): Promise<StorageStats> {
    try {
      const stats: StorageStats = {
        totalFiles: 0,
        totalSize: 0,
        deviceCounts: {},
        recentFiles: [],
      };

      const devices = await promisify(fs.readdir)(this.storagePath);
      
      for (const device of devices) {
        if (device.startsWith('_')) continue; // Skip special directories

        const devicePath = path.join(this.storagePath, device);
        const deviceStat = await promisify(fs.stat)(devicePath);
        
        if (!deviceStat.isDirectory()) continue;

        const files = await promisify(fs.readdir)(devicePath);
        const imageFiles = files.filter(file => this.isImageFile(file));
        
        stats.deviceCounts[device] = imageFiles.length;
        stats.totalFiles += imageFiles.length;

        // Calculate total size and collect recent files
        for (const file of imageFiles) {
          const filePath = path.join(devicePath, file);
          const fileStat = await promisify(fs.stat)(filePath);
          stats.totalSize += fileStat.size;

          // Add to recent files (last 10 files overall)
          if (stats.recentFiles.length < 10) {
            stats.recentFiles.push(`${device}/${file}`);
          }
        }
      }

      // Sort recent files by name (which includes timestamp)
      stats.recentFiles.sort((a, b) => b.localeCompare(a));
      stats.recentFiles = stats.recentFiles.slice(0, 10);

      return stats;
    } catch (error) {
      this.logger.error(`Failed to get storage stats: ${error.message}`);
      return {
        totalFiles: 0,
        totalSize: 0,
        deviceCounts: {},
        recentFiles: [],
      };
    }
  }

  async syncWithRsync(options: RsyncOptions): Promise<{ success: boolean; output: string }> {
    return new Promise((resolve) => {
      try {
        const args = this.buildRsyncArgs(options);
        
        this.logger.log(`Starting rsync: rsync ${args.join(' ')}`);
        
        const rsync = spawn('rsync', args);
        let output = '';
        let errorOutput = '';

        rsync.stdout.on('data', (data) => {
          output += data.toString();
        });

        rsync.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        rsync.on('close', (code) => {
          if (code === 0) {
            this.logger.log('Rsync completed successfully');
            this.emit('rsync-complete', { success: true, output });
            resolve({ success: true, output });
          } else {
            this.logger.error(`Rsync failed with code ${code}: ${errorOutput}`);
            this.emit('rsync-error', { success: false, output: errorOutput });
            resolve({ success: false, output: errorOutput });
          }
        });

        rsync.on('error', (error) => {
          this.logger.error(`Rsync spawn error: ${error.message}`);
          resolve({ success: false, output: error.message });
        });

      } catch (error) {
        this.logger.error(`Rsync setup error: ${error.message}`);
        resolve({ success: false, output: error.message });
      }
    });
  }

  async cleanupOldImages(deviceId: string, retentionDays: number = 30): Promise<number> {
    try {
      const devicePath = path.join(this.storagePath, deviceId);
      
      if (!fs.existsSync(devicePath)) {
        return 0;
      }

      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

      const files = await promisify(fs.readdir)(devicePath);
      let deletedCount = 0;

      for (const file of files) {
        if (!this.isImageFile(file)) continue;

        const filePath = path.join(devicePath, file);
        const stat = await promisify(fs.stat)(filePath);

        if (stat.mtime < cutoffDate) {
          await this.deleteImage(deviceId, file);
          deletedCount++;
        }
      }

      this.logger.log(`Cleaned up ${deletedCount} old images for device ${deviceId}`);
      return deletedCount;
    } catch (error) {
      this.logger.error(`Failed to cleanup old images: ${error.message}`);
      return 0;
    }
  }

  // Private helper methods

  private generateFilename(deviceId: string, timestamp: string, checksum: string): string {
    const date = new Date(timestamp);
    const dateStr = date.toISOString().replace(/[:.]/g, '-').substring(0, 19);
    const checksumShort = checksum.substring(0, 8);
    return `img_${deviceId}_${dateStr}_${checksumShort}.jpg`;
  }

  private getThumbnailFilename(filename: string): string {
    const ext = path.extname(filename);
    const base = path.basename(filename, ext);
    return `${base}_thumb.jpg`;
  }

  private async ensureDeviceDirectory(deviceId: string): Promise<string> {
    const devicePath = path.join(this.storagePath, deviceId);
    await this.ensureDirectoryExists(devicePath);

    // Also ensure thumbnail directory for device
    const deviceThumbnailPath = path.join(this.thumbnailPath, deviceId);
    await this.ensureDirectoryExists(deviceThumbnailPath);

    return devicePath;
  }

  private async ensureDirectoryExists(dirPath: string): Promise<void> {
    try {
      await promisify(fs.mkdir)(dirPath, { recursive: true });
    } catch (error) {
      if (error.code !== 'EEXIST') {
        throw error;
      }
    }
  }

  private async generateThumbnail(imagePath: string, deviceId: string, filename: string): Promise<void> {
    try {
      const thumbnailFilename = this.getThumbnailFilename(filename);
      const thumbnailPath = path.join(this.thumbnailPath, deviceId, thumbnailFilename);

      await sharp(imagePath)
        .resize(200, 200, { fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: 80 })
        .toFile(thumbnailPath);

    } catch (error) {
      this.logger.warn(`Failed to generate thumbnail for ${filename}: ${error.message}`);
    }
  }

  private async saveImageMetadata(metadata: ImageMetadata): Promise<void> {
    try {
      const metadataPath = path.join(this.storagePath, metadata.deviceId, `${metadata.filename}.meta`);
      await promisify(fs.writeFile)(metadataPath, JSON.stringify(metadata, null, 2));
    } catch (error) {
      this.logger.warn(`Failed to save metadata for ${metadata.filename}: ${error.message}`);
    }
  }

  private getMimeTypeFromBuffer(buffer: Buffer): string {
    if (buffer.length < 4) return 'application/octet-stream';

    const header = buffer.subarray(0, 4);
    
    if (header[0] === 0xFF && header[1] === 0xD8 && header[2] === 0xFF) return 'image/jpeg';
    if (header[0] === 0x89 && header[1] === 0x50 && header[2] === 0x4E && header[3] === 0x47) return 'image/png';
    if (header[0] === 0x47 && header[1] === 0x49 && header[2] === 0x46 && header[3] === 0x38) return 'image/gif';
    if (header[0] === 0x52 && header[1] === 0x49 && header[2] === 0x46 && header[3] === 0x46) return 'image/webp';

    return 'application/octet-stream';
  }

  private isImageFile(filename: string): boolean {
    const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff'];
    const ext = path.extname(filename).toLowerCase();
    return imageExtensions.includes(ext);
  }

  private buildRsyncArgs(options: RsyncOptions): string[] {
    const args: string[] = [];

    // Basic options
    if (options.recursive) args.push('-r');
    if (options.compress) args.push('-z');
    if (options.preservePermissions) args.push('-p');
    if (options.deleteExtraneous) args.push('--delete');
    if (options.dryRun) args.push('--dry-run');

    // Always use archive mode for better file handling
    args.push('-a');

    // Verbose output
    args.push('-v');

    // Progress indicator
    args.push('--progress');

    // Include/exclude patterns
    if (options.includePatterns) {
      options.includePatterns.forEach(pattern => {
        args.push('--include', pattern);
      });
    }

    if (options.excludePatterns) {
      options.excludePatterns.forEach(pattern => {
        args.push('--exclude', pattern);
      });
    }

    // Source and destination
    args.push(options.source);
    args.push(options.destination);

    return args;
  }
}