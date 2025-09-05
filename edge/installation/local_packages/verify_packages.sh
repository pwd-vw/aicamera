#!/bin/bash

# AI Camera v2.0.0 - Package Verification Script
# This script verifies that all required packages are available for offline installation

set -e

echo "🔍 AI Camera v2.0.0 - Package Verification"
echo "=========================================="

PACKAGES_DIR="$(dirname "$0")"
ERRORS=0

# Check if packages directory exists
if [ ! -d "$PACKAGES_DIR" ]; then
    echo "❌ Packages directory not found: $PACKAGES_DIR"
    exit 1
fi

echo "📁 Packages directory: $PACKAGES_DIR"

# Check Python wheel files
echo ""
echo "🔍 Checking Python wheel files..."
WHEEL_COUNT=$(ls -1 "$PACKAGES_DIR"/*.whl 2>/dev/null | wc -l)
if [ "$WHEEL_COUNT" -gt 0 ]; then
    echo "✅ Found $WHEEL_COUNT Python wheel files"
else
    echo "❌ No Python wheel files found"
    ((ERRORS++))
fi

# Check requirements file
echo ""
echo "🔍 Checking requirements file..."
if [ -f "$PACKAGES_DIR/requirements_local.txt" ]; then
    echo "✅ Requirements file found: requirements_local.txt"
    echo "📋 Packages in requirements: $(grep -c '^[^#]' "$PACKAGES_DIR/requirements_local.txt")"
else
    echo "❌ Requirements file not found: requirements_local.txt"
    ((ERRORS++))
fi

# Check system packages list
echo ""
echo "🔍 Checking system packages list..."
if [ -f "$PACKAGES_DIR/system_packages.txt" ]; then
    echo "✅ System packages list found: system_packages.txt"
    echo "📋 System packages: $(grep -c '^[^#]' "$PACKAGES_DIR/system_packages.txt")"
else
    echo "❌ System packages list not found: system_packages.txt"
    ((ERRORS++))
fi

# Check installation instructions
echo ""
echo "🔍 Checking installation instructions..."
if [ -f "$PACKAGES_DIR/OFFLINE_INSTALLATION_INSTRUCTIONS.md" ]; then
    echo "✅ Installation instructions found: OFFLINE_INSTALLATION_INSTRUCTIONS.md"
else
    echo "❌ Installation instructions not found: OFFLINE_INSTALLATION_INSTRUCTIONS.md"
    ((ERRORS++))
fi

# Check system package installation script
echo ""
echo "🔍 Checking system package installation script..."
if [ -f "$PACKAGES_DIR/install_system_packages_offline.sh" ]; then
    echo "✅ System package installation script found: install_system_packages_offline.sh"
else
    echo "❌ System package installation script not found: install_system_packages_offline.sh"
    ((ERRORS++))
fi

# Summary
echo ""
echo "📊 Verification Summary:"
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ All packages and files are ready for offline installation"
    echo "🚀 You can now copy this directory to the target system"
    echo ""
    echo "📋 Next steps:"
    echo "   1. Copy local_packages/ to target system"
    echo "   2. Run install_system_packages_offline.sh on target system"
    echo "   3. Run install_offline.sh on target system"
else
    echo "❌ Found $ERRORS issues - please fix before offline installation"
    exit 1
fi
