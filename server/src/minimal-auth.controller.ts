import { Controller, Post, Body, Get, UseGuards, Request } from '@nestjs/common';
import { AuthService } from './auth/auth.service';

@Controller('auth')
export class MinimalAuthController {
  constructor(private readonly authService: AuthService) {}

  @Post('login')
  async login(@Body() loginDto: { username: string; password: string }) {
    try {
      return await this.authService.login(loginDto);
    } catch (error) {
      return { error: 'Login failed', message: error.message };
    }
  }

  @Get('profile')
  async getProfile(@Request() req) {
    // Simple profile endpoint
    return { message: 'Profile endpoint' };
  }
}
