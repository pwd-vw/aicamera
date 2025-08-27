import { Injectable, Logger, OnModuleInit, OnModuleDestroy } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as SSH2 from 'ssh2';
import * as fs from 'fs';
import * as path from 'path';
import { promisify } from 'util';
import * as crypto from 'crypto';
import { EventEmitter } from 'events';

export interface SftpServerConfig {
  port: number;
  hostKeys: string[];
  allowedUsers: Array<{
    username: string;
    password?: string;
    publicKey?: Buffer;
  }>;
  rootPath: string;
  maxConnections: number;
}

export interface FileTransferProgress {
  filename: string;
  deviceId: string;
  transferred: number;
  total: number;
  percentage: number;
  speed: number; // bytes per second
}

@Injectable()
export class SftpService extends EventEmitter implements OnModuleInit, OnModuleDestroy {
  private readonly logger = new Logger(SftpService.name);
  private server: SSH2.Server;
  private isRunning = false;
  private activeConnections = new Set<SSH2.Connection>();
  private transferStats = new Map<string, FileTransferProgress>();

  constructor(private readonly configService: ConfigService) {
    super();
  }

  async onModuleInit() {
    if (this.configService.get<boolean>('SFTP_ENABLED', true)) {
      await this.startServer();
    }
  }

  async onModuleDestroy() {
    await this.stopServer();
  }

  private async startServer(): Promise<void> {
    try {
      const config = this.getServerConfig();
      
      // Ensure upload directory exists
      await this.ensureDirectoryExists(config.rootPath);
      
      this.server = new SSH2.Server({
        hostKeys: config.hostKeys.map(keyPath => fs.readFileSync(keyPath)),
      }, (client, info) => {
        this.handleClient(client, info, config);
      });

      this.server.listen(config.port, '0.0.0.0', () => {
        this.isRunning = true;
        this.logger.log(`SFTP server started on port ${config.port}`);
        this.logger.log(`Root path: ${config.rootPath}`);
        this.emit('server-started', { port: config.port });
      });

      this.server.on('error', (error) => {
        this.logger.error(`SFTP server error: ${error.message}`);
        this.emit('error', error);
      });

    } catch (error) {
      this.logger.error(`Failed to start SFTP server: ${error.message}`);
      throw error;
    }
  }

  private async stopServer(): Promise<void> {
    if (this.server && this.isRunning) {
      this.logger.log('Stopping SFTP server');
      
      // Close all active connections
      this.activeConnections.forEach(connection => {
        connection.end();
      });
      this.activeConnections.clear();
      
      this.server.close();
      this.isRunning = false;
      this.logger.log('SFTP server stopped');
    }
  }

  private getServerConfig(): SftpServerConfig {
    const sftpPort = this.configService.get<number>('SFTP_PORT', 2222);
    const uploadPath = this.configService.get<string>('IMAGE_STORAGE_PATH', './image_storage');
    const maxConnections = this.configService.get<number>('SFTP_MAX_CONNECTIONS', 10);
    
    // Get host keys (generate if not exist)
    const hostKeyPath = this.configService.get<string>('SFTP_HOST_KEY', './ssh_host_key');
    const hostKeys = [this.ensureHostKey(hostKeyPath)];

    // Configure allowed users (devices)
    const allowedUsers = this.getAllowedUsers();

    return {
      port: sftpPort,
      hostKeys,
      allowedUsers,
      rootPath: path.resolve(uploadPath),
      maxConnections,
    };
  }

  private ensureHostKey(keyPath: string): string {
    if (!fs.existsSync(keyPath)) {
      this.logger.log(`Generating SSH host key: ${keyPath}`);
      // Generate SSH host key (in production, use proper SSH key generation)
      const key = crypto.generateKeyPairSync('rsa', {
        modulusLength: 2048,
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
        publicKeyEncoding: { type: 'spki', format: 'pem' }
      });
      fs.writeFileSync(keyPath, key.privateKey);
      fs.chmodSync(keyPath, 0o600);
    }
    return keyPath;
  }

  private getAllowedUsers(): Array<{ username: string; password?: string; publicKey?: Buffer }> {
    // In production, this should come from a secure configuration or database
    const defaultUsers = [
      {
        username: 'aicamera',
        password: this.configService.get<string>('SFTP_PASSWORD', 'aicamera123'),
      }
    ];

    // Add device-specific users from environment
    const deviceUsers = this.configService.get<string>('SFTP_DEVICE_USERS');
    if (deviceUsers) {
      try {
        const users = JSON.parse(deviceUsers);
        defaultUsers.push(...users);
      } catch (error) {
        this.logger.warn('Invalid SFTP_DEVICE_USERS configuration');
      }
    }

    return defaultUsers;
  }

