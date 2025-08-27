#!/usr/bin/env python3
"""
Cleanup script for detection data
Removes all files from captured_images folder and clears detection_results table
"""

import os
import sqlite3
import shutil
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def cleanup_captured_images():
    """Remove all files from captured_images folder"""
    captured_images_dir = Path("captured_images")
    
    if not captured_images_dir.exists():
        logger.info("captured_images directory does not exist")
        return 0
    
    # Count files before deletion
    image_files = list(captured_images_dir.glob("*.jpg")) + list(captured_images_dir.glob("*.png")) + list(captured_images_dir.glob("*.jpeg"))
    file_count = len(image_files)
    
    if file_count == 0:
        logger.info("No image files found in captured_images directory")
        return 0
    
    logger.info(f"Found {file_count} image files to remove")
    
    # Remove all files
    for file_path in image_files:
        try:
            file_path.unlink()
            logger.debug(f"Removed: {file_path}")
        except Exception as e:
            logger.error(f"Failed to remove {file_path}: {e}")
    
    logger.info(f"Successfully removed {file_count} image files from captured_images")
    return file_count

def cleanup_database():
    """Clear all records from detection_results table"""
    db_path = "db/lpr_data.db"
    
    if not os.path.exists(db_path):
        logger.error(f"Database file not found: {db_path}")
        return 0
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count records before deletion
        cursor.execute("SELECT COUNT(*) FROM detection_results")
        record_count = cursor.fetchone()[0]
        
        if record_count == 0:
            logger.info("No records found in detection_results table")
            return 0
        
        logger.info(f"Found {record_count} records to remove from detection_results table")
        
        # Clear all records
        cursor.execute("DELETE FROM detection_results")
        conn.commit()
        
        # Reset auto-increment counter
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='detection_results'")
        conn.commit()
        
        logger.info(f"Successfully removed {record_count} records from detection_results table")
        conn.close()
        return record_count
        
    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        return 0

def main():
    """Main cleanup function"""
    logger.info("Starting detection data cleanup...")
    
    # Cleanup captured_images
    files_removed = cleanup_captured_images()
    
    # Cleanup database
    records_removed = cleanup_database()
    
    # Summary
    logger.info("=" * 50)
    logger.info("CLEANUP SUMMARY:")
    logger.info(f"Files removed from captured_images: {files_removed}")
    logger.info(f"Records removed from database: {records_removed}")
    logger.info("=" * 50)
    
    if files_removed > 0 or records_removed > 0:
        logger.info("Cleanup completed successfully!")
    else:
        logger.info("No data found to clean up")

if __name__ == "__main__":
    main()
