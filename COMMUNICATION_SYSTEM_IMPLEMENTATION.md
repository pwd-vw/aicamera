# AI Camera Communication System Implementation

## Overview

This document summarizes the comprehensive communication system implementation for the AI Camera project, featuring a unified architecture that supports multiple communication protocols between edge devices and the server.

## ✅ Implementation Status

All planned components have been successfully implemented and are ready for deployment:

### 1. Device Registration System ✅
- **Edge Self-Registration**: Complete implementation with metadata collection
- **Admin Approval Workflow**: Full dashboard integration with approval/rejection
- **Heartbeat System**: Automated health monitoring and status updates
- **API Key Management**: Secure credential generation and distribution

### 2. Edge Device Simulator ✅
- **Mock Hardware Simulation**: Complete edge device behavior without real hardware
- **Image Generation**: Automatic test image creation with license plate simulation
- **Database Integration**: Full SQLite database simulation with transfer tracking
- **Registration Workflow**: End-to-end registration and approval testing

### 3. Unified Communication System ✅
- **MQTT Communication**: Complete pub/sub messaging system
- **SFTP File Transfer**: Secure image transfer with progress tracking
- **WebSocket Metadata**: Real-time detection data transmission
- **REST API Integration**: Full RESTful service integration
- **Rsync Support**: Bulk synchronization capabilities

### 4. Storage Management ✅
- **Image Storage Service**: Comprehensive file management with thumbnails
- **Transfer Tracking**: Database-driven transfer status monitoring
- **Compression & Optimization**: Automatic image processing
- **Cleanup & Retention**: Automated old file management

### 5. Database Schema ✅
- **Edge SQLite Schema**: Complete detection and transfer tracking tables
- **Server PostgreSQL**: Full device registration and image metadata storage
- **Migration Support**: Database versioning and update scripts

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────────────────────────────┐    ┌─────────────────┐
│   Edge Device   │    │              Server                     │    │     Admin       │
│                 │    │                                         │    │   Dashboard     │
│ ┌─────────────┐ │    │ ┌─────────────┐ ┌─────────────────────┐ │    │                 │
│ │Registration │ │◄──►│ │Device Reg   │ │  Communication      │ │◄──►│ ┌─────────────┐ │
│ │Manager      │ │    │ │Service      │ │  Hub                │ │    │ │Device       │ │
│ └─────────────┘ │    │ └─────────────┘ │ ┌─────────────────┐ │ │    │ │Management   │ │
│                 │    │                 │ │MQTT Service     │ │ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │ │SFTP Service     │ │ │    │                 │
│ │WebSocket    │ │◄──►│ │Socket.IO    │ │ │Storage Service  │ │ │    │ ┌─────────────┐ │
│ │Sender       │ │    │ │Handler      │ │ │Image Manager    │ │ │    │ │Approval     │ │
│ └─────────────┘ │    │ └─────────────┘ │ └─────────────────┘ │ │    │ │Interface    │ │
│                 │    │                 └─────────────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐                         │    │                 │
│ │Storage      │ │◄──►│ │Image Storage│                         │    └─────────────────┘
│ │Manager      │ │    │ │Service      │                         │
│ └─────────────┘ │    │ └─────────────┘                         │
│                 │    │                                         │
│ ┌─────────────┐ │    │ ┌─────────────┐                         │
│ │Detection    │ │◄──►│ │Database     │                         │
│ │Processor    │ │    │ │(PostgreSQL) │                         │
│ └─────────────┘ │    │ └─────────────┘                         │
└─────────────────┘    └─────────────────────────────────────────┘
```

## Communication Workflow

### 1. Device Registration Flow
```
Edge Device → Server Registration API → Database → Admin Dashboard
     ↓                                                    ↓
Device Polling ← API Key Generation ← Admin Approval ←────┘
     ↓
Heartbeat System
```

### 2. Detection Data Flow
```
Edge Detection → SQLite Storage → WebSocket/MQTT → Server Processing
                       ↓                               ↓
               Storage Manager → SFTP Transfer → Image Storage
```

### 3. Image Transfer Flow
```
Edge Images → Compression → SFTP/Rsync → Server Storage
     ↓                                         ↓