  private handleClient(client: SSH2.Connection, info: SSH2.ClientInfo, config: SftpServerConfig): void {
    const clientId = `${info.ip}:${info.header.remotePort}`;
    this.logger.log(`New SFTP client connected: ${clientId}`);

    if (this.activeConnections.size >= config.maxConnections) {
      this.logger.warn(`Connection rejected: max connections (${config.maxConnections}) exceeded`);
      client.end();
      return;
    }

    this.activeConnections.add(client);

    client.on('authentication', (ctx) => {
      this.handleAuthentication(ctx, config.allowedUsers);
    });

    client.on('ready', () => {
      this.logger.log(`Client authenticated: ${clientId}`);
      
      client.on('session', (accept, reject) => {
        const session = accept();
        
        session.on('sftp', (accept, reject) => {
          const sftp = accept();
          this.handleSftpSession(sftp, clientId, config);
        });
      });
    });

    client.on('close', () => {
      this.logger.log(`Client disconnected: ${clientId}`);
      this.activeConnections.delete(client);
    });

    client.on('error', (error) => {
      this.logger.error(`Client error (${clientId}): ${error.message}`);
      this.activeConnections.delete(client);
    });
  }

  private handleAuthentication(ctx: SSH2.AuthContext, allowedUsers: Array<{ username: string; password?: string; publicKey?: Buffer }>): void {
    const user = allowedUsers.find(u => u.username === ctx.username);
    
    if (!user) {
      this.logger.warn(`Authentication failed: unknown user ${ctx.username}`);
      ctx.reject();
      return;
    }

    if (ctx.method === 'password' && user.password) {
      if (ctx.password === user.password) {
        ctx.accept();
      } else {
        this.logger.warn(`Authentication failed: incorrect password for ${ctx.username}`);
        ctx.reject();
      }
    } else if (ctx.method === 'publickey' && user.publicKey) {
      if (ctx.key && ctx.key.data.equals(user.publicKey)) {
        if (ctx.signature && ctx.key.verify(ctx.blob, ctx.signature)) {
          ctx.accept();
        } else {
          this.logger.warn(`Authentication failed: invalid signature for ${ctx.username}`);
          ctx.reject();
        }
      } else {
        this.logger.warn(`Authentication failed: unknown key for ${ctx.username}`);
        ctx.reject();
      }
    } else {
      this.logger.warn(`Authentication failed: unsupported method ${ctx.method} for ${ctx.username}`);
      ctx.reject();
    }
  }

  private handleSftpSession(sftp: SSH2.SFTPWrapper, clientId: string, config: SftpServerConfig): void {
    this.logger.log(`SFTP session started for client: ${clientId}`);

    sftp.on('OPEN', (reqid, filename, flags, attrs) => {
      const fullPath = path.resolve(config.rootPath, path.relative('/', filename));
      
      // Security check: ensure path is within root directory
      if (!fullPath.startsWith(config.rootPath)) {
        this.logger.warn(`Access denied: path outside root directory: ${filename}`);
        sftp.status(reqid, SSH2.SFTP_STATUS_PERMISSION_DENIED);
        return;
      }

      try {
        const fd = fs.openSync(fullPath, this.getFsFlags(flags));
        const handle = Buffer.allocUnsafe(4);
        handle.writeUInt32BE(fd, 0);
        
        this.logger.debug(`File opened: ${filename}`);
        sftp.handle(reqid, handle);

        // Track file transfer if it's a write operation
        if (flags & SSH2.SFTP_OPEN_WRITE) {
          const deviceId = this.extractDeviceIdFromPath(filename);
          if (deviceId) {
            this.initFileTransfer(filename, deviceId);
          }
        }

      } catch (error) {
        this.logger.error(`Failed to open file ${filename}: ${error.message}`);
        sftp.status(reqid, SSH2.SFTP_STATUS_FAILURE);
      }
    });

    sftp.on('WRITE', (reqid, handle, offset, data) => {
      try {
        const fd = handle.readUInt32BE(0);
        fs.writeSync(fd, data, 0, data.length, offset);
        
        // Update transfer progress
        this.updateTransferProgress(handle.toString('hex'), data.length);
        
        sftp.status(reqid, SSH2.SFTP_STATUS_OK);
        
      } catch (error) {
        this.logger.error(`Write error: ${error.message}`);
        sftp.status(reqid, SSH2.SFTP_STATUS_FAILURE);
      }
    });

    sftp.on('CLOSE', (reqid, handle) => {
      try {
        const fd = handle.readUInt32BE(0);
        fs.closeSync(fd);
        sftp.status(reqid, SSH2.SFTP_STATUS_OK);
        
        // Complete file transfer tracking
        this.completeFileTransfer(handle.toString('hex'));
        
      } catch (error) {
        this.logger.error(`Close error: ${error.message}`);
        sftp.status(reqid, SSH2.SFTP_STATUS_FAILURE);
      }
    });

    sftp.on('MKDIR', (reqid, path, attrs) => {
      try {
        const fullPath = path.resolve(config.rootPath, path.relative('/', path));
        if (!fullPath.startsWith(config.rootPath)) {
          sftp.status(reqid, SSH2.SFTP_STATUS_PERMISSION_DENIED);
          return;
        }

        fs.mkdirSync(fullPath, { recursive: true });
        sftp.status(reqid, SSH2.SFTP_STATUS_OK);
        
      } catch (error) {
        sftp.status(reqid, SSH2.SFTP_STATUS_FAILURE);
      }
    });

    sftp.on('STAT', (reqid, path) => {
      try {
        const fullPath = path.resolve(config.rootPath, path.relative('/', path));
        if (!fullPath.startsWith(config.rootPath)) {
          sftp.status(reqid, SSH2.SFTP_STATUS_PERMISSION_DENIED);
          return;
        }

        const stats = fs.statSync(fullPath);
        sftp.attrs(reqid, {
          mode: stats.mode,
          uid: stats.uid,
          gid: stats.gid,
          size: stats.size,
          atime: Math.floor(stats.atime.getTime() / 1000),
          mtime: Math.floor(stats.mtime.getTime() / 1000),
        });
        
      } catch (error) {
        sftp.status(reqid, SSH2.SFTP_STATUS_NO_SUCH_FILE);
      }
    });
  }

