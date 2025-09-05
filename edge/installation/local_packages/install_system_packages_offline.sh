#!/bin/bash

# AI Camera v2.0.0 - System Packages Installation for Offline Setup
# This script installs system packages required for offline installation

set -e

echo "🚀 Installing AI Camera v2.0.0 System Packages for Offline Setup..."
echo "📦 Installing system packages required for offline installation..."

# Update package lists
echo "🔄 Updating package lists..."
sudo apt-get update

# Install all packages from the list
echo "📦 Installing system packages..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    pkg-config \
    python3-opencv \
    libcamera-dev \
    libcamera-tools \
    python3-libcamera \
    libcamera-apps \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    liblzma-dev \
    ninja-build \
    nginx

echo "✅ System packages installed successfully!"
echo ""
echo "📋 OpenCV installation summary:"
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')" 2>/dev/null || echo "⚠️  OpenCV not accessible - may need virtual environment setup"
echo ""
echo "🚀 System is now ready for offline AI Camera installation!"
