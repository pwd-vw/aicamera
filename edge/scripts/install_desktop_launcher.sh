#!/bin/bash

# Desktop Launcher Installation Script for AI Camera
# This script installs the desktop launcher for the AI Camera web interface

set -e

echo "🖥️  Installing AI Camera Desktop Launcher..."

# Check if we're running as the correct user
if [[ "$USER" != "camuser" ]]; then
    echo "❌ This script must be run as camuser"
    echo "   Please run: sudo -u camuser ./scripts/install_desktop_launcher.sh"
    exit 1
fi

# Check if desktop environment is available
if [[ -z "$DISPLAY" ]]; then
    echo "❌ No desktop environment detected (DISPLAY is not set)"
    echo "   This script should be run in a graphical environment"
    exit 1
fi

# Check if Desktop directory exists
if [[ ! -d "/home/camuser/Desktop" ]]; then
    echo "❌ Desktop directory not found at /home/camuser/Desktop"
    echo "   Creating Desktop directory..."
    mkdir -p /home/camuser/Desktop
fi

# Check if launcher file exists
if [[ ! -f "aicamera-browser.desktop" ]]; then
    echo "❌ Desktop launcher file not found: aicamera-browser.desktop"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Install the desktop launcher
echo "📋 Copying desktop launcher to Desktop..."
cp aicamera-browser.desktop /home/camuser/Desktop/
chmod +x /home/camuser/Desktop/aicamera-browser.desktop
chown camuser:camuser /home/camuser/Desktop/aicamera-browser.desktop

echo "✅ Desktop launcher installed successfully!"
echo "📋 Location: /home/camuser/Desktop/aicamera-browser.desktop"
echo "🚀 You can now double-click the launcher to open the AI Camera web interface"

# Check if kiosk browser service is available
if systemctl list-unit-files | grep -q "kiosk-browser.service"; then
    echo ""
    echo "🖥️  Kiosk browser service is available"
    echo "📋 To start full screen mode: sudo systemctl start kiosk-browser.service"
    echo "📋 To stop full screen mode: sudo systemctl stop kiosk-browser.service"
else
    echo ""
    echo "ℹ️  Kiosk browser service not found"
    echo "📋 Run install.sh to set up the kiosk browser service"
fi
