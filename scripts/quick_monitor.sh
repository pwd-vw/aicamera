#!/bin/bash

# Quick System Monitor for AI Camera
# Simple one-time check of system resources

echo "=== AI Camera System Quick Monitor ==="
echo "Timestamp: $(date)"
echo

echo "📊 System Overview:"
echo "Load Average: $(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')"
echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "Memory Usage: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
echo "Disk Usage: $(df -h / | tail -1 | awk '{print $5}')"
echo

echo "💾 Memory Details:"
free -h
echo

echo "🤖 AI Camera Processes:"
ps aux | grep -E "(gunicorn|python.*aicamera)" | grep -v grep || echo "No AI Camera processes found"
echo

echo "🔥 Top 5 CPU Processes:"
ps aux --sort=-%cpu | head -6 | tail -5
echo

echo "💿 Top 5 Memory Processes:"
ps aux --sort=-%mem | head -6 | tail -5
echo

echo "🔧 AI Camera Service Status:"
systemctl is-active aicamera_lpr.service && echo "✅ ACTIVE" || echo "❌ INACTIVE"
