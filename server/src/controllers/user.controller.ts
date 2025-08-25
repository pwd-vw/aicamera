import { Controller, Get, Put, Delete, Body, Param, UseGuards, Request } from '@nestjs/common';
import { UserService } from '../services/user.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { RolesGuard } from '../auth/guards/roles.guard';
import { Roles } from '../auth/decorators/roles.decorator';
import { UserRole } from '../../generated/prisma';
import { RateLimitApiRead, RateLimitApiWrite, RateLimitUserManagement } from '../decorators/rate-limit.decorators';

@Controller('users')
@UseGuards(JwtAuthGuard, RolesGuard)
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get()
  @Roles(UserRole.admin)
  @RateLimitApiRead()
  async findAll() {
    return this.userService.findAll();
  }

  @Get('stats')
  @Roles(UserRole.admin)
  @RateLimitApiRead()
  async getUserStats() {
    return this.userService.getUserStats();
  }

  @Get('active')
  @Roles(UserRole.admin)
  @RateLimitApiRead()
  async getActiveUsers() {
    return this.userService.getActiveUsers();
  }

  @Get('role/:role')
  @Roles(UserRole.admin)
  @RateLimitApiRead()
  async getUsersByRole(@Param('role') role: UserRole) {
    return this.userService.getUsersByRole(role);
  }

  @Get('profile')
  @RateLimitApiRead()
  async getProfile(@Request() req) {
    return this.userService.findById(req.user.id);
  }

  @Get(':id')
  @Roles(UserRole.admin)
  @RateLimitApiRead()
  async findById(@Param('id') id: string) {
    return this.userService.findById(id);
  }

  @Put(':id')
  @Roles(UserRole.admin)
  @RateLimitUserManagement()
  async updateUser(
    @Param('id') id: string,
    @Body() data: {
      email?: string;
      username?: string;
      role?: UserRole;
      firstName?: string;
      lastName?: string;
      isActive?: boolean;
    },
  ) {
    return this.userService.updateUser(id, data);
  }

  @Put('profile')
  @RateLimitApiWrite()
  async updateProfile(
    @Request() req,
    @Body() data: {
      email?: string;
      firstName?: string;
      lastName?: string;
    },
  ) {
    return this.userService.updateUser(req.user.id, data);
  }

  @Delete(':id')
  @Roles(UserRole.admin)
  @RateLimitUserManagement()
  async deleteUser(@Param('id') id: string) {
    await this.userService.deleteUser(id);
    return { message: 'User deleted successfully' };
  }
}
