#!/usr/bin/env python3
"""
AI Camera Simulation Service
Runs the edge application in simulation mode without hardware dependencies
"""

import os
import sys
import time
import threading
import random
from datetime import datetime, timedelta
import sqlite3
import json

# Add the edge directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def log_message(message, level="INFO"):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {message}")

def simulate_health_data():
    """Simulate health monitoring data"""
    db_path = "edge/db/simulation_data.db"
    
    while True:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Generate simulated health data
            cpu_usage = random.uniform(20.0, 80.0)
            memory_usage = random.uniform(30.0, 90.0)
            disk_usage = random.uniform(40.0, 85.0)
            temperature = random.uniform(35.0, 65.0)
            
            cursor.execute('''
                INSERT INTO health_monitoring 
                (cpu_usage, memory_usage, disk_usage, temperature, 
                 camera_status, ai_status, system_status, uptime_seconds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                cpu_usage, memory_usage, disk_usage, temperature,
                'SIMULATED', 'SIMULATED', 'HEALTHY',
                random.randint(3600, 86400)
            ))
            
            conn.commit()
            conn.close()
            
            log_message(f"Health data recorded - CPU: {cpu_usage:.1f}%, Memory: {memory_usage:.1f}%")
            
        except Exception as e:
            log_message(f"Error recording health data: {e}", "ERROR")
        
        time.sleep(10)  # Record health data every 10 seconds

def simulate_detection_data():
    """Simulate AI detection results"""
    db_path = "edge/db/simulation_data.db"
    
    sample_plates = ['ABC123', 'XYZ789', 'DEF456', 'GHI789', 'JKL012', 'MNO345', 'PQR678']
    vehicle_types = ['car', 'truck', 'motorcycle', 'bus']
    colors = ['red', 'blue', 'green', 'white', 'black', 'silver']
    makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes', 'Audi', 'Volkswagen']
    
    while True:
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Generate simulated detection
            license_plate = random.choice(sample_plates)
            confidence = random.uniform(0.7, 0.99)
            vehicle_type = random.choice(vehicle_types)
            color = random.choice(colors)
            make = random.choice(makes)
            
            cursor.execute('''
                INSERT INTO detection_results 
                (detection_type, confidence, bounding_box, license_plate,
                 vehicle_type, color, make, model, image_path, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                'license_plate',
                confidence,
                f"{random.randint(100, 500)},{random.randint(100, 300)},{random.randint(600, 800)},{random.randint(400, 600)}",
                license_plate,
                vehicle_type,
                color,
                make,
                f"Model{random.randint(1, 10)}",
                f"simulated_detection_{int(time.time())}.jpg",
                random.randint(50, 200)
            ))
            
            conn.commit()
            conn.close()
            
            log_message(f"Detection simulated - Plate: {license_plate}, Confidence: {confidence:.2f}")
            
        except Exception as e:
            log_message(f"Error simulating detection: {e}", "ERROR")
        
        time.sleep(5)  # Simulate detection every 5 seconds

def main():
    """Main simulation function"""
    log_message("🚀 Starting AI Camera Simulation Service")
    log_message("📋 Mode: Simulation (No Hardware Dependencies)")
    log_message("🎯 Features: Health Monitoring, Detection Simulation, Database Storage")
    
    # Start health monitoring simulation in background
    health_thread = threading.Thread(target=simulate_health_data, daemon=True)
    health_thread.start()
    log_message("📊 Health monitoring simulation started")
    
    # Start detection simulation in background
    detection_thread = threading.Thread(target=simulate_detection_data, daemon=True)
    detection_thread.start()
    log_message("🔍 Detection simulation started")
    
    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log_message("🛑 Simulation service stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
