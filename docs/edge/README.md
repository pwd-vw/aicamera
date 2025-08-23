# Edge Component Documentation

## Overview

The Edge component is a Python-based AI camera system designed for license plate recognition (LPR) using Raspberry Pi 5 and Hailo-8 AI Accelerator.

## Features

- **Real-time LPR Detection**: License plate recognition using Hailo AI
- **Camera Integration**: Support for Raspberry Pi Camera Module 3
- **Web Interface**: Flask-based dashboard for monitoring and control
- **Health Monitoring**: System health and performance monitoring
- **Image Storage**: Local storage of captured images
- **Multi-protocol Communication**: WebSocket, REST API, and MQTT support

## Architecture

```
edge/
├── src/                    # Application source code
│   ├── app.py             # Main Flask application
│   ├── components/        # Core components
│   ├── core/              # Core utilities and configuration
│   ├── services/          # Business logic services
│   └── web/               # Web interface and blueprints
├── scripts/               # Edge-specific scripts
├── systemd_service/       # Systemd service files
├── tests/                 # Test suite
└── requirements.txt       # Python dependencies
```

## Quick Start

1. **Install Dependencies:**
   ```bash
   cd edge
   python3 -m venv venv_hailo
   source venv_hailo/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   ```bash
   cp env.template .env
   # Edit .env with your configuration
   ```

3. **Start Application:**
   ```bash
   python src/app.py
   ```

4. **Access Web Interface:**
   - Open browser to `http://localhost:5000`
   - Health check: `http://localhost:5000/health`

## Configuration

See [Configuration Guide](configuration.md) for detailed configuration options.

## API Reference

See [API Reference](api-reference.md) for complete API documentation.

## Development

See [Development Guide](../developer/edge-development.md) for development setup and guidelines.

## Troubleshooting

See [Troubleshooting Guide](../guides/troubleshooting.md) for common issues and solutions.