  private getFsFlags(sftpFlags: number): string {
    let flags = '';
    
    if (sftpFlags & SSH2.SFTP_OPEN_READ) flags += 'r';
    if (sftpFlags & SSH2.SFTP_OPEN_WRITE) flags += 'w';
    if (sftpFlags & SSH2.SFTP_OPEN_APPEND) flags += 'a';
    if (sftpFlags & SSH2.SFTP_OPEN_CREAT) flags += 'w';
    if (sftpFlags & SSH2.SFTP_OPEN_TRUNC) flags += 'w';
    
    return flags || 'r';
  }

  private extractDeviceIdFromPath(filename: string): string | null {
    // Extract device ID from path like /device-id/images/file.jpg
    const parts = filename.split('/').filter(p => p.length > 0);
    return parts.length > 0 ? parts[0] : null;
  }

  private initFileTransfer(filename: string, deviceId: string): void {
    const transferId = crypto.createHash('md5').update(`${filename}-${Date.now()}`).digest('hex');
    
    this.transferStats.set(transferId, {
      filename,
      deviceId,
      transferred: 0,
      total: 0,
      percentage: 0,
      speed: 0,
    });
  }

  private updateTransferProgress(transferId: string, bytes: number): void {
    const stats = this.transferStats.get(transferId);
    if (stats) {
      stats.transferred += bytes;
      stats.percentage = stats.total > 0 ? (stats.transferred / stats.total) * 100 : 0;
      
      this.emit('transfer-progress', stats);
    }
  }

  private completeFileTransfer(transferId: string): void {
    const stats = this.transferStats.get(transferId);
    if (stats) {
      this.logger.log(`File transfer completed: ${stats.filename} (${stats.transferred} bytes)`);
      this.emit('transfer-complete', stats);
      this.transferStats.delete(transferId);
    }
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

  // Public API methods

  getServerStatus() {
    return {
      running: this.isRunning,
      activeConnections: this.activeConnections.size,
      port: this.configService.get<number>('SFTP_PORT', 2222),
      rootPath: this.configService.get<string>('IMAGE_STORAGE_PATH', './image_storage'),
    };
  }

  getTransferStats() {
    return Array.from(this.transferStats.values());
  }

  async createDeviceDirectory(deviceId: string): Promise<string> {
    const rootPath = this.configService.get<string>('IMAGE_STORAGE_PATH', './image_storage');
    const devicePath = path.join(rootPath, deviceId);
    
    await this.ensureDirectoryExists(devicePath);
    await this.ensureDirectoryExists(path.join(devicePath, 'images'));
    await this.ensureDirectoryExists(path.join(devicePath, 'temp'));
    
    return devicePath;
  }
}