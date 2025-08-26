# Validation System Documentation

This document describes the comprehensive validation system implemented using NestJS's built-in class-validator support.

## Overview

The validation system provides robust input validation, data transformation, and error handling throughout the AI Camera application using class-validator and class-transformer.

## Features

- **Global Validation Pipe**: Automatic validation for all incoming requests
- **Custom Validation Decorators**: Domain-specific validation rules
- **Comprehensive DTOs**: Type-safe data transfer objects with validation
- **Custom Error Handling**: Formatted validation error responses
- **Data Transformation**: Automatic type conversion and sanitization
- **Security Validation**: Input sanitization and format validation

## Installation

The validation system uses the following packages:

```bash
npm install class-validator class-transformer
```

## Configuration

### Global Validation Pipe

The application uses a global validation pipe configured in `src/config/validation.config.ts`:

```typescript
export const validationConfig: ValidationPipeOptions = {
  transform: true,                    // Transform payloads to DTOs
  whitelist: true,                    // Strip non-whitelisted properties
  forbidNonWhitelisted: true,         // Throw error for non-whitelisted properties
  forbidUnknownValues: true,          // Throw error for unknown values
  disableErrorMessages: process.env.NODE_ENV === 'production',
  validationError: {
    target: false,
    value: false,
  },
  transformOptions: {
    enableImplicitConversion: true,
  },
  exceptionFactory: (errors) => {
    // Custom error formatting
  },
};
```

### Validation Module

The validation module is configured as a global module in `src/modules/validation.module.ts`:

```typescript
@Global()
@Module({
  providers: [
    {
      provide: APP_PIPE,
      useValue: new ValidationPipe(validationConfig),
    },
  ],
})
export class ValidationModule {}
```

## Custom Validation Decorators

### Domain-Specific Validators

#### Password Validation
```typescript
@IsStrongPassword()
password: string;
```
- Requires 8+ characters
- At least 1 uppercase, 1 lowercase, 1 number, 1 special character

#### IP Address Validation
```typescript
@IsIPAddress()
ipAddress: string;
```
- Validates IPv4 address format

#### Camera ID Validation
```typescript
@IsCameraId()
cameraId: string;
```
- Format: `cam-XXX` where XXX is alphanumeric (3-10 chars)

#### License Plate Validation
```typescript
@IsLicensePlate()
licensePlate: string;
```
- Format: 1-3 letters, 1-4 numbers, optional 1-2 letters

#### Coordinate Validation
```typescript
@IsCoordinate()
latitude: number;  // -90 to 90
longitude: number; // -180 to 180
```
- Validates latitude/longitude ranges

#### File Validation
```typescript
@IsFileSize(10) // 10MB max
@IsFileType(['image/jpeg', 'image/png'])
file: Express.Multer.File;
```
- Validates file size and type

## DTOs (Data Transfer Objects)

### Authentication DTOs

#### LoginDto
```typescript
export class LoginDto {
  @IsString()
  @IsNotEmpty({ message: 'Username is required' })
  @Length(3, 50, { message: 'Username must be between 3 and 50 characters' })
  @Matches(/^[a-zA-Z0-9_-]+$/, { message: 'Username can only contain letters, numbers, underscores, and hyphens' })
  username: string;

  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @MinLength(6, { message: 'Password must be at least 6 characters long' })
  password: string;
}
```

#### RegisterDto
```typescript
export class RegisterDto {
  @IsEmail({}, { message: 'Please provide a valid email address' })
  @IsNotEmpty({ message: 'Email is required' })
  email: string;

  @IsString()
  @IsNotEmpty({ message: 'Username is required' })
  @Length(3, 50, { message: 'Username must be between 3 and 50 characters' })
  @Matches(/^[a-zA-Z0-9_-]+$/, { message: 'Username can only contain letters, numbers, underscores, and hyphens' })
  username: string;

  @IsString()
  @IsNotEmpty({ message: 'Password is required' })
  @IsStrongPassword({ message: 'Password must be strong (8+ chars, uppercase, lowercase, number, special char)' })
  password: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'First name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'First name can only contain letters, spaces, hyphens, and apostrophes' })
  firstName?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Last name must be between 1 and 50 characters' })
  @Matches(/^[a-zA-Z\s-']+$/, { message: 'Last name can only contain letters, spaces, hyphens, and apostrophes' })
  lastName?: string;

  @IsOptional()
  @IsEnum(UserRole, { message: 'Role must be one of: admin, operator, viewer' })
  role?: UserRole;
}
```

### Camera DTOs

