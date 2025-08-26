# JWT Authentication System

This document describes the JWT-based authentication system implemented for the AI Camera server component.

## Overview

The authentication system provides secure user authentication and authorization using JWT tokens, with role-based access control (RBAC) and comprehensive user management features.

## Features

- **JWT-based Authentication**: Secure token-based authentication
- **Role-based Access Control**: Three user roles (admin, operator, viewer)
- **Password Hashing**: Secure password storage using bcrypt
- **Token Refresh**: Automatic token refresh mechanism
- **User Management**: Complete CRUD operations for users
- **Profile Management**: User profile updates and password changes
- **Route Protection**: Guards for protecting API endpoints

## User Roles

### Admin
- Full system access
- User management
- System configuration
- Analytics and reporting
- All CRUD operations

### Operator
- Camera management
- Detection monitoring
- Basic analytics
- Limited user operations

### Viewer
- Read-only access
- View dashboards
- View reports
- No modification permissions

## Installation

The following packages are required:
```bash
npm install @nestjs/jwt @nestjs/passport passport passport-jwt bcryptjs @types/passport-jwt @types/bcryptjs
```

## Environment Variables

Add the following to your `.env` file:
```
JWT_SECRET=your-super-secret-jwt-key-here
JWT_EXPIRES_IN=1h
```

## Database Schema

### User Model
```prisma
model User {
  id        String   @id @default(uuid()) @db.Uuid
  email     String   @unique
  username  String   @unique
  password  String
  role      UserRole @default(viewer)
  firstName String?  @map("first_name")
  lastName  String?  @map("last_name")
  isActive  Boolean  @default(true) @map("is_active")
  lastLogin DateTime? @map("last_login") @db.Timestamptz(6)
  createdAt DateTime @default(now()) @map("created_at") @db.Timestamptz(6)
  updatedAt DateTime @updatedAt @map("updated_at") @db.Timestamptz(6)

  analyticsEvents AnalyticsEvent[]

  @@map("users")
}

enum UserRole {
  admin
  operator
  viewer
}
```

## API Endpoints

### Authentication Endpoints

#### POST /auth/login
Login with username and password.
```json
{
  "username": "admin",
  "password": "admin123"
}
```

Response:
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid",
    "email": "admin@aicamera.com",
    "username": "admin",
    "role": "admin",
    "firstName": "Admin",
    "lastName": "User"
  }
}
```

#### POST /auth/register
Register a new user.
```json
{
  "email": "user@example.com",
  "username": "newuser",
  "password": "password123",
  "firstName": "John",
  "lastName": "Doe",
  "role": "operator"
}
```

#### POST /auth/refresh
Refresh access token using refresh token.
```json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### GET /auth/profile
Get current user profile (requires authentication).

#### PUT /auth/profile
Update current user profile.
```json
{
  "firstName": "Updated",
  "lastName": "Name",
  "email": "updated@example.com"
}
```

#### PUT /auth/change-password
Change user password.
```json
{
  "currentPassword": "oldpassword",
  "newPassword": "newpassword"
}
```

#### POST /auth/logout
Logout (token invalidation).

### User Management Endpoints (Admin Only)

#### GET /users
Get all users.

#### GET /users/stats
Get user statistics.

#### GET /users/active
Get active users only.

#### GET /users/role/:role
Get users by role.

#### GET /users/:id
Get specific user.

#### PUT /users/:id
Update user (admin only).
```json
{
  "email": "updated@example.com",
  "role": "operator",
  "isActive": true
}
```

#### DELETE /users/:id
Delete user (admin only).

## Guards and Decorators

### JwtAuthGuard
Protects routes requiring authentication.
```typescript
@UseGuards(JwtAuthGuard)
@Get('protected-route')
async protectedRoute() {
  return 'This route is protected';
}
```

### RolesGuard
Protects routes based on user roles.
```typescript
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles(UserRole.admin)
@Get('admin-only')
async adminOnlyRoute() {
  return 'Admin only content';
}
```

### @Public() Decorator
Marks routes as public (no authentication required).
```typescript
@Public()
@Get('public-route')
async publicRoute() {
  return 'This route is public';
}
```

