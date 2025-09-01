# AI Camera Simulation Environment

This directory contains the simulation environment for the AI Camera project, designed for development and testing without hardware dependencies.

## Features

- **Health Monitoring Simulation**: Simulates system health data (CPU, memory, disk, temperature)
- **Detection Simulation**: Generates fake license plate and vehicle detection results
- **Database Storage**: SQLite database for storing simulation data
- **WebSocket Communication**: Ready for server communication
- **No Hardware Dependencies**: Works on any machine without camera or AI hardware

## Quick Start

1. **Installation** (from project root):
   ```bash
   ./edge/installation/install_simulation.sh
   ```

2. **Start Simulation**:
   ```bash
   ./edge/start_simulation.sh
   ```

3. **Run Tests**:
   ```bash
   python edge/test_simulation.py
   ```

## Database Schema

### Health Monitoring Table
- `id`: Primary key
- `timestamp`: Record timestamp
- `cpu_usage`: Simulated CPU usage percentage
- `memory_usage`: Simulated memory usage percentage
- `disk_usage`: Simulated disk usage percentage
- `temperature`: Simulated system temperature
- `camera_status`: Always "SIMULATED"
- `ai_status`: Always "SIMULATED"
- `system_status`: System health status
- `uptime_seconds`: Simulated uptime

### Detection Results Table
- `id`: Primary key
- `timestamp`: Detection timestamp
- `detection_type`: Type of detection (e.g., "license_plate")
- `confidence`: Detection confidence (0.0-1.0)
- `bounding_box`: Simulated bounding box coordinates
- `license_plate`: Simulated license plate number
- `vehicle_type`: Vehicle type (car, truck, motorcycle, bus)
- `color`: Vehicle color
- `make`: Vehicle make
- `model`: Vehicle model
- `image_path`: Path to simulated image
- `processing_time_ms`: Simulated processing time

### System Events Table
- `id`: Primary key
- `timestamp`: Event timestamp
- `event_type`: Type of system event
- `event_level`: Event severity (INFO, WARNING, ERROR)
- `message`: Event message
- `details`: Additional event details

## Configuration

Environment variables are stored in `edge/config/simulation/.env`:

- `ENVIRONMENT=simulation`: Indicates simulation mode
- `DATABASE_URL`: SQLite database path
- `SIMULATION_MODE=true`: Enables simulation features
- `SIMULATION_DETECTION_INTERVAL=5`: Detection simulation interval (seconds)
- `SIMULATION_HEALTH_INTERVAL=10`: Health monitoring interval (seconds)

## Development

### Adding New Simulation Features

1. Update the database schema in `edge/scripts/init_simulation_db.py`
2. Add simulation logic to `edge/scripts/run_simulation.py`
3. Update tests in `edge/test_simulation.py`

### Integration with Server

The simulation environment is designed to work with the Node.js server:

1. Health data is stored in SQLite and can be queried via API
2. Detection results are stored and can be sent to the server
3. WebSocket communication is available for real-time updates

## Troubleshooting

### Common Issues

1. **Virtual Environment Not Found**:
   ```bash
   ./edge/installation/install_simulation.sh
   ```

2. **Database Connection Error**:
   ```bash
   python edge/scripts/init_simulation_db.py
   ```

3. **Import Errors**:
   ```bash
   source edge/venv_simulation/bin/activate
   pip install -r edge/installation/requirements_simulation.txt
   ```

### Logs

Simulation logs are stored in `edge/logs/simulation.log`

## Files Structure

```
edge/
├── installation/
│   ├── install_simulation.sh          # Installation script
│   └── requirements_simulation.txt    # Simulation dependencies
├── scripts/
│   ├── init_simulation_db.py          # Database initialization
│   ├── run_simulation.py              # Simulation service
│   └── test_simulation.py             # Test script
├── config/
│   └── simulation/
│       └── .env                       # Simulation configuration
├── db/
│   └── simulation_data.db             # SQLite database
├── logs/                              # Log files
├── venv_simulation/                   # Python virtual environment
├── start_simulation.sh                # Startup script
└── SIMULATION_README.md               # This file
```
