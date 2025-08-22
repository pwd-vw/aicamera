#!/usr/bin/env python3
"""
Database Schema Migration v2 for AI Camera v1.3

This migration adds enhanced OCR result storage to support both
Hailo OCR and EasyOCR results for better Thai license plate recognition.

Migration Changes:
- Add separate columns for Hailo OCR and EasyOCR results
- Add OCR performance metrics
- Add best result selection metadata
- Maintain backward compatibility with existing data

Author: AI Camera Team
Version: 1.3
Date: August 2025
"""

import sqlite3
import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

from edge.src.core.utils.logging_config import get_logger
from edge.src.core.config import DATABASE_PATH

logger = get_logger(__name__)


class SchemaMigrationV2:
    """
    Database Schema Migration v2 for enhanced OCR support.
    
    This migration adds support for storing results from both Hailo OCR
    and EasyOCR simultaneously, enabling better comparison and analysis
    of OCR performance for Thai license plates.
    """
    
    def __init__(self, database_path: str = None, logger=None):
        """
        Initialize schema migration.
        
        Args:
            database_path: Path to SQLite database file
            logger: Logger instance
        """
        self.database_path = database_path or DATABASE_PATH
        self.logger = logger or get_logger(__name__)
        self.connection = None
    
    def connect(self) -> bool:
        """
        Connect to the database.
        
        Returns:
            bool: True if connection successful
        """
        try:
            self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            return False
    
    def check_migration_needed(self) -> bool:
        """
        Check if migration is needed by looking for new columns.
        
        Returns:
            bool: True if migration is needed
        """
        try:
            if not self.connection:
                return False
            
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA table_info(detection_results)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Check if new columns exist
            new_columns = [
                'hailo_ocr_results', 'easyocr_results', 'best_ocr_method',
                'ocr_processing_time_ms', 'parallel_ocr_success'
            ]
            
            for column in new_columns:
                if column not in columns:
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
            backup_path = f"{self.database_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup using SQLite backup API
            backup_conn = sqlite3.connect(backup_path)
            self.connection.backup(backup_conn)
            backup_conn.close()
            
            self.logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            return False
    
    def migrate_schema(self) -> bool:
        """
        Perform the schema migration.
        
        Returns:
            bool: True if migration successful
        """
        try:
            cursor = self.connection.cursor()
            
            # Add new columns for enhanced OCR support
            new_columns = [
                # Hailo OCR results (JSON)
                "ALTER TABLE detection_results ADD COLUMN hailo_ocr_results TEXT DEFAULT NULL",
                
                # EasyOCR results (JSON) 
                "ALTER TABLE detection_results ADD COLUMN easyocr_results TEXT DEFAULT NULL",
                
                # Best OCR method selected (hailo/easyocr/none)
                "ALTER TABLE detection_results ADD COLUMN best_ocr_method TEXT DEFAULT NULL",
                
                # OCR processing time in milliseconds
                "ALTER TABLE detection_results ADD COLUMN ocr_processing_time_ms REAL DEFAULT 0.0",
                
                # Whether parallel OCR was successful
                "ALTER TABLE detection_results ADD COLUMN parallel_ocr_success BOOLEAN DEFAULT 0",
                
                # OCR confidence scores
                "ALTER TABLE detection_results ADD COLUMN hailo_ocr_confidence REAL DEFAULT 0.0",
                "ALTER TABLE detection_results ADD COLUMN easyocr_confidence REAL DEFAULT 0.0",
                
                # OCR processing statistics
                "ALTER TABLE detection_results ADD COLUMN hailo_processing_time_ms REAL DEFAULT 0.0",
                "ALTER TABLE detection_results ADD COLUMN easyocr_processing_time_ms REAL DEFAULT 0.0",
                
                # OCR error information
                "ALTER TABLE detection_results ADD COLUMN hailo_ocr_error TEXT DEFAULT NULL",
                "ALTER TABLE detection_results ADD COLUMN easyocr_error TEXT DEFAULT NULL"
            ]
            
            for sql in new_columns:
                try:
                    cursor.execute(sql)
                    self.logger.debug(f"Added column: {sql}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" in str(e).lower():
                        self.logger.debug(f"Column already exists, skipping: {sql}")
                    else:
                        raise
            
            # Create indexes for better query performance
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_best_ocr_method ON detection_results(best_ocr_method)",
                "CREATE INDEX IF NOT EXISTS idx_parallel_ocr_success ON detection_results(parallel_ocr_success)",
                "CREATE INDEX IF NOT EXISTS idx_hailo_confidence ON detection_results(hailo_ocr_confidence)",
                "CREATE INDEX IF NOT EXISTS idx_easyocr_confidence ON detection_results(easyocr_confidence)"
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
                VALUES (2, 'Enhanced OCR support with Hailo and EasyOCR parallel processing')
            """)
            
            self.connection.commit()
            self.logger.info("Schema migration v2 completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema migration failed: {e}")
            if self.connection:
                self.connection.rollback()
            return False
    
    def migrate_existing_data(self) -> bool:
        """
        Migrate existing OCR data to new schema format.
        
        This method converts existing ocr_results JSON to the new format
        with separate Hailo and EasyOCR fields.
        
        Returns:
            bool: True if data migration successful
        """
        try:
            cursor = self.connection.cursor()
            
            # Get all records with existing OCR data
            cursor.execute("""
                SELECT id, ocr_results 
                FROM detection_results 
                WHERE ocr_results IS NOT NULL 
                AND ocr_results != ''
                AND ocr_results != '[]'
                AND hailo_ocr_results IS NULL
            """)
            
            records = cursor.fetchall()
            migrated_count = 0
            
            for record in records:
                try:
                    record_id = record['id']
                    ocr_results_json = record['ocr_results']
                    
                    # Parse existing OCR results
                    ocr_results = json.loads(ocr_results_json)
                    
                    if not isinstance(ocr_results, list) or len(ocr_results) == 0:
                        continue
                    
                    # Process each OCR result
                    hailo_results = []
                    easyocr_results = []
                    best_method = 'unknown'
                    
                    for ocr_result in ocr_results:
                        if isinstance(ocr_result, dict):
                            ocr_method = ocr_result.get('ocr_method', 'unknown')
                            
                            if ocr_method == 'hailo':
                                hailo_results.append(ocr_result)
                            elif ocr_method == 'easyocr':
                                easyocr_results.append(ocr_result)
                            
                            # Determine best method based on confidence
                            if not best_method or best_method == 'unknown':
                                best_method = ocr_method
                    
                    # Update record with migrated data
                    cursor.execute("""
                        UPDATE detection_results 
                        SET hailo_ocr_results = ?,
                            easyocr_results = ?,
                            best_ocr_method = ?
                        WHERE id = ?
                    """, (
                        json.dumps(hailo_results) if hailo_results else None,
                        json.dumps(easyocr_results) if easyocr_results else None,
                        best_method if best_method != 'unknown' else None,
                        record_id
                    ))
                    
                    migrated_count += 1
                    
                except Exception as e:
                    self.logger.warning(f"Failed to migrate record {record_id}: {e}")
                    continue
            
            self.connection.commit()
            self.logger.info(f"Migrated {migrated_count} existing OCR records")
            return True
            
        except Exception as e:
            self.logger.error(f"Data migration failed: {e}")
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
                self.logger.info("Schema migration v2 not needed - already up to date")
                return True
            
            self.logger.info("Starting schema migration v2...")
            
            # Create backup
            if not self.backup_database():
                self.logger.warning("Backup failed, but continuing with migration")
            
            # Perform schema migration
            if not self.migrate_schema():
                return False
            
            # Migrate existing data
            if not self.migrate_existing_data():
                self.logger.warning("Data migration had issues, but schema migration completed")
            
            self.logger.info("Schema migration v2 completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Migration process failed: {e}")
            return False
        
        finally:
            if self.connection:
                self.connection.close()


def run_migration(database_path: str = None) -> bool:
    """
    Run the schema migration v2.
    
    Args:
        database_path: Path to database file
        
    Returns:
        bool: True if migration successful
    """
    migration = SchemaMigrationV2(database_path)
    return migration.run_migration()


if __name__ == '__main__':
    # Run migration when executed directly
    success = run_migration()
    if success:
        print("✅ Schema migration v2 completed successfully")
    else:
        print("❌ Schema migration v2 failed")
        exit(1)