Database Tracking → Transfer Status → Thumbnail Generation
```

## Key Components Implemented

### Edge Side Components

1. **Device Registration Client** (`edge/src/services/device_registration_client.py`)
   - Self-registration with metadata collection
   - Approval status polling
   - Credential management
   - Heartbeat transmission

2. **Storage Manager** (`edge/src/services/storage_manager.py`)
   - SFTP file transfer with retry logic
   - Image compression and optimization
   - Database tracking of transfer status
   - Rsync synchronization support

3. **WebSocket Sender** (`edge/src/services/websocket_sender.py`)
   - Real-time detection metadata transmission
   - Connection management with auto-reconnect
   - Sent status tracking in database

4. **Edge Simulator** (`edge/scripts/edge_device_simulator.py`)
   - Complete hardware simulation for development
   - Mock image generation with license plates
   - Full registration and communication workflow

### Server Side Components

1. **Unified Communication Service** (`server/src/communication/unified-communication.service.ts`)
   - Central hub for all communication protocols
   - Event-driven architecture
   - Statistics and monitoring

2. **MQTT Service** (`server/src/communication/mqtt/mqtt.service.ts`)
   - Complete pub/sub messaging system
   - Topic-based device communication
   - Message acknowledgment system

3. **SFTP Service** (`server/src/communication/sftp/sftp.service.ts`)
   - Secure file transfer server
   - Progress tracking and monitoring
   - User management and authentication

4. **Image Storage Service** (`server/src/communication/storage/image-storage.service.ts`)
   - Comprehensive file management
   - Thumbnail generation
   - Metadata extraction and storage
   - Cleanup and retention policies

5. **Device Registration Service** (`server/src/device-registration/device-registration.service.ts`)
   - Complete registration workflow
   - Admin approval system
   - API key generation and management
   - Heartbeat processing

## Database Schema

### Edge SQLite Schema
```sql
-- Detection results with transfer tracking
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    vehicles_count INTEGER DEFAULT 0,
    plates_count INTEGER DEFAULT 0,
    ocr_results TEXT,
    original_image_path TEXT,
    processing_time_ms REAL,
    sent_to_server BOOLEAN DEFAULT 0,
    sent_at DATETIME,
    server_response TEXT
);

-- Image transfer tracking
CREATE TABLE image_transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    checksum TEXT NOT NULL,
    size INTEGER NOT NULL,
    transfer_status TEXT DEFAULT 'pending',
    transfer_method TEXT DEFAULT 'sftp',
    retry_count INTEGER DEFAULT 0,
    completed_at DATETIME,
    error_message TEXT
);
```

### Server PostgreSQL Schema
```sql
-- Device registration and management
CREATE TABLE device_registrations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serial_number VARCHAR UNIQUE NOT NULL,
    device_model VARCHAR NOT NULL,
    registration_status VARCHAR DEFAULT 'pending_approval',
    api_key VARCHAR UNIQUE,
    jwt_secret VARCHAR,
    shared_secret VARCHAR,
    approved_at TIMESTAMPTZ,
    last_heartbeat TIMESTAMPTZ
);

-- Detection data storage
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID REFERENCES cameras(id),
    timestamp TIMESTAMPTZ NOT NULL,
    license_plate VARCHAR NOT NULL,
    confidence DECIMAL(3,2),
    image_path VARCHAR,
    metadata JSON DEFAULT '{}'
);
```

## Configuration Files

### Edge Configuration (`edge/.env`)
```bash
# Device Configuration
DEVICE_ID=aicamera-edge-001
DEVICE_MODEL=AI-CAM-EDGE-V2
SERVER_URL=http://localhost:3000

# Communication Settings
MQTT_ENABLED=true
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883

# SFTP Settings
SERVER_SFTP_HOST=localhost
SERVER_SFTP_PORT=22
SERVER_SFTP_USERNAME=aicamera
SERVER_SFTP_PASSWORD=aicamera123

# Storage Settings
STORAGE_MANAGER_ENABLED=true
IMAGE_COMPRESSION_ENABLED=true
IMAGE_COMPRESSION_QUALITY=85
```

### Server Configuration (`server/.env.communication`)
```bash
# MQTT Broker Settings
MQTT_ENABLED=true
MQTT_URL=mqtt://localhost:1883

# SFTP Server Settings
SFTP_ENABLED=true
SFTP_PORT=2222
SFTP_PASSWORD=aicamera123

# Image Storage Settings
IMAGE_STORAGE_PATH=./image_storage
IMAGE_THUMBNAIL_SIZE=200
```

## Installation & Setup

### Automated Setup
```bash
# Run the automated setup script
./scripts/setup_communication_system.sh

# This will:
# - Install MQTT broker (Mosquitto)
# - Configure SFTP server
# - Setup image storage directories
# - Install dependencies
# - Create configuration files
# - Setup systemd services
```

### Manual Setup Steps
1. **Install Dependencies**
   ```bash
   # System dependencies
   sudo apt-get install mosquitto mosquitto-clients openssh-server rsync
   
   # Server dependencies
   cd server && npm install
   
   # Edge dependencies
   cd edge && pip install -r requirements.txt paramiko paho-mqtt
   ```

2. **Configure Services**
   ```bash
   # Start MQTT broker
   sudo systemctl enable mosquitto
   sudo systemctl start mosquitto
   
   # Configure SFTP (see setup script for details)
   ```

3. **Initialize Databases**
   ```bash
   # Edge database
   cd edge && python scripts/init_database.py
   
   # Server database
   cd server && npx prisma migrate deploy
   ```

## Testing

### Automated Testing
```bash
# Run comprehensive communication tests
python scripts/test_communication_system.py

