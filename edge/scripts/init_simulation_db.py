#!/usr/bin/env python3
"""
Initialize simulation database with schema for health monitoring and detection results
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

def init_simulation_database():
    """Initialize the simulation database with required tables"""
    
    db_path = "edge/db/simulation_data.db"
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"🗑️ Removed existing database: {db_path}")
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create health monitoring table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_monitoring (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cpu_usage REAL,
            memory_usage REAL,
            disk_usage REAL,
            temperature REAL,
            camera_status TEXT,
            ai_status TEXT,
            system_status TEXT,
            uptime_seconds INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create detection results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detection_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            detection_type TEXT,
            confidence REAL,
            bounding_box TEXT,
            license_plate TEXT,
            vehicle_type TEXT,
            color TEXT,
            make TEXT,
            model TEXT,
            image_path TEXT,
            processing_time_ms INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create system events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT,
            event_level TEXT,
            message TEXT,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_health_timestamp ON health_monitoring(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_detection_timestamp ON detection_results(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON system_events(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_detection_type ON detection_results(detection_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_level ON system_events(event_level)')
    
    # Insert initial system event
    cursor.execute('''
        INSERT INTO system_events (event_type, event_level, message, details)
        VALUES (?, ?, ?, ?)
    ''', ('SYSTEM_STARTUP', 'INFO', 'Simulation database initialized', 
          f'Database created at {datetime.now().isoformat()}'))
    
    # Generate some sample data for testing
    generate_sample_data(cursor)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Simulation database initialized: {db_path}")
    print("📊 Tables created:")
    print("   - health_monitoring")
    print("   - detection_results") 
    print("   - system_events")
    print("📈 Sample data generated for testing")

def generate_sample_data(cursor):
    """Generate sample data for testing"""
    
    # Generate sample health data
    for i in range(10):
        timestamp = datetime.now() - timedelta(minutes=i*5)
        cursor.execute('''
            INSERT INTO health_monitoring 
            (timestamp, cpu_usage, memory_usage, disk_usage, temperature, 
             camera_status, ai_status, system_status, uptime_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            random.uniform(20.0, 80.0),
            random.uniform(30.0, 90.0),
            random.uniform(40.0, 85.0),
            random.uniform(35.0, 65.0),
            'SIMULATED',
            'SIMULATED',
            'HEALTHY',
            random.randint(3600, 86400)
        ))
    
    # Generate sample detection data
    sample_plates = ['ABC123', 'XYZ789', 'DEF456', 'GHI789', 'JKL012']
    vehicle_types = ['car', 'truck', 'motorcycle', 'bus']
    colors = ['red', 'blue', 'green', 'white', 'black', 'silver']
    makes = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes']
    
    for i in range(15):
        timestamp = datetime.now() - timedelta(minutes=i*3)
        cursor.execute('''
            INSERT INTO detection_results 
            (timestamp, detection_type, confidence, bounding_box, license_plate,
             vehicle_type, color, make, model, image_path, processing_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            'license_plate',
            random.uniform(0.7, 0.99),
            f"{random.randint(100, 500)},{random.randint(100, 300)},{random.randint(600, 800)},{random.randint(400, 600)}",
            random.choice(sample_plates),
            random.choice(vehicle_types),
            random.choice(colors),
            random.choice(makes),
            f"Model{random.randint(1, 10)}",
            f"simulated_image_{i}.jpg",
            random.randint(50, 200)
        ))
    
    # Generate sample system events
    events = [
        ('CAMERA_INIT', 'INFO', 'Simulated camera initialized', 'Camera simulation mode enabled'),
        ('AI_MODEL_LOAD', 'INFO', 'AI detection model loaded', 'Using simulated detection model'),
        ('WEBSOCKET_START', 'INFO', 'WebSocket server started', 'Listening on port 5001'),
        ('DATABASE_CONNECT', 'INFO', 'Database connection established', 'SQLite simulation database'),
        ('HEALTH_CHECK', 'INFO', 'Health monitoring started', 'Simulated health data collection')
    ]
    
    for event_type, level, message, details in events:
        cursor.execute('''
            INSERT INTO system_events (event_type, event_level, message, details)
            VALUES (?, ?, ?, ?)
        ''', (event_type, level, message, details))

if __name__ == "__main__":
    init_simulation_database()
