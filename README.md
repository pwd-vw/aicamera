# AI Camera Monorepo

Edge AI Camera system for License Plate Recognition (LPR) detection with distributed architecture.

**Repository:** https://github.com/popwandee/aicamera.git

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Edge Camera   │    │   Load Balancer │    │   Web Dashboard │
│   (Python)      │────│   (Nginx)       │────│   (React/Vue)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Server    │    │   Database      │    │   Redis Cache   │
│   (Node.js)     │    │   (PostgreSQL)  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Repository Structure

```
aicamera/
├── edge/                    # Python-based edge camera application
│   ├── src/                # Edge application source code
│   ├── scripts/            # Edge-specific scripts and utilities
│   ├── installation/       # Installation and configuration files
│   │   ├── install.sh      # Main installation script
│   │   ├── setup_env.sh    # Environment setup script
│   │   ├── requirements.txt # Python dependencies
│   │   └── .env.production # Production environment config
│   ├── venv_hailo/         # Python virtual environment
│   ├── captured_images/    # Local image storage
│   ├── db/                 # Database files
│   ├── logs/               # Application logs
│   ├── nginx.conf          # Web server configuration
│   ├── gunicorn_config.py  # WSGI server configuration
│   ├── systemd_service/    # System service files
│   └── tests/              # Python tests
├── server/                 # Node.js-based data ingestion server
│   ├── src/                # Server source code
│   │   ├── routes/         # API routes
│   │   ├── utils/          # Utility functions
│   │   ├── database/       # Database models
│   │   ├── socket/         # WebSocket handlers
│   │   ├── communication/  # Multi-protocol communication
│   │   └── services/       # Business logic services
│   ├── database/           # Database schema and migrations
│   │   └── schema.sql      # PostgreSQL schema
│   ├── protocols/          # Shared communication protocols
│   │   ├── api-spec.json   # REST API specification
│   │   ├── socket-events.json # Socket.IO event specs
│   │   └── communication-strategy.json # Multi-protocol strategy
│   └── package.json        # Node.js dependencies
├── docs/                   # Documentation
└── resources/              # AI models and configuration files
```

## 🔄 Communication Strategy

### Multi-Protocol Approach
1. **WebSocket (Primary)** - Real-time bidirectional communication
2. **REST API (Backup)** - HTTP REST API for reliable communication
3. **MQTT (Fallback)** - Lightweight messaging for poor network conditions

### Image Transfer
- **SFTP + rsync** - Secure file transfer for captured images
- Source: `captured_images/` (edge)
- Destination: `image_storage/` (server)

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ (for server)
- Python 3.11+ (for edge)
- PostgreSQL 14+ (for database)
- Redis 6+ (for caching)
- Hailo AI Accelerator (for edge inference)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/popwandee/aicamera.git
   cd aicamera
   ```

2. **Setup the monorepo:**
   ```bash
   npm run setup
   ```

3. **Install server dependencies:**
   ```bash
   cd server
   npm install
   ```

4. **Install edge dependencies:**
   ```bash
   cd edge/installation
   ./install.sh
   ```

5. **Configure environment:**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

6. **Setup database:**
   ```bash
   # Create database
   createdb aicamera
   
   # Apply schema
   psql -d aicamera -f server/database/schema.sql
   ```

### Development

- **Start server:** `cd server && npm start`
- **Start edge:** `cd edge && python src/app.py`
- **Run tests:** `cd server && npm test` or `cd edge && python -m pytest`

## 🔧 Hardware Requirements

### Edge Camera (Raspberry Pi 5)
- Raspberry Pi 5 (8GB recommended)
- Camera Module 3 or High-Quality Camera
- Hailo-8 AI Accelerator
- Active Cooler for Raspberry Pi 5

### Server
- Any Linux server with Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Sufficient storage for image storage

## 📡 API Documentation

### REST API
- **Base URL:** `http://localhost:3000/api/v1`
- **Specification:** `server/protocols/api-spec.json`
- **Health Check:** `GET /health`

### WebSocket Events
- **Specification:** `server/protocols/socket-events.json`
- **Events:** Camera registration, detection data, status updates

### MQTT Topics
- **Pattern:** `aicamera/{camera_id}/{event_type}`
- **Events:** detection, status, alert

## 🗄️ Database Schema

The system uses PostgreSQL with the following main tables:
- `cameras` - Edge camera devices
- `detections` - License plate detection results
- `analytics` - Aggregated analytics data
- `camera_health` - Camera health monitoring
- `system_events` - System events and logs

See `server/database/schema.sql` for complete schema.

## 🔐 Security

- **Authentication:** JWT tokens for API access
- **Image Transfer:** SSH key-based authentication for SFTP
- **Network:** TLS/SSL encryption for all communications
- **Rate Limiting:** API rate limiting to prevent abuse

## 📊 Monitoring

### Health Checks
- Server: `GET /health`
- Edge: `GET /health`
- Database: `pg_isready`

### Metrics
- Connection status
- Message latency
- Success rates
- Image transfer speed
- Queue sizes

## 🚀 Deployment

### Development
```bash
npm run dev:server
npm run dev:edge
```

### Production
```bash
# Using PM2 for Node.js
cd server && npm start

# Using systemd for Python
sudo systemctl start aicamera-edge
```

### Docker
```bash
docker-compose up -d
```

## 📚 Documentation

- [API Documentation](docs/api/)
- [Deployment Guide](docs/deployment/)
- [Development Guide](docs/development/)
- [Hardware Setup](docs/hardware/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues:** [GitHub Issues](https://github.com/popwandee/aicamera/issues)
- **Documentation:** [docs/](docs/)
- **Wiki:** [GitHub Wiki](https://github.com/popwandee/aicamera/wiki)

---

**Built with ❤️ for edge AI applications**
