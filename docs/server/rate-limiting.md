# Rate Limiting System

This document describes the comprehensive rate limiting system implemented to prevent abuse and protect the AI Camera application.

## Overview

The rate limiting system provides multi-layered protection against abuse with role-based limits, endpoint-specific restrictions, and comprehensive monitoring capabilities.

## Features

- **Role-based Rate Limiting**: Different limits for anonymous, authenticated, and admin users
- **Endpoint-specific Limits**: Custom limits for different types of endpoints
- **IP-based Tracking**: Track requests by IP address and user ID
- **Real-time Monitoring**: Monitor rate limiting events and generate alerts
- **Configurable Limits**: Easy to adjust limits for different scenarios
- **Analytics Integration**: Rate limiting events are logged to analytics system

## Rate Limit Configuration

### User Role Limits

#### Anonymous Users (No Authentication)
```typescript
ANONYMOUS: {
  LOGIN: { ttl: 60000, limit: 3 },        // 3 login attempts per minute
  REGISTER: { ttl: 300000, limit: 1 },    // 1 registration per 5 minutes
  API: { ttl: 60000, limit: 10 },         // 10 API calls per minute
  UPLOAD: { ttl: 60000, limit: 2 },       // 2 uploads per minute
}
```

#### Authenticated Users
```typescript
AUTHENTICATED: {
  API: { ttl: 60000, limit: 100 },        // 100 API calls per minute
  UPLOAD: { ttl: 60000, limit: 20 },      // 20 uploads per minute
  EXPORT: { ttl: 300000, limit: 5 },      // 5 exports per 5 minutes
}
```

#### Admin Users
```typescript
ADMIN: {
  API: { ttl: 60000, limit: 500 },        // 500 API calls per minute
  UPLOAD: { ttl: 60000, limit: 100 },     // 100 uploads per minute
  EXPORT: { ttl: 60000, limit: 20 },      // 20 exports per minute
  USER_MANAGEMENT: { ttl: 60000, limit: 50 }, // 50 user operations per minute
}
```

### Endpoint-specific Limits

#### Authentication Endpoints
- **Login**: 3 attempts per minute (anonymous), 10 per minute (authenticated)
- **Register**: 1 attempt per 5 minutes
- **Refresh Token**: 10 attempts per minute

#### API Endpoints
- **Read Operations**: 100 requests per minute (authenticated)
- **Write Operations**: 30 requests per minute (authenticated)
- **Delete Operations**: 10 requests per minute (authenticated)

#### File Operations
- **Upload**: 10 requests per minute (authenticated)
- **Download**: 50 requests per minute (authenticated)

#### Admin Operations
- **User Management**: 20 operations per minute (admin only)
- **System Operations**: 50 operations per minute (admin only)

## Implementation

### Custom Rate Limit Guard

The system uses a custom rate limiting guard that applies different limits based on:
- User role (anonymous, authenticated, admin)
- Endpoint type (authentication, API, file operations, admin)
- HTTP method (GET, POST, PUT, DELETE)

```typescript
@Injectable()
export class CustomRateLimitGuard extends ThrottlerGuard {
  protected getThrottleOptions(context: ExecutionContext) {
    const request = context.switchToHttp().getRequest();
    const user = request.user;
    const url = request.url;
    const method = request.method;
    
    // Determine limits based on user role and endpoint
    // Return appropriate limit and TTL
  }
}
```

### Rate Limit Decorators

Easy-to-use decorators for applying rate limits to endpoints:

```typescript
// Authentication endpoints
@RateLimitAuthLogin()
@Post('login')
async login() { }

@RateLimitAuthRegister()
@Post('register')
async register() { }

// API endpoints
@RateLimitApiRead()
@Get('users')
async getUsers() { }

@RateLimitApiWrite()
@Post('users')
async createUser() { }

// File operations
@RateLimitFileUpload()
@Post('upload')
async uploadFile() { }

// Admin operations
@RateLimitUserManagement()
@Put('users/:id')
async updateUser() { }
```

## Monitoring and Analytics

### Rate Limit Events

All rate limiting events are logged to the analytics system with the following information:
- IP address
- User ID and role
- Request method and URL
- Response status code
- Request duration
- Rate limit remaining and reset time
- Whether the request was blocked

### Monitoring Endpoints

#### GET /rate-limit-monitoring/stats
Get rate limiting statistics for a time period.

**Query Parameters:**
- `startDate`: Start date for statistics (ISO string)
- `endDate`: End date for statistics (ISO string)

**Response:**
```json
{
  "totalEvents": 150,
  "blockedRequests": 25,
  "allowedRequests": 125,
  "topBlockedIPs": [
    { "ip": "192.168.1.100", "count": 10 },
    { "ip": "192.168.1.101", "count": 5 }
  ],
  "topBlockedEndpoints": [
    { "endpoint": "/auth/login", "count": 15 },
    { "endpoint": "/auth/register", "count": 8 }
  ],
  "eventsByHour": [
    { "hour": "2024-01-15T10:00:00Z", "count": 25 },
    { "hour": "2024-01-15T11:00:00Z", "count": 30 }
  ]
}
```

