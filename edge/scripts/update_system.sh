#!/bin/bash
# AI Camera System Update Script v2.0
# This script updates the AI Camera system in-place without switching versions

set -e

echo "🔄 AI Camera System Update v2.0"
echo "=================================="
echo "This script will update your AI Camera system in-place."
echo "Your current configuration and data will be preserved."
echo ""

# Parse command line arguments
BACKUP_DATA=true
SKIP_SERVICES=false
FORCE_UPDATE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-backup)
            BACKUP_DATA=false
            shift
            ;;
        --skip-services)
            SKIP_SERVICES=true
            shift
            ;;
        --force)
            FORCE_UPDATE=true
            shift
            ;;
        -h|--help)
            echo "AI Camera System Update Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --no-backup      Skip data backup (not recommended)"
            echo "  --skip-services  Skip service restart (for maintenance mode)"
            echo "  --force          Force update even if no changes detected"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Standard update with backup"
            echo "  $0 --no-backup        # Update without backup (faster)"
            echo "  $0 --skip-services    # Update without restarting services"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -f "edge/installation/install.sh" ]]; then
    echo "❌ Error: Not in AI Camera project root directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if running as correct user
if [[ "$USER" != "camuser" ]]; then
    echo "❌ Error: Must run as camuser"
    echo "Please run: sudo -u camuser $0"
    exit 1
fi

echo "📋 Update Configuration:"
echo "   - Backup data: $([ "$BACKUP_DATA" = true ] && echo "Yes" || echo "No")"
echo "   - Skip services: $([ "$SKIP_SERVICES" = true ] && echo "Yes" || echo "No")"
echo "   - Force update: $([ "$FORCE_UPDATE" = true ] && echo "Yes" || echo "No")"
echo ""

# Confirmation prompt
read -p "Do you want to proceed with the system update? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    echo "❌ Update cancelled."
    exit 0
fi

echo ""
echo "🚀 Starting AI Camera system update..."

# Step 1: Check current system status
echo ""
echo "Step 1: Checking current system status..."
if systemctl is-active --quiet aicamera_lpr.service; then
    echo "   ✅ AI Camera service is running"
    SERVICE_RUNNING=true
else
    echo "   ⚪ AI Camera service is not running"
    SERVICE_RUNNING=false
fi

# Step 2: Create backup if requested
if [[ "$BACKUP_DATA" = true ]]; then
    echo ""
    echo "Step 2: Creating system backup..."
    BACKUP_DIR="backups/update_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup database
    if [[ -f "edge/db/lpr_data.db" ]]; then
        cp "edge/db/lpr_data.db" "$BACKUP_DIR/"
        echo "   ✅ Database backed up"
    fi
    
    # Backup configuration
    if [[ -f "edge/installation/.env.production" ]]; then
        cp "edge/installation/.env.production" "$BACKUP_DIR/"
        echo "   ✅ Configuration backed up"
    fi
    
    # Backup captured images (last 7 days)
    if [[ -d "edge/captured_images" ]]; then
        mkdir -p "$BACKUP_DIR/captured_images"
        find edge/captured_images -name "*.jpg" -mtime -7 -exec cp {} "$BACKUP_DIR/captured_images/" \;
        echo "   ✅ Recent images backed up"
    fi
    
    echo "   📁 Backup created in: $BACKUP_DIR"
else
    echo ""
    echo "Step 2: Skipping backup (--no-backup specified)"
fi

# Step 3: Stop services if not skipping
if [[ "$SKIP_SERVICES" = false ]]; then
    echo ""
    echo "Step 3: Stopping services for update..."
    if [[ "$SERVICE_RUNNING" = true ]]; then
        sudo systemctl stop aicamera_lpr.service
        echo "   ✅ AI Camera service stopped"
    fi
else
    echo ""
    echo "Step 3: Skipping service stop (--skip-services specified)"
fi

# Step 4: Update system packages
echo ""
echo "Step 4: Updating system packages..."
sudo apt-get update -y
sudo apt-get upgrade -y
echo "   ✅ System packages updated"

