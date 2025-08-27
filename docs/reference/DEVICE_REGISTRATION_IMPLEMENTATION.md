# Device Registration Mechanism Implementation

## Overview

This implementation provides a comprehensive device registration system for the AI Camera mono repository project. The system supports three registration mechanisms to scale with a large number of cameras/edge devices.

## Architecture

### Server Side (NestJS)
- **Location**: `/server/src/device-registration/`
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT + API Key based authentication
- **API**: RESTful endpoints for all registration mechanisms

### Edge Side (Python)
- **Location**: `/edge/src/services/`
- **Client**: Python-based registration client with automatic retry and heartbeat
- **Integration**: Integrated with Flask application startup

### Frontend (Vue 3)
- **Location**: `/server/frontend/src/components/DeviceRegistration/`
- **Dashboard**: Admin interface for device management and approval

## Registration Mechanisms

### 1. Self-Registration (Edge → Server)

**Flow:**
1. Edge device calls `/device-registration/register` with metadata
2. Server validates and creates pending registration
3. Admin reviews and approves/rejects via dashboard
4. Server generates credentials upon approval
5. Edge device polls for approval status
6. Device starts heartbeat service when approved

**Implementation:**
- **Server**: `DeviceRegistrationController.selfRegisterDevice()`
- **Edge**: `DeviceRegistrationClient.self_register()`
- **Status**: Pending approval → Approved → Active

### 2. Pre-Provision (Admin → Server → Edge)

**Flow:**
1. Admin creates device configuration via dashboard
2. Server generates credentials immediately
3. Admin provides credentials to edge device
4. Edge device uses pre-configured credentials
5. Device becomes active immediately

**Implementation:**
- **Server**: `DeviceRegistrationController.preProvisionDevice()`
- **Edge**: `DeviceRegistrationClient.use_pre_provisioned_credentials()`
- **Status**: Provisioned → Active

### 3. Admin Approval (Self-Registration with Approval)

**Flow:**
1. Edge device registers (same as self-registration)
2. Registration marked as "pending approval"
3. Admin reviews device metadata in dashboard
4. Admin approves/rejects with optional notes
5. Server generates credentials on approval
6. Edge device receives approval and starts operation

**Implementation:**
- **Server**: `DeviceRegistrationController.approveDevice()`
- **Frontend**: `ApproveDeviceModal.vue`
- **Status**: Pending approval → Approved → Active

## Database Schema

### DeviceRegistration Table
```sql
CREATE TABLE "device_registrations" (
    "id" UUID PRIMARY KEY,
    "serial_number" TEXT UNIQUE NOT NULL,
    "device_model" TEXT NOT NULL,
    "device_type" TEXT DEFAULT 'camera',
    "ip_address" TEXT,
    "mac_address" TEXT,
    "location_lat" DECIMAL(10,8),
    "location_lng" DECIMAL(11,8),
    "location_address" TEXT,
    "registration_status" DeviceRegistrationStatus DEFAULT 'pending_approval',
    "registration_type" DeviceRegistrationType NOT NULL,
    "api_key" TEXT UNIQUE,
    "jwt_secret" TEXT,
    "shared_secret" TEXT,
    "metadata" JSONB DEFAULT '{}',
    "approved_by" UUID REFERENCES users(id),
    "approved_at" TIMESTAMPTZ,
    "rejected_by" UUID REFERENCES users(id),
    "rejected_at" TIMESTAMPTZ,
    "rejection_reason" TEXT,
    "last_heartbeat" TIMESTAMPTZ,
    "created_at" TIMESTAMPTZ DEFAULT NOW(),
    "updated_at" TIMESTAMPTZ
);
```

### Enums
```sql
CREATE TYPE "DeviceRegistrationStatus" AS ENUM (
    'pending_approval', 'approved', 'rejected', 
    'provisioned', 'active', 'inactive'
);

CREATE TYPE "DeviceRegistrationType" AS ENUM (
    'self_registration', 'pre_provision', 'admin_approval'
);
```

## API Endpoints

### Public Endpoints (No Authentication)
- `POST /device-registration/register` - Self-registration
- `POST /device-registration/heartbeat` - Device heartbeat (API key auth)
- `GET /device-registration/status/:serialNumber` - Device status check

### Admin Endpoints (JWT Authentication)
- `GET /device-registration` - List all devices
- `GET /device-registration/pending/approvals` - Pending approvals
- `POST /device-registration/pre-provision` - Pre-provision device
- `POST /device-registration/approve` - Approve device
- `POST /device-registration/reject` - Reject device
- `GET /device-registration/serial/:serialNumber` - Get device by serial

## Authentication & Security

### Device Authentication
- **API Key**: Generated 64-character hex string (`ak_` prefix)
- **JWT Secret**: 128-character hex string for JWT signing
- **Shared Secret**: Base64-encoded 32-byte secret

### API Key Authentication
```typescript
// Headers required for device endpoints
{
  'X-API-Key': 'device_api_key',
  'X-Device-Serial': 'device_serial_number'
}
```

### Admin Authentication
```typescript
// Headers required for admin endpoints
{
  'Authorization': 'Bearer jwt_token'
}
```

## File Structure

