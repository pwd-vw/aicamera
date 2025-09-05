# AI Camera v2.0.0 - Offline Installation Instructions

## Prerequisites
- Target system must be running Ubuntu/Debian-based Linux
- Python 3.11+ must be installed
- Root/sudo access required

## Step 1: Install System Packages
On the target system (with internet), run:
```bash
# Update package lists
sudo apt-get update

# Install all system packages
sudo apt-get install -y $(cat system_packages.txt | grep -v '^#' | grep -v '^$' | tr '\n' ' ')
```

## Step 2: Copy Packages to Target System
Copy the entire `local_packages` directory to the target system:
```bash
# Copy to target system (replace with actual target path)
scp -r local_packages/ user@target-system:/path/to/aicamera/edge/installation/
```

## Step 3: Run Offline Installation
On the target system (without internet), run:
```bash
# Navigate to AI Camera directory
cd /path/to/aicamera

# Run offline installation
./edge/installation/install_offline.sh
```

## Troubleshooting

### OpenCV Issues
If OpenCV import fails:
```bash
# Verify system OpenCV is installed
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"

# If not working, reinstall system OpenCV
sudo apt-get install --reinstall python3-opencv
```

### Missing Dependencies
If Python packages fail to install:
```bash
# Check if all wheel files are present
ls -la local_packages/*.whl

# Verify requirements file
cat local_packages/requirements_local.txt
```

### System Package Issues
If system packages are missing:
```bash
# Install missing packages from the list
sudo apt-get install -y <missing-package-name>
```

## Package Contents
- **Python wheels**: All Python packages as wheel files
- **System packages list**: List of required system packages
- **Requirements file**: Local requirements for pip installation
- **Installation script**: Offline installation script

## Support
For issues, check:
1. System package installation
2. Python virtual environment setup
3. File permissions
4. Available disk space (minimum 2GB)
