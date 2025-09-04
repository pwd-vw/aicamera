#!/bin/bash

# AI Camera Edge Startup Script

echo "🚀 Starting AI Camera Edge Application..."

# Check if virtual environment exists
if [ ! -d "venv_hailo" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Check if configuration exists
if [ ! -f ".env.production" ]; then
    echo "❌ Configuration file not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating Python virtual environment..."
source venv_hailo/bin/activate

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import paho.mqtt.client, paramiko, PIL, requests, websocket" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing Python dependencies. Installing..."
    pip install -r requirements.txt
fi

# Start the application
echo "🚀 Starting edge application..."
python3 src/main.py

# Deactivate virtual environment on exit
deactivate
