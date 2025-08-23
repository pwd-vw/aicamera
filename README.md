# AI Camera Monorepo

## Project Overview

This is a monorepo for an AI Camera system with distributed architecture:

- **Edge Component**: Python-based LPR detection on Raspberry Pi 5 + Hailo AI Accelerator
- **Server Component**: Node.js-based data ingestion and management server
- **Communication**: Multi-protocol (WebSocket primary, REST API backup, MQTT fallback)
- **Image Transfer**: SFTP/rsync for secure image transfer

## Architecture

```
aicamera/
├── edge/                    # Python-based edge camera application
│   ├── src/                # Edge application source code
│   ├── requirements.txt    # Python dependencies
│   ├── scripts/           # Edge-specific scripts
│   ├── systemd_service/   # Edge systemd service files
│   └── tests/             # Python tests
├── server/                 # Node.js-based data ingestion server
│   ├── src/                # Server source code
│   │   ├── routes/         # API routes
│   │   ├── utils/          # Utility functions
│   │   ├── database/       # Database models
│   │   ├── socket/         # WebSocket handlers
│   │   ├── communication/  # Multi-protocol communication
│   │   └── services/       # Business logic services
│   ├── database/           # Database schema and migrations
│   ├── protocols/          # Shared communication protocols
│   ├── scripts/           # Server-specific scripts
│   ├── systemd_service/   # Server systemd service files
│   └── package.json        # Node.js dependencies
├── scripts/                # Build, test, and deployment scripts
├── docs/                   # Documentation
│   ├── edge/              # Edge component documentation
│   ├── server/            # Server component documentation
│   ├── shared/            # Shared protocols and schemas
│   ├── guides/            # User guides
│   ├── admin/             # Administrator documentation
│   ├── developer/         # Developer documentation
│   ├── deployment/        # Deployment guides
│   ├── project/           # Project management docs
│   └── scripts/           # Script documentation
└── captured_images/        # Local image storage (edge)
```

## Table of Contents

### 📚 Documentation

#### **Edge Component**
- [Edge Overview](docs/edge/README.md) - Edge component documentation
- [Edge Installation](docs/edge/installation.md) - Installation guide
- [Edge Configuration](docs/edge/configuration.md) - Configuration options
- [Edge API Reference](docs/edge/api-reference.md) - API documentation

#### **Server Component**
- [Server Overview](docs/server/README.md) - Server component documentation
- [Server Installation](docs/server/installation.md) - Installation guide
- [Server Configuration](docs/server/configuration.md) - Configuration options
- [Server API Reference](docs/server/api-reference.md) - API documentation

#### **Shared Resources**
- [Communication Protocols](docs/shared/protocols.md) - WebSocket, REST, MQTT protocols
- [Database Schema](docs/shared/database-schema.md) - Shared database schema
- [API Specifications](docs/shared/api-specifications.md) - OpenAPI specifications
- [Data Models](docs/shared/data-models.md) - Shared data structures

#### **User Guides**
- [Quick Start Guide](docs/guides/quick-start.md) - Get started quickly
- [User Manual](docs/guides/user-manual.md) - Complete user guide
- [Troubleshooting](docs/guides/troubleshooting.md) - Common issues and solutions
- [FAQ](docs/guides/faq.md) - Frequently asked questions

#### **Administrator Documentation**
- [System Administration](docs/admin/system-admin.md) - System administration guide
- [Monitoring & Logging](docs/admin/monitoring.md) - System monitoring
- [Security Guide](docs/admin/security.md) - Security best practices
- [Backup & Recovery](docs/admin/backup-recovery.md) - Backup procedures

#### **Developer Documentation**
- [Development Setup](docs/developer/setup.md) - Development environment setup
- [Contributing Guidelines](docs/developer/contributing.md) - How to contribute
- [Code Standards](docs/developer/code-standards.md) - Coding standards
- [Testing Guide](docs/developer/testing.md) - Testing procedures

#### **Deployment**
- [Deployment Overview](docs/deployment/overview.md) - Deployment strategies
- [Edge Deployment](docs/deployment/edge-deployment-setup.md) - Edge deployment guide
- [Server Deployment](docs/deployment/server-deployment.md) - Server deployment guide
- [CI/CD Pipeline](docs/deployment/ci-cd.md) - Continuous integration/deployment
- [Workflow Configuration](docs/deployment/workflow-config.md) - GitHub Actions configuration

