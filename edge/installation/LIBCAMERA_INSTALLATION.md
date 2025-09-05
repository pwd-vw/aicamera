# AI Camera Edge Device Installation Guide

This guide covers the installation of AI Camera edge devices with proper libcamera and rpicam support.

## Overview

The AI Camera project is a monorepo containing both edge and server components. This installation guide focuses on setting up edge devices that can capture and process camera data.

## System Requirements

### Raspberry Pi (Recommended)
- Raspberry Pi 4 or newer
- Raspberry Pi OS (Bookworm) or Ubuntu 22.04+
- Camera module (CSI or USB)
- 4GB+ RAM recommended
- 32GB+ SD card

### Generic Linux Systems
- Ubuntu 20.04+ or Debian 11+
- USB camera or compatible camera hardware
- 2GB+ RAM
- 16GB+ storage

## Installation Methods

### 1. Automated Installation (Recommended)

Use the new edge installation script that automatically detects your system and installs appropriate camera software:

```bash
# Navigate to the edge installation directory
cd /path/to/aicamera/edge/installation

# Run the edge installation script
./install_edge.sh
```

#### Installation Options

```bash
# Auto-detect system and install
./install_edge.sh

# Force Raspberry Pi installation (even on non-RPi systems)
./install_edge.sh --target-system raspberry-pi

# Force generic Linux installation
./install_edge.sh --target-system generic

# Force rpicam installation on any system
./install_edge.sh --force-rpicam

# Offline installation with local packages
./install_edge.sh --local-packages --packages-dir /path/to/packages
```

### 2. Manual Installation

If you prefer manual installation or need to customize the process:

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git curl wget

# 2. For Raspberry Pi: Add Raspberry Pi repository
echo "deb http://archive.raspberrypi.org/debian/ bookworm main" | sudo tee /etc/apt/sources.list.d/raspberrypi.list
curl -fsSL https://archive.raspberrypi.org/debian/raspberrypi-archive-keyring.gpg | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/raspberrypi-archive-keyring.gpg
sudo apt-get update

# 3. Install camera software
# For Raspberry Pi:
sudo apt-get install -y libcamera-tools python3-libcamera rpicam-apps

# For generic Linux:
sudo apt-get install -y libcamera-tools python3-libcamera

# 4. Create virtual environment
python3 -m venv --system-site-packages venv_edge
source venv_edge/bin/activate

# 5. Install Python dependencies
pip install -r requirements.txt
```

## Camera Software Components

### libcamera
- **Purpose**: Modern camera stack for Linux
- **Version**: 0.5.1+ (latest from Raspberry Pi repository)
- **Components**:
  - `libcamera-tools`: Command-line tools
  - `python3-libcamera`: Python bindings
  - `libcamera-dev`: Development files

### rpicam (Raspberry Pi only)
- **Purpose**: Optimized camera applications for Raspberry Pi
- **Components**:
  - `rpicam-hello`: Camera detection and testing
  - `rpicam-still`: Still image capture
  - `rpicam-vid`: Video recording
  - `rpicam-detect`: AI detection integration

## Validation and Testing

### Run Validation Script

After installation, validate your setup:

```bash
python3 edge/scripts/validate_libcamera.py
```

This script will:
- Detect your system architecture
- Check libcamera installation
- Verify rpicam tools (on Raspberry Pi)
- Test camera hardware
- Validate Python integration

### Manual Camera Testing

#### Raspberry Pi
```bash
# List available cameras
rpicam-hello --list-cameras

# Test camera capture
rpicam-still -o test.jpg

# Test video recording
rpicam-vid -t 5000 -o test.h264
```

#### Generic Linux
```bash
# List video devices
v4l2-ctl --list-devices

# Test camera with cheese (if GUI available)
cheese

# Test with libcamera
libcamera-hello --list-cameras
```

## Configuration

### Environment Configuration

Create or edit the production environment file:

```bash
nano edge/installation/.env.production
```

Key configuration options:
```env
# Camera settings
CAMERA_ID=0
CAMERA_RESOLUTION=1920x1080
CAMERA_FPS=30

# System identification
AICAMERA_ID=1
CHECKPOINT_ID=1
CAMERA_LOCATION="Main Entrance"

# Detection settings
DETECTION_MODEL=hailo
CONFIDENCE_THRESHOLD=0.5
```

### Service Configuration

The installation script automatically configures a systemd service:

```bash
# Check service status
sudo systemctl status aicamera_lpr.service

# Start service
sudo systemctl start aicamera_lpr.service

# View logs
sudo journalctl -u aicamera_lpr.service -f
```

## Troubleshooting

### Common Issues

#### 1. libcamera not found in Python
```bash
# Recreate virtual environment with system site-packages
deactivate
rm -rf venv_edge
python3 -m venv --system-site-packages venv_edge
source venv_edge/bin/activate
pip install -r requirements.txt
```

#### 2. Camera not detected
```bash
# Check camera hardware
ls /dev/video*

# Check camera permissions
sudo chmod 666 /dev/video*

# Check system logs
dmesg | grep -i camera
```

#### 3. rpicam tools not working
```bash
# Ensure Raspberry Pi repository is configured
grep -r "raspberrypi.org" /etc/apt/sources.list*

# Reinstall rpicam tools
sudo apt-get install --reinstall rpicam-apps
```

#### 4. Virtual environment issues
```bash
# Check virtual environment activation
echo $VIRTUAL_ENV

# Verify Python path
which python
python -c "import sys; print(sys.path)"
```

### Validation Output Interpretation

The validation script provides detailed output:

- ✅ **PASSED**: Component working correctly
- ❌ **FAILED**: Component needs attention
- ⚠️ **SKIPPED**: Component not applicable to your system

### Getting Help

1. Run the validation script: `python3 edge/scripts/validate_libcamera.py`
2. Check service logs: `sudo journalctl -u aicamera_lpr.service -f`
3. Review installation logs in the terminal output
4. Check system logs: `dmesg | grep -i camera`

## Development vs Production

### Development Setup
- Use the main `install.sh` script for development
- Includes additional development tools and debugging features
- More verbose output and error handling

### Production Setup
- Use the new `install_edge.sh` script for production edge devices
- Optimized for minimal resource usage
- Focused on camera functionality and reliability

## Next Steps

After successful installation:

1. **Configure the system**: Edit `.env.production` with your specific settings
2. **Test camera functionality**: Run validation and manual tests
3. **Start the service**: `sudo systemctl start aicamera_lpr.service`
4. **Monitor operation**: Check logs and web interface
5. **Deploy to production**: Follow your deployment procedures

## Support

For issues specific to:
- **Raspberry Pi**: Check [Raspberry Pi Camera Documentation](https://www.raspberrypi.com/documentation/computers/camera_software.html)
- **libcamera**: Check [libcamera Documentation](https://libcamera.org/)
- **AI Camera Project**: Check project documentation and issues
