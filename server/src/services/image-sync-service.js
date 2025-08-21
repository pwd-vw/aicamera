const { Client } = require('ssh2');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');
const logger = require('../utils/logger');

/**
 * Image Synchronization Service
 * Handles SFTP/rsync transfer of captured images from edge to server
 */
class ImageSyncService {
  constructor(config) {
    this.config = {
      sftp: {
        host: config.sftp?.host || 'localhost',
        port: config.sftp?.port || 22,
        username: config.sftp?.username || 'aicamera',
        privateKey: config.sftp?.privateKey || '~/.ssh/id_rsa',
        passphrase: config.sftp?.passphrase
      },
      rsync: {
        options: config.rsync?.options || [
          '-avz',
          '--delete',
          '--progress',
          '--compress',
          '--partial',
          '--timeout=300'
        ],
        excludePatterns: config.rsync?.excludePatterns || [
          '*.tmp',
          '*.temp',
          '*.lock',
          '.DS_Store',
          'Thumbs.db'
        ]
      },
      paths: {
        source: config.paths?.source || '/home/aicamera/captured_images/',
        destination: config.paths?.destination || '/var/lib/aicamera/image_storage/',
        temp: config.paths?.temp || '/tmp/aicamera_sync/'
      },
      schedule: {
        frequency: config.schedule?.frequency || 300000, // 5 minutes
        batchSize: config.schedule?.batchSize || 100,
        maxFileSize: config.schedule?.maxFileSize || 10 * 1024 * 1024 // 10MB
      }
    };

    this.isRunning = false;
    this.syncInterval = null;
    this.edgeConnections = new Map(); // Store edge camera connections
    this.syncQueue = [];
    this.stats = {
      totalFiles: 0,
      totalSize: 0,
      lastSync: null,
      errors: 0,
      success: 0
    };

    this.init();
  }

  /**
   * Initialize the image sync service
   */
  async init() {
    try {
      // Create destination directory if it doesn't exist
      await this.ensureDirectoryExists(this.config.paths.destination);
      await this.ensureDirectoryExists(this.config.paths.temp);

      // Start the sync scheduler
      this.startSyncScheduler();

      logger.info('Image sync service initialized');
    } catch (error) {
      logger.error('Failed to initialize image sync service:', error);
    }
  }

  /**
   * Register an edge camera for image sync
   */
  async registerEdgeCamera(cameraId, edgeConfig) {
    try {
      const connection = {
        cameraId,
        config: {
          ...this.config.sftp,
          host: edgeConfig.host || this.config.sftp.host,
          username: edgeConfig.username || this.config.sftp.username,
          privateKey: edgeConfig.privateKey || this.config.sftp.privateKey
        },
        lastSync: null,
        status: 'registered'
      };

      this.edgeConnections.set(cameraId, connection);
      logger.info('Edge camera registered for image sync:', cameraId);
      
      return true;
    } catch (error) {
      logger.error('Failed to register edge camera:', error);
      return false;
    }
  }

  /**
   * Unregister an edge camera
   */
  unregisterEdgeCamera(cameraId) {
    this.edgeConnections.delete(cameraId);
    logger.info('Edge camera unregistered from image sync:', cameraId);
  }

