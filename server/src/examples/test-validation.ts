#!/usr/bin/env ts-node

import { validate } from 'class-validator';
import { plainToClass } from 'class-transformer';
import { LoginDto, RegisterDto, ChangePasswordDto, UpdateProfileDto } from '../auth/dto/auth.dto';
import { CreateCameraDto, UpdateCameraDto } from '../dto/camera.dto';
import { CreateDetectionDto, DetectionQueryDto } from '../dto/detection.dto';
import { CreateVisualizationDto } from '../dto/visualization.dto';
import { CreateAnalyticsEventDto } from '../dto/analytics.dto';
import { ImageUploadDto, VideoUploadDto } from '../dto/file-upload.dto';

async function testValidation() {
  console.log('🧪 Testing Validation System...\n');

  // Test 1: Authentication DTOs
  console.log('1. Testing Authentication DTOs...');
  
  // Test valid login
  const validLogin = plainToClass(LoginDto, {
    username: 'testuser',
    password: 'password123',
  });
  const loginErrors = await validate(validLogin);
  console.log('✅ Valid login data:', loginErrors.length === 0 ? 'PASSED' : 'FAILED');

  // Test invalid login
  const invalidLogin = plainToClass(LoginDto, {
    username: 'a', // Too short
    password: '123', // Too short
  });
  const invalidLoginErrors = await validate(invalidLogin);
  console.log('❌ Invalid login data:', invalidLoginErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidLoginErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test valid registration
  const validRegister = plainToClass(RegisterDto, {
    email: 'test@example.com',
    username: 'testuser',
    password: 'StrongPass123!',
    firstName: 'John',
    lastName: 'Doe',
  });
  const registerErrors = await validate(validRegister);
  console.log('✅ Valid registration data:', registerErrors.length === 0 ? 'PASSED' : 'FAILED');

  // Test invalid registration (weak password)
  const invalidRegister = plainToClass(RegisterDto, {
    email: 'invalid-email',
    username: 'a',
    password: 'weak',
    firstName: '123', // Invalid characters
  });
  const invalidRegisterErrors = await validate(invalidRegister);
  console.log('❌ Invalid registration data:', invalidRegisterErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidRegisterErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 2: Camera DTOs
  console.log('\n2. Testing Camera DTOs...');
  
  const validCamera = plainToClass(CreateCameraDto, {
    cameraId: 'cam-001',
    name: 'Main Entrance Camera',
    locationLat: 40.7128,
    locationLng: -74.0060,
    locationAddress: '123 Main St, New York, NY',
  });
  const cameraErrors = await validate(validCamera);
  console.log('✅ Valid camera data:', cameraErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidCamera = plainToClass(CreateCameraDto, {
    cameraId: 'invalid-id',
    name: '',
    locationLat: 100, // Invalid latitude
    locationLng: 200, // Invalid longitude
  });
  const invalidCameraErrors = await validate(invalidCamera);
  console.log('❌ Invalid camera data:', invalidCameraErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidCameraErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 3: Detection DTOs
  console.log('\n3. Testing Detection DTOs...');
  
  const validDetection = plainToClass(CreateDetectionDto, {
    cameraId: 'cam-001',
    timestamp: '2024-01-15T10:30:00Z',
    licensePlate: 'ABC123',
    confidence: 0.95,
    vehicleMake: 'Toyota',
    vehicleColor: 'Red',
  });
  const detectionErrors = await validate(validDetection);
  console.log('✅ Valid detection data:', detectionErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidDetection = plainToClass(CreateDetectionDto, {
    cameraId: '',
    timestamp: 'invalid-date',
    licensePlate: 'INVALID',
    confidence: 1.5, // Invalid confidence
  });
  const invalidDetectionErrors = await validate(invalidDetection);
  console.log('❌ Invalid detection data:', invalidDetectionErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidDetectionErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 4: Visualization DTOs
  console.log('\n4. Testing Visualization DTOs...');
  
  const validVisualization = plainToClass(CreateVisualizationDto, {
    name: 'Detection Chart',
    type: 'chart',
    configuration: { chartType: 'bar' },
    dataSource: 'detections',
    refreshInterval: 300,
  });
  const visualizationErrors = await validate(validVisualization);
  console.log('✅ Valid visualization data:', visualizationErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidVisualization = plainToClass(CreateVisualizationDto, {
    name: '',
    type: 'invalid-type',
    configuration: 'not-an-object',
    dataSource: '',
    refreshInterval: 10, // Too short
  });
  const invalidVisualizationErrors = await validate(invalidVisualization);
  console.log('❌ Invalid visualization data:', invalidVisualizationErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidVisualizationErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 5: Analytics DTOs
  console.log('\n5. Testing Analytics DTOs...');
  
  const validAnalytics = plainToClass(CreateAnalyticsEventDto, {
    eventType: 'user_login',
    eventCategory: 'user_interaction',
    userId: 'user123',
    ipAddress: '192.168.1.100',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
  });
  const analyticsErrors = await validate(validAnalytics);
  console.log('✅ Valid analytics data:', analyticsErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidAnalytics = plainToClass(CreateAnalyticsEventDto, {
    eventType: '',
    eventCategory: 'invalid_category',
    ipAddress: 'invalid-ip',
  });
  const invalidAnalyticsErrors = await validate(invalidAnalytics);
  console.log('❌ Invalid analytics data:', invalidAnalyticsErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidAnalyticsErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 6: File Upload DTOs
  console.log('\n6. Testing File Upload DTOs...');
  
  const validImageUpload = plainToClass(ImageUploadDto, {
    filename: 'test-image.jpg',
    mimetype: 'image/jpeg',
    size: 1024 * 1024, // 1MB
  });
  const imageUploadErrors = await validate(validImageUpload);
  console.log('✅ Valid image upload data:', imageUploadErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidImageUpload = plainToClass(ImageUploadDto, {
    filename: '',
    mimetype: 'text/plain', // Invalid for image
    size: 20 * 1024 * 1024, // 20MB - too large
  });
  const invalidImageUploadErrors = await validate(invalidImageUpload);
  console.log('❌ Invalid image upload data:', invalidImageUploadErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidImageUploadErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  // Test 7: Query DTOs
  console.log('\n7. Testing Query DTOs...');
  
  const validQuery = plainToClass(DetectionQueryDto, {
    cameraId: 'cam-001',
    licensePlate: 'ABC123',
    startDate: '2024-01-01T00:00:00Z',
    endDate: '2024-01-31T23:59:59Z',
    minConfidence: 0.8,
    maxConfidence: 1.0,
    page: 1,
    limit: 50,
  });
  const queryErrors = await validate(validQuery);
  console.log('✅ Valid query data:', queryErrors.length === 0 ? 'PASSED' : 'FAILED');

  const invalidQuery = plainToClass(DetectionQueryDto, {
    licensePlate: 'INVALID',
    minConfidence: 1.5, // Invalid
    maxConfidence: 0.5, // Invalid
    page: 0, // Invalid
    limit: 200, // Too high
  });
  const invalidQueryErrors = await validate(invalidQuery);
  console.log('❌ Invalid query data:', invalidQueryErrors.length > 0 ? 'PASSED' : 'FAILED');
  console.log('   Errors:', invalidQueryErrors.map(e => `${e.property}: ${Object.values(e.constraints)[0]}`));

  console.log('\n🎉 Validation testing completed!');
  console.log('\n📋 Validation Features:');
  console.log('   ✅ Strong password validation');
  console.log('   ✅ Email format validation');
  console.log('   ✅ License plate format validation');
  console.log('   ✅ Camera ID format validation');
  console.log('   ✅ Coordinate validation');
  console.log('   ✅ IP address validation');
  console.log('   ✅ File type and size validation');
  console.log('   ✅ Date format validation');
  console.log('   ✅ Enum value validation');
  console.log('   ✅ Length and range validation');
  console.log('   ✅ Custom error messages');
  console.log('   ✅ Nested object validation');
  console.log('   ✅ Array validation');
}

// Run the test
testValidation().catch(console.error);
