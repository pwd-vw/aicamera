#!/usr/bin/env ts-node

import { PrismaService } from '../database/prisma.service';
import { JwtService } from '@nestjs/jwt';
import { AuthService } from '../auth/auth.service';
import { RateLimitMonitoringService } from '../services/rate-limit-monitoring.service';

async function testRateLimiting() {
  const prisma = new PrismaService();
  
  // Create JWT service
  const jwtService = new JwtService({
    secret: process.env.JWT_SECRET || 'your-secret-key',
    signOptions: { expiresIn: '1h' },
  });
  
  // Create services
  const authService = new AuthService(prisma, jwtService);
  const rateLimitMonitoringService = new RateLimitMonitoringService(prisma, null as any);

  try {
    console.log('🧪 Testing Rate Limiting System...\n');

    // Test 1: Simulate rate limit events
    console.log('1. Simulating rate limit events...');
    
    // Simulate some rate limit events
    await rateLimitMonitoringService.logRateLimitEvent({
      ip: '192.168.1.100',
      userId: 'user123',
      userRole: 'admin',
      method: 'POST',
      url: '/auth/login',
      statusCode: 429,
      duration: 150,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      rateLimitRemaining: '0',
      rateLimitReset: '60',
      isBlocked: true,
    });

    await rateLimitMonitoringService.logRateLimitEvent({
      ip: '192.168.1.101',
      userId: undefined,
      userRole: 'anonymous',
      method: 'POST',
      url: '/auth/register',
      statusCode: 429,
      duration: 120,
      userAgent: 'curl/7.68.0',
      rateLimitRemaining: '0',
      rateLimitReset: '300',
      isBlocked: true,
    });

    await rateLimitMonitoringService.logRateLimitEvent({
      ip: '192.168.1.100',
      userId: 'user123',
      userRole: 'admin',
      method: 'GET',
      url: '/users',
      statusCode: 200,
      duration: 50,
      userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
      rateLimitRemaining: '95',
      rateLimitReset: '60',
      isBlocked: false,
    });

    console.log('✅ Rate limit events logged successfully');

    // Test 2: Get rate limit statistics
    console.log('\n2. Getting rate limit statistics...');
    const stats = await rateLimitMonitoringService.getRateLimitStats();
    
    console.log('📊 Rate Limit Statistics:');
    console.log(`   Total Events: ${stats.totalEvents}`);
    console.log(`   Blocked Requests: ${stats.blockedRequests}`);
    console.log(`   Allowed Requests: ${stats.allowedRequests}`);
    console.log(`   Top Blocked IPs: ${stats.topBlockedIPs.length}`);
    console.log(`   Top Blocked Endpoints: ${stats.topBlockedEndpoints.length}`);

    // Test 3: Get rate limit alerts
    console.log('\n3. Getting rate limit alerts...');
    const alerts = await rateLimitMonitoringService.getRateLimitAlerts();
    
    console.log('🚨 Rate Limit Alerts:');
    if (alerts.length === 0) {
      console.log('   No alerts at this time');
    } else {
      alerts.forEach((alert, index) => {
        console.log(`   Alert ${index + 1}: ${alert.message} (${alert.severity})`);
      });
    }

    // Test 4: Demonstrate rate limit configuration
    console.log('\n4. Rate Limit Configuration Overview:');
    console.log('📋 Rate Limits by User Role:');
    console.log('   Anonymous Users:');
    console.log('     - Login: 3 attempts per minute');
    console.log('     - Register: 1 attempt per 5 minutes');
    console.log('     - API: 10 requests per minute');
    console.log('     - Upload: 2 uploads per minute');
    console.log('   Authenticated Users:');
    console.log('     - API: 100 requests per minute');
    console.log('     - Upload: 20 uploads per minute');
    console.log('     - Export: 5 exports per 5 minutes');
    console.log('   Admin Users:');
    console.log('     - API: 500 requests per minute');
    console.log('     - Upload: 100 uploads per minute');
    console.log('     - Export: 20 exports per minute');
    console.log('     - User Management: 50 operations per minute');

    console.log('\n🎉 Rate limiting test completed successfully!');
    console.log('\n📋 Next steps:');
    console.log('   1. Test rate limiting with actual HTTP requests');
    console.log('   2. Monitor rate limit events in production');
    console.log('   3. Set up alerts for suspicious activity');
    console.log('   4. Configure Redis for distributed rate limiting');

  } catch (error) {
    console.error('❌ Rate limiting test failed:', error);
  } finally {
    await prisma.$disconnect();
  }
}

// Run the test
testRateLimiting().catch(console.error);
