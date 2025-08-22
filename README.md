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

1. **Clone the repository:**
   ```bash
   git clone https://github.com/popwandee/aicamera.git
   cd aicamera
   ```

2. **Setup Edge Component:**
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

5. **Start Services:**
   ```bash
   # Start Edge (development)
   cd edge && python src/app.py
   
   # Start Server (development)
   cd server && npm run dev
   ```

### 📋 Requirements

- **Edge**: Python 3.11+, Raspberry Pi 5, Hailo-8 AI Accelerator
- **Server**: Node.js 18+, PostgreSQL 14+, Redis 6+
- **Network**: Stable internet connection for communication

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
