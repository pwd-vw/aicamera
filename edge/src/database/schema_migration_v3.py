#!/usr/bin/env python3
"""
Database Schema Migration v3 for AI Camera v1.3

This migration adds the image_path column to the detection_results table
and ensures proper path structure for captured images.

Changes:
- Add image_path column to detection_results table
- Update path structure to use /edge/captured_images/
- Ensure backward compatibility with existing data

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sqlite3
import os
import logging
from pathlib import Path
from datetime import datetime

def migrate_database(database_path: str, logger=None):
    """
    Migrate database to schema version 3.
    
    Args:
        database_path: Path to the SQLite database
        logger: Logger instance
    
    Returns:
        bool: True if migration successful, False otherwise
    """
    if logger is None:
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
    
    try:
        logger.info("Starting database migration to schema v3")
        
        # Connect to database
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Check if image_path column already exists
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_path' not in columns:
            logger.info("Adding image_path column to detection_results table")
            
            # Add image_path column
            cursor.execute("""
                ALTER TABLE detection_results 
                ADD COLUMN image_path TEXT DEFAULT NULL
            """)
            
            # Update existing records to have proper image_path
            cursor.execute("""
                UPDATE detection_results 
                SET image_path = CASE 
                    WHEN annotated_image_path IS NOT NULL AND annotated_image_path != '' 
                    THEN 'edge/captured_images/' || SUBSTR(annotated_image_path, INSTR(annotated_image_path, '/') + 1)
                    ELSE NULL 
                END
                WHERE image_path IS NULL
            """)
            
            logger.info("Updated existing records with proper image_path")
        else:
            logger.info("image_path column already exists")
        
        # Create captured_images directory if it doesn't exist
        # Get the project root directory (parent of the database directory)
        project_root = Path(database_path).parent.parent.parent
        captured_images_dir = project_root / "edge" / "captured_images"
        captured_images_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ensured captured_images directory exists: {captured_images_dir}")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'image_path' in columns:
            logger.info("✅ Database migration to schema v3 completed successfully")
            conn.close()
            return True
        else:
            logger.error("❌ Database migration failed - image_path column not found")
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"❌ Database migration failed: {e}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    # Test migration
    # Use relative path from project root
    import os
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    database_path = os.path.join(project_root, "edge", "db", "lpr_data.db")
    success = migrate_database(database_path)
    print(f"Migration {'successful' if success else 'failed'}")