#### **Project Management**
- [Project Overview](docs/project/overview.md) - Project details
- [Architecture](docs/project/architecture.md) - System architecture
- [Versioning Strategy](docs/project/versioning.md) - Semantic versioning
- [Changelog](docs/project/CHANGELOG.md) - Release history
- [Roadmap](docs/project/roadmap.md) - Future development plans

#### **Scripts Documentation**
- [Scripts Overview](docs/scripts/overview.md) - Script documentation
- [Edge Scripts](docs/scripts/edge-scripts.md) - Edge-specific scripts
- [Server Scripts](docs/scripts/server-scripts.md) - Server-specific scripts
- [Deployment Scripts](docs/scripts/deployment-scripts.md) - Deployment automation

### 🚀 Quick Start

#### **Option 1: Automated Installation (Recommended for Production)**

For **Edge Component v2.0** with full production setup:

```bash
# Clone the repository
git clone https://github.com/popwandee/aicamera.git
cd aicamera

# Run automated installation script
cd edge/installation
chmod +x install.sh
./install.sh
```

The installation script will:
- ✅ Install all system dependencies (Hailo SDK, libcamera, nginx)
- ✅ Set up Python virtual environment with Hailo support
- ✅ Install AI models and dependencies
- ✅ Configure nginx reverse proxy
- ✅ Set up systemd service for auto-startup
- ✅ Initialize database and web interface
- ✅ Validate all components

**After installation:**
- 🌐 Web Interface: http://localhost
- 📊 Service Status: `sudo systemctl status aicamera_v1.3.service`
- 📋 Service Logs: `sudo journalctl -u aicamera_v1.3.service -f`

#### **Option 2: Manual Development Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/popwandee/aicamera.git
   cd aicamera
   ```

2. **Setup Edge Component (Development):**
   ```bash
   cd edge
   python3 -m venv venv_hailo
   source venv_hailo/bin/activate
   pip install -r requirements.txt
   ```

3. **Setup Server Component:**
   ```bash
   cd server
   npm install
   ```

4. **Configure Environment:**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

5. **Start Services (Development):**
   ```bash
   # Start Edge (development)
   cd edge && python src/app.py
   
   # Start Server (development)
   cd server && npm run dev
   ```

### 📋 Requirements

#### **Edge Component v2.0 Requirements:**
- **Hardware**: Raspberry Pi 5 (4GB+ RAM recommended)
- **AI Accelerator**: Hailo-8 AI Accelerator (for optimal performance)
- **Camera**: Raspberry Pi Camera Module 3 (or compatible USB camera)
- **Storage**: 32GB+ SD card (Class 10+ recommended)
- **OS**: Raspberry Pi OS 64-bit (Bookworm or newer)
- **Python**: 3.11+ (automatically installed by script)
- **Network**: Stable internet connection for model downloads

#### **Server Component Requirements:**
- **Node.js**: 18+
- **Database**: PostgreSQL 14+, Redis 6+
- **Network**: Stable internet connection for communication

### 🔧 Edge v2.0 Installation Guide

#### **Prerequisites:**
1. **Fresh Raspberry Pi OS Installation** (recommended)
2. **Internet Connection** for dependency downloads
3. **Sudo Access** for system configuration
4. **Hailo SDK** (optional - script will attempt installation)

#### **Installation Steps:**

1. **Clone Repository:**
   ```bash
   git clone https://github.com/popwandee/aicamera.git
   cd aicamera
   ```

2. **Run Installation Script:**
   ```bash
   cd edge/installation
   chmod +x install.sh
   ./install.sh
   ```

3. **Configuration (Interactive):**
   - The script will prompt for:
     - `AICAMERA_ID`: Unique camera identifier
     - `CHECKPOINT_ID`: Checkpoint identifier
     - `CAMERA_LOCATION`: Human-readable location name

4. **Post-Installation:**
   - Web interface available at: http://localhost
   - Service auto-starts on boot
   - Logs: `sudo journalctl -u aicamera_v1.3.service -f`

#### **Installation Features:**

✅ **Automated Setup:**
- System dependency installation (Hailo SDK, libcamera, nginx)
- Python virtual environment with Hailo support
- AI model installation and validation
- Database initialization and schema setup
- Nginx reverse proxy configuration
- Systemd service configuration
- Camera hardware detection and setup

✅ **Validation & Testing:**
- EasyOCR installation validation
- libcamera hardware compatibility check
- Database connectivity testing
- Web interface accessibility verification
- Service health monitoring

✅ **Production Ready:**
- Auto-startup on system boot
- Proper file permissions and ownership
- Log rotation and management
- Error handling and recovery
- Health monitoring endpoints

#### **Troubleshooting:**

**Common Issues:**
- **Camera not detected**: Check camera connections and permissions
- **Hailo SDK issues**: Script will continue without Hailo (limited functionality)
- **Nginx errors**: Check configuration with `sudo nginx -t`
- **Service won't start**: Check logs with `sudo journalctl -u aicamera_v1.3.service`

**Manual Recovery:**
```bash
# Restart service
sudo systemctl restart aicamera_v1.3.service

