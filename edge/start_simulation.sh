#!/bin/bash

# AI Camera Simulation Startup Script

echo "🚀 Starting AI Camera Simulation..."

# Check if we're in the right directory
if [[ ! -f "edge/scripts/run_simulation.py" ]]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Activate virtual environment
if [[ -d "edge/venv_simulation" ]]; then
    echo "🐍 Activating simulation virtual environment..."
    source edge/venv_simulation/bin/activate
else
    echo "❌ Error: Simulation virtual environment not found"
    echo "   Please run: ./edge/installation/install_simulation.sh"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p edge/logs

# Start the simulation service
echo "🎯 Starting simulation service..."
python edge/scripts/run_simulation.py