#### GET /rate-limit-monitoring/alerts
Get current rate limiting alerts.

**Response:**
```json
[
  {
    "type": "high_blocked_requests",
    "severity": "warning",
    "message": "IP 192.168.1.100 has 15 blocked requests in the last hour",
    "ip": "192.168.1.100",
    "count": 15,
    "timestamp": "2024-01-15T12:00:00Z"
  }
]
```

## Usage Examples

### Protecting Authentication Endpoints

```typescript
@Controller('auth')
export class AuthController {
  @Public()
  @Post('login')
  @RateLimitAuthLogin()
  async login(@Body() loginDto: LoginDto) {
    return this.authService.login(loginDto);
  }

  @Public()
  @Post('register')
  @RateLimitAuthRegister()
  async register(@Body() registerDto: RegisterDto) {
    return this.authService.register(registerDto);
  }
}
```

### Protecting API Endpoints

```typescript
@Controller('users')
@UseGuards(JwtAuthGuard)
export class UserController {
  @Get()
  @RateLimitApiRead()
  async findAll() {
    return this.userService.findAll();
  }

  @Post()
  @RateLimitApiWrite()
  async create(@Body() createUserDto: CreateUserDto) {
    return this.userService.create(createUserDto);
  }

  @Delete(':id')
  @RateLimitApiDelete()
  async delete(@Param('id') id: string) {
    return this.userService.delete(id);
  }
}
```

### Protecting File Upload Endpoints

```typescript
@Controller('upload')
@UseGuards(JwtAuthGuard)
export class UploadController {
  @Post()
  @RateLimitFileUpload()
  async uploadFile(@UploadedFile() file: Express.Multer.File) {
    return this.uploadService.processFile(file);
  }
}
```

## Configuration

### Environment Variables

```bash
# Rate limiting configuration
RATE_LIMIT_ENABLED=true
RATE_LIMIT_STORAGE=memory  # or 'redis' for distributed systems
RATE_LIMIT_DEBUG=false
```

### Redis Configuration (Optional)

For distributed systems, configure Redis for rate limiting storage:

```typescript
// In rate-limit.config.ts
export const rateLimitConfig: ThrottlerModuleOptions = {
  storage: new RedisStore({
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
  }),
  // ... other configuration
};
```

## Testing

### Test Rate Limiting

Run the rate limiting test script:

```bash
npx ts-node src/examples/test-rate-limiting.ts
```

### Manual Testing

Test rate limiting with curl:

```bash
# Test login rate limiting
for i in {1..5}; do
  curl -X POST http://localhost:3000/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"test","password":"test"}'
  echo "Request $i"
  sleep 1
done

# Test API rate limiting
for i in {1..15}; do
  curl -X GET http://localhost:3000/users \
    -H "Authorization: Bearer YOUR_TOKEN"
  echo "Request $i"
  sleep 1
done
```

## Best Practices

### 1. Gradual Limit Adjustment
- Start with conservative limits
- Monitor usage patterns
- Adjust limits based on legitimate usage

### 2. User Communication
- Return clear error messages when limits are exceeded
- Include retry-after headers
- Provide rate limit information in response headers

### 3. Monitoring and Alerting
- Set up alerts for unusual rate limiting patterns
- Monitor blocked requests by IP and endpoint
- Track rate limiting effectiveness

### 4. Security Considerations
- Use IP-based tracking for anonymous users
- Combine with user authentication for better tracking
- Consider geographic-based limits for global applications

### 5. Performance Optimization
- Use Redis for distributed rate limiting
- Implement caching for rate limit calculations
- Monitor rate limiting overhead

## Troubleshooting

### Common Issues

1. **Rate limits too strict**: Adjust limits in configuration
2. **Rate limits not working**: Check guard application and configuration
3. **Performance issues**: Consider Redis storage for high-traffic applications
4. **False positives**: Review legitimate usage patterns

### Debug Mode

Enable debug logging:

```typescript
// In rate-limit.config.ts
export const rateLimitConfig: ThrottlerModuleOptions = {
  // ... other config
  debug: process.env.NODE_ENV === 'development',
};
```

### Monitoring Commands

```bash
# Check rate limiting statistics
curl -X GET http://localhost:3000/rate-limit-monitoring/stats \
  -H "Authorization: Bearer ADMIN_TOKEN"

# Check current alerts
curl -X GET http://localhost:3000/rate-limit-monitoring/alerts \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

## Next Steps

1. **Production Deployment**: Configure Redis for distributed rate limiting
2. **Advanced Monitoring**: Set up real-time alerts and dashboards
3. **Geographic Limits**: Implement location-based rate limiting
4. **Machine Learning**: Use ML to detect and prevent abuse patterns
5. **API Documentation**: Include rate limiting information in API docs