#### CreateCameraDto
```typescript
export class CreateCameraDto {
  @IsString()
  @IsNotEmpty({ message: 'Camera ID is required' })
  @IsCameraId({ message: 'Camera ID must be in format cam-XXX' })
  cameraId: string;

  @IsString()
  @IsNotEmpty({ message: 'Camera name is required' })
  @Length(1, 255, { message: 'Camera name must be between 1 and 255 characters' })
  name: string;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Latitude must be between -90 and 90' })
  locationLat?: number;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Longitude must be between -180 and 180' })
  locationLng?: number;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Location address must be between 1 and 500 characters' })
  locationAddress?: string;

  @IsOptional()
  @IsEnum(CameraStatus, { message: 'Status must be one of: active, inactive, maintenance' })
  status?: CameraStatus;

  @IsOptional()
  @IsBoolean()
  detectionEnabled?: boolean;

  @IsOptional()
  @IsEnum(ImageQuality, { message: 'Image quality must be one of: low, medium, high' })
  imageQuality?: ImageQuality;

  @IsOptional()
  @IsNumber()
  uploadInterval?: number;

  @IsOptional()
  @IsObject()
  configuration?: Record<string, any>;
}
```

### Detection DTOs

#### CreateDetectionDto
```typescript
export class CreateDetectionDto {
  @IsString()
  @IsNotEmpty({ message: 'Camera ID is required' })
  cameraId: string;

  @IsDateString({}, { message: 'Timestamp must be a valid ISO date string' })
  @IsNotEmpty({ message: 'Timestamp is required' })
  timestamp: string;

  @IsString()
  @IsNotEmpty({ message: 'License plate is required' })
  @IsLicensePlate({ message: 'License plate must be in valid format' })
  licensePlate: string;

  @IsNumber()
  @Min(0, { message: 'Confidence must be between 0 and 1' })
  @Max(1, { message: 'Confidence must be between 0 and 1' })
  confidence: number;

  @IsOptional()
  @IsUrl({}, { message: 'Image URL must be a valid URL' })
  imageUrl?: string;

  @IsOptional()
  @IsString()
  @Length(1, 500, { message: 'Image path must be between 1 and 500 characters' })
  imagePath?: string;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Latitude must be between -90 and 90' })
  locationLat?: number;

  @IsOptional()
  @IsNumber()
  @IsCoordinate({ message: 'Longitude must be between -180 and 180' })
  locationLng?: number;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Vehicle make must be between 1 and 100 characters' })
  vehicleMake?: string;

  @IsOptional()
  @IsString()
  @Length(1, 100, { message: 'Vehicle model must be between 1 and 100 characters' })
  vehicleModel?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle color must be between 1 and 50 characters' })
  vehicleColor?: string;

  @IsOptional()
  @IsString()
  @Length(1, 50, { message: 'Vehicle type must be between 1 and 50 characters' })
  vehicleType?: string;

  @IsOptional()
  @IsEnum(DetectionStatus, { message: 'Status must be one of: pending, processed, failed' })
  status?: DetectionStatus;

  @IsOptional()
  @IsObject()
  metadata?: Record<string, any>;
}
```

### File Upload DTOs

#### ImageUploadDto
```typescript
export class ImageUploadDto extends FileUploadDto {
  @IsFileType(['image/jpeg', 'image/png', 'image/gif', 'image/webp'], { message: 'File must be a valid image type (JPEG, PNG, GIF, WebP)' })
  mimetype: string;

  @IsFileSize(10, { message: 'Image file size must not exceed 10MB' })
  size: number;
}
```

#### VideoUploadDto
```typescript
export class VideoUploadDto extends FileUploadDto {
  @IsFileType(['video/mp4', 'video/avi', 'video/mov', 'video/wmv'], { message: 'File must be a valid video type (MP4, AVI, MOV, WMV)' })
  mimetype: string;

  @IsFileSize(100, { message: 'Video file size must not exceed 100MB' })
  size: number;
}
```

## Error Handling

### Validation Error Format

