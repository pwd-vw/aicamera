#!/bin/bash
# Factory Reset Script for AI Camera v1.3
# This script completely removes the installation and prepares for fresh install

set -e

echo "🚨 FACTORY RESET - AI Camera v1.3"
echo "=================================="
echo "This script will completely remove the AI Camera installation."
echo "All data, configurations, and services will be deleted."
echo ""

# Confirmation prompt
read -p "Are you sure you want to proceed with factory reset? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Factory reset cancelled."
    exit 0
fi

echo ""
echo "🔄 Starting factory reset process..."

# Step 1: Stop and disable services
echo "📋 Step 1: Stopping and disabling services..."
if sudo systemctl is-active --quiet aicamera_v1.3.service; then
    echo "   Stopping aicamera_v1.3 service..."
    sudo systemctl stop aicamera_v1.3.service
    echo "   ✅ Service stopped"
else
    echo "   ⚪ Service not running"
fi

if sudo systemctl is-active --quiet nginx; then
    echo "   Stopping nginx service..."
    sudo systemctl stop nginx
    echo "   ✅ Nginx stopped"
else
    echo "   ⚪ Nginx not running"
fi

# Disable services
echo "   Disabling services..."
sudo systemctl disable aicamera_v1.3.service 2>/dev/null || echo "   ⚪ Service not enabled"
sudo systemctl disable nginx 2>/dev/null || echo "   ⚪ Nginx not enabled"

# Step 2: Remove systemd service files
echo ""
echo "📋 Step 2: Removing systemd service files..."
if [[ -f "/etc/systemd/system/aicamera_v1.3.service" ]]; then
    sudo rm -f /etc/systemd/system/aicamera_v1.3.service
    echo "   ✅ Removed aicamera_v1.3.service"
else
    echo "   ⚪ Service file not found"
fi

# Reload systemd
sudo systemctl daemon-reload

# Step 3: Remove nginx configuration
echo ""
echo "📋 Step 3: Removing nginx configuration..."
if [[ -f "/etc/nginx/sites-enabled/aicamera" ]]; then
    sudo rm -f /etc/nginx/sites-enabled/aicamera
    echo "   ✅ Removed nginx site link"
fi

if [[ -f "/etc/nginx/sites-available/aicamera" ]]; then
    sudo rm -f /etc/nginx/sites-available/aicamera
    echo "   ✅ Removed nginx site config"
fi

# Restore default nginx config if backup exists
if [[ -f "/etc/nginx/sites-available/default.backup" ]]; then
    sudo cp /etc/nginx/sites-available/default.backup /etc/nginx/sites-available/default
    sudo ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
    echo "   ✅ Restored default nginx config"
fi

# Step 4: Remove Unix socket
echo ""
echo "📋 Step 4: Removing Unix socket..."
if [[ -S "/tmp/aicamera.sock" ]]; then
    sudo rm -f /tmp/aicamera.sock
    echo "   ✅ Removed Unix socket"
else
    echo "   ⚪ Unix socket not found"
fi

# Step 5: Remove project data and files
echo ""
echo "📋 Step 5: Removing project data and files..."

# Remove database
if [[ -f "db/lpr_data.db" ]]; then
    rm -f db/lpr_data.db
    echo "   ✅ Removed SQLite database"
else
    echo "   ⚪ Database not found"
fi

# Remove captured images
if [[ -d "captured_images" ]]; then
    rm -rf captured_images
    echo "   ✅ Removed captured images"
else
    echo "   ⚪ Captured images directory not found"
fi

# Remove logs
if [[ -d "logs" ]]; then
    rm -rf logs
    echo "   ✅ Removed logs directory"
else
    echo "   ⚪ Logs directory not found"
fi

# Remove environment files
if [[ -f ".env.production" ]]; then
    rm -f .env.production
    echo "   ✅ Removed .env.production"
else
    echo "   ⚪ .env.production not found"
fi

if [[ -f ".env" ]]; then
    rm -f .env
    echo "   ✅ Removed .env"
else
    echo "   ⚪ .env not found"
fi

# Step 6: Remove Python virtual environment
echo ""
echo "📋 Step 6: Removing Python virtual environment..."
if [[ -d "venv_hailo" ]]; then
    echo "   Removing virtual environment..."
    rm -rf venv_hailo
    echo "   ✅ Removed virtual environment"
else
    echo "   ⚪ Virtual environment not found"
fi