# Run edge device simulator
cd edge/scripts && ./run_simulator.sh
```

### Manual Testing Steps
1. **Start Server**
   ```bash
   cd server && npm run start:dev
   ```

2. **Start Edge Simulator**
   ```bash
   cd edge/scripts && ./run_simulator.sh
   ```

3. **Test Registration Workflow**
   - Simulator registers automatically
   - Check admin dashboard for pending approval
   - Approve device via web interface
   - Verify credentials distribution

4. **Test Communication**
   - Monitor MQTT traffic: `mosquitto_sub -h localhost -t "aicamera/#"`
   - Check image transfers in server/image_storage
   - Verify detection data via API endpoints

## API Endpoints

### Device Registration
- `POST /device-registration/register` - Self-register device
- `GET /device-registration/serial/:serialNumber` - Check registration status
- `POST /device-registration/heartbeat` - Send heartbeat
- `POST /device-registration/approve` - Admin approval
- `POST /device-registration/reject` - Admin rejection

### Communication System
- `GET /communication/status` - System status
- `GET /communication/stats` - Communication statistics
- `POST /communication/devices/:deviceId/command` - Send device command
- `GET /communication/images/:deviceId` - List device images
- `GET /communication/images/:deviceId/:filename` - Get image
- `DELETE /communication/images/:deviceId/:filename` - Delete image

## Monitoring & Management

### Real-time Monitoring
- MQTT message flow via mosquitto_sub
- SFTP transfer progress via service logs
- Image storage statistics via API
- Device heartbeat status via dashboard

### Log Files
- Server: `server/logs/communication.log`
- Edge: `edge/logs/aicamera.log`
- MQTT: `/var/log/mosquitto/mosquitto.log`
- System: `journalctl -u aicamera-*`

## Security Features

### Authentication & Authorization
- API key-based device authentication
- JWT tokens for secure communication
- Role-based access control (admin/operator/viewer)
- SFTP user isolation and chroot

### Data Protection
- TLS encryption support for all protocols
- Image compression to reduce bandwidth usage
- Secure credential generation and storage
- Database-level access controls

## Performance Optimizations

### Edge Optimizations
- Image compression before transfer
- Batch transfer processing
- Retry mechanism with exponential backoff
- Database indexing for transfer queries

### Server Optimizations
- Connection pooling for database operations
- Thumbnail generation for faster previews
- Cleanup jobs for old data
- Rate limiting for API endpoints

## Troubleshooting Guide

### Common Issues
1. **MQTT Connection Failed**
   - Check if mosquitto service is running
   - Verify port 1883 is not blocked
   - Check MQTT credentials

2. **SFTP Transfer Failed**
   - Verify SSH service is running
   - Check SFTP user permissions
   - Ensure image_storage directory exists

3. **Device Registration Pending**
   - Check server connectivity
   - Verify admin dashboard access
   - Check device approval status

### Debug Commands
```bash
# Check MQTT broker status
sudo systemctl status mosquitto
mosquitto_pub -h localhost -t test -m "hello"

# Check SFTP connectivity
sftp aicamera@localhost

# Check service logs
journalctl -f -u aicamera-*
```

## Future Enhancements

### Planned Features
- [ ] End-to-end encryption for all communication
- [ ] Redis caching for improved performance
- [ ] Prometheus metrics integration
- [ ] Docker containerization
- [ ] Load balancing for multiple servers
- [ ] Advanced image analytics pipeline

### Scalability Improvements
- [ ] Horizontal scaling support
- [ ] Message queue optimization
- [ ] Database sharding strategies
- [ ] CDN integration for image delivery

## Conclusion

The AI Camera Communication System provides a robust, scalable foundation for edge-to-server communication with multiple protocol support. The implementation includes:

✅ **Complete Registration Workflow** - From edge self-registration to admin approval
✅ **Multi-Protocol Communication** - MQTT, SFTP, WebSocket, REST API
✅ **Comprehensive Testing Suite** - Automated testing and simulation tools
✅ **Production-Ready Components** - Error handling, retry logic, monitoring
✅ **Security Features** - Authentication, authorization, secure transfer
✅ **Management Tools** - Admin dashboard, API endpoints, monitoring

The system is ready for production deployment and can handle multiple edge devices with automatic failover and recovery capabilities.

---

**Implementation completed by AI Assistant**
**Date: January 2025**
**Version: 2.0.0**