import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { MinimalAuthController } from './minimal-auth.controller';
import { AuthService } from './auth/auth.service';
import { PrismaService } from './database/prisma.service';
import { JwtModule } from '@nestjs/jwt';

@Module({
  imports: [
    ConfigModule.forRoot({ isGlobal: true }),
    JwtModule.register({
      secret: process.env.JWT_SECRET || 'your-secret-key',
      signOptions: { expiresIn: '1h' },
    }),
  ],
  controllers: [MinimalAuthController],
  providers: [AuthService, PrismaService],
})
export class MinimalAppModule {}