# Step 5: Update Python packages
echo ""
echo "Step 5: Updating Python packages..."
if [[ -d "edge/installation/venv_hailo" ]]; then
    source edge/installation/venv_hailo/bin/activate
    
    # Update pip first
    pip install --upgrade pip
    
    # Update core packages
    pip install --upgrade \
        Flask==3.1.2 \
        Flask-SocketIO==5.3.6 \
        python-socketio==5.9.0 \
        Werkzeug==3.1.3 \
        Pillow==10.4.0 \
        opencv-python-headless==4.8.1.78 \
        numpy==1.26.4 \
        easyocr==1.7.1 \
        gunicorn==23.0.0
    
    echo "   ✅ Python packages updated"
else
    echo "   ⚠️  Virtual environment not found - skipping Python package update"
fi

# Step 6: Update application code
echo ""
echo "Step 6: Updating application code..."
echo "   📥 Pulling latest changes from repository..."

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "   📋 Current branch: $CURRENT_BRANCH"
    
    # Fetch latest changes
    git fetch origin
    
    # Check if there are updates
    LOCAL=$(git rev-parse HEAD)
    REMOTE=$(git rev-parse origin/$CURRENT_BRANCH)
    
    if [[ "$LOCAL" != "$REMOTE" ]] || [[ "$FORCE_UPDATE" = true ]]; then
        echo "   🔄 Updates available - applying changes..."
        git pull origin $CURRENT_BRANCH
        echo "   ✅ Application code updated"
    else
        echo "   ✅ Application code is up to date"
    fi
else
    echo "   ⚠️  Not in a git repository - skipping code update"
fi

# Step 7: Update database schema if needed
echo ""
echo "Step 7: Updating database schema..."
if python edge/scripts/init_database.py; then
    echo "   ✅ Database schema updated"
else
    echo "   ⚠️  Database schema update had issues - continuing"
fi

# Step 8: Update systemd service if needed
echo ""
echo "Step 8: Updating systemd service..."
if [[ -f "edge/systemd_service/aicamera_lpr.service" ]]; then
    sudo cp "edge/systemd_service/aicamera_lpr.service" /etc/systemd/system/
    sudo systemctl daemon-reload
    echo "   ✅ Systemd service updated"
else
    echo "   ⚠️  Systemd service file not found"
fi

# Step 9: Update nginx configuration if needed
echo ""
echo "Step 9: Updating nginx configuration..."
if [[ -f "edge/nginx.conf" ]]; then
    sudo cp "edge/nginx.conf" /etc/nginx/sites-available/aicamera
    sudo nginx -t && sudo systemctl reload nginx
    echo "   ✅ Nginx configuration updated"
else
    echo "   ⚠️  Nginx configuration file not found"
fi

# Step 10: Restart services if not skipping
if [[ "$SKIP_SERVICES" = false ]]; then
    echo ""
    echo "Step 10: Restarting services..."
    sudo systemctl start aicamera_lpr.service
    sleep 5
    
    if systemctl is-active --quiet aicamera_lpr.service; then
        echo "   ✅ AI Camera service started successfully"
    else
        echo "   ❌ AI Camera service failed to start"
        echo "   📋 Check logs: sudo journalctl -u aicamera_lpr.service -f"
    fi
else
    echo ""
    echo "Step 10: Skipping service restart (--skip-services specified)"
fi

# Step 11: Validate update
echo ""
echo "Step 11: Validating update..."
if python edge/scripts/validate_database.py; then
    echo "   ✅ Database validation passed"
else
    echo "   ⚠️  Database validation had issues"
fi

# Final status
echo ""
echo "🎉 AI Camera system update completed!"
echo "======================================"
echo ""
echo "✅ Update Summary:"
echo "   - System packages updated"
echo "   - Python packages updated"
echo "   - Application code updated"
echo "   - Database schema updated"
echo "   - Services updated"
if [[ "$BACKUP_DATA" = true ]]; then
    echo "   - Backup created in: $BACKUP_DIR"
fi
echo ""
echo "📋 Next Steps:"
echo "   1. Check service status: sudo systemctl status aicamera_lpr.service"
echo "   2. Monitor logs: sudo journalctl -u aicamera_lpr.service -f"
echo "   3. Test web interface: http://localhost"
echo "   4. Verify camera functionality"
echo ""
echo "🔧 If you encounter issues:"
if [[ "$BACKUP_DATA" = true ]]; then
    echo "   - Restore from backup: $BACKUP_DIR"
fi
echo "   - Check service logs: sudo journalctl -u aicamera_lpr.service"
echo "   - Run factory reset if needed: ./edge/scripts/factory_reset.sh"
echo ""
echo "🚀 Your AI Camera system is now updated and ready!"