```
server/
├── src/device-registration/
│   ├── device-registration.controller.ts
│   ├── device-registration.service.ts
│   ├── device-registration.module.ts
│   ├── dto/device-registration.dto.ts
│   └── guards/device-api-key.guard.ts
├── prisma/
│   ├── schema.prisma (updated)
│   └── migrations/001_device_registration/
└── frontend/src/components/DeviceRegistration/
    ├── DeviceRegistrationList.vue
    ├── PreProvisionModal.vue
    ├── ApproveDeviceModal.vue
    ├── RejectDeviceModal.vue
    └── DeviceDetailsModal.vue

edge/
└── src/services/
    ├── device_registration_client.py
    └── registration_manager.py
```

## Configuration

### Server Environment Variables
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
JWT_SECRET=your-jwt-secret
```

### Edge Environment Variables
```env
SERVER_URL=http://localhost:3000
REGISTRATION_TYPE=self  # self, pre_provision
DEVICE_SERIAL_NUMBER=CAM001-2024-001
DEVICE_MODEL=AI-CAM-4K-V2
DEVICE_LAT=13.7563
DEVICE_LNG=100.5018
DEVICE_LOCATION="Bangkok, Thailand"

# For pre-provision mode
DEVICE_API_KEY=ak_generated_key
DEVICE_JWT_SECRET=generated_jwt_secret
DEVICE_SHARED_SECRET=generated_shared_secret

# Heartbeat settings
HEARTBEAT_INTERVAL=60
APPROVAL_CHECK_INTERVAL=30
MAX_APPROVAL_WAIT_TIME=3600
```

## Usage Examples

### 1. Self-Registration Flow

**Edge Device:**
```python
from edge.src.services.registration_manager import initialize_registration

# Initialize registration manager
registration_manager = initialize_registration("http://server:3000")

# Start self-registration process
success = registration_manager.start_registration_process("self")

if success:
    print("Registration initiated, waiting for approval...")
```

**Admin Dashboard:**
1. Open device registration dashboard
2. Review pending devices
3. Click "Approve" on desired device
4. Provide camera name and optional notes
5. Device receives credentials and becomes active

### 2. Pre-Provision Flow

**Admin Dashboard:**
1. Click "Pre-provision Device"
2. Fill device information form
3. System generates credentials immediately
4. Copy credentials to device configuration

**Edge Device:**
```bash
# Set environment variables
export REGISTRATION_TYPE=pre_provision
export DEVICE_API_KEY=ak_generated_key
export DEVICE_JWT_SECRET=generated_jwt_secret
export DEVICE_SHARED_SECRET=generated_shared_secret

# Start application
python -m edge.src.app
```

### 3. Admin Approval Flow

Same as self-registration, but with explicit admin approval step.

## Monitoring & Management

### Device Health Monitoring
- Heartbeat every 60 seconds (configurable)
- Last heartbeat timestamp tracked
- Online/offline status calculation
- Automatic status updates (inactive → active)

### Admin Dashboard Features
- Real-time device status
- Pending approval notifications
- Device filtering and search
- Bulk operations support
- Detailed device information
- Registration timeline
- Credential management

## Scaling Considerations

### Database Indexing
- Unique indexes on `serial_number` and `api_key`
- Composite indexes for filtering by status and type
- Timestamp indexes for heartbeat queries

### Performance Optimizations
- Pagination for device lists
- Efficient heartbeat updates
- Batch operations for bulk approvals
- Connection pooling for database

### Security Measures
- Rate limiting on registration endpoints
- API key rotation capability
- Audit logging for admin actions
- Secure credential generation

## Deployment

### Database Migration
```bash
cd server
npx prisma migrate deploy
npx prisma generate
```

### Server Deployment
```bash
cd server
npm install
npm run build
npm run start:prod
```

### Edge Deployment
```bash
cd edge
pip install -r requirements.txt
python -m edge.src.app
```

## Testing

### Server Tests
```bash
cd server
npm test
```

### Edge Tests
```bash
cd edge
python -m pytest tests/
```

### Integration Tests
- Device registration flows
- Authentication mechanisms
- Heartbeat functionality
- Admin approval workflows

## Troubleshooting

### Common Issues

1. **Registration Fails**: Check server connectivity and API endpoints
2. **Approval Timeout**: Verify admin dashboard access and approval process
3. **Heartbeat Issues**: Check API key validity and network connectivity
4. **Credential Errors**: Verify environment variables and credential format

### Debug Mode
Enable debug logging in both server and edge applications:

```bash
# Server
DEBUG=device-registration:* npm run start:dev

# Edge
PYTHONPATH=/workspace/edge python -m edge.src.app --log-level DEBUG
```

## Future Enhancements

1. **Certificate-based Authentication**: PKI support for enhanced security
2. **Device Groups**: Organize devices by location or function
3. **Automated Provisioning**: Integration with device discovery protocols
4. **Mobile Admin App**: React Native app for field approvals
5. **Analytics Dashboard**: Registration metrics and trends
6. **Webhook Integration**: External system notifications
7. **Device Firmware Management**: OTA update coordination

## Support

For issues and questions:
- Check logs in `/workspace/server/logs/` and `/workspace/edge/logs/`
- Review API documentation at `http://server:3000/api/docs`
- Monitor database queries for performance issues
- Use admin dashboard for device management and troubleshooting