import { Injectable, ConflictException, NotFoundException, BadRequestException, Logger } from '@nestjs/common';
import { PrismaService } from '../database/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { 
  SelfRegisterDeviceDto, 
  PreProvisionDeviceDto, 
  ApproveDeviceDto, 
  RejectDeviceDto, 
  UpdateDeviceRegistrationDto,
  DeviceHeartbeatDto,
  DeviceRegistrationResponseDto 
} from './dto/device-registration.dto';
import { 
  DeviceRegistration, 
  DeviceRegistrationStatus, 
  DeviceRegistrationType,
  CameraStatus 
} from '../../generated/prisma';
import * as crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class DeviceRegistrationService {
  private readonly logger = new Logger(DeviceRegistrationService.name);

  constructor(
    private readonly prisma: PrismaService,
    private readonly jwtService: JwtService,
  ) {}

  /**
   * Self-registration mechanism: Edge device registers itself
   */
  async selfRegisterDevice(dto: SelfRegisterDeviceDto): Promise<DeviceRegistrationResponseDto> {
    this.logger.log(`Self-registration request from device: ${dto.serialNumber}`);

    // Check if device already exists
    const existingDevice = await this.prisma.deviceRegistration.findUnique({
      where: { serialNumber: dto.serialNumber },
    });

    if (existingDevice) {
      if (existingDevice.registrationStatus === DeviceRegistrationStatus.approved) {
        throw new ConflictException('Device is already registered and approved');
      } else if (existingDevice.registrationStatus === DeviceRegistrationStatus.pending_approval) {
        throw new ConflictException('Device registration is pending approval');
      } else if (existingDevice.registrationStatus === DeviceRegistrationStatus.rejected) {
        throw new ConflictException('Device registration was rejected. Contact administrator.');
      }
    }

    // Create new registration
    const deviceRegistration = await this.prisma.deviceRegistration.create({
      data: {
        serialNumber: dto.serialNumber,
        deviceModel: dto.deviceModel,
        deviceType: dto.deviceType || 'camera',
        ipAddress: dto.ipAddress,
        macAddress: dto.macAddress,
        locationLat: dto.locationLat,
        locationLng: dto.locationLng,
        locationAddress: dto.locationAddress,
        registrationStatus: DeviceRegistrationStatus.pending_approval,
        registrationType: DeviceRegistrationType.self_registration,
        metadata: dto.metadata || {},
      },
    });

    this.logger.log(`Device registered with ID: ${deviceRegistration.id}, awaiting approval`);

    return {
      id: deviceRegistration.id,
      serialNumber: deviceRegistration.serialNumber,
      registrationStatus: deviceRegistration.registrationStatus,
      registrationType: deviceRegistration.registrationType,
      createdAt: deviceRegistration.createdAt,
      message: 'Device registered successfully. Awaiting admin approval.',
    };
  }

  /**
   * Pre-provision mechanism: Admin creates device configuration first
   */
  async preProvisionDevice(dto: PreProvisionDeviceDto, adminUserId: string): Promise<DeviceRegistrationResponseDto> {
    this.logger.log(`Pre-provisioning device: ${dto.serialNumber} by admin: ${adminUserId}`);

    // Check if device already exists
    const existingDevice = await this.prisma.deviceRegistration.findUnique({
      where: { serialNumber: dto.serialNumber },
    });

    if (existingDevice) {
      throw new ConflictException('Device with this serial number already exists');
    }

    // Generate credentials
    const apiKey = this.generateApiKey();
    const jwtSecret = this.generateJwtSecret();
    const sharedSecret = this.generateSharedSecret();

    // Create device registration
    const deviceRegistration = await this.prisma.deviceRegistration.create({
      data: {
        serialNumber: dto.serialNumber,
        deviceModel: dto.deviceModel,
        deviceType: dto.deviceType || 'camera',
        ipAddress: dto.ipAddress,
        macAddress: dto.macAddress,
        locationLat: dto.locationLat,
        locationLng: dto.locationLng,
        locationAddress: dto.locationAddress,
        registrationStatus: DeviceRegistrationStatus.provisioned,
        registrationType: DeviceRegistrationType.pre_provision,
        apiKey,
        jwtSecret,
        sharedSecret,
        metadata: dto.metadata || {},
        approvedBy: adminUserId,
        approvedAt: new Date(),
      },
    });

    // Create camera entity
    await this.prisma.camera.create({
      data: {
        cameraId: dto.serialNumber,
        name: dto.name,
        locationLat: dto.locationLat,
        locationLng: dto.locationLng,
        locationAddress: dto.locationAddress,
        status: CameraStatus.inactive,
        deviceRegistrationId: deviceRegistration.id,
      },
    });

    this.logger.log(`Device pre-provisioned with ID: ${deviceRegistration.id}`);

    return {
      id: deviceRegistration.id,
      serialNumber: deviceRegistration.serialNumber,
      registrationStatus: deviceRegistration.registrationStatus,
      registrationType: deviceRegistration.registrationType,
      apiKey: deviceRegistration.apiKey,
      jwtSecret: deviceRegistration.jwtSecret,
      sharedSecret: deviceRegistration.sharedSecret,
      createdAt: deviceRegistration.createdAt,
      approvedAt: deviceRegistration.approvedAt,
      message: 'Device pre-provisioned successfully. Use the provided credentials for device configuration.',
    };
  }

  /**
   * Admin approval mechanism: Approve pending device
   */
  async approveDevice(dto: ApproveDeviceDto, adminUserId: string): Promise<DeviceRegistrationResponseDto> {
    this.logger.log(`Approving device: ${dto.deviceId} by admin: ${adminUserId}`);

    const deviceRegistration = await this.prisma.deviceRegistration.findUnique({
      where: { id: dto.deviceId },
    });

    if (!deviceRegistration) {
      throw new NotFoundException('Device registration not found');
    }

    if (deviceRegistration.registrationStatus !== DeviceRegistrationStatus.pending_approval) {
      throw new BadRequestException('Device is not in pending approval status');
    }

    // Generate credentials
    const apiKey = this.generateApiKey();
    const jwtSecret = this.generateJwtSecret();
    const sharedSecret = this.generateSharedSecret();

    // Update device registration
    const updatedRegistration = await this.prisma.deviceRegistration.update({
      where: { id: dto.deviceId },
      data: {
        registrationStatus: DeviceRegistrationStatus.approved,
        apiKey,
        jwtSecret,
        sharedSecret,
        approvedBy: adminUserId,
        approvedAt: new Date(),
        metadata: {
          ...deviceRegistration.metadata,
          approvalNotes: dto.notes,
        },
      },
    });

    // Create camera entity
    await this.prisma.camera.create({
      data: {
        cameraId: deviceRegistration.serialNumber,
        name: dto.cameraName || `Camera ${deviceRegistration.serialNumber}`,
        locationLat: deviceRegistration.locationLat,
        locationLng: deviceRegistration.locationLng,
        locationAddress: deviceRegistration.locationAddress,
        status: CameraStatus.inactive,
        deviceRegistrationId: updatedRegistration.id,
      },
    });

    this.logger.log(`Device approved with ID: ${updatedRegistration.id}`);

    return {
      id: updatedRegistration.id,
      serialNumber: updatedRegistration.serialNumber,
      registrationStatus: updatedRegistration.registrationStatus,
      registrationType: updatedRegistration.registrationType,
      apiKey: updatedRegistration.apiKey,
      jwtSecret: updatedRegistration.jwtSecret,
      sharedSecret: updatedRegistration.sharedSecret,
      createdAt: updatedRegistration.createdAt,
      approvedAt: updatedRegistration.approvedAt,
      message: 'Device approved successfully. Credentials have been generated.',
    };
  }

  /**
   * Reject device registration
   */
  async rejectDevice(dto: RejectDeviceDto, adminUserId: string): Promise<{ message: string }> {
    this.logger.log(`Rejecting device: ${dto.deviceId} by admin: ${adminUserId}`);

    const deviceRegistration = await this.prisma.deviceRegistration.findUnique({
      where: { id: dto.deviceId },
    });

    if (!deviceRegistration) {
      throw new NotFoundException('Device registration not found');
    }

    if (deviceRegistration.registrationStatus !== DeviceRegistrationStatus.pending_approval) {
      throw new BadRequestException('Device is not in pending approval status');
    }

    await this.prisma.deviceRegistration.update({
      where: { id: dto.deviceId },
      data: {
        registrationStatus: DeviceRegistrationStatus.rejected,
        rejectedBy: adminUserId,
        rejectedAt: new Date(),
        rejectionReason: dto.reason,
      },
    });

    this.logger.log(`Device rejected: ${dto.deviceId}`);

    return { message: 'Device registration rejected successfully' };
  }

  /**
   * Get device registration by serial number
   */
  async getDeviceBySerialNumber(serialNumber: string): Promise<DeviceRegistration> {
    const device = await this.prisma.deviceRegistration.findUnique({
      where: { serialNumber },
      include: {
        camera: true,
        approvedByUser: {
          select: { id: true, username: true, firstName: true, lastName: true },
        },
      },
    });

    if (!device) {
      throw new NotFoundException('Device not found');
    }

    return device;
  }

  /**
   * Get all device registrations with filtering
   */
  async getAllDevices(
    status?: DeviceRegistrationStatus,
    type?: DeviceRegistrationType,
    limit = 50,
    offset = 0,
  ) {
    const where: any = {};
    if (status) where.registrationStatus = status;
    if (type) where.registrationType = type;

    const [devices, total] = await Promise.all([
      this.prisma.deviceRegistration.findMany({
        where,
        include: {
          camera: true,
          approvedByUser: {
            select: { id: true, username: true, firstName: true, lastName: true },
          },
          rejectedByUser: {
            select: { id: true, username: true, firstName: true, lastName: true },
          },
        },
        orderBy: { createdAt: 'desc' },
        take: limit,
        skip: offset,
      }),
      this.prisma.deviceRegistration.count({ where }),
    ]);

    return {
      devices,
      total,
      limit,
      offset,
    };
  }

  /**
   * Update device heartbeat
   */
  async updateHeartbeat(dto: DeviceHeartbeatDto): Promise<{ message: string }> {
    const device = await this.prisma.deviceRegistration.findUnique({
      where: { serialNumber: dto.serialNumber },
    });

    if (!device) {
      throw new NotFoundException('Device not found');
    }

    if (device.registrationStatus !== DeviceRegistrationStatus.approved && 
        device.registrationStatus !== DeviceRegistrationStatus.provisioned &&
        device.registrationStatus !== DeviceRegistrationStatus.active) {
      throw new BadRequestException('Device is not approved for heartbeat updates');
    }

    await this.prisma.deviceRegistration.update({
      where: { serialNumber: dto.serialNumber },
      data: {
        lastHeartbeat: new Date(),
        ipAddress: dto.ipAddress || device.ipAddress,
        registrationStatus: DeviceRegistrationStatus.active,
        metadata: {
          ...device.metadata,
          lastHeartbeatData: dto.statusData,
        },
      },
    });

    // Update camera status if exists
    if (device.camera) {
      await this.prisma.camera.update({
        where: { deviceRegistrationId: device.id },
        data: { status: CameraStatus.active },
      });
    }

    return { message: 'Heartbeat updated successfully' };
  }

  /**
   * Validate device credentials
   */
  async validateDeviceCredentials(serialNumber: string, apiKey: string): Promise<DeviceRegistration | null> {
    const device = await this.prisma.deviceRegistration.findFirst({
      where: {
        serialNumber,
        apiKey,
        registrationStatus: {
          in: [DeviceRegistrationStatus.approved, DeviceRegistrationStatus.provisioned, DeviceRegistrationStatus.active],
        },
      },
    });

    return device;
  }

  /**
   * Generate API key
   */
  private generateApiKey(): string {
    return `ak_${crypto.randomBytes(32).toString('hex')}`;
  }

  /**
   * Generate JWT secret
   */
  private generateJwtSecret(): string {
    return crypto.randomBytes(64).toString('hex');
  }

  /**
   * Generate shared secret
   */
  private generateSharedSecret(): string {
    return crypto.randomBytes(32).toString('base64');
  }
}