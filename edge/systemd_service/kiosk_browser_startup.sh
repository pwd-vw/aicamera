#!/bin/bash

echo "Checking display availability..."

# Check if display is available
if xset q >/dev/null 2>&1; then
    echo "Display detected - launching browser in kiosk mode..."
    chromium-browser --kiosk \
        --disable-gpu \
        --no-sandbox \
        --disable-dev-shm-usage \
        --disable-web-security \
        --disable-features=VizDisplayCompositor \
        --no-first-run \
        --no-default-browser-check \
        --disable-background-timer-throttling \
        --disable-backgrounding-occluded-windows \
        --disable-renderer-backgrounding \
        --disable-features=TranslateUI \
        --disable-ipc-flooding-protection \
        --autoplay-policy=no-user-gesture-required \
        --disable-session-crashed-bubble \
        --disable-infobars \
        --disable-notifications \
        --new-window \
        --allow-running-insecure-content \
        --user-data-dir=/tmp/chromium-kiosk \
        --remote-debugging-port=9222 \
        http://localhost/
else
    echo "No display detected - running in headless mode with sleep loop"
    while true; do
        sleep 3600
    done
fi
