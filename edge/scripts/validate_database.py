#!/usr/bin/env python3
"""
Database Validation Script for AI Camera v1.3

This script validates that the database is properly initialized and all
required components are working correctly.

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from edge.src.core.config import DATABASE_PATH
    from edge.src.components.database_manager import DatabaseManager
    from edge.src.core.utils.logging_config import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def validate_database_schema():
    """Validate that all required database tables exist."""
    print("🔍 Validating database schema...")
    
    try:
        import sqlite3
        db_path = Path(DATABASE_PATH)
        
        if not db_path.exists():
            print(f"❌ Database file not found: {db_path}")
            return False
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check required tables
        required_tables = [
            'detection_results',
            'system_events', 
            'configuration',
            'health_checks',
            'websocket_sender_logs'
        ]
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = []
        for table in required_tables:
            if table not in existing_tables:
                missing_tables.append(table)
        
        if missing_tables:
            print(f"❌ Missing tables: {', '.join(missing_tables)}")
            conn.close()
            return False
        
        print("✅ All required tables exist")
        
        # Check for required columns in detection_results table
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        required_columns = [
            'id', 'timestamp', 'vehicles_count', 'plates_count', 
            'ocr_results', 'annotated_image_path', 'image_path',
            'cropped_plates_paths', 'vehicle_detections', 'plate_detections',
            'processing_time_ms', 'created_at', 'sent_to_server', 'sent_at', 
            'server_response', 'hailo_ocr_results', 'easyocr_results', 
            'best_ocr_method', 'ocr_processing_time_ms', 'parallel_ocr_success',
            'hailo_ocr_confidence', 'easyocr_confidence', 'hailo_processing_time_ms',
            'easyocr_processing_time_ms', 'hailo_ocr_error', 'easyocr_error'
        ]
        
        missing_columns = []
        for column in required_columns:
            if column not in columns:
                missing_columns.append(column)
        
        if missing_columns:
            print(f"❌ Missing columns in detection_results table: {', '.join(missing_columns)}")
            conn.close()
            return False
        
        print("✅ All required columns exist in detection_results table")
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database schema validation failed: {e}")
        return False


def validate_database_manager():
    """Validate that DatabaseManager can be initialized and has required methods."""
    print("🔍 Validating DatabaseManager component...")
    
    try:
        # Test initialization
        db_manager = DatabaseManager()
        
        # Test initialize method
        if not db_manager.initialize():
            print("❌ DatabaseManager initialization failed")
            return False
        
        # Test execute_query method
        try:
            results = db_manager.execute_query("SELECT 1 as test")
            if not results or len(results) == 0:
                print("❌ execute_query method returned no results")
                return False
            print("✅ execute_query method working")
        except Exception as e:
            print(f"❌ execute_query method failed: {e}")
            return False
        
        # Test other methods
        try:
            stats = db_manager.get_detection_statistics()
            print("✅ get_detection_statistics method working")
        except Exception as e:
            print(f"❌ get_detection_statistics method failed: {e}")
            return False
        
        print("✅ DatabaseManager validation passed")
        return True
        
    except Exception as e:
        print(f"❌ DatabaseManager validation failed: {e}")
        return False


def validate_health_monitor_database():
    """Validate that health monitor can access database."""
    print("🔍 Validating health monitor database access...")
    
    try:
        from edge.src.components.health_monitor import HealthMonitor
        
        health_monitor = HealthMonitor()
        
        # Test database connection check
        if not health_monitor.initialize():
            print("❌ HealthMonitor initialization failed")
            return False
        
        # Test database connectivity check
        db_ok = health_monitor.check_database_connection()
        if not db_ok:
            print("❌ Health monitor database connection check failed")
            return False
        
        print("✅ Health monitor database validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Health monitor database validation failed: {e}")
        return False


def validate_storage_monitor_database():
    """Validate that storage monitor can access database."""
    print("🔍 Validating storage monitor database access...")
    
    try:
        from edge.src.components.storage_monitor import StorageMonitor
        
        storage_monitor = StorageMonitor()
        
        # Test get_files_by_status method
        try:
            sent_files, unsent_files = storage_monitor.get_files_by_status()
            print("✅ Storage monitor database access working")
            return True
        except Exception as e:
            print(f"❌ Storage monitor database access failed: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Storage monitor validation failed: {e}")
        return False


def main():
    """Main validation function."""
    print("🚀 Starting Database Validation for AI Camera v1.3...")
    print(f"📋 Database path: {DATABASE_PATH}")
    
    all_passed = True
    
    # Run all validations
    if not validate_database_schema():
        all_passed = False
    
    if not validate_database_manager():
        all_passed = False
    
    if not validate_health_monitor_database():
        all_passed = False
    
    if not validate_storage_monitor_database():
        all_passed = False
    
    # Summary
    print("\n" + "="*50)
    if all_passed:
        print("✅ All database validations passed!")
        print("🎉 Database is ready for production use")
        return 0
    else:
        print("❌ Some database validations failed")
        print("🔧 Please run the database initialization script:")
        print("   python edge/scripts/init_database.py")
        return 1


if __name__ == "__main__":
    sys.exit(main())
