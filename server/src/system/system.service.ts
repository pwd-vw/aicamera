import { Injectable, Logger } from '@nestjs/common';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

@Injectable()
export class SystemService {
  private readonly logger = new Logger(SystemService.name);
  private readonly controlScript = '/home/devuser/aicamera/scripts/aicamera-control.sh';

  async getSystemStatus() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} status`);
      return {
        success: true,
        status: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to get system status: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async startServices() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} start`);
      this.logger.log('Services started successfully');
      return {
        success: true,
        message: 'Services started successfully',
        output: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to start services: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async stopServices() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} stop`);
      this.logger.log('Services stopped successfully');
      return {
        success: true,
        message: 'Services stopped successfully',
        output: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to stop services: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async restartServices() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} restart`);
      this.logger.log('Services restarted successfully');
      return {
        success: true,
        message: 'Services restarted successfully',
        output: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to restart services: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async installServices() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} install`);
      this.logger.log('Services installed successfully');
      return {
        success: true,
        message: 'Services installed successfully',
        output: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to install services: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }

  async buildAndDeploy() {
    try {
      const { stdout } = await execAsync(`${this.controlScript} deploy`);
      this.logger.log('Build and deploy completed successfully');
      return {
        success: true,
        message: 'Build and deploy completed successfully',
        output: stdout,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      this.logger.error(`Failed to build and deploy: ${errorMessage}`);
      return {
        success: false,
        error: errorMessage,
        timestamp: new Date().toISOString(),
      };
    }
  }
}
