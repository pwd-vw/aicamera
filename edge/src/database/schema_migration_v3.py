#!/usr/bin/env python3
"""
Database Schema Migration v3 for AI Camera v2.0

This migration adds the original_image_path column to support the complete
image storage pipeline with 4 image types:
1. Original captured image
2. Vehicle detection image  
3. Plate detection image
4. Cropped plates

Migration Changes:
- Add original_image_path column to detection_results table
- Ensure all image path columns are properly indexed
- Maintain backward compatibility with existing data

Author: AI Camera Team
Version: 2.0
Date: August 2025
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import sys
import os

# Simple logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path - relative to project root
def get_database_path():
    """Get the database path relative to the project root."""
    # Go up from src/database to project root
    project_root = Path(__file__).parent.parent.parent.parent
    return project_root / "edge" / "db" / "lpr_data.db"


class SchemaMigrationV3:
    """
    Database Schema Migration v3 for complete image storage support.
    
    This migration adds support for storing the original image path
    to complete the 4-image storage pipeline.
    """
    
    def __init__(self, database_path: str = None, logger=None):
        """
        Initialize schema migration.
    
    Args:
            database_path: Path to SQLite database file
        logger: Logger instance
        """
        self.database_path = database_path or str(get_database_path())
        self.logger = logger or logging.getLogger(__name__)
        self.connection = None
    
    def connect(self) -> bool:
        """
        Connect to the database.
    
    Returns:
            bool: True if connection successful
        """
        try:
            # Ensure database directory exists
            Path(self.database_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False
    
    def check_migration_needed(self) -> bool:
        """
        Check if migration is needed by looking for original_image_path column.
        
        Returns:
            bool: True if migration is needed
        """
        try:
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA table_info(detection_results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Check if original_image_path column exists
            if 'original_image_path' not in columns:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking migration status: {e}")
            return False
    
    def backup_database(self) -> bool:
        """
        Create a backup of the database before migration.
        
        Returns:
            bool: True if backup successful
        """
        try:
            backup_path = f"{self.database_path}.backup_v3_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup by copying the database file
            import shutil
            shutil.copy2(self.database_path, backup_path)
            
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False
    
    def run_migration(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            bool: True if migration successful
        """
        try:
            if not self.connect():
                return False
            
            # Check if migration is needed
            if not self.check_migration_needed():
                self.logger.info("Migration v3 not needed - original_image_path column already exists")
                return True
            
            self.logger.info("Starting schema migration v3...")
            
            # Create backup
            if not self.backup_database():
                self.logger.warning("Failed to create backup, but continuing with migration")
            
            cursor = self.connection.cursor()
            
            # Add original_image_path column
            try:
                cursor.execute("ALTER TABLE detection_results ADD COLUMN original_image_path TEXT")
                self.logger.info("Added original_image_path column to detection_results table")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    self.logger.info("original_image_path column already exists")
                else:
                    raise
            
            # Create indexes for better query performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_original_image_path ON detection_results(original_image_path)",
                "CREATE INDEX IF NOT EXISTS idx_vehicle_detected_image_path ON detection_results(vehicle_detected_image_path)",
                "CREATE INDEX IF NOT EXISTS idx_plate_image_path ON detection_results(plate_image_path)"
            ]
            
            for sql in indexes:
                cursor.execute(sql)
                self.logger.debug(f"Created index: {sql}")
            
            # Update schema version
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    description TEXT
                )
            """)
            
            cursor.execute("""
                INSERT OR REPLACE INTO schema_version (version, description)
                VALUES (3, 'Complete image storage pipeline with original_image_path support')
            """)
            
            self.connection.commit()
            self.logger.info("Schema migration v3 completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema migration v3 failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def verify_migration(self) -> bool:
        """
        Verify that the migration was successful.
        
        Returns:
            bool: True if verification successful
        """
        try:
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            
            # Check if original_image_path column exists
        cursor.execute("PRAGMA table_info(detection_results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = [
                'original_image_path'
            ]
            
            missing_columns = [col for col in required_columns if col not in columns]
            
            if missing_columns:
                self.logger.error(f"Missing required columns after migration: {missing_columns}")
                return False
            
            # Check if indexes exist
            cursor.execute("PRAGMA index_list(detection_results)")
            indexes = [row[1] for row in cursor.fetchall()]
            
            required_indexes = [
                'idx_original_image_path',
                'idx_vehicle_detected_image_path',
                'idx_plate_image_path'
            ]
            
            missing_indexes = [idx for idx in required_indexes if idx not in indexes]
            
            if missing_indexes:
                self.logger.warning(f"Missing indexes after migration: {missing_indexes}")
            
            self.logger.info("Migration v3 verification completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration verification failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up database connection."""
        if self.connection:
            self.connection.close()


def main():
    """Run the migration."""
    logger.info("=== Database Schema Migration v3 ===")
    
    migration = SchemaMigrationV3()
    
    try:
        # Run migration
        if migration.run_migration():
            # Verify migration
            if migration.verify_migration():
                logger.info("✅ Migration v3 completed and verified successfully")
                return 0
            else:
                logger.error("❌ Migration v3 verification failed")
                return 1
        else:
            logger.error("❌ Migration v3 failed")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Migration v3 error: {e}")
        return 1
    finally:
        migration.cleanup()


if __name__ == "__main__":
    exit(main())
