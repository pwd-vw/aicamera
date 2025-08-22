# Server Component Documentation

## Overview

The Server component is a Node.js-based data ingestion and management server designed to handle communication with Edge cameras and provide centralized data management.

## Features

- **Data Ingestion**: Receive and process data from Edge cameras
- **Multi-protocol Communication**: WebSocket, REST API, and MQTT support
- **Database Management**: PostgreSQL database with Sequelize ORM
- **Real-time Monitoring**: WebSocket-based real-time updates
- **Image Storage**: Centralized image storage and management
- **Analytics**: Data analytics and reporting capabilities
- **Health Monitoring**: System health and performance monitoring

## Architecture

```
server/
├── src/                    # Application source code
│   ├── index.js           # Main application entry point
│   ├── routes/            # API routes
│   ├── utils/             # Utility functions
│   ├── database/          # Database models and connection
│   ├── socket/            # WebSocket handlers
│   ├── communication/     # Multi-protocol communication
│   └── services/          # Business logic services
├── database/              # Database schema and migrations
├── protocols/             # Communication protocols
├── scripts/              # Server-specific scripts
├── systemd_service/      # Systemd service files
└── package.json          # Node.js dependencies
```

## Quick Start

1. **Install Dependencies:**
   ```bash
   cd server
   npm install
   ```

2. **Configure Environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

3. **Setup Database:**
   ```bash
   # Create database
   createdb aicamera
   
   # Apply schema
   psql -d aicamera -f database/schema.sql
   ```

4. **Start Application:**
   ```bash
   npm start
   ```

5. **Access API:**
   - API Base: `http://localhost:3000/api/v1`
   - Health check: `http://localhost:3000/health`
   - WebSocket: `ws://localhost:3000`

## Configuration

See [Configuration Guide](configuration.md) for detailed configuration options.

## API Reference

See [API Reference](api-reference.md) for complete API documentation.

## Development

See [Development Guide](../developer/server-development.md) for development setup and guidelines.

## Troubleshooting

See [Troubleshooting Guide](../guides/troubleshooting.md) for common issues and solutions.
