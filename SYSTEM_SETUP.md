# AI Camera System Setup and Control

This document explains how to set up and manage the AI Camera system using systemd services and the provided control script.

## Problem Solved

The original issue was a port conflict where multiple Node.js processes were trying to use port 3000, causing `EADDRINUSE` errors. This has been resolved by:

1. **Environment-based port configuration** - The backend now uses `process.env.PORT` instead of hardcoded port 3000
2. **Proper systemd service management** - Services are managed through systemd for reliable startup/shutdown
3. **Comprehensive control script** - A single script handles all system operations
4. **Web-based control interface** - A Vue.js component provides a user-friendly web interface

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Control       │
│   (Port 5173)   │◄──►│   (Port 3000)   │◄──►│   Script        │
│   (Vite)        │    │   (NestJS)      │    │   (systemd)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Files Created/Modified

### Backend Changes
- `server/src/main.ts` - Updated to use environment variables for port
- `server/src/system/` - New system management module
  - `system.controller.ts` - REST API endpoints for system control
  - `system.service.ts` - Service layer for system operations
  - `system.module.ts` - Module configuration
- `server/src/app.module.ts` - Added SystemModule import

### Systemd Services
- `server/systemd_service/aicamera-backend.service` - Backend service configuration
- `server/systemd_service/aicamera-frontend.service` - Frontend service configuration

### Control Script
- `scripts/aicamera-control.sh` - Comprehensive control script with the following commands:
  - `install` - Install and enable systemd services
  - `uninstall` - Uninstall and disable systemd services
  - `start` - Start all services
  - `stop` - Stop all services
  - `restart` - Restart all services
  - `status` - Show status of all services and ports
  - `logs [service]` - Show logs (default: all services)
  - `build` - Build backend and frontend
  - `deploy` - Build and restart services

### Frontend Interface
- `server/frontend/src/views/SystemControl.vue` - Web-based system control interface

## Quick Start Guide

### 1. Install Services
```bash
cd /home/devuser/aicamera
./scripts/aicamera-control.sh install
```

### 2. Start Services
```bash
./scripts/aicamera-control.sh start
```

### 3. Check Status
```bash
./scripts/aicamera-control.sh status
```

### 4. Access the Application
- **Backend API**: http://localhost:3000
- **Frontend**: http://localhost:5173
- **System Control**: http://localhost:5173/system-control (if route is configured)

## Service Management

### Using the Control Script

```bash
# Install services (one-time setup)
./scripts/aicamera-control.sh install

# Start all services
./scripts/aicamera-control.sh start

# Stop all services
./scripts/aicamera-control.sh stop

# Restart all services
./scripts/aicamera-control.sh restart

# Check status
./scripts/aicamera-control.sh status

# View logs
./scripts/aicamera-control.sh logs aicamera-backend
./scripts/aicamera-control.sh logs aicamera-frontend

# Build and deploy
./scripts/aicamera-control.sh deploy

# Uninstall services
./scripts/aicamera-control.sh uninstall
```

### Using systemd Directly

```bash
# Start services
systemctl --user start aicamera-backend
systemctl --user start aicamera-frontend

# Stop services
systemctl --user stop aicamera-backend
systemctl --user stop aicamera-frontend

# Check status
systemctl --user status aicamera-backend
systemctl --user status aicamera-frontend

# View logs
journalctl --user -u aicamera-backend -f
journalctl --user -u aicamera-frontend -f

# Enable auto-start
systemctl --user enable aicamera-backend
systemctl --user enable aicamera-frontend
```

## Web Interface

The system includes a Vue.js-based web interface for system control. Features include:

- **Real-time status monitoring** - Shows service and port status
- **Service control buttons** - Install, start, stop, restart services
- **Build and deploy** - One-click build and deployment
- **Activity logs** - Real-time log display
- **Toast notifications** - User feedback for operations

### API Endpoints

The backend provides REST API endpoints for system control:

- `GET /system/status` - Get system status
- `POST /system/install` - Install services
- `POST /system/start` - Start services
- `POST /system/stop` - Stop services
- `POST /system/restart` - Restart services
- `POST /system/build` - Build and deploy

## Troubleshooting

### Port Conflicts
If you encounter port conflicts:

1. Check what's using the port:
   ```bash
   netstat -tulpn | grep :3000
   ```

2. Kill conflicting processes:
   ```bash
   kill -9 <PID>
   ```

3. Restart services:
   ```bash
   ./scripts/aicamera-control.sh restart
   ```

### Service Issues
If services fail to start:

1. Check service status:
   ```bash
   ./scripts/aicamera-control.sh status
   ```

2. View service logs:
   ```bash
   ./scripts/aicamera-control.sh logs aicamera-backend
   ```

3. Reinstall services:
   ```bash
   ./scripts/aicamera-control.sh uninstall
   ./scripts/aicamera-control.sh install
   ```

### Build Issues
If build fails:

1. Check dependencies:
   ```bash
   cd server && npm install
   cd frontend && npm install
   ```

2. Clean and rebuild:
   ```bash
   cd server && npm run build
   cd frontend && npm run build
   ```

## Configuration

### Environment Variables

The backend uses the following environment variables:

- `PORT` - Backend port (default: 3000)
- `NODE_ENV` - Environment (production/development)

### Service Configuration

Service files are located in `server/systemd_service/`:

- `aicamera-backend.service` - Backend service configuration
- `aicamera-frontend.service` - Frontend service configuration

Key configuration options:
- `Restart=always` - Services restart automatically on failure
- `RestartSec=10` - Wait 10 seconds before restart
- `StartLimitInterval=60` - Limit restarts to prevent loops
- `StartLimitBurst=3` - Maximum 3 restarts per minute

## Security Considerations

1. **User permissions** - Services run as the `devuser` account
2. **Port binding** - Services bind to all interfaces (0.0.0.0)
3. **Logging** - All service logs are captured by systemd
4. **Restart limits** - Services have restart limits to prevent resource exhaustion

## Monitoring

### Log Monitoring
```bash
# Follow all service logs
journalctl --user -f -u aicamera-backend -u aicamera-frontend

# View recent logs
journalctl --user -u aicamera-backend --since "1 hour ago"
```

### Status Monitoring
```bash
# Check service status
./scripts/aicamera-control.sh status

# Monitor ports
netstat -tulpn | grep -E ":(3000|5173)"
```

## Future Enhancements

1. **Health checks** - Add health check endpoints
2. **Metrics** - Add system metrics collection
3. **Configuration UI** - Web-based configuration management
4. **Backup/restore** - System backup and restore functionality
5. **Multi-instance support** - Support for multiple service instances

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review service logs using the control script
3. Verify systemd service status
4. Check port usage and conflicts
