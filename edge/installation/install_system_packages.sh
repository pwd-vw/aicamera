#!/bin/bash

# AI Camera v2.0.0 - System Package Installer
# This script installs system packages that are faster than pip for ARM64

set -e

echo "🚀 Installing AI Camera v2.0.0 System Packages..."
echo "📦 Installing OpenCV via system package manager..."

# Update package lists
echo "🔄 Updating package lists..."
sudo apt-get update

# Install OpenCV system package (much faster than pip build)
echo "📦 Installing python3-opencv..."
sudo apt-get install -y python3-opencv

# Install other system dependencies
echo "📦 Installing additional system dependencies..."
sudo apt-get install -y \
    python3-dev \
    python3-pip \
    python3-venv \
    libcamera-dev \
    libcamera-tools \
    python3-libcamera \
    build-essential \
    cmake \
    pkg-config \
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
    ninja-build

echo "✅ System packages installed successfully!"
echo ""
echo "📋 OpenCV installation summary:"
python3 -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
echo ""
echo "🚀 You can now run the Python package installation:"
echo "   pip install -r requirements.txt"
