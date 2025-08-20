#!/usr/bin/env python3
"""
Update Sample Data Images Script for AI Camera v1.3

This script updates the existing sample detection records to use
actual image files from the captured_images folder.

Features:
- Updates annotated_image_path to use real images
- Updates cropped_plates_paths to use real images
- Maintains existing detection data structure
- Uses car_det_results.png and car_rec_results.png

Usage:
    python3 update_sample_data_images.py

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sys
import sqlite3
import json
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Image files in captured_images
CAPTURED_IMAGES = [
    'car_det_results.png',
    'car_rec_results.png'
]

class ImageUpdater:
    """Update sample data with real image paths."""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # Correct database path
            db_path = project_root / 'db' / 'lpr_data.db'
        
        self.db_path = Path(db_path)
        self.connection = None
        self.captured_images_dir = project_root / 'captured_images'
    
    def initialize(self):
        """Initialize database connection."""
        try:
            # Connect to database
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            
            print(f"✅ Database connected: {self.db_path}")
            
            # Check if captured_images directory exists
            if not self.captured_images_dir.exists():
                print(f"❌ Captured images directory not found: {self.captured_images_dir}")
                return False
            
            # Check if image files exist
            for img_file in CAPTURED_IMAGES:
                img_path = self.captured_images_dir / img_file
                if not img_path.exists():
                    print(f"❌ Image file not found: {img_path}")
                    return False
                else:
                    print(f"✅ Found image: {img_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize: {e}")
            return False
    
    def get_all_records(self):
        """Get all detection records from database."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM detection_results ORDER BY id")
            return cursor.fetchall()
        except Exception as e:
            print(f"❌ Error getting records: {e}")
            return []
    
    def update_record_images(self, record_id, record_data):
        """Update a single record with real image paths."""
        try:
            # Choose random image for annotated image
            annotated_image = random.choice(CAPTURED_IMAGES)
            annotated_image_path = f"captured_images/{annotated_image}"
            
            # Parse existing cropped plates paths
            cropped_plates_paths = json.loads(record_data['cropped_plates_paths'])
            
            # Update cropped plates paths to use real images
            updated_cropped_paths = []
            for i, old_path in enumerate(cropped_plates_paths):
                # Choose random image for each plate
                plate_image = random.choice(CAPTURED_IMAGES)
                new_path = f"captured_images/{plate_image}"
                updated_cropped_paths.append(new_path)
            
            # Update database
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE detection_results 
                SET annotated_image_path = ?, cropped_plates_paths = ?
                WHERE id = ?
            """, (
                annotated_image_path,
                json.dumps(updated_cropped_paths),
                record_id
            ))
            
            self.connection.commit()
            
            print(f"✅ Updated record {record_id}:")
            print(f"   Annotated: {annotated_image_path}")
            print(f"   Cropped plates: {len(updated_cropped_paths)} images")
            
            return True
            
        except Exception as e:
            print(f"❌ Error updating record {record_id}: {e}")
            return False
    
    def update_all_records(self):
        """Update all records with real image paths."""
        try:
            print("📊 Getting all detection records...")
            records = self.get_all_records()
            
            if not records:
                print("❌ No records found to update")
                return False
            
            print(f"📝 Found {len(records)} records to update")
            
            updated_count = 0
            for record in records:
                if self.update_record_images(record['id'], record):
                    updated_count += 1
            
            print(f"✅ Successfully updated {updated_count}/{len(records)} records")
            return True
            
        except Exception as e:
            print(f"❌ Error updating records: {e}")
            return False
    
    def show_statistics(self):
        """Show updated statistics."""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_detections,
                    SUM(vehicles_count) as total_vehicles,
                    SUM(plates_count) as total_plates,
                    AVG(processing_time_ms) as avg_processing_time_ms,
                    MAX(timestamp) as last_detection
                FROM detection_results
            """)
            
            row = cursor.fetchone()
            if row:
                print("📈 Updated Database Statistics:")
                print(f"  Total detections: {row['total_detections'] or 0}")
                print(f"  Total vehicles: {row['total_vehicles'] or 0}")
                print(f"  Total plates: {row['total_plates'] or 0}")
                print(f"  Average processing time: {row['avg_processing_time_ms'] or 0:.1f}ms")
                print(f"  Last detection: {row['last_detection']}")
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
    
    def cleanup(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("✅ Database connection closed")

def main():
    """Main function."""
    print("🖼️  AI Camera v1.3 - Update Sample Data Images")
    print("=" * 50)
    
    try:
        # Initialize updater
        updater = ImageUpdater()
        
        if not updater.initialize():
            print("❌ Failed to initialize image updater")
            return 1
        
        # Update all records
        if updater.update_all_records():
            print("✅ Image update completed successfully!")
            
            # Show statistics
            updater.show_statistics()
            
            print("")
            print("You can now test the detection results UI with real images:")
            print("  http://localhost/detection/")
            print("")
            print("Updated features:")
            print("  - Real annotated images from captured_images/")
            print("  - Real cropped plate images")
            print("  - Maintained all detection data and statistics")
        else:
            print("❌ Image update failed!")
            return 1
        
        # Cleanup
        updater.cleanup()
        
    except KeyboardInterrupt:
        print("⏹️  Operation cancelled by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
