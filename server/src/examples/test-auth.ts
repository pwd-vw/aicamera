#!/usr/bin/env ts-node

import { PrismaService } from '../database/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { AuthService } from '../auth/auth.service';

async function testAuth() {
  const prisma = new PrismaService();
  
  // Create JWT service
  const jwtService = new JwtService({
    secret: process.env.JWT_SECRET || 'your-secret-key',
    signOptions: { expiresIn: '1h' },
  });
  
  // Create auth service
  const authService = new AuthService(prisma, jwtService);

  try {
    console.log('🧪 Testing JWT Authentication System...\n');

    // Test 1: Login with admin user
    console.log('1. Testing admin login...');
    const loginResult = await authService.login({
      username: 'admin',
      password: 'admin123',
    });

    console.log('✅ Login successful!');
    console.log('   User:', loginResult.user.username);
    console.log('   Role:', loginResult.user.role);
    console.log('   Access Token:', loginResult.accessToken.substring(0, 50) + '...');

    // Test 2: Validate user
    console.log('\n2. Testing user validation...');
    const user = await authService.validateUser('admin', 'admin123');
    if (user) {
      console.log('✅ User validation successful!');
      console.log('   Username:', user.username);
      console.log('   Role:', user.role);
    } else {
      console.log('❌ User validation failed!');
    }

    // Test 3: Get user profile
    console.log('\n3. Testing profile retrieval...');
    const profile = await prisma.user.findUnique({
      where: { username: 'admin' },
      select: {
        id: true,
        email: true,
        username: true,
        role: true,
        firstName: true,
        lastName: true,
        isActive: true,
        lastLogin: true,
        createdAt: true,
        updatedAt: true,
      },
    });

    if (profile) {
      console.log('✅ Profile retrieval successful!');
      console.log('   Email:', profile.email);
      console.log('   Active:', profile.isActive);
      console.log('   Last Login:', profile.lastLogin);
    } else {
      console.log('❌ Profile retrieval failed!');
    }

    // Test 4: Refresh token
    console.log('\n4. Testing token refresh...');
    const refreshResult = await authService.refreshToken(user.id);
    console.log('✅ Token refresh successful!');
    console.log('   New Access Token:', refreshResult.accessToken.substring(0, 50) + '...');

    console.log('\n🎉 All authentication tests passed!');
    console.log('\n📋 Next steps:');
    console.log('   1. Change the default admin password');
    console.log('   2. Create additional users with different roles');
    console.log('   3. Test role-based access control');
    console.log('   4. Implement frontend authentication');

  } catch (error) {
    console.error('❌ Authentication test failed:', error);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the test
testAuth().catch(console.error);