# Step 7: Remove Python packages (optional)
echo ""
echo "📋 Step 7: Removing Python packages..."
read -p "Do you want to remove all Python packages? This will affect other projects. (yes/no): " remove_packages
if [[ "$remove_packages" == "yes" ]]; then
    echo "   Removing Python packages..."
    echo "   ⚠️  Note: System Python packages are protected by externally-managed-environment"
    echo "   📋 Only removing packages from virtual environment (if it exists)"
    
    # Try to remove packages from virtual environment if it exists
    if [[ -d "venv_hailo" ]]; then
        echo "   Virtual environment still exists, removing packages..."
        venv_hailo/bin/pip list | grep -E "(opencv|flask|gunicorn|degirum|picamera)" | awk '{print $1}' | xargs -r venv_hailo/bin/pip uninstall -y
        echo "   ✅ Removed AI Camera related packages from virtual environment"
    else
        echo "   ⚪ Virtual environment already removed, skipping package removal"
    fi
    
    echo "   💡 System packages are protected and cannot be removed automatically"
    echo "   💡 If needed, manually remove with: sudo apt remove python3-<package>"
else
    echo "   ⚪ Skipping package removal"
fi

# Step 8: Clean up system packages (optional)
echo ""
echo "📋 Step 8: Cleaning up system packages..."
read -p "Do you want to remove nginx? (yes/no): " remove_nginx
if [[ "$remove_nginx" == "yes" ]]; then
    echo "   Removing nginx..."
    sudo apt remove -y nginx nginx-common
    sudo apt autoremove -y
    echo "   ✅ Removed nginx"
else
    echo "   ⚪ Keeping nginx installed"
fi

# Step 8.5: Clean up system Python packages (optional)
echo ""
echo "📋 Step 8.5: Cleaning up system Python packages..."
read -p "Do you want to remove system Python packages? (yes/no): " remove_system_packages
if [[ "$remove_system_packages" == "yes" ]]; then
    echo "   ⚠️  Removing system Python packages..."
    echo "   📋 This will remove packages that might affect other projects"
    
    # List packages that might be installed
    packages_to_remove=""
    if dpkg -l | grep -q python3-opencv; then
        packages_to_remove="$packages_to_remove python3-opencv"
    fi
    if dpkg -l | grep -q python3-flask; then
        packages_to_remove="$packages_to_remove python3-flask"
    fi
    if dpkg -l | grep -q python3-gunicorn; then
        packages_to_remove="$packages_to_remove python3-gunicorn"
    fi
    
    if [[ -n "$packages_to_remove" ]]; then
        echo "   Removing: $packages_to_remove"
        sudo apt remove -y $packages_to_remove
        sudo apt autoremove -y
        echo "   ✅ Removed system Python packages"
    else
        echo "   ⚪ No system Python packages found to remove"
    fi
else
    echo "   ⚪ Keeping system Python packages"
fi

# Step 9: Clean up directories
echo ""
echo "📋 Step 9: Cleaning up directories..."
for dir in db logs captured_images; do
    if [[ -d "$dir" ]]; then
        rmdir "$dir" 2>/dev/null && echo "   ✅ Removed empty directory: $dir" || echo "   ⚪ Directory not empty: $dir"
    fi
done

# Step 10: Reset git (optional)
echo ""
echo "📋 Step 10: Git cleanup..."
read -p "Do you want to reset git to clean state? (yes/no): " reset_git
if [[ "$reset_git" == "yes" ]]; then
    echo "   Resetting git..."
    git reset --hard HEAD
    git clean -fd
    echo "   ✅ Git reset completed"
else
    echo "   ⚪ Skipping git reset"
fi

# Final cleanup
echo ""
echo "📋 Final cleanup..."
# Remove any remaining temporary files
find . -name "*.pyc" -delete 2>/dev/null || true
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Removed Python cache files"

echo ""
echo "🎉 FACTORY RESET COMPLETED!"
echo "=========================="
echo ""
echo "✅ All AI Camera v1.3 components have been removed:"
echo "   - Services stopped and disabled"
echo "   - Systemd service files removed"
echo "   - Nginx configuration removed"
echo "   - Database deleted"
echo "   - Captured images removed"
echo "   - Logs removed"
echo "   - Environment files removed"
echo "   - Virtual environment removed"
echo "   - Python packages cleaned (virtual environment)"
echo "   - System packages cleaned (optional)"
echo "   - Python cache cleaned"
echo ""
echo "🔄 To reinstall, run:"
echo "   ./install.sh"
echo ""
echo "📋 Before reinstalling, you may want to:"
echo "   1. Reboot the system: sudo reboot"
echo "   2. Check available disk space: df -h"
echo "   3. Check system status: systemctl status"
echo ""
echo "🚀 Ready for fresh installation!"
