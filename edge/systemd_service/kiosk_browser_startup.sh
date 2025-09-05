#!/bin/bash

echo "Checking display availability..."

# Check if display is available
if xset q >/dev/null 2>&1; then
    echo "Display detected - launching browser in kiosk mode..."
    chromium-browser \
          --app=http://localhost/ \
          --no-first-run \
          --no-default-browser-check \
          --disable-infobars \
          --disable-notifications
else
    echo "No display detected - running in headless mode with sleep loop"
    while true; do
        sleep 3600
    done
fi