When validation fails, the system returns a structured error response:

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "value": "invalid-email",
      "message": "Please provide a valid email address",
      "code": "INVALID_EMAIL"
    },
    {
      "field": "password",
      "value": "weak",
      "message": "Password must be strong (8+ chars, uppercase, lowercase, number, special char)",
      "code": "WEAK_PASSWORD"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Error Codes

The system provides standardized error codes for different validation failures:

- `FIELD_REQUIRED` - Required field is missing
- `INVALID_EMAIL` - Invalid email format
- `MIN_LENGTH` - String too short
- `MAX_LENGTH` - String too long
- `INVALID_LENGTH` - String length not in range
- `INVALID_FORMAT` - String doesn't match pattern
- `INVALID_ENUM_VALUE` - Invalid enum value
- `INVALID_NUMBER` - Invalid number
- `MIN_VALUE` - Number too small
- `MAX_VALUE` - Number too large
- `INVALID_DATE` - Invalid date format
- `INVALID_URL` - Invalid URL format
- `INVALID_IP_ADDRESS` - Invalid IP address
- `WEAK_PASSWORD` - Password doesn't meet strength requirements
- `INVALID_CAMERA_ID` - Invalid camera ID format
- `INVALID_LICENSE_PLATE` - Invalid license plate format
- `INVALID_COORDINATE` - Invalid coordinate value
- `FILE_TOO_LARGE` - File size exceeds limit
- `INVALID_FILE_TYPE` - Invalid file type

## Usage Examples

### Controller with Validation

```typescript
@Controller('auth')
export class AuthController {
  @Post('login')
  async login(@Body() loginDto: LoginDto) {
    // loginDto is automatically validated and transformed
    return this.authService.login(loginDto);
  }

  @Post('register')
  async register(@Body() registerDto: RegisterDto) {
    // registerDto is automatically validated and transformed
    return this.authService.register(registerDto);
  }
}
```

### Query Parameters Validation

```typescript
@Controller('detections')
export class DetectionController {
  @Get()
  async findAll(@Query() queryDto: DetectionQueryDto) {
    // Query parameters are automatically validated
    return this.detectionService.findAll(queryDto);
  }
}
```

### File Upload Validation

```typescript
@Controller('upload')
export class UploadController {
  @Post('image')
  @UseInterceptors(FileInterceptor('file'))
  async uploadImage(
    @UploadedFile() file: Express.Multer.File,
    @Body() uploadDto: ImageUploadDto,
  ) {
    // File and metadata are validated
    return this.uploadService.processImage(file, uploadDto);
  }
}
```

## Testing

### Test Validation

Run the validation test script:

```bash
npx ts-node src/examples/test-validation.ts
```

### Manual Testing

Test validation with curl:

```bash
# Test valid registration
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "StrongPass123!",
    "firstName": "John",
    "lastName": "Doe"
  }'

# Test invalid registration
curl -X POST http://localhost:3000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "username": "a",
    "password": "weak",
    "firstName": "123"
  }'
```

## Best Practices

### 1. Use Specific Validation Decorators
- Use domain-specific decorators when available
- Combine multiple decorators for comprehensive validation
- Provide clear, user-friendly error messages

### 2. Validate at Multiple Levels
- DTO level validation for request data
- Service level validation for business logic
- Database level constraints for data integrity

### 3. Custom Error Messages
- Provide descriptive error messages
- Use consistent error message format
- Include helpful suggestions when possible

### 4. Security Considerations
- Validate and sanitize all inputs
- Use whitelist approach for allowed properties
- Implement proper file type and size validation
- Validate file uploads thoroughly

### 5. Performance Optimization
- Use efficient validation decorators
- Avoid complex validation logic in decorators
- Cache validation results when possible

## Configuration Options

### Environment Variables

```bash
# Validation configuration
VALIDATION_WHITELIST=true
VALIDATION_FORBID_NON_WHITELISTED=true
VALIDATION_FORBID_UNKNOWN_VALUES=true
VALIDATION_DISABLE_ERROR_MESSAGES=false
```

### Custom Validation Options

```typescript
// Controller-level validation pipe
@UsePipes(new ValidationPipe({
  transform: true,
  whitelist: true,
  forbidNonWhitelisted: true,
  skipMissingProperties: true,
}))
export class CustomController {}

// Method-level validation pipe
@Post()
@UsePipes(new ValidationPipe({ groups: ['create'] }))
async create(@Body() createDto: CreateDto) {}
```

## Troubleshooting

### Common Issues

1. **Validation not working**: Ensure ValidationModule is imported globally
2. **Custom decorators not working**: Check decorator registration and imports
3. **File validation issues**: Verify file interceptor configuration
4. **Type conversion errors**: Check transform options in validation config

### Debug Mode

Enable debug logging for validation:

```typescript
// In validation.config.ts
export const validationConfig: ValidationPipeOptions = {
  // ... other config
  debug: process.env.NODE_ENV === 'development',
};
```

## Next Steps

1. **Add more custom validators** for domain-specific requirements
2. **Implement validation groups** for different operations
3. **Add conditional validation** based on business rules
4. **Create validation schemas** for complex nested objects
5. **Implement async validation** for database checks
