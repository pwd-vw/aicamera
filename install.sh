#!/bin/bash

# AI Camera Monorepo Installation Script
# This script delegates to the appropriate component installation

set -e

echo "🚀 AI Camera Monorepo Installation"
echo "=================================="

# Check if we're in the right directory
if [[ ! -f "README.md" ]]; then
    echo "❌ Error: Please run this script from the aicamera root directory"
    exit 1
fi

# Check if edge installation directory exists
if [[ ! -d "edge/installation" ]]; then
    echo "❌ Error: Edge installation directory not found"
    echo "   Expected: edge/installation/"
    exit 1
fi

echo "📋 Installing Edge Component..."
echo "   Running: edge/installation/install.sh"
echo ""

# Run the edge installation script
if [[ -f "edge/installation/install.sh" ]]; then
    chmod +x edge/installation/install.sh
    ./edge/installation/install.sh
else
    echo "❌ Error: Edge installation script not found"
    echo "   Expected: edge/installation/install.sh"
    exit 1
fi

echo ""
echo "✅ Installation completed!"
echo "📋 Next steps:"
echo "   - Configure your environment in edge/installation/.env.production"
echo "   - Start the service: sudo systemctl start aicamera_v1.3.service"
echo "   - Check status: sudo systemctl status aicamera_v1.3.service"
echo "   - View logs: sudo journalctl -u aicamera_v1.3.service -f"
