#!/bin/bash

# Script to create the kiosk-browser.service file
# This script generates a systemd service file with proper display detection

SERVICE_FILE="/etc/systemd/system/kiosk-browser.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Creating kiosk-browser.service file..."

# Create the service file content
cat > "$SERVICE_FILE" << 'EOF'
[Unit]
Description=AI Camera Browser (Smart Display Detection)
After=network.target aicamera_lpr.service nginx.service lightdm.service
Wants=network.target
Requires=network.target aicamera_lpr.service nginx.service
# Wait for display manager to be ready
After=graphical-session.target
Wants=graphical-session.target

[Service]
Type=simple
User=camuser
Group=camuser
WorkingDirectory=/home/camuser/aicamera

# Set display environment for visible browser
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/camuser/.Xauthority
Environment=XDG_RUNTIME_DIR=/run/user/1000

# Wait for the web service to be ready before starting browser
ExecStartPre=/bin/bash -c 'echo "Waiting for nginx to be ready..."'
ExecStartPre=/bin/bash -c 'timeout 30 bash -c "until systemctl is-active --quiet nginx; do sleep 2; done"'
ExecStartPre=/bin/bash -c 'echo "Waiting for aicamera_lpr service to be ready..."'
ExecStartPre=/bin/bash -c 'timeout 60 bash -c "until systemctl is-active --quiet aicamera_lpr.service; do sleep 3; done"'
ExecStartPre=/bin/bash -c 'echo "Waiting for web service to respond..."'
ExecStartPre=/bin/bash -c 'timeout 120 bash -c "until curl -s -f http://localhost/ >/dev/null 2>&1; do sleep 5; done"'
ExecStartPre=/bin/bash -c 'echo "Web service is ready!"'
ExecStartPre=/bin/bash -c 'echo "Waiting for display to be ready..."'
ExecStartPre=/bin/bash -c 'timeout 60 bash -c "until xset q >/dev/null 2>&1; do sleep 2; done"'
ExecStartPre=/bin/bash -c 'echo "Display is ready!"'
ExecStart=/home/camuser/aicamera/edge/systemd_service/kiosk_browser_startup.sh

# Restart policy - restart if browser exits
Restart=always
RestartSec=30

# Kill the browser process on service stop
KillMode=mixed
KillSignal=SIGTERM
TimeoutStopSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ai-camera-browser-smart

[Install]
WantedBy=multi-user.target
EOF

echo "Service file created at: $SERVICE_FILE"
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Service file content:"
echo "====================="
cat "$SERVICE_FILE"
echo "====================="

echo ""
echo "To enable and start the service, run:"
echo "sudo systemctl enable kiosk-browser.service"
echo "sudo systemctl start kiosk-browser.service"
echo ""
echo "To check status:"
echo "sudo systemctl status kiosk-browser.service"