### @Roles() Decorator
Specifies required roles for a route.
```typescript
@Roles(UserRole.admin, UserRole.operator)
@Get('admin-or-operator')
async adminOrOperatorRoute() {
  return 'Admin or operator content';
}
```

## Usage Examples

### Protecting Routes
```typescript
@Controller('cameras')
@UseGuards(JwtAuthGuard)
export class CameraController {
  @Get()
  @Roles(UserRole.admin, UserRole.operator)
  async getAllCameras() {
    return this.cameraService.findAll();
  }

  @Post()
  @Roles(UserRole.admin)
  async createCamera(@Body() data: CreateCameraDto) {
    return this.cameraService.create(data);
  }
}
```

### Accessing User Information
```typescript
@Get('profile')
@UseGuards(JwtAuthGuard)
async getProfile(@Request() req) {
  // req.user contains the authenticated user
  return req.user;
}
```

### Creating Admin Users
```typescript
// In a setup script or admin panel
const admin = await this.authService.createAdminUser(
  'admin@aicamera.com',
  'admin',
  'securepassword'
);
```

## Security Features

### Password Security
- Passwords are hashed using bcrypt with salt rounds of 10
- Password validation with minimum length requirements
- Secure password change functionality

### Token Security
- JWT tokens with configurable expiration
- Refresh token mechanism
- Token validation on each request

### Role-based Security
- Fine-grained access control
- Route-level protection
- Method-level authorization

### Input Validation
- DTO validation using class-validator
- Email format validation
- Username uniqueness validation

## Error Handling

The authentication system provides comprehensive error handling:

- `UnauthorizedException`: Invalid credentials or inactive account
- `ConflictException`: Email or username already exists
- `BadRequestException`: Invalid input data
- `NotFoundException`: User not found

## Best Practices

### Token Management
1. Store tokens securely (HttpOnly cookies for web apps)
2. Implement token refresh before expiration
3. Clear tokens on logout
4. Use HTTPS in production

### Password Security
1. Enforce strong password policies
2. Implement password change requirements
3. Monitor failed login attempts
4. Use secure password reset mechanisms

### Role Management
1. Follow principle of least privilege
2. Regularly audit user roles
3. Implement role-based UI components
4. Log role changes for audit trails

### API Security
1. Use HTTPS for all API calls
2. Implement rate limiting
3. Validate all input data
4. Log authentication events

## Testing

### Unit Tests
```typescript
describe('AuthService', () => {
  it('should validate user credentials', async () => {
    const result = await authService.validateUser('admin', 'password');
    expect(result).toBeDefined();
  });
});
```

### Integration Tests
```typescript
describe('AuthController', () => {
  it('should login with valid credentials', async () => {
    const response = await request(app)
      .post('/auth/login')
      .send({ username: 'admin', password: 'password' });
    
    expect(response.status).toBe(200);
    expect(response.body.accessToken).toBeDefined();
  });
});
```

## Migration Guide

### From No Authentication
1. Install required packages
2. Add User model to Prisma schema
3. Run database migration
4. Implement guards on existing routes
5. Update frontend to handle authentication

### From Basic Authentication
1. Replace existing auth with JWT system
2. Update user model to include roles
3. Implement role-based guards
4. Update API endpoints with proper protection

## Troubleshooting

### Common Issues

1. **Token Expired**: Implement refresh token mechanism
2. **Invalid Token**: Check JWT_SECRET configuration
3. **Role Access Denied**: Verify user roles and route permissions
4. **Database Connection**: Ensure Prisma is properly configured

### Debug Mode
Enable debug logging in development:
```typescript
// In auth.module.ts
JwtModule.register({
  secret: process.env.JWT_SECRET,
  signOptions: { expiresIn: '1h' },
  // Add debug options
})
```

## Next Steps

1. Implement password reset functionality
2. Add two-factor authentication (2FA)
3. Implement session management
4. Add audit logging for security events
5. Implement API rate limiting
6. Add OAuth integration (Google, GitHub, etc.)