# Check service status
sudo systemctl status aicamera_v1.3.service

# View logs
sudo journalctl -u aicamera_v1.3.service -f

# Reinstall if needed
cd edge/installation && ./install.sh

#### **Advanced Installation Options:**

The installation script supports additional parameters for custom setups:

```bash
# Install with specific Hailo wheels
./install.sh --pyhailort /path/to/pyhailort.whl --pytappas /path/to/pytappas.whl

# Install with specific Hailo Apps Infrastructure version
./install.sh --tag 25.3.1

# Install with all resources (models, etc.)
./install.sh --all
```

#### **Installation Script Features:**

🔧 **Smart Dependency Management:**
- Automatic Hailo SDK detection and installation
- Fallback mode when Hailo SDK is unavailable
- Virtual environment with system site-packages for libcamera access
- Wheel-based installation for faster setup

🔧 **Hardware Compatibility:**
- Automatic camera hardware detection
- libcamera stack installation and validation
- Camera permission and device setup
- Hardware-specific optimizations

🔧 **Production Configuration:**
- Nginx reverse proxy with Unix socket
- Systemd service with auto-restart
- Proper file permissions and ownership
- Log management and rotation

🔧 **Validation & Testing:**
- Comprehensive component validation
- Web interface accessibility testing
- Service health monitoring
- Error recovery mechanisms

#### **Installation Directory Structure:**

After installation, the following structure is created:

```
/home/camuser/aicamera/
├── edge/
│   ├── venv_hailo/              # Python virtual environment
│   ├── logs/                    # Application logs
│   ├── db/                      # SQLite database
│   ├── captured_images/         # Captured license plate images
│   └── installation/
│       ├── install.sh           # Installation script
│       ├── requirements.txt     # Python dependencies
│       └── .env.production      # Production configuration
├── resources/
│   └── models/                  # AI models (downloaded during installation)
└── server/                      # Server component (if installed)
```

#### **System Services Created:**

- **`aicamera_v1.3.service`**: Main AI Camera application service
- **`nginx`**: Web server and reverse proxy
- **`kiosk-browser.service`**: Optional kiosk browser for display (if enabled)

#### **Configuration Files:**

- **`/etc/systemd/system/aicamera_v1.3.service`**: Systemd service configuration
- **`/etc/nginx/sites-available/aicamera`**: Nginx site configuration
- **`/tmp/aicamera.sock`**: Unix socket for Gunicorn communication
- **`edge/installation/.env.production`**: Application configuration

#### **Post-Installation Verification:**

After installation, verify everything is working:

```bash
# Check service status
sudo systemctl status aicamera_v1.3.service

# Test web interface
curl http://localhost/health

# Check nginx status
sudo systemctl status nginx

# View application logs
sudo journalctl -u aicamera_v1.3.service -f

# Test camera functionality
curl http://localhost/camera/status

# Check database
ls -la edge/db/
```

#### **Monitoring & Maintenance:**

**Daily Monitoring:**
- Service status: `sudo systemctl status aicamera_v1.3.service`
- Log monitoring: `sudo journalctl -u aicamera_v1.3.service -f`
- Web interface: http://localhost

**Maintenance Commands:**
```bash
# Restart service
sudo systemctl restart aicamera_v1.3.service

# Update application (after git pull)
cd edge/installation && ./install.sh

# Check disk space
df -h

# Monitor system resources
htop

# View captured images
ls -la edge/captured_images/
```

### 🔧 Development

- **Edge Development**: See [Edge Development Guide](docs/developer/edge-development.md)
- **Server Development**: See [Server Development Guide](docs/developer/server-development.md)
- **Testing**: See [Testing Guide](docs/developer/testing.md)

### 📞 Support

- **Documentation**: [Complete Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/popwandee/aicamera/issues)
- **Discussions**: [GitHub Discussions](https://github.com/popwandee/aicamera/discussions)

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
