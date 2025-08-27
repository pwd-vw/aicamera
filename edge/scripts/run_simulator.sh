#!/bin/bash

# Edge Device Simulator Runner Script
# This script sets up and runs the edge device simulator

echo "🚀 Starting AI Camera Edge Device Simulator..."

# Check if virtual environment exists
if [ ! -d "venv_simulator" ]; then
    echo "📦 Creating virtual environment for simulator..."
    python3 -m venv venv_simulator
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv_simulator/bin/activate

# Install requirements
echo "📥 Installing simulator requirements..."
pip install -r requirements_simulator.txt

# Set default values
SERVER_URL="${SERVER_URL:-http://localhost:3000}"
DEVICE_ID="${DEVICE_ID:-sim-$(date +%s)}"
DETECTION_INTERVAL="${DETECTION_INTERVAL:-15}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-45}"
HEARTBEAT_INTERVAL="${HEARTBEAT_INTERVAL:-60}"

echo "⚙️  Configuration:"
echo "   Server URL: $SERVER_URL"
echo "   Device ID: $DEVICE_ID"
echo "   Detection Interval: ${DETECTION_INTERVAL}s"
echo "   Health Check Interval: ${HEALTH_INTERVAL}s"
echo "   Heartbeat Interval: ${HEARTBEAT_INTERVAL}s"

echo ""
echo "📋 Instructions:"
echo "1. Make sure your server is running at $SERVER_URL"
echo "2. The simulator will register as device '$DEVICE_ID'"
echo "3. Go to your admin dashboard and approve the device"
echo "4. The simulator will start sending mock detection data"
echo ""
echo "🔄 Starting simulator..."

# Run the simulator
python edge_device_simulator.py \
    --server-url "$SERVER_URL" \
    --device-id "$DEVICE_ID" \
    --detection-interval "$DETECTION_INTERVAL" \
    --health-interval "$HEALTH_INTERVAL" \
    --heartbeat-interval "$HEARTBEAT_INTERVAL"