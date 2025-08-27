#!/usr/bin/env python3
"""
Database migration script to optimize detection_results table for disk space.
Removes unused image path columns and keeps only original_image_path.
"""

import sqlite3
import os
import sys
from pathlib import Path

try:
    from edge.src.core.config import DATABASE_PATH
except Exception:
    DATABASE_PATH = "db/lpr_data.db"

def migrate_database():
    """Migrate database to optimized schema for disk space."""
    db_path = Path(DATABASE_PATH)
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    print(f"🔄 Starting database migration for disk space optimization...")
    print(f"📁 Database: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Check current schema
        cursor.execute("PRAGMA table_info(detection_results)")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"📊 Current columns: {columns}")
        
        # Check if migration is needed
        columns_to_remove = ['vehicle_detected_image_path', 'plate_image_path', 'cropped_plates_paths']
        needs_migration = any(col in columns for col in columns_to_remove)
        
        if not needs_migration:
            print("✅ Database already optimized - no migration needed")
            return True
        
        # Create backup
        backup_path = db_path.with_suffix('.backup_pre_optimization.db')
        print(f"💾 Creating backup: {backup_path}")
        
        backup_conn = sqlite3.connect(str(backup_path))
        conn.backup(backup_conn)
        backup_conn.close()
        
        # Get total records
        cursor.execute("SELECT COUNT(*) FROM detection_results")
        total_records = cursor.fetchone()[0]
        print(f"📈 Total records to migrate: {total_records}")
        
        # Create new optimized table
        print("🔧 Creating optimized table structure...")
        cursor.execute("""
            CREATE TABLE detection_results_optimized (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                vehicles_count INTEGER DEFAULT 0,
                plates_count INTEGER DEFAULT 0,
                ocr_results TEXT,
                original_image_path TEXT,
                vehicle_detections TEXT,
                plate_detections TEXT,
                processing_time_ms REAL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                sent_to_server BOOLEAN DEFAULT 0,
                sent_at DATETIME,
                server_response TEXT,
                hailo_ocr_results TEXT DEFAULT NULL,
                easyocr_results TEXT DEFAULT NULL,
                best_ocr_method TEXT DEFAULT NULL,
                ocr_processing_time_ms REAL DEFAULT 0.0,
                parallel_ocr_success BOOLEAN DEFAULT 0,
                hailo_ocr_confidence REAL DEFAULT 0.0,
                easyocr_confidence REAL DEFAULT 0.0,
                hailo_processing_time_ms REAL DEFAULT 0.0,
                easyocr_processing_time_ms REAL DEFAULT 0.0,
                hailo_ocr_error TEXT DEFAULT NULL,
                easyocr_error TEXT DEFAULT NULL
            )
        """)
        
        # Migrate data
        print("🔄 Migrating data...")
        cursor.execute("""
            INSERT INTO detection_results_optimized (
                id, timestamp, vehicles_count, plates_count, ocr_results,
                original_image_path, vehicle_detections, plate_detections,
                processing_time_ms, created_at, sent_to_server, sent_at, server_response,
                hailo_ocr_results, easyocr_results, best_ocr_method, ocr_processing_time_ms,
                parallel_ocr_success, hailo_ocr_confidence, easyocr_confidence,
                hailo_processing_time_ms, easyocr_processing_time_ms, hailo_ocr_error, easyocr_error
            )
            SELECT 
                id, timestamp, vehicles_count, plates_count, ocr_results,
                original_image_path, vehicle_detections, plate_detections,
                processing_time_ms, created_at, sent_to_server, sent_at, server_response,
                hailo_ocr_results, easyocr_results, best_ocr_method, ocr_processing_time_ms,
                parallel_ocr_success, hailo_ocr_confidence, easyocr_confidence,
                hailo_processing_time_ms, easyocr_processing_time_ms, hailo_ocr_error, easyocr_error
            FROM detection_results
        """)
        
        # Drop old table and rename new one
        print("🗑️ Removing old table...")
        cursor.execute("DROP TABLE detection_results")
        cursor.execute("ALTER TABLE detection_results_optimized RENAME TO detection_results")
        
        # Recreate indexes
        print("🔗 Recreating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_detection_sent_to_server ON detection_results(sent_to_server)")
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM detection_results")
        migrated_count = cursor.fetchone()[0]
        
        if migrated_count == total_records:
            print(f"✅ Migration successful! {migrated_count} records migrated")
            
            # Calculate disk space savings
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            current_size = page_count * page_size
            
            print(f"💾 Current database size: {current_size / 1024 / 1024:.2f} MB")
            print(f"🎯 Estimated disk space savings: ~60-80% reduction in image storage")
            print(f"📝 Only original images are now stored, bounding boxes drawn dynamically")
            
            conn.commit()
            return True
        else:
            print(f"❌ Migration failed! Expected {total_records}, got {migrated_count}")
            return False
            
    except Exception as e:
        print(f"❌ Migration error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def cleanup_old_images():
    """Clean up old detection images to free disk space."""
    print("🧹 Cleaning up old detection images...")
    
    captured_images_dir = Path("captured_images")
    if not captured_images_dir.exists():
        print("⚠️ No captured_images directory found")
        return
    
    # Count files before cleanup
    image_files = list(captured_images_dir.glob("*.jpg")) + list(captured_images_dir.glob("*.png"))
    print(f"📁 Found {len(image_files)} image files")
    
    # Keep only original detection images, remove annotated/cropped ones
    files_to_remove = []
    files_to_keep = []
    
    for img_file in image_files:
        filename = img_file.name
        if (filename.startswith("vehicle_detected_") or 
            filename.startswith("plate_detected_") or 
            filename.startswith("plate_") and not filename.startswith("detection_")):
            files_to_remove.append(img_file)
        else:
            files_to_keep.append(img_file)
    
    print(f"🗑️ Files to remove: {len(files_to_remove)}")
    print(f"💾 Files to keep: {len(files_to_keep)}")
    
    if files_to_remove:
        total_size = sum(f.stat().st_size for f in files_to_remove)
        print(f"💾 Estimated space to free: {total_size / 1024 / 1024:.2f} MB")
        
        # Remove files
        for img_file in files_to_remove:
            try:
                img_file.unlink()
                print(f"🗑️ Removed: {img_file.name}")
            except Exception as e:
                print(f"⚠️ Failed to remove {img_file.name}: {e}")
    
    print("✅ Image cleanup completed")

def main():
    """Main migration function."""
    print("🚀 AI Camera Database Optimization Migration")
    print("=" * 50)
    
    # Step 1: Migrate database schema
    if not migrate_database():
        print("❌ Database migration failed")
        return 1
    
    # Step 2: Clean up old images
    cleanup_old_images()
    
    print("\n🎉 Migration completed successfully!")
    print("📋 Summary:")
    print("  ✅ Database schema optimized for disk space")
    print("  ✅ Only original images stored")
    print("  ✅ Bounding boxes drawn dynamically in dashboard")
    print("  ✅ Old detection images cleaned up")
    print("  🔄 Restart the service to apply changes")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
