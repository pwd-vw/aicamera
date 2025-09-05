# AI Camera v2.0.0 - Offline Installation Guide

This guide explains how to perform a complete offline installation of AI Camera v2.0.0 using locally downloaded packages.

## Overview

The offline installation system allows you to:
- Download all required packages locally
- Install without internet connectivity
- Ensure consistent package versions
- Speed up installations on multiple machines
- Work in air-gapped environments

## Quick Start

### 1. Download Packages (Online)
```bash
# Download all packages locally
./download_packages.sh
```

### 2. Install Offline
```bash
# Perform complete offline installation
./install_offline.sh
```

## Detailed Usage

### Package Management

#### Download Packages
```bash
# Download all stable packages locally
./download_packages.sh
```

This script will:
- Create a local packages directory
- Download all Python wheel files
- Download GitHub packages and create wheels
- Generate a local requirements file
- Verify package integrity

#### Manage Packages
```bash
# Show available commands
./manage_packages.sh help

# List all local packages
./manage_packages.sh list

# Update existing packages
./manage_packages.sh update

# Verify package integrity
./manage_packages.sh verify

# Clean packages directory
./manage_packages.sh clean
```

### Installation Options

#### Standard Installation (Online)
```bash
# Standard installation with online packages
./install.sh
```

#### Offline Installation
```bash
# Offline installation with local packages
./install.sh --local-packages

# Specify custom packages directory
./install.sh --local-packages --packages-dir /path/to/packages
```

#### Complete Offline Installation
```bash
# Automated offline installation (downloads + installs)
./install_offline.sh
```

## File Structure

```
edge/installation/
├── install.sh                 # Main installation script
├── install_offline.sh         # Complete offline installation
├── download_packages.sh       # Package downloader
├── manage_packages.sh         # Package management
├── requirements.txt           # Online requirements
├── local_packages/            # Local packages directory
│   ├── *.whl                 # Python wheel files
│   └── requirements_local.txt # Local requirements
└── README_OFFLINE.md         # This file
```

## Package Information

### Included Packages

#### Core Framework
- Flask>=3.1.1
- Flask-SocketIO==5.3.6
- python-socketio==5.9.0
- Werkzeug>=3.0.6

#### Camera and Image Processing
- Pillow>=10.4.0
- opencv-python==4.8.1.78
- numpy>=1.24.3
- picamera2 (system package)

#### Database
- SQLAlchemy==2.0.23
- alembic==1.12.1

#### AI and OCR
- easyocr==1.7.1
- degirum>=0.18.2
- degirum-tools==0.19.1
- degirum-cli==0.2.0

#### WebSocket and Communication
- websockets==11.0.3
- paho-mqtt
- paramiko
- websocket-client

#### Development and Testing
- notebook>=7.2.2
- ipykernel==6.25.2
- pytest>=7.4.3
- pytest-cov>=4.1.0

#### System Monitoring
- psutil==7.0.0
- python-dotenv==1.0.0
- matplotlib>=3.7.2
- setproctitle==1.3.2

#### Additional Dependencies
- gunicorn
- eventlet
- scikit-image==0.21.0
- faker>=20.0.0

### GitHub Packages
- hailo-apps-infra (from GitHub)

## System Requirements

### Hardware
- Raspberry Pi 5 (recommended)
- Minimum 4GB RAM
- 16GB+ storage space
- Camera Module 3

### Software
- Raspberry Pi OS (Bookworm)
- Python 3.11
- Internet connection (for initial package download)

## Installation Process

### 1. Package Download Phase
1. Check system requirements
2. Create local packages directory
3. Download Python wheel files
4. Clone and build GitHub packages
5. Generate local requirements file
6. Verify package integrity

### 2. Installation Phase
1. Update system packages
2. Setup SSH for deployment
3. Prepare camera system
4. Install Hailo SDK
5. Create virtual environment
6. Install local packages
7. Fix camera compatibility
8. Setup database
9. Configure nginx
10. Setup systemd services
11. Validate installation

## Troubleshooting

### Common Issues

#### Package Download Failures
```bash
# Check internet connectivity
ping 8.8.8.8

# Verify package integrity
./manage_packages.sh verify

# Re-download packages
./manage_packages.sh update --force
```

#### Installation Failures
```bash
# Check service status
sudo systemctl status aicamera_lpr.service

# View service logs
sudo journalctl -u aicamera_lpr.service -f

# Check camera initialization
python -c "from edge.src.components.camera_handler import CameraHandler; c=CameraHandler(); print(c.initialize_camera())"
```

#### Camera Issues
```bash
# Check camera permissions
ls -la /dev/video*

# Test camera manually
python3 -c "from picamera2 import Picamera2; p=Picamera2(); print('Camera OK')"

# Check libcamera
libcamera-hello --list-cameras
```

### Package Management Issues

#### Corrupted Packages
```bash
# Verify package integrity
./manage_packages.sh verify

# Clean and re-download
./manage_packages.sh clean --force
./download_packages.sh
```

#### Missing Packages
```bash
# List current packages
./manage_packages.sh list

# Update packages
./manage_packages.sh update
```

## Advanced Usage

### Custom Package Directory
```bash
# Use custom packages directory
./install.sh --local-packages --packages-dir /custom/path
```

### Package Updates
```bash
# Update specific packages
./manage_packages.sh update

# Force update without confirmation
./manage_packages.sh update --force
```

### Backup and Restore
```bash
# Backup packages
cp -r local_packages/ local_packages_backup/

# Restore packages
cp -r local_packages_backup/ local_packages/
```

## Security Considerations

### Package Integrity
- All packages are verified during download
- Wheel files are checked for corruption
- GitHub packages are built from source

### Offline Security
- No external network access during installation
- All dependencies are locally verified
- Consistent package versions across installations

## Performance Benefits

### Installation Speed
- Faster installation (no network delays)
- Parallel package installation
- Optimized dependency resolution

### Reliability
- No network dependency during installation
- Consistent package versions
- Reduced installation failures

## Support

For issues with offline installation:
1. Check the troubleshooting section
2. Verify package integrity
3. Review installation logs
4. Check system requirements

## Version Information

- AI Camera Version: 2.0.0
- Python Version: 3.11
- Architecture: aarch64 (ARM64)
- Last Updated: $(date)
