#!/bin/bash

# Kiosk Browser Service Management Script
# Usage: ./scripts/kiosk_browser.sh [start|stop|restart|status|enable|disable]

SERVICE_NAME="kiosk-browser.service"

show_usage() {
    echo "Usage: $0 [start|stop|restart|status|enable|disable|logs]"
    echo ""
    echo "Commands:"
    echo "  start   - Start the kiosk browser service"
    echo "  stop    - Stop the kiosk browser service"
    echo "  restart - Restart the kiosk browser service"
    echo "  status  - Show service status"
    echo "  enable  - Enable service to start on boot"
    echo "  disable - Disable service from starting on boot"
    echo "  logs    - Show service logs (follow mode)"
    echo ""
    echo "Examples:"
    echo "  $0 start    # Start kiosk browser"
    echo "  $0 status   # Check if running"
    echo "  $0 logs     # View logs"
}

check_service_exists() {
    if ! sudo systemctl list-unit-files | grep -q "$SERVICE_NAME"; then
        echo "❌ Service $SERVICE_NAME not found. Please run install.sh first."
        exit 1
    fi
}

case "$1" in
    start)
        check_service_exists
        echo "🖥️  Starting kiosk browser service..."
        sudo systemctl start "$SERVICE_NAME"
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            echo "✅ Kiosk browser started successfully"
        else
            echo "❌ Failed to start kiosk browser"
            sudo systemctl status "$SERVICE_NAME"
        fi
        ;;
    stop)
        check_service_exists
        echo "🖥️  Stopping kiosk browser service..."
        sudo systemctl stop "$SERVICE_NAME"
        echo "✅ Kiosk browser stopped"
        ;;
    restart)
        check_service_exists
        echo "🖥️  Restarting kiosk browser service..."
        sudo systemctl restart "$SERVICE_NAME"
        if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
            echo "✅ Kiosk browser restarted successfully"
        else
            echo "❌ Failed to restart kiosk browser"
            sudo systemctl status "$SERVICE_NAME"
        fi
        ;;
    status)
        check_service_exists
        echo "📋 Kiosk browser service status:"
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
        ;;
    enable)
        check_service_exists
        echo "🖥️  Enabling kiosk browser service to start on boot..."
        sudo systemctl enable "$SERVICE_NAME"
        echo "✅ Kiosk browser service enabled"
        ;;
    disable)
        check_service_exists
        echo "🖥️  Disabling kiosk browser service from starting on boot..."
        sudo systemctl disable "$SERVICE_NAME"
        echo "✅ Kiosk browser service disabled"
        ;;
    logs)
        check_service_exists
        echo "📋 Showing kiosk browser service logs (Ctrl+C to exit):"
        sudo journalctl -u "$SERVICE_NAME" -f
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
