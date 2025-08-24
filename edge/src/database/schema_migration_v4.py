#!/usr/bin/env python3
"""
Database Schema Migration v4 - Update Detection Results Table

This migration updates the detection_results table to use new field names:
- annotated_image_path -> vehicle_detected_image_path
- image_path -> plate_image_path

Author: AI Camera Team
Version: 4.0
Date: August 2025
"""

import sqlite3
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from edge.src.core.config import DATABASE_PATH
from edge.src.core.utils.logging_config import get_logger

logger = get_logger(__name__)


def migrate_detection_results_table():
    """
    Migrate detection_results table to use new field names.
    """
    try:
        if not DATABASE_PATH or not os.path.exists(DATABASE_PATH):
            logger.error(f"Database not found: {DATABASE_PATH}")
            return False
        
        logger.info(f"Starting migration for database: {DATABASE_PATH}")
        
        # Connect to database
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        # Check if old columns exist
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        logger.info(f"Current columns: {columns}")
        
        # Check if migration is needed
        if 'annotated_image_path' in columns and 'vehicle_detected_image_path' not in columns:
            logger.info("Migration needed: updating field names...")
            
            # Add new columns
            cursor.execute("ALTER TABLE detection_results ADD COLUMN vehicle_detected_image_path TEXT")
            cursor.execute("ALTER TABLE detection_results ADD COLUMN plate_image_path TEXT")
            
            # Copy data from old columns to new columns
            cursor.execute("""
                UPDATE detection_results 
                SET vehicle_detected_image_path = annotated_image_path,
                    plate_image_path = image_path
                WHERE vehicle_detected_image_path IS NULL
            """)
            
            # Drop old columns (SQLite doesn't support DROP COLUMN, so we'll keep them for now)
            # In a production environment, you might want to recreate the table
            logger.info("Migration completed: new columns added and data copied")
            
        elif 'vehicle_detected_image_path' in columns:
            logger.info("Migration already completed: new columns exist")
        else:
            logger.info("No migration needed: table structure is current")
        
        connection.commit()
        connection.close()
        
        logger.info("Database migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def verify_migration():
    """
    Verify that the migration was successful.
    """
    try:
        if not DATABASE_PATH or not os.path.exists(DATABASE_PATH):
            logger.error(f"Database not found: {DATABASE_PATH}")
            return False
        
        connection = sqlite3.connect(DATABASE_PATH)
        cursor = connection.cursor()
        
        # Check table structure
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        logger.info(f"Final table columns: {columns}")
        
        # Verify new columns exist
        required_columns = ['vehicle_detected_image_path', 'plate_image_path']
        missing_columns = [col for col in required_columns if col not in columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return False
        
        # Check if there's data in the new columns
        cursor.execute("SELECT COUNT(*) FROM detection_results WHERE vehicle_detected_image_path IS NOT NULL")
        vehicle_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM detection_results WHERE plate_image_path IS NOT NULL")
        plate_count = cursor.fetchone()[0]
        
        logger.info(f"Records with vehicle_detected_image_path: {vehicle_count}")
        logger.info(f"Records with plate_image_path: {plate_count}")
        
        connection.close()
        
        logger.info("Migration verification completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Database Schema Migration v4 - Detection Results Table Update")
    print("=" * 60)
    
    # Run migration
    if migrate_detection_results_table():
        print("✅ Migration completed successfully")
        
        # Verify migration
        if verify_migration():
            print("✅ Migration verification passed")
            print("\n🎉 Database schema updated successfully!")
            print("\nNew field names:")
            print("  - vehicle_detected_image_path (was annotated_image_path)")
            print("  - plate_image_path (was image_path)")
        else:
            print("❌ Migration verification failed")
            sys.exit(1)
    else:
        print("❌ Migration failed")
        sys.exit(1)
