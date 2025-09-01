#!/bin/bash
# AI Camera Browser Startup Script
# รองรับทั้งการต่อจอ monitor และ headless mode

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CONFIG_FILE="$PROJECT_DIR/config/kiosk_browser.conf"
HANDLER_SCRIPT="$SCRIPT_DIR/kiosk_browser_handler.py"
LOG_FILE="/tmp/startup_browser.log"

# Default values
WEB_URL="http://localhost/"
BROWSER_PATH="/usr/lib/chromium/chromium"
USER_DATA_DIR="/tmp/chromium-ai-camera"
REMOTE_DEBUG_PORT="9222"
WAIT_TIMEOUT="120"
CHECK_INTERVAL="30"
MAX_RETRIES="3"
HEADLESS_FALLBACK="true"

# Functions
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO:${NC} $1" | tee -a "$LOG_FILE"
}

# Load configuration if exists
load_config() {
    if [[ -f "$CONFIG_FILE" ]]; then
        log "Loading configuration from $CONFIG_FILE"
        
        # Parse config file
        while IFS='=' read -r key value; do
            # Skip comments and empty lines
            [[ $key =~ ^#.*$ ]] && continue
            [[ -z $key ]] && continue
            
            # Remove leading/trailing whitespace
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs)
            
            case $key in
                "web_url") WEB_URL="$value" ;;
                "browser_path") BROWSER_PATH="$value" ;;
                "user_data_dir") USER_DATA_DIR="$value" ;;
                "remote_debug_port") REMOTE_DEBUG_PORT="$value" ;;
                "wait_timeout") WAIT_TIMEOUT="$value" ;;
                "check_interval") CHECK_INTERVAL="$value" ;;
                "max_retries") MAX_RETRIES="$value" ;;
                "headless_fallback") HEADLESS_FALLBACK="$value" ;;
            esac
        done < "$CONFIG_FILE"
        
        log "Configuration loaded successfully"
    else
        warn "Configuration file not found, using default values"
    fi
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    # Check Chromium
    if ! [[ -f "$BROWSER_PATH" ]]; then
        error "Chromium browser not found at $BROWSER_PATH"
        exit 1
    fi
    
    # Check required Python packages
    python3 -c "import psutil" 2>/dev/null || {
        error "psutil package not installed. Install with: pip3 install psutil"
        exit 1
    }
    
    log "All dependencies are satisfied"
}

# Detect environment
detect_environment() {
    log "Detecting environment..."
    
    # Check DISPLAY
    if [[ -z "$DISPLAY" ]]; then
        log "No DISPLAY environment variable detected"
        ENVIRONMENT="headless"
        return
    fi
    
    # Check X server
    if ! xset q &>/dev/null; then
        log "X server not responding"
        ENVIRONMENT="headless"
        return
    fi
    
    # Check screen resolution
    if ! xrandr --current &>/dev/null; then
        log "Cannot get screen resolution"
        ENVIRONMENT="headless"
        return
    fi
    
    # Check if embedded system
    if [[ $(uname -m) == "aarch64" ]] || [[ $(uname -m) == "armv7l" ]]; then
        log "ARM architecture detected (likely embedded system)"
        ENVIRONMENT="headless"
        return
    fi
    
    # Check memory
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $MEMORY_GB -lt 2 ]]; then
        log "Low memory detected (${MEMORY_GB}GB), using headless mode"
        ENVIRONMENT="headless"
        return
    fi
    
    log "Full display environment detected"
    ENVIRONMENT="kiosk"
}

