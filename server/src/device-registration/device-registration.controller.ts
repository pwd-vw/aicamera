import {
  Controller,
  Post,
  Get,
  Put,
  Patch,
  Body,
  Param,
  Query,
  UseGuards,
  Request,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiResponse, ApiBearerAuth, ApiQuery } from '@nestjs/swagger';
import { DeviceRegistrationService } from './device-registration.service';
import {
  SelfRegisterDeviceDto,
  PreProvisionDeviceDto,
  ApproveDeviceDto,
  RejectDeviceDto,
  UpdateDeviceRegistrationDto,
  DeviceHeartbeatDto,
  DeviceRegistrationResponseDto,
} from './dto/device-registration.dto';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { DeviceApiKeyGuard } from './guards/device-api-key.guard';
import { DeviceRegistrationStatus, DeviceRegistrationType, UserRole } from '../../generated/prisma';

@ApiTags('Device Registration')
@Controller('device-registration')
export class DeviceRegistrationController {
  constructor(private readonly deviceRegistrationService: DeviceRegistrationService) {}

  /**
   * Self-registration endpoint for edge devices
   */
  @Post('register')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ 
    summary: 'Self-register device',
    description: 'Allows edge devices to register themselves with the server' 
  })
  @ApiResponse({ 
    status: 201, 
    description: 'Device registered successfully', 
    type: DeviceRegistrationResponseDto 
  })
  @ApiResponse({ status: 409, description: 'Device already exists' })
  async selfRegisterDevice(
    @Body() dto: SelfRegisterDeviceDto,
  ): Promise<DeviceRegistrationResponseDto> {
    return this.deviceRegistrationService.selfRegisterDevice(dto);
  }

  /**
   * Pre-provision device (Admin only)
   */
  @Post('pre-provision')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({ 
    summary: 'Pre-provision device',
    description: 'Admin creates device configuration with credentials before device connects' 
  })
  @ApiResponse({ 
    status: 201, 
    description: 'Device pre-provisioned successfully', 
    type: DeviceRegistrationResponseDto 
  })
  @ApiResponse({ status: 409, description: 'Device already exists' })
  async preProvisionDevice(
    @Body() dto: PreProvisionDeviceDto,
    @Request() req,
  ): Promise<DeviceRegistrationResponseDto> {
    return this.deviceRegistrationService.preProvisionDevice(dto, req.user.sub);
  }

  /**
   * Approve pending device registration (Admin only)
   */
  @Post('approve')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ 
    summary: 'Approve device registration',
    description: 'Admin approves a pending device registration and generates credentials' 
  })
  @ApiResponse({ 
    status: 200, 
    description: 'Device approved successfully', 
    type: DeviceRegistrationResponseDto 
  })
  @ApiResponse({ status: 404, description: 'Device not found' })
  @ApiResponse({ status: 400, description: 'Device not in pending status' })
  async approveDevice(
    @Body() dto: ApproveDeviceDto,
    @Request() req,
  ): Promise<DeviceRegistrationResponseDto> {
    return this.deviceRegistrationService.approveDevice(dto, req.user.sub);
  }

  /**
   * Reject device registration (Admin only)
   */
  @Post('reject')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator)
  @ApiBearerAuth()
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ 
    summary: 'Reject device registration',
    description: 'Admin rejects a pending device registration' 
  })
  @ApiResponse({ status: 200, description: 'Device rejected successfully' })
  @ApiResponse({ status: 404, description: 'Device not found' })
  @ApiResponse({ status: 400, description: 'Device not in pending status' })
  async rejectDevice(
    @Body() dto: RejectDeviceDto,
    @Request() req,
  ): Promise<{ message: string }> {
    return this.deviceRegistrationService.rejectDevice(dto, req.user.sub);
  }

  /**
   * Get all device registrations (Admin/Operator only)
   */
  @Get()
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Get all device registrations',
    description: 'Retrieve all device registrations with optional filtering' 
  })
  @ApiQuery({ name: 'status', enum: DeviceRegistrationStatus, required: false })
  @ApiQuery({ name: 'type', enum: DeviceRegistrationType, required: false })
  @ApiQuery({ name: 'limit', type: Number, required: false, example: 50 })
  @ApiQuery({ name: 'offset', type: Number, required: false, example: 0 })
  @ApiResponse({ status: 200, description: 'Device registrations retrieved successfully' })
  async getAllDevices(
    @Query('status') status?: DeviceRegistrationStatus,
    @Query('type') type?: DeviceRegistrationType,
    @Query('limit') limit?: number,
    @Query('offset') offset?: number,
  ) {
    return this.deviceRegistrationService.getAllDevices(status, type, limit, offset);
  }

  /**
   * Get device registration by serial number
   */
  @Get('serial/:serialNumber')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Get device by serial number',
    description: 'Retrieve device registration details by serial number' 
  })
  @ApiResponse({ status: 200, description: 'Device found' })
  @ApiResponse({ status: 404, description: 'Device not found' })
  async getDeviceBySerialNumber(@Param('serialNumber') serialNumber: string) {
    return this.deviceRegistrationService.getDeviceBySerialNumber(serialNumber);
  }

  /**
   * Get device registration by ID
   */
  @Get(':id')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator, UserRole.viewer)
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Get device by ID',
    description: 'Retrieve device registration details by ID' 
  })
  @ApiResponse({ status: 200, description: 'Device found' })
  @ApiResponse({ status: 404, description: 'Device not found' })
  async getDeviceById(@Param('id') id: string) {
    return this.deviceRegistrationService.getDeviceBySerialNumber(id);
  }

  /**
   * Device heartbeat endpoint
   */
  @Post('heartbeat')
  @UseGuards(DeviceApiKeyGuard)
  @HttpCode(HttpStatus.OK)
  @ApiOperation({ 
    summary: 'Device heartbeat',
    description: 'Registered devices send heartbeat to maintain active status' 
  })
  @ApiResponse({ status: 200, description: 'Heartbeat updated successfully' })
  @ApiResponse({ status: 401, description: 'Invalid device credentials' })
  @ApiResponse({ status: 404, description: 'Device not found' })
  async updateHeartbeat(@Body() dto: DeviceHeartbeatDto): Promise<{ message: string }> {
    return this.deviceRegistrationService.updateHeartbeat(dto);
  }

  /**
   * Get pending approvals (Admin/Operator only)
   */
  @Get('pending/approvals')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles(UserRole.admin, UserRole.operator)
  @ApiBearerAuth()
  @ApiOperation({ 
    summary: 'Get pending device approvals',
    description: 'Retrieve all devices pending admin approval' 
  })
  @ApiResponse({ status: 200, description: 'Pending devices retrieved successfully' })
  async getPendingApprovals() {
    return this.deviceRegistrationService.getAllDevices(
      DeviceRegistrationStatus.pending_approval,
      undefined,
      100,
      0
    );
  }

  /**
   * Device status check (for approved devices)
   */
  @Get('status/:serialNumber')
  @UseGuards(DeviceApiKeyGuard)
  @ApiOperation({ 
    summary: 'Check device status',
    description: 'Allows registered devices to check their current status' 
  })
  @ApiResponse({ status: 200, description: 'Device status retrieved' })
  @ApiResponse({ status: 401, description: 'Invalid device credentials' })
  @ApiResponse({ status: 404, description: 'Device not found' })
  async getDeviceStatus(@Param('serialNumber') serialNumber: string) {
    const device = await this.deviceRegistrationService.getDeviceBySerialNumber(serialNumber);
    return {
      serialNumber: device.serialNumber,
      status: device.registrationStatus,
      lastHeartbeat: device.lastHeartbeat,
      approvedAt: device.approvedAt,
    };
  }
}