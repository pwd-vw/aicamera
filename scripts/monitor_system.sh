#!/bin/bash

# AI Camera System Real-time Monitor
# Usage: ./monitor_system.sh [interval_seconds]

INTERVAL=${1:-2}  # Default 2 seconds interval
CLEAR_SCREEN=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to clear screen
clear_screen() {
    if [ "$CLEAR_SCREEN" = true ]; then
        clear
    fi
}

# Function to get CPU usage percentage
get_cpu_usage() {
    top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1
}

# Function to get memory usage
get_memory_usage() {
    free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}'
}

# Function to get AI Camera specific processes
get_aicamera_processes() {
    ps aux | grep -E "(gunicorn|python.*aicamera)" | grep -v grep
}

# Function to get system load
get_system_load() {
    uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//'
}

# Function to get disk usage
get_disk_usage() {
    df -h / | tail -1 | awk '{print $5}' | sed 's/%//'
}

# Function to get temperature (if available)
get_temperature() {
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        temp=$(cat /sys/class/thermal/thermal_zone0/temp)
        echo "scale=1; $temp/1000" | bc
    else
        echo "N/A"
    fi
}

# Function to check AI Camera service status
check_aicamera_service() {
    if systemctl is-active --quiet aicamera_lpr.service; then
        echo -e "${GREEN}● ACTIVE${NC}"
    else
        echo -e "${RED}● INACTIVE${NC}"
    fi
}

# Function to get network connections
get_network_connections() {
    netstat -tuln | grep -E ":(80|443|8080|5000)" | wc -l
}

# Main monitoring loop
while true; do
    clear_screen
    
    # Get current timestamp
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get system metrics
    CPU_USAGE=$(get_cpu_usage)
    MEMORY_USAGE=$(get_memory_usage)
    LOAD_AVERAGE=$(get_system_load)
    DISK_USAGE=$(get_disk_usage)
    TEMPERATURE=$(get_temperature)
    NETWORK_CONNS=$(get_network_connections)
    
    # Display header
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    AI Camera System Real-time Monitor                      ║${NC}"
    echo -e "${CYAN}║                              $TIMESTAMP                                    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # System Overview
    echo -e "${YELLOW}📊 SYSTEM OVERVIEW${NC}"
    echo -e "${BLUE}CPU Usage:${NC}     ${CPU_USAGE}%"
    echo -e "${BLUE}Memory Usage:${NC}  ${MEMORY_USAGE}%"
    echo -e "${BLUE}Load Average:${NC}  ${LOAD_AVERAGE}"
    echo -e "${BLUE}Disk Usage:${NC}    ${DISK_USAGE}%"
    echo -e "${BLUE}Temperature:${NC}   ${TEMPERATURE}°C"
    echo -e "${BLUE}Network Conns:${NC} ${NETWORK_CONNS}"
    echo -e "${BLUE}AI Camera Service:${NC} $(check_aicamera_service)"
    echo
    
    # Memory Details
    echo -e "${YELLOW}💾 MEMORY DETAILS${NC}"
    free -h | grep -E "(Mem|Swap)" | while read line; do
        echo -e "${BLUE}$line${NC}"
    done
    echo
    
    # AI Camera Processes
    echo -e "${YELLOW}🤖 AI CAMERA PROCESSES${NC}"
    AICAMERA_PROCS=$(get_aicamera_processes)
    if [ -n "$AICAMERA_PROCS" ]; then
        echo "$AICAMERA_PROCS" | while read line; do
            PID=$(echo "$line" | awk '{print $2}')
            CPU=$(echo "$line" | awk '{print $3}')
            MEM=$(echo "$line" | awk '{print $4}')
            CMD=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}')
            echo -e "${GREEN}PID: $PID${NC} | ${CYAN}CPU: $CPU%${NC} | ${PURPLE}MEM: $MEM%${NC} | ${BLUE}$CMD${NC}"
        done
    else
        echo -e "${RED}No AI Camera processes found${NC}"
    fi
    echo
    
    # Top CPU Processes
    echo -e "${YELLOW}🔥 TOP CPU PROCESSES${NC}"
    ps aux --sort=-%cpu | head -6 | tail -5 | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        CPU=$(echo "$line" | awk '{print $3}')
        MEM=$(echo "$line" | awk '{print $4}')
        CMD=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}' | cut -c1-50)
        echo -e "${GREEN}PID: $PID${NC} | ${CYAN}CPU: $CPU%${NC} | ${PURPLE}MEM: $MEM%${NC} | ${BLUE}$CMD${NC}"
    done
    echo
    
    # Top Memory Processes
    echo -e "${YELLOW}💿 TOP MEMORY PROCESSES${NC}"
    ps aux --sort=-%mem | head -6 | tail -5 | while read line; do
        PID=$(echo "$line" | awk '{print $2}')
        CPU=$(echo "$line" | awk '{print $3}')
        MEM=$(echo "$line" | awk '{print $4}')
        CMD=$(echo "$line" | awk '{for(i=11;i<=NF;i++) printf "%s ", $i; print ""}' | cut -c1-50)
        echo -e "${GREEN}PID: $PID${NC} | ${CYAN}CPU: $CPU%${NC} | ${PURPLE}MEM: $MEM%${NC} | ${BLUE}$CMD${NC}"
    done
    echo
    
    # Footer
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║ Press Ctrl+C to exit | Refresh every ${INTERVAL}s | $(hostname) | $(whoami)    ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    
    sleep $INTERVAL
done
