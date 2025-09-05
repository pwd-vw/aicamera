# AI Camera v2.0.0 Installation Guide

## Quick Start (Recommended)

### 1. Install System Dependencies First
```bash
# Run the system package installer
./edge/installation/install_system_packages.sh
```

This installs:
- OpenCV via system package (much faster than pip)
- All required build dependencies
- Development tools and libraries

### 2. Install Python Dependencies
```bash
# Activate your virtual environment
source venv_hailo/bin/activate

# Install Python packages
pip install -r edge/installation/requirements.txt
```

## Alternative: Offline Installation

### 1. Download Packages Locally
```bash
# Download all packages to local directory
./edge/installation/download_packages.sh
```

### 2. Install from Local Packages
```bash
# Install from downloaded packages
pip install -r edge/installation/local_packages/requirements_local.txt
```

## Key Improvements Made

### ✅ **Faster Installation**
- **OpenCV**: Now uses system package (`python3-opencv`) instead of building from source
- **Latest Versions**: Updated to latest stable versions of all packages
- **Progress Tracking**: Added progress indicators to download script

### ✅ **Better ARM64 Support**
- **System Packages**: Uses pre-compiled system packages where possible
- **Build Dependencies**: Added all missing system dependencies
- **Wheel Priority**: Downloads wheels first, skips source builds

### ✅ **Consolidated Requirements**
- **Single File**: Merged all requirements into one file
- **Latest LTS**: Updated to latest long-term support versions
- **Clear Documentation**: Added installation notes and alternatives

## Package Versions Updated

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| Flask | 3.1.1 | 3.1.2 | Latest stable |
| SQLAlchemy | 2.0.23 | 2.0.43 | Latest stable |
| Pillow | 10.4.0 | 11.3.0 | Latest stable |
| numpy | 1.24.3 | 1.26.4 | Latest stable |
| pandas | 2.0.3 | 2.2.3 | Latest stable |
| matplotlib | 3.7.2 | 3.9.2 | Latest stable |
| pytest | 7.4.3 | 8.3.4 | Latest stable |
| paramiko | 2.12.0 | 3.4.0 | Latest stable |

## Troubleshooting

### If OpenCV Installation Fails
```bash
# Install OpenCV system package manually
sudo apt-get update
sudo apt-get install python3-opencv

# Verify installation
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
```

### If Build Dependencies Are Missing
```bash
# Install all build dependencies
sudo apt-get install -y build-essential cmake pkg-config libssl-dev libffi-dev
```

### If Wheel Downloads Fail
```bash
# Use system packages instead
sudo apt-get install python3-pip python3-dev python3-venv
```

## Performance Comparison

| Method | OpenCV Installation Time | Total Installation Time |
|--------|-------------------------|------------------------|
| **Old (pip build)** | 2-4 hours | 3-5 hours |
| **New (system package)** | 2-5 minutes | 10-15 minutes |

## Next Steps

1. **Test Installation**: Run `python3 -c "import cv2, flask, sqlalchemy; print('All packages imported successfully')"`
2. **Start Application**: Follow the main README.md for application startup
3. **Monitor Performance**: Check system resources during operation

## Support

If you encounter issues:
1. Check the system dependencies are installed
2. Verify Python virtual environment is activated
3. Check available disk space (at least 2GB free)
4. Review the installation logs for specific error messages