  /**
   * Start the sync scheduler
   */
  startSyncScheduler() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }

    this.syncInterval = setInterval(() => {
      this.performSync();
    }, this.config.schedule.frequency);

    logger.info('Image sync scheduler started');
  }

  /**
   * Stop the sync scheduler
   */
  stopSyncScheduler() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
    }
    logger.info('Image sync scheduler stopped');
  }

  /**
   * Perform image synchronization
   */
  async performSync() {
    if (this.isRunning) {
      logger.debug('Sync already in progress, skipping');
      return;
    }

    this.isRunning = true;
    logger.info('Starting image synchronization...');

    try {
      for (const [cameraId, connection] of this.edgeConnections) {
        await this.syncCameraImages(cameraId, connection);
      }

      this.stats.lastSync = new Date();
      logger.info('Image synchronization completed');
    } catch (error) {
      logger.error('Image synchronization failed:', error);
      this.stats.errors++;
    } finally {
      this.isRunning = false;
    }
  }

  /**
   * Sync images for a specific camera
   */
  async syncCameraImages(cameraId, connection) {
    try {
      logger.debug(`Syncing images for camera: ${cameraId}`);

      // Create camera-specific destination directory
      const cameraDestDir = path.join(this.config.paths.destination, cameraId);
      await this.ensureDirectoryExists(cameraDestDir);

      // Use rsync for efficient file transfer
      const success = await this.rsyncTransfer(cameraId, connection, cameraDestDir);

      if (success) {
        connection.lastSync = new Date();
        connection.status = 'synced';
        this.stats.success++;
        logger.info(`Successfully synced images for camera: ${cameraId}`);
      } else {
        connection.status = 'failed';
        this.stats.errors++;
        logger.error(`Failed to sync images for camera: ${cameraId}`);
      }

    } catch (error) {
      connection.status = 'error';
      this.stats.errors++;
      logger.error(`Error syncing images for camera ${cameraId}:`, error);
    }
  }

  /**
   * Perform rsync transfer
   */
  async rsyncTransfer(cameraId, connection, destination) {
    return new Promise((resolve, reject) => {
      const sourcePath = `${connection.config.username}@${connection.config.host}:${this.config.paths.source}`;
      
      // Build rsync command
      const rsyncArgs = [
        ...this.config.rsync.options,
        '--exclude-from=-', // Read exclude patterns from stdin
        sourcePath,
        destination
      ];

      logger.debug(`Running rsync: rsync ${rsyncArgs.join(' ')}`);

      const rsyncProcess = spawn('rsync', rsyncArgs, {
        stdio: ['pipe', 'pipe', 'pipe']
      });

      // Send exclude patterns to rsync
      const excludePatterns = this.config.rsync.excludePatterns.join('\n');
      rsyncProcess.stdin.write(excludePatterns);
      rsyncProcess.stdin.end();

      let stdout = '';
      let stderr = '';

      rsyncProcess.stdout.on('data', (data) => {
        stdout += data.toString();
        logger.debug(`rsync stdout: ${data.toString()}`);
      });

      rsyncProcess.stderr.on('data', (data) => {
        stderr += data.toString();
        logger.debug(`rsync stderr: ${data.toString()}`);
      });

      rsyncProcess.on('close', (code) => {
        if (code === 0) {
          logger.info(`rsync completed successfully for camera ${cameraId}`);
          resolve(true);
        } else {
          logger.error(`rsync failed with code ${code} for camera ${cameraId}: ${stderr}`);
          resolve(false);
        }
      });

      rsyncProcess.on('error', (error) => {
        logger.error(`rsync process error for camera ${cameraId}:`, error);
        reject(error);
      });

      // Set timeout
      setTimeout(() => {
        rsyncProcess.kill('SIGTERM');
        logger.warn(`rsync timeout for camera ${cameraId}`);
        resolve(false);
      }, 300000); // 5 minutes timeout
    });
  }

  /**
   * Alternative SFTP transfer method
   */
  async sftpTransfer(cameraId, connection, destination) {
    return new Promise((resolve, reject) => {
      const sftpClient = new Client();

      sftpClient.on('ready', async () => {
        try {
          sftpClient.sftp(async (err, sftp) => {
            if (err) {
              reject(err);
              return;
            }

            try {
              // List files in source directory
              const files = await this.listSftpFiles(sftp, this.config.paths.source);
              
              // Transfer files
              for (const file of files.slice(0, this.config.schedule.batchSize)) {
                await this.transferSftpFile(sftp, file, destination);
              }

              sftpClient.end();
              resolve(true);
            } catch (error) {
              sftpClient.end();
              reject(error);
            }
          });
        } catch (error) {
          sftpClient.end();
          reject(error);
        }
      });

      sftpClient.on('error', (err) => {
        reject(err);
      });

      // Connect to SFTP server
      const connectConfig = {
        host: connection.config.host,
        port: connection.config.port,
        username: connection.config.username
      };

      if (connection.config.privateKey) {
        try {
          const privateKey = await fs.readFile(connection.config.privateKey);
          connectConfig.privateKey = privateKey;
          if (connection.config.passphrase) {
            connectConfig.passphrase = connection.config.passphrase;
          }
        } catch (error) {
          logger.error('Failed to read private key:', error);
          reject(error);
          return;
        }
      }

      sftpClient.connect(connectConfig);
    });
  }

  /**
   * List files in SFTP directory
   */
  listSftpFiles(sftp, remotePath) {
    return new Promise((resolve, reject) => {
      sftp.readdir(remotePath, (err, list) => {
        if (err) {
          reject(err);
          return;
        }

        // Filter for image files
        const imageFiles = list.filter(file => 
          file.attrs.isFile() && 
          /\.(jpg|jpeg|png|bmp|tiff)$/i.test(file.filename)
        );

        resolve(imageFiles);
      });
    });
  }

  /**
   * Transfer a single file via SFTP
   */
  transferSftpFile(sftp, file, destination) {
    return new Promise((resolve, reject) => {
      const remotePath = path.join(this.config.paths.source, file.filename);
      const localPath = path.join(destination, file.filename);

      sftp.fastGet(remotePath, localPath, (err) => {
        if (err) {
          reject(err);
        } else {
          this.stats.totalFiles++;
          this.stats.totalSize += file.attrs.size;
          resolve();
        }
      });
    });
  }

  /**
   * Ensure directory exists
   */
  async ensureDirectoryExists(dirPath) {
    try {
      await fs.access(dirPath);
    } catch (error) {
      await fs.mkdir(dirPath, { recursive: true });
      logger.info(`Created directory: ${dirPath}`);
    }
  }

  /**
   * Get sync statistics
   */
  getStats() {
    return {
      ...this.stats,
      isRunning: this.isRunning,
      registeredCameras: this.edgeConnections.size,
      cameras: Array.from(this.edgeConnections.entries()).map(([id, conn]) => ({
        cameraId: id,
        status: conn.status,
        lastSync: conn.lastSync
      }))
    };
  }

  /**
   * Force sync for a specific camera
   */
  async forceSync(cameraId) {
    const connection = this.edgeConnections.get(cameraId);
    if (!connection) {
      throw new Error(`Camera ${cameraId} not registered for sync`);
    }

    logger.info(`Force syncing images for camera: ${cameraId}`);
    await this.syncCameraImages(cameraId, connection);
  }

  /**
   * Clean up old images
   */
  async cleanupOldImages(retentionDays = 30) {
    try {
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - retentionDays);

      logger.info(`Cleaning up images older than ${retentionDays} days`);

      for (const [cameraId] of this.edgeConnections) {
        const cameraDestDir = path.join(this.config.paths.destination, cameraId);
        await this.cleanupDirectory(cameraDestDir, cutoffDate);
      }

      logger.info('Image cleanup completed');
    } catch (error) {
      logger.error('Image cleanup failed:', error);
    }
  }

  /**
   * Clean up directory by removing old files
   */
  async cleanupDirectory(dirPath, cutoffDate) {
    try {
      const files = await fs.readdir(dirPath);
      
      for (const file of files) {
        const filePath = path.join(dirPath, file);
        const stats = await fs.stat(filePath);
        
        if (stats.mtime < cutoffDate) {
          await fs.unlink(filePath);
          logger.debug(`Deleted old file: ${filePath}`);
        }
      }
    } catch (error) {
      logger.error(`Error cleaning up directory ${dirPath}:`, error);
    }
  }

  /**
   * Stop the service
   */
  async stop() {
    this.stopSyncScheduler();
    this.isRunning = false;
    logger.info('Image sync service stopped');
  }
}

module.exports = ImageSyncService;
