import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';
import { DeviceRegistrationService } from '../device-registration.service';

@Injectable()
export class DeviceApiKeyGuard implements CanActivate {
  constructor(private deviceRegistrationService: DeviceRegistrationService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    
    // Get API key from headers
    const apiKey = request.headers['x-api-key'] || request.headers['authorization']?.replace('Bearer ', '');
    const serialNumber = request.headers['x-device-serial'] || request.body?.serialNumber;

    if (!apiKey || !serialNumber) {
      throw new UnauthorizedException('Missing API key or device serial number');
    }

    try {
      const device = await this.deviceRegistrationService.validateDeviceCredentials(serialNumber, apiKey);
      
      if (!device) {
        throw new UnauthorizedException('Invalid device credentials');
      }

      // Attach device info to request
      request.device = device;
      return true;
    } catch (error) {
      throw new UnauthorizedException('Device authentication failed');
    }
  }
}