# Setup environment variables
setup_environment() {
    log "Setting up environment variables..."
    
    export WEB_URL="$WEB_URL"
    export BROWSER_PATH="$BROWSER_PATH"
    export USER_DATA_DIR="$USER_DATA_DIR"
    export REMOTE_DEBUG_PORT="$REMOTE_DEBUG_PORT"
    export WAIT_TIMEOUT="$WAIT_TIMEOUT"
    export CHECK_INTERVAL="$CHECK_INTERVAL"
    export MAX_RETRIES="$MAX_RETRIES"
    export HEADLESS_FALLBACK="$HEADLESS_FALLBACK"
    
    # Set DISPLAY for kiosk mode
    if [[ "$ENVIRONMENT" == "kiosk" ]]; then
        export DISPLAY="${DISPLAY:-:0}"
        export XAUTHORITY="${XAUTHORITY:-/home/$USER/.Xauthority}"
    fi
    
    log "Environment variables set for $ENVIRONMENT mode"
}

# Wait for services
wait_for_services() {
    log "Waiting for required services..."
    
    # Wait for nginx
    log "Waiting for nginx service..."
    timeout 30 bash -c "until systemctl is-active --quiet nginx; do sleep 2; done" || {
        error "Nginx service not ready after 30 seconds"
        return 1
    }
    
    # Wait for aicamera_lpr
    log "Waiting for aicamera_lpr service..."
    timeout 60 bash -c "until systemctl is-active --quiet aicamera_lpr.service; do sleep 3; done" || {
        error "AICamera LPR service not ready after 60 seconds"
        return 1
    }
    
    # Wait for web service
    log "Waiting for web service to respond..."
    timeout "$WAIT_TIMEOUT" bash -c "until curl -s -f $WEB_URL >/dev/null 2>&1; do sleep 5; done" || {
        error "Web service not responding after $WAIT_TIMEOUT seconds"
        return 1
    }
    
    log "All required services are ready"
    return 0
}

# Start browser
start_browser() {
    log "Starting browser in $ENVIRONMENT mode..."
    
    if [[ ! -f "$HANDLER_SCRIPT" ]]; then
        error "Handler script not found at $HANDLER_SCRIPT"
        return 1
    fi
    
    # Make script executable
    chmod +x "$HANDLER_SCRIPT"
    
    # Start handler
    python3 "$HANDLER_SCRIPT" &
    HANDLER_PID=$!
    
    log "Browser handler started with PID $HANDLER_PID"
    
    # Wait a bit to see if it starts successfully
    sleep 5
    
    if kill -0 "$HANDLER_PID" 2>/dev/null; then
        log "Browser handler is running successfully"
        echo "$HANDLER_PID" > /tmp/browser_handler.pid
        return 0
    else
        error "Browser handler failed to start"
        return 1
    fi
}

# Main function
main() {
    log "Starting AI Camera Browser Startup Script..."
    
    # Check if not running as root
    check_root
    
    # Load configuration
    load_config
    
    # Check dependencies
    check_dependencies
    
    # Detect environment
    detect_environment
    
    # Setup environment variables
    setup_environment
    
    # Wait for services
    if ! wait_for_services; then
        error "Failed to wait for services"
        exit 1
    fi
    
    # Start browser
    if ! start_browser; then
        error "Failed to start browser"
        exit 1
    fi
    
    log "Browser startup completed successfully"
    log "Environment: $ENVIRONMENT"
    log "Log file: $LOG_FILE"
    
    # Keep script running to monitor browser
    log "Monitoring browser process..."
    while kill -0 "$HANDLER_PID" 2>/dev/null; do
        sleep 10
    done
    
    warn "Browser handler process has exited"
    exit 1
}

# Signal handlers
cleanup() {
    log "Received signal, cleaning up..."
    
    if [[ -n "$HANDLER_PID" ]]; then
        log "Stopping browser handler (PID: $HANDLER_PID)..."
        kill "$HANDLER_PID" 2>/dev/null || true
        
        # Wait for process to stop
        timeout 10 bash -c "while kill -0 $HANDLER_PID 2>/dev/null; do sleep 1; done" || {
            warn "Force killing browser handler..."
            kill -9 "$HANDLER_PID" 2>/dev/null || true
        }
    fi
    
    # Remove PID file
    rm -f /tmp/browser_handler.pid
    
    log "Cleanup completed"
    exit 0
}

# Set signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
