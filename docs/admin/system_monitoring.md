# AI Camera System Monitoring Guide

## Overview
This guide provides various methods to monitor CPU, RAM, and system resources in real-time for the AI Camera system.

## Quick Monitoring Commands

### 1. Basic System Commands

#### CPU and Memory Overview
```bash
# Quick system overview
top -bn1 | head -20

# CPU usage percentage
top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1

# Memory usage
free -h

# Load average
uptime
```

#### Process Monitoring
```bash
# Top CPU processes
ps aux --sort=-%cpu | head -10

# Top memory processes
ps aux --sort=-%mem | head -10

# AI Camera specific processes
ps aux | grep -E "(gunicorn|python.*aicamera)" | grep -v grep
```

### 2. Interactive Monitoring Tools

#### htop (Recommended)
```bash
htop
```
- **Features**: Interactive, color-coded, process tree view
- **Controls**: 
  - `F1`: Help
  - `F2`: Setup
  - `F3`: Search
  - `F4`: Filter
  - `F5`: Tree view
  - `F6`: Sort by
  - `q`: Quit

#### top
```bash
top -d 1  # Update every 1 second
```
- **Features**: Classic system monitor
- **Controls**: `q` to quit

#### iotop (Disk I/O)
```bash
sudo iotop
```
- **Features**: Monitor disk I/O usage
- **Note**: Requires sudo privileges

### 3. Custom Monitoring Scripts

#### Quick Monitor (One-time check)
```bash
./scripts/quick_monitor.sh
```
**Output includes:**
- System overview (CPU, Memory, Load, Disk)
- AI Camera processes
- Top CPU and Memory processes
- Service status

#### Real-time Monitor (Continuous)
```bash
# Default 2-second interval
./scripts/monitor_system.sh

# Custom interval (5 seconds)
./scripts/monitor_system.sh 5
```
**Features:**
- Color-coded output
- AI Camera specific monitoring
- System temperature
- Network connections
- Service status
- Auto-refresh

### 4. Web-based Monitoring

#### AI Camera Dashboard
- **URL**: `http://localhost/`
- **Features**: Real-time status updates via WebSocket
- **Refresh**: Every 30-60 seconds

#### Health Dashboard
- **URL**: `http://localhost/health/`
- **Features**: Detailed system health information
- **API**: `http://localhost/health/` (JSON format)

## Monitoring Specific Components

### AI Camera Service
```bash
# Service status
systemctl status aicamera_lpr.service

# Service logs
journalctl -u aicamera_lpr.service -f

# Recent errors
journalctl -u aicamera_lpr.service --since "10 minutes ago" | grep -i error
```

### Gunicorn Workers
```bash
# Worker processes
ps aux | grep gunicorn

# Worker memory usage
ps aux | grep gunicorn | awk '{sum+=$6} END {print "Total Memory (KB):", sum}'
```

### Camera Components
```bash
# Camera status API
curl -s http://localhost/camera/status | jq '.'

# Detection status API
curl -s http://localhost/detection/status | jq '.'
```

## Performance Thresholds

### Normal Operating Ranges
- **CPU Usage**: < 70% (excluding development tools)
- **Memory Usage**: < 80%
- **Load Average**: < 4.0 (for 4-core system)
- **Disk Usage**: < 85%
- **Temperature**: < 70°C

### AI Camera Specific
- **Gunicorn Worker**: < 30% CPU, < 2GB RAM
- **Detection Processing**: < 50% CPU during peak
- **Video Streaming**: < 20% CPU

## Troubleshooting High Resource Usage

### High CPU Usage
1. **Check top processes**: `ps aux --sort=-%cpu | head -5`
2. **Identify development tools**: Cursor, Chromium, etc.
3. **Check AI Camera processes**: Look for gunicorn workers
4. **Monitor detection pipeline**: Check for processing loops

### High Memory Usage
1. **Check memory processes**: `ps aux --sort=-%mem | head -5`
2. **Monitor gunicorn workers**: Check for memory leaks
3. **Check swap usage**: `free -h`
4. **Restart service if needed**: `sudo systemctl restart aicamera_lpr.service`

### System Load Issues
1. **Check load average**: `uptime`
2. **Identify bottleneck**: CPU, Memory, or I/O
3. **Monitor disk I/O**: `sudo iotop`
4. **Check for runaway processes**

## Automated Monitoring

### Systemd Service Monitoring
```bash
# Enable service monitoring
sudo systemctl enable aicamera_lpr.service

# Check service health
systemctl is-active aicamera_lpr.service
systemctl is-enabled aicamera_lpr.service
```

### Log Monitoring
```bash
# Follow logs in real-time
journalctl -u aicamera_lpr.service -f

# Monitor for errors
journalctl -u aicamera_lpr.service | grep -i error | tail -10
```

## Best Practices

### Regular Monitoring
1. **Daily**: Run `./scripts/quick_monitor.sh`
2. **During development**: Use `htop` or `./scripts/monitor_system.sh`
3. **After changes**: Monitor for 10-15 minutes
4. **Weekly**: Check service logs for errors

### Performance Optimization
1. **Monitor during peak usage**
2. **Identify resource bottlenecks**
3. **Adjust detection intervals if needed**
4. **Optimize image processing parameters**

### Alert Thresholds
- **CPU > 80%**: Investigate immediately
- **Memory > 85%**: Check for memory leaks
- **Load > 6.0**: System overload
- **Temperature > 75°C**: Thermal throttling risk

## Script Usage Examples

### Quick System Check
```bash
# One-time system overview
./scripts/quick_monitor.sh
```

### Continuous Monitoring
```bash
# Monitor every 2 seconds (default)
./scripts/monitor_system.sh

# Monitor every 5 seconds
./scripts/monitor_system.sh 5

# Monitor every 10 seconds
./scripts/monitor_system.sh 10
```

### Background Monitoring
```bash
# Run in background
nohup ./scripts/monitor_system.sh > monitor.log 2>&1 &

# Check background process
ps aux | grep monitor_system

# Stop background monitoring
pkill -f monitor_system.sh
```

## Integration with Web Interface

The monitoring data is also available through the web interface:

- **Main Dashboard**: `http://localhost/` - Real-time status
- **Health Dashboard**: `http://localhost/health/` - Detailed health info
- **API Endpoints**: JSON format for programmatic access

## Emergency Procedures

### Service Restart
```bash
sudo systemctl restart aicamera_lpr.service
```

### Force Kill High CPU Process
```bash
# Find process
ps aux --sort=-%cpu | head -1

# Kill if necessary (replace PID)
sudo kill -9 <PID>
```

### System Reboot (Last Resort)
```bash
sudo reboot
```

## Notes

- **Development Tools**: Cursor Editor and Chromium Browser may show high CPU usage during development
- **AI Camera Service**: Should maintain stable resource usage
- **Detection Pipeline**: May spike during processing but should return to normal
- **Memory Usage**: Gunicorn workers may use significant memory for image processing
