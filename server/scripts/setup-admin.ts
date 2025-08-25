#!/usr/bin/env ts-node

import { PrismaService } from '../src/database/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { UserRole } from '../generated/prisma';

async function setupAdmin() {
  const prisma = new PrismaService();
  
  // Create a simple JWT service for admin creation
  const jwtService = new JwtService({
    secret: process.env.JWT_SECRET || 'your-secret-key',
    signOptions: { expiresIn: '1h' },
  });
  
  // Import AuthService dynamically to avoid circular dependencies
  const { AuthService } = await import('../src/auth/auth.service');
  const authService = new AuthService(prisma, jwtService);

  try {
    console.log('Setting up initial admin user...');

    // Check if admin already exists
    const existingAdmin = await prisma.user.findFirst({
      where: {
        OR: [
          { username: 'admin' },
          { email: 'admin@aicamera.com' },
        ],
      },
    });

    if (existingAdmin) {
      console.log('Admin user already exists:', existingAdmin.username);
      return;
    }

    // Create admin user
    const admin = await authService.createAdminUser(
      'admin@aicamera.com',
      'admin',
      'admin123',
    );

    console.log('✅ Admin user created successfully!');
    console.log('Username:', admin.username);
    console.log('Email:', admin.email);
    console.log('Role:', admin.role);
    console.log('\n⚠️  IMPORTANT: Change the default password after first login!');

  } catch (error) {
    console.error('❌ Error creating admin user:', error);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the setup
setupAdmin().catch(console.error);